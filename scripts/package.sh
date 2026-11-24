#!/bin/sh
# Build every package format into dist/. Pass format names to
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

if [ "${ALLOW_DIRTY:-0}" != "1" ]; then
  if ! git -C "$ROOT" diff --quiet || ! git -C "$ROOT" diff --cached --quiet; then
    echo "package: commit the current work before a release build" >&2
    echo "package: for a local test build set ALLOW_DIRTY=1" >&2
    exit 1
  fi
fi

old=""
if [ -d "$ROOT/dist" ]; then
  for file in "$ROOT"/dist/firegila_*_amd64.deb; do
    [ -e "$file" ] || continue
    base=$(basename "$file")
    version=${base#firegila_}
    old=${version%%_*}
  done
fi
if [ -n "$old" ] && [ "$old" != "$VERSION" ]; then
  archive="${TTP_PKGS:-$HOME/TacTalaPaca/TTP-pkgs}/pkgs/firegila/$old"
  if [ ! -d "$archive" ]; then
    echo "package: previous build $old is not archived in $archive" >&2
    echo "package: archive it before building $VERSION" >&2
    exit 1
  fi
  echo "package: previous build $old is archived, clearing dist"
fi

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

write_sums
echo "package: $OUT"
ls -lh "$OUT"
