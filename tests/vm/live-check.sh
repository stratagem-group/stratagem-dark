#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Only enabled when QEMU explicitly supplies opt/stratagem/test firmware data.
set -uo pipefail
mkdir -p /mnt/test-results
mount -t 9p -o trans=virtio,version=9p2000.L test-results /mnt/test-results || exit 1
exec > >(tee /mnt/test-results/live-check.log /dev/ttyS0) 2>&1
finish() {
  local status=$?
  journalctl -b --no-pager > /mnt/test-results/journal.log
  if ((status == 0)); then echo STRATAGEM_DARK_TEST_PASS; else echo STRATAGEM_DARK_TEST_FAIL; fi
  sync
  systemctl poweroff
}
trap finish EXIT
set -e
for i in $(seq 1 120); do
  if pgrep -u stratagem -x Hyprland >/dev/null && pgrep -u stratagem -x quickshell >/dev/null; then break; fi
  sleep 2
done
pgrep -u stratagem -x Hyprland
pgrep -u stratagem -x quickshell
uid=$(id -u stratagem)
export XDG_RUNTIME_DIR=/run/user/$uid
export STRATAGEM_DARK_PATH=/usr/share/stratagem
export WAYLAND_DISPLAY=$(basename "$(find "$XDG_RUNTIME_DIR" -maxdepth 1 -type s -name 'wayland-*' | head -n1)")
export HYPRLAND_INSTANCE_SIGNATURE=$(find "$XDG_RUNTIME_DIR/hypr" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | head -n1)
runuser -u stratagem --preserve-environment -- hyprctl configerrors | tee /mnt/test-results/hyprland-errors.txt
# hyprctl emits blank lines even when there are no configuration errors.
test -z "$(tr -d '[:space:]' < /mnt/test-results/hyprland-errors.txt)"
# A process existing does not mean its QML engine and IPC endpoint are ready.
ready=0
for attempt in $(seq 1 30); do
  if runuser -u stratagem --preserve-environment -- stratagem-shell shell ping 2>/dev/null | grep -qx ok; then
    ready=1
    break
  fi
  sleep 1
done
test "$ready" = 1
runuser -u stratagem --preserve-environment -- foot --check-config
runuser -u stratagem --preserve-environment -- foot sh -c 'printf "STRATAGEM DARK\nSecurity workstation testing session\n\n"; dark --version; printf "\nBlackArch tools:\n"; capa --version; sleep 120' &
sleep 5
runuser -u stratagem --preserve-environment -- grim /tmp/stratagem-desktop.png
cp /tmp/stratagem-desktop.png /mnt/test-results/desktop.png
runuser -u stratagem --preserve-environment -- stratagem-shell shell summon stratagem.menu '{}'
sleep 2
runuser -u stratagem --preserve-environment -- grim /tmp/stratagem-menu.png
cp /tmp/stratagem-menu.png /mnt/test-results/menu.png
capa --version
yara --version
tcpdump --version
dark validate
# Idempotence: a second setup preserves all user configuration.
runuser -u stratagem -- dark setup --apply > /mnt/test-results/setup-repeat.json
python - <<'PY'
import json
x=json.load(open('/mnt/test-results/setup-repeat.json'))
assert not x['created'], x
PY
! systemctl is-active sshd.service
! systemctl is-enabled sshd.service
! sudo -l -U stratagem 2>/dev/null | grep -q NOPASSWD
ss -lntup > /mnt/test-results/listeners.txt
pacman -Q > /mnt/test-results/packages.txt

systemctl is-active stratagem-dark-firewall.service
nft -j list table inet stratagem_dark > /mnt/test-results/firewall.json
python - <<'VERIFY'
import json
from pathlib import Path
chains = {item['chain']['name']: item['chain'] for item in json.load(open('/mnt/test-results/firewall.json'))['nftables'] if 'chain' in item}
assert chains['input']['policy'] == 'drop'
assert chains['forward']['policy'] == 'drop'
for line in Path('/mnt/test-results/listeners.txt').read_text().splitlines()[1:]:
    fields = line.split()
    endpoint = fields[4]
    address, port = endpoint.rsplit(':', 1)
    if fields[0] == 'udp' and port in {'68', '546'}:
        continue
    assert address.startswith('127.') or address in {'[::1]', '::1'}, line
VERIFY

# Regression gates from physical live testing: firmware, auth agent, shortcuts and actual tools.
find /usr/lib/firmware -name 'iwlwifi*' -print -quit | grep -q .
runuser -u stratagem --preserve-environment -- systemctl --user is-active hyprpolkitagent.service
runuser -u stratagem --preserve-environment -- hyprctl -j binds > /mnt/test-results/bindings.json
runuser -u stratagem --preserve-environment -- nmcli general permissions > /mnt/test-results/network-permissions.txt
opencode --version > /mnt/test-results/agent-version.txt
python - <<'DESKTOP'
import json,subprocess
from pathlib import Path
bindings=json.load(open('/mnt/test-results/bindings.json'))
for key,description in [('K','Keyboard shortcuts'),('A','New authorized engagement'),('T','Tool cheat sheet')]:
    matches=[x for x in bindings if x.get('key')==key and x.get('modmask')==64]
    assert len(matches)==1 and matches[0].get('description')==description, matches

DESKTOP
python /usr/lib/stratagem-dark/check-tools.py /mnt/test-results/tools.json --user stratagem
runuser -u stratagem --preserve-environment -- stratagem-shell shell summon stratagem.menu '{"menu":"apps"}'
sleep 2
runuser -u stratagem --preserve-environment -- grim /tmp/stratagem-apps.png
cp /tmp/stratagem-apps.png /mnt/test-results/apps.png

runuser -u stratagem --preserve-environment -- stratagem-shell applications list > /mnt/test-results/applications.json
python - <<'APPS'
import json
rows=json.load(open('/mnt/test-results/applications.json'))
assert len(rows)>5, rows
ids=[r['id'].removesuffix('.desktop') for r in rows]
assert len(ids)==len(set(ids)), rows
assert sum(r['name'].lower()=='foot' for r in rows)<=1, rows
APPS

runuser -u stratagem -- python /usr/lib/stratagem-dark/desktop-ui-test.py > /tmp/desktop-ui.log 2>&1 || { cat /tmp/desktop-ui.log; exit 1; }
cp /tmp/desktop-ui.log /mnt/test-results/desktop-ui.log

# Theme application must update actual terminal and compositor configuration.
for theme in nord catppuccin-latte phosphor; do
  runuser -u stratagem --preserve-environment -- env STRATAGEM_DARK_THEME_SKIP_BACKGROUND=1 stratagem-theme-set "$theme"
  runuser -u stratagem --preserve-environment -- foot --check-config
  runuser -u stratagem --preserve-environment -- hyprctl configerrors > /tmp/theme-errors
  test -z "$(tr -d '[:space:]' < /tmp/theme-errors)"
  test "$(cat /home/stratagem/.local/state/stratagem/current/theme.name)" = "$theme"
  ! grep -R '{{ ' /home/stratagem/.local/state/stratagem/current/theme/
done
runuser -u stratagem --preserve-environment -- timeout 30 stratagem-theme-choose > /tmp/theme-picker.log 2>&1 &
picker_pid=$!
sleep 5
kill -0 "$picker_pid"
runuser -u stratagem --preserve-environment -- grim /tmp/theme-picker.png
cp /tmp/theme-picker.png /mnt/test-results/theme-picker.png
# Exercise the real picker's keyboard acceptance, not a test-only apply API.
runuser -u stratagem --preserve-environment -- hyprctl dispatch sendshortcut ', Return,'
wait "$picker_pid"
cat /tmp/theme-picker.log > /mnt/test-results/theme-picker.log

bash /usr/lib/stratagem-dark/wifi-check.sh > /mnt/test-results/wifi-check.log 2>&1 || { cat /mnt/test-results/wifi-check.log; exit 1; }
