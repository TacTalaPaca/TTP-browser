#!/bin/sh
# RPM package. rpmbuild gets a source tar of the staged tree and a spec.
set -eu
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
. "$ROOT/scripts/packages/common.sh"
stage="$1"

top="$(mktemp -d)"
trap 'rm -rf "$top"' EXIT
mkdir -p "$top/BUILD" "$top/RPMS" "$top/SOURCES" "$top/SPECS" "$top/SRPMS"
src="$top/src/firegila-${VERSION}"
mkdir -p "$src"
cp -a "$stage"/. "$src/"
tar -czf "$top/SOURCES/firegila-${VERSION}.tar.gz" \
  -C "$top/src" "firegila-${VERSION}"

sed -e "s/@VERSION@/$VERSION/" \
    -e "s/@REVISION@/$REVISION/" \
    -e "s|@DEPENDS@|$RPM_DEPENDS|" \
    "$ROOT/packaging/rpm/firegila.spec.in" > "$top/SPECS/firegila.spec"

rpmbuild --define "_topdir $top" -bb "$top/SPECS/firegila.spec"
cp "$top"/RPMS/x86_64/firegila-"${VERSION}"-"${REVISION}"*.rpm "$OUT/"
echo "rpm: $(basename "$OUT"/firegila-"${VERSION}"-"${REVISION}"*.rpm)"
