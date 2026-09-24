#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Pinned trust bootstrap. Never execute upstream strap.sh.
set -euo pipefail
repo_root=$(cd -- "$(dirname -- "$0")/.." && pwd)
trust_dir=${1:?trust output directory required}
mkdir -p "$trust_dir"
curl --fail --location --retry 3 https://www.blackarch.org/keyring/blackarch-keyring-20251011.tar.gz -o "$trust_dir/keyring.tar.gz"
printf '%s  %s\n' '6ec9e038c0a877f8e666286112a871586ac5f02a4912a2e5d284530994226b6f01e647a2d98de4ec27c45ddee24097b9e823e443197eed8d05d135747199c774' "$trust_dir/keyring.tar.gz" | sha512sum -c -
curl --fail --location --retry 3 https://www.blackarch.org/keyring/blackarch-keyring-20251011.tar.gz.sig -o "$trust_dir/keyring.tar.gz.sig"
# The archive hash above is the trust anchor, taken from the pinned upstream recipe.
# strap.sh's old signer differs from the actual 20251011 archive signer.
mkdir -p "$trust_dir/keyrings"
tar -xzf "$trust_dir/keyring.tar.gz" --strip-components=1 -C "$trust_dir/keyrings"
key_home=$(mktemp -d)
chmod 700 "$key_home"
trap 'rm -rf "$key_home"' EXIT
gpg --homedir "$key_home" --batch --import "$trust_dir/keyrings/blackarch.gpg"
gpg --homedir "$key_home" --batch --status-fd 1 --verify "$trust_dir/keyring.tar.gz.sig" "$trust_dir/keyring.tar.gz" > "$trust_dir/verification.txt"
grep -Eq '^\[GNUPG:\] VALIDSIG CBA3C7D4798912702DCF568E67D8BDF42AD93F4E ' "$trust_dir/verification.txt"
install -m644 "$trust_dir/keyrings/blackarch.gpg" "$trust_dir/keyrings/blackarch-trusted" "$trust_dir/keyrings/blackarch-revoked" /usr/share/pacman/keyrings/
pacman-key --populate blackarch
