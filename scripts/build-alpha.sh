#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Run only in a disposable privileged Arch Linux build container.
set -euo pipefail
[[ $(id -u) == 0 && -f /.dockerenv ]] || { echo 'Use the isolated CI/container builder.' >&2; exit 2; }
cd /src
export SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH:?commit timestamp required}
export LC_ALL=C.UTF-8
out=/src/dist
work=/build
mkdir -p "$out" "$work"
# Configure the builder against the fixed Arch snapshot, before adding BlackArch.
sed '/^\[blackarch\]/,$d' build-support/pacman.conf > /etc/pacman.conf
pacman-key --init
pacman-key --populate archlinux
pacman -Syu --noconfirm archiso python git gnupg openssl base-devel librsvg
scripts/setup-blackarch.sh "$work/trust"
cp build-support/pacman.conf "$work/pacman.conf"
# Build only our package; upstream binaries remain signed packages from their repositories.
python scripts/package-root.py "$work/payload"
rsvg-convert -w 1920 -h 1080 branding/wallpaper.svg -o "$work/payload/usr/share/stratagem-dark/branding/wallpaper.png"
mkdir -p "$work/pkg"
cp -a "$work/payload" "$work/pkg/payload"
cat > "$work/pkg/PKGBUILD" <<'PKG'
pkgname=stratagem-dark-desktop
pkgver=0.2.0alpha1
pkgrel=1
pkgdesc='STRATAGEM DARK desktop and security workstation integration'
arch=('x86_64')
url='https://github.com/stratagem-group/stratagem-dark'
license=('MIT')
depends=('python' 'hyprland' 'quickshell' 'foot' 'uwsm' 'jq' 'swaybg')
package() {
  cp -a "$startdir/payload/." "$pkgdir/"
}
PKG
id builder >/dev/null 2>&1 || useradd -m builder
chown -R builder:builder "$work/pkg"
runuser -u builder -- bash -c 'cd /build/pkg && makepkg --nodeps --noconfirm'
mkdir -p "$work/bundle/repository" "$work/db/local"
mapfile -t packages < <(cat build-support/desktop.packages build-support/blackarch.packages | sed '/^#/d; /^$/d' | sort -u)
# Empty package DB resolves the complete dependency closure, not the builder's installed subset.
pacman --config "$work/pacman.conf" --dbpath "$work/db" --cachedir "$work/bundle/repository" -Syw --noconfirm "${packages[@]}"
cp "$work/pkg/"*.pkg.tar.zst "$work/bundle/repository/"
cp -a "$work/trust" "$work/bundle/trust"
cp build-support/builder-image.txt build-support/snapshot.txt "$work/bundle/"
cp -a /src "$work/bundle/source"
rm -rf "$work/bundle/source/.git" "$work/bundle/source/dist" "$work/bundle/source/build"
# Test-release signing identity is generated in this disposable job, never committed.
export GNUPGHOME="$work/signing"
mkdir -m700 "$GNUPGHOME"
gpg --batch --pinentry-mode loopback --passphrase '' --quick-gen-key 'STRATAGEM DARK Testing Build <testing@invalid>' ed25519 sign 0
signer=$(gpg --with-colons --list-keys | awk -F: '$1=="fpr" {print $10; exit}')
gpg --armor --export "$signer" > "$work/bundle/release-key.asc"
printf '%s\n' "$signer" > "$out/RELEASE-KEY-FINGERPRINT.txt"
pacman-key --add "$work/bundle/release-key.asc"
pacman-key --lsign-key "$signer"
gpg --batch --yes --detach-sign "$work/bundle/repository/"stratagem-dark-desktop-*.pkg.tar.zst
# Archive metadata, official signatures and an SPDX inventory become the release lock.
python scripts/release-manifest.py "$work/bundle" "$work/db" "$GIT_COMMIT"
gpg --batch --yes --armor --detach-sign "$work/bundle/manifest.json"
cp "$work/bundle/release-key.asc" "$out/RELEASE-KEY.asc"
# Local repository retains verified upstream package signatures; database gets our test signature.
repo-add --sign --key "$signer" "$work/bundle/repository/stratagem-dark.db.tar.gz" "$work/bundle/repository/"*.pkg.tar.zst
python scripts/assemble-iso.py "$work/bundle" "$work/profile" "$signer"
mkarchiso -v -w "$work/iso-work" -o "$out" "$work/profile"
# Bundle repository index was generated after the manifest: not part of the installer trust contract.
# The installer reads only locked package archives, not the mutable repository index.
tar --sort=name --mtime="@$SOURCE_DATE_EPOCH" --owner=0 --group=0 --numeric-owner -I 'zstd -T0 -6' -cf "$out/stratagem-dark-0.2.0-alpha1-x86_64-bundle.tar.zst" -C "$work" bundle
cp "$work/bundle/manifest.json" "$work/bundle/manifest.json.asc" "$work/bundle/sbom.spdx.json" "$out/"
python scripts/vulnerability-report.py "$work/bundle/manifest.json" "$out/security-report.json"
cd "$out"
sha256sum *.iso *.tar.zst manifest.json manifest.json.asc sbom.spdx.json security-report.json RELEASE-KEY.asc RELEASE-KEY-FINGERPRINT.txt > SHA256SUMS
gpg --batch --yes --armor --detach-sign SHA256SUMS
