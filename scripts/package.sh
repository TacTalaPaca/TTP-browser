#!/bin/sh
# Build every package format into packages/<version>. Pass format names to
# build a subset: tarball, deb, rpm, arch, appimage.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
. "$ROOT/scripts/packages/common.sh"

formats="$*"
if [ -z "$formats" ]; then
  formats="tarball deb rpm arch appimage"
fi

require_build
[ -n "$(changelog_bullets)" ] || {
  echo "package: no CHANGELOG entry for $VERSION" >&2
  exit 1
}
prepare_out

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
stage_root "$STAGE"

for format in $formats; do
  case "$format" in
    tarball) "$ROOT/scripts/packages/tarball.sh" "$STAGE" ;;
    deb) "$ROOT/scripts/packages/deb.sh" "$STAGE" ;;
    rpm) "$ROOT/scripts/packages/rpm.sh" "$STAGE" ;;
    arch) "$ROOT/scripts/packages/arch.sh" "$STAGE" ;;
    appimage) "$ROOT/scripts/packages/appimage.sh" "$STAGE" ;;
    *)
      echo "package: unknown format: $format" >&2
      exit 1
      ;;
  esac
done

write_buildinfo
write_sums
echo "package: $OUT"
ls -lh "$OUT"
