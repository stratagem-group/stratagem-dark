# Optional BlackArch adapter — design only

No repository is enabled by this scaffold. Select individual curated packages after
verifying licensing, architecture, dependency conflicts and signed artifact availability.
Pin the keyring archive/hash and independently verified full signing fingerprints.
Record signed repository DB and package hashes and retain immutable release artifacts.
Do not pipe strap scripts to root, use trust-all signatures, or import an entire group.
Never silently replace an Arch package with a same-named BlackArch package.
A failed trust or license check must prevent the transaction before package changes.
