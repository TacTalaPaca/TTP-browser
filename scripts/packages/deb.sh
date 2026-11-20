#!/bin/sh
# Debian package. Uses the shared staging tree, adds DEBIAN metadata, builds,
# then removes the metadata so the other formats see a clean tree.
set -eu
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
. "$ROOT/scripts/packages/common.sh"
stage="$1"

size="$(du -sk "$stage/usr" | cut -f1)"
mkdir -p "$stage/DEBIAN"
sed -e "s/@VERSION@/$VERSION/" \
    -e "s/@REVISION@/$REVISION/" \
    -e "s/@ARCH@/$DEB_ARCH/" \
    -e "s/@SIZE@/$size/" \
    -e "s|@DEPENDS@|$DEB_DEPENDS|" \
    -e "s|@MAINTAINER@|$MAINTAINER|" \
    -e "s|@HOMEPAGE@|$HOMEPAGE|" \
    -e "s|@SUMMARY@|$SUMMARY|" \
    "$ROOT/packaging/deb/control.in" > "$stage/DEBIAN/control"
{
  printf 'firegila (%s-%s) unstable; urgency=medium\n\n' \
    "$VERSION" "$REVISION"
  changelog_bullets | sed 's/^/  * /'
  printf '\n -- %s  %s\n' "$MAINTAINER" "$(LC_ALL=C date -R)"
} | gzip -9n > "$stage/usr/share/doc/firegila/changelog.Debian.gz"
cp "$ROOT/packaging/deb/postinst" "$stage/DEBIAN/postinst"
cp "$ROOT/packaging/deb/postrm" "$stage/DEBIAN/postrm"
chmod 755 "$stage/DEBIAN/postinst" "$stage/DEBIAN/postrm"
dpkg-deb --build --root-owner-group "$stage" \
  "$OUT/firegila_${VERSION}_${DEB_ARCH}.deb"
rm -rf "$stage/DEBIAN"
rm -f "$stage/usr/share/doc/firegila/changelog.Debian.gz"
echo "deb: firegila_${VERSION}_${DEB_ARCH}.deb"
