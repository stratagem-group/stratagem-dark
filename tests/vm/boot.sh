#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -euo pipefail
iso=${1:?ISO required}
results=${2:?results directory required}
mkdir -p "$results"
results=$(realpath "$results")
cp /usr/share/OVMF/OVMF_VARS_4M.fd "$results/OVMF_VARS.fd"
timeout 720 qemu-system-x86_64 -machine q35,accel=kvm:tcg -cpu max -m 4096 -smp 2 \
  -drive if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd \
  -drive if=pflash,format=raw,file="$results/OVMF_VARS.fd" \
  -cdrom "$iso" -boot d -device virtio-vga -display none \
  -qmp unix:"$results/qmp.sock",server=on,wait=off \
  -serial file:"$results/serial.log" -no-reboot \
  -netdev user,id=net0 -device virtio-net-pci,netdev=net0 \
  -virtfs local,path="$results",mount_tag=test-results,security_model=none,id=results \
  -fw_cfg name=opt/stratagem/test,string=1 &
qemu_pid=$!
login_status=0
python3 tests/vm/login.py "$results" || login_status=$?
wait "$qemu_pid" || true
rm -f "$results/qmp.sock"
[[ "$login_status" == 0 ]]
grep -q STRATAGEM_DARK_TEST_PASS "$results/serial.log"
