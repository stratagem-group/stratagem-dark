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
test ! -s /mnt/test-results/hyprland-errors.txt
runuser -u stratagem --preserve-environment -- stratagem-shell shell ping | grep -qx ok
runuser -u stratagem --preserve-environment -- foot sh -c 'printf "STRATAGEM DARK\nSecurity workstation testing session\n\n"; dark --version; printf "\nBlackArch tools:\n"; capa --version; sleep 120' &
sleep 5
runuser -u stratagem --preserve-environment -- grim /tmp/stratagem-desktop.png
cp /tmp/stratagem-desktop.png /mnt/test-results/desktop.png
runuser -u stratagem --preserve-environment -- stratagem-shell shell summon stratagem.menu '{}'
sleep 2
runuser -u stratagem --preserve-environment -- grim /tmp/stratagem-menu.png
cp /tmp/stratagem-menu.png /mnt/test-results/menu.png
capa --version
whatweb --version
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
