#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Disposable QEMU live acceptance only: two simulated radios, WPA2 AP and DHCP.
set -euo pipefail
[[ -e /sys/firmware/qemu_fw_cfg/by_name/opt/stratagem/test/raw ]] || exit 2
work=$(mktemp -d)
cleanup() {
  [[ ! -f $work/hostapd.pid ]] || kill "$(cat "$work/hostapd.pid")" || true
  [[ ! -f $work/dnsmasq.pid ]] || kill "$(cat "$work/dnsmasq.pid")" || true
  for handle in $(nft -a list chain inet stratagem_dark input | awk '/comment "VM simulated WiFi"/ {print $NF}'); do
    nft delete rule inet stratagem_dark input handle "$handle" || true
  done
  rm -rf "$work"
}
trap cleanup EXIT
modprobe mac80211_hwsim radios=2
mapfile -t radios < <(iw dev | awk '$1=="Interface" {print $2}' | sort -V)
[[ ${#radios[@]} == 2 ]]
station=${radios[0]}; accesspoint=${radios[1]}
nmcli device set "$accesspoint" managed no
ip addr add 192.0.2.1/24 dev "$accesspoint"
ip link set "$accesspoint" up
cat > "$work/hostapd.conf" <<EOF
interface=$accesspoint
driver=nl80211
ssid=STRATAGEM-Test-WiFi
hw_mode=g
channel=1
wpa=2
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
wpa_passphrase=92739273
EOF
hostapd -B -P "$work/hostapd.pid" "$work/hostapd.conf"
# A confined DHCP allowance only on the simulated AP interface in this test VM.
nft insert rule inet stratagem_dark input iifname "$accesspoint" udp dport 67 accept comment 'VM simulated WiFi'
dnsmasq --conf-file=/dev/null --interface="$accesspoint" --bind-interfaces --port=0 --dhcp-range=192.0.2.20,192.0.2.30,255.255.255.0,1h --pid-file="$work/dnsmasq.pid"
nmcli radio wifi on
for attempt in $(seq 1 15); do
  nmcli device wifi rescan ifname "$station" || true
  if nmcli -t -f SSID device wifi list ifname "$station" | grep -qx STRATAGEM-Test-WiFi; then break; fi
  sleep 2
done
# Operate the actual panel from the desktop session. No test-only UI bypass.
ui() { runuser -u stratagem --preserve-environment -- "$@"; }
sleep 3
ui stratagem-shell stratagem.network open
sleep 3
ui hyprctl dispatch sendshortcut ', Down,'
ui hyprctl dispatch sendshortcut ', Return,'
sleep 1
ui grim /tmp/wifi-password.png
cp /tmp/wifi-password.png /mnt/test-results/wifi-password.png
for digit in 9 2 7 3 9 2 7 3; do
  ui hyprctl dispatch sendshortcut ", $digit,"
  sleep 0.1
done
ui hyprctl dispatch sendshortcut ', Return,'
for attempt in $(seq 1 60); do
  [[ $(nmcli -g GENERAL.STATE device show "$station") == 100* ]] && break
  sleep 1
done
ui grim /tmp/wifi-connected.png
cp /tmp/wifi-connected.png /mnt/test-results/wifi-connected.png
[[ $(nmcli -g GENERAL.STATE device show "$station") == 100* ]]
[[ $(nmcli -g connection.permissions connection show STRATAGEM-Test-WiFi) == user:stratagem* ]]
# Opening the panel must not disrupt an established connection.
ui stratagem-shell stratagem.network close
ui stratagem-shell stratagem.network open
sleep 3
[[ $(nmcli -g GENERAL.STATE device show "$station") == 100* ]]
# Reconnect with the native saved-profile path and no second password.
nmcli device disconnect "$station"
ui stratagem-shell stratagem.network close
ui stratagem-shell stratagem.network open
sleep 2
ui hyprctl dispatch sendshortcut ', Down,'
ui hyprctl dispatch sendshortcut ', Return,'
for attempt in $(seq 1 60); do
  [[ $(nmcli -g GENERAL.STATE device show "$station") == 100* ]] && break
  sleep 1
done
[[ $(nmcli -g GENERAL.STATE device show "$station") == 100* ]]
[[ $(nmcli -g NAME connection show | grep -cx STRATAGEM-Test-WiFi) == 1 ]]
echo 'Graphical private WPA2 creation, scan stability and saved reconnect passed.'
