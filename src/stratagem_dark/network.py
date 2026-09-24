# SPDX-License-Identifier: MIT
"""Create personal Wi-Fi profiles over NetworkManager D-Bus as the desktop user.

The QML panel sends credentials through stdin. No privileged helper or shell.
Existing enterprise profiles remain managed by NetworkManager's editor.
"""
import json
import os
import pwd
import sys
import time

BUS = 'org.freedesktop.NetworkManager'
BASE = '/org/freedesktop/NetworkManager'
PROPS = 'org.freedesktop.DBus.Properties'


def connect(request):
    if os.geteuid() == 0:
        raise ValueError('Connect as your desktop user.')
    ssid = request.get('ssid')
    secret = request.get('password', '')
    if not isinstance(ssid, str) or not 1 <= len(ssid.encode()) <= 32:
        raise ValueError('Choose a valid wireless network.')
    if not isinstance(secret, str) or len(secret) > 64 or '\n' in secret or '\0' in secret:
        raise ValueError('Invalid wireless password.')
    import dbus
    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object(BUS, BASE), BUS)
    username = pwd.getpwuid(os.geteuid()).pw_name
    candidates = []
    for device_path in manager.GetDevices():
        device = bus.get_object(BUS, device_path)
        props = dbus.Interface(device, PROPS)
        if int(props.Get(BUS+'.Device', 'DeviceType')) != 2:
            continue
        for ap_path in dbus.Interface(device, BUS+'.Device.Wireless').GetAllAccessPoints():
            ap = dbus.Interface(bus.get_object(BUS, ap_path), PROPS).GetAll(BUS+'.AccessPoint')
            if bytes(ap['Ssid']) == ssid.encode():
                candidates.append((int(ap['Strength']), device_path, ap_path))
    if not candidates:
        raise ValueError('Network is no longer visible. Scan and try again.')
    _, device_path, ap_path = max(candidates)
    # Reuse an owned saved profile, including its security/certificate settings.
    settings_api = dbus.Interface(bus.get_object(BUS, BASE+'/Settings'), BUS+'.Settings')
    profile = None
    for path in settings_api.ListConnections():
        candidate = dbus.Interface(bus.get_object(BUS, path), BUS+'.Settings.Connection')
        settings = candidate.GetSettings()
        if bytes(settings.get('802-11-wireless', {}).get('ssid', b'')) != ssid.encode():
            continue
        permissions = [str(x) for x in settings.get('connection', {}).get('permissions', [])]
        if 'user:'+username+':' not in permissions:
            continue
        if secret:
            security = settings.get('802-11-wireless-security', {})
            if security.get('key-mgmt') not in ('wpa-psk', 'sae'):
                raise ValueError('Use Advanced network settings for enterprise credentials.')
            security['psk'] = dbus.String(secret)
            settings['802-11-wireless-security'] = security
            candidate.Update(settings)
        profile = manager.ActivateConnection(path, device_path, ap_path)
        break
    if profile is None:
        # NM fills AP-specific fields, just as Quickshell's native path does.
        # The explicit permissions field makes this modify.own, not modify.system.
        settings = {'connection': dbus.Dictionary({
            'id': dbus.String(ssid),
            'permissions': dbus.Array(['user:'+username+':'], signature='s'),
        }, signature='sv')}
        if secret:
            settings['802-11-wireless-security'] = dbus.Dictionary({'psk': dbus.String(secret)}, signature='sv')
        _, profile = manager.AddAndActivateConnection(dbus.Dictionary(settings, signature='sa{sv}'), device_path, ap_path)
    state = dbus.Interface(bus.get_object(BUS, profile), PROPS)
    for _ in range(90):
        try:
            value = int(state.Get(BUS+'.Connection.Active', 'State'))
        except dbus.DBusException:
            raise ValueError('Connection ended. Check the password and network availability.') from None
        if value == 2:
            return 0
        if value == 4:
            raise ValueError('Connection failed. Check the password and network availability.')
        time.sleep(0.5)
    raise ValueError('Connection timed out. Check the network and try again.')


def main():
    try:
        request = json.loads(sys.stdin.readline(4096))
        if not isinstance(request, dict):
            raise ValueError('Invalid network request.')
        return connect(request)
    except Exception:
        # D-Bus errors may contain settings. Never print credentials or raw errors.
        print('Could not connect. Check the password, signal and network settings.')
        return 1
