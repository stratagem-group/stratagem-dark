#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Real pacman transactions in a disposable fresh Arch chroot, using the actual bundle.
set -euo pipefail
bundle=${1:?bundle path required}
signer=${2:?trusted fingerprint required}
results=${3:?results directory required}
target=/build/install-test
mkdir -p "$target" "$results"
config=/build/install-test-pacman.conf
cat > "$config" <<CONF
[options]
Architecture = x86_64
SigLevel = Required DatabaseOptional
LocalFileSigLevel = Required
[stratagem-dark]
Server = file://$bundle/repository
CONF
pacstrap -C "$config" -K "$target" base python gnupg sudo
arch-chroot "$target" useradd -m tester
mkdir -p "$target/bundle"
mount --bind "$bundle" "$target/bundle"
trap 'umount "$target/bundle" 2>/dev/null || true' EXIT
for attempt in 1 2; do
 arch-chroot "$target" /bundle/source/bin/dark install --bundle /bundle --key-fingerprint "$signer" --user tester --apply > "$results/install-$attempt.log" 2>&1 || { cat "$results/install-$attempt.log"; exit 1; }
 cp "$target/var/lib/stratagem-dark/transaction.json" "$results/transaction-$attempt.json"
 arch-chroot "$target" pacman -Q > "$results/packages-$attempt.txt"
done
cmp "$results/packages-1.txt" "$results/packages-2.txt"
# Existing user edits must survive another setup pass.
printf '\n# USER_CUSTOMIZATION_TEST\n' >> "$target/home/tester/.config/foot/foot.ini"
arch-chroot "$target" runuser -u tester -- dark setup --apply > "$results/config-preservation.json"
grep -q USER_CUSTOMIZATION_TEST "$target/home/tester/.config/foot/foot.ini"
arch-chroot "$target" systemctl is-enabled sddm.service NetworkManager.service stratagem-dark-firewall.service > "$results/services.txt"
arch-chroot "$target" nft --check -f /usr/share/stratagem-dark/firewall.nft
arch-chroot "$target" python /usr/lib/stratagem-dark/check-tools.py /tmp/tools.json
cp "$target/tmp/tools.json" "$results/tools.json"
umount "$target/bundle"
trap - EXIT
if [[ ${STRATAGEM_KEEP_TEST_ROOT:-0} != 1 ]]; then rm -rf "$target"; fi
printf '%s\n' 'STRATAGEM DARK: offline install, repeat install, and user-config preservation passed.' | tee "$results/result.txt"
