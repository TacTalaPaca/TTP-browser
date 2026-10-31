#!/bin/sh
# Download + verify the ESR tarball listed in ESR_VERSION. Linux x86_64 en-US.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VER="$(tr -d ' \n' < "$ROOT/ESR_VERSION")"
URL="https://archive.mozilla.org/pub/firefox/releases/${VER}/linux-x86_64/en-US/firefox-${VER}.tar.xz"
OUT="$ROOT/sources/firefox-${VER}.tar.xz"

mkdir -p "$ROOT/sources"
if [ -f "$OUT" ]; then
  echo "fetch: already have $(basename "$OUT")"
else
  echo "fetch: $URL"
  curl -L -o "$OUT" "$URL"
fi

echo "fetch: verifying against archive SHA256SUMS..."
SUMS="$(mktemp)"
curl -sL "https://archive.mozilla.org/pub/firefox/releases/${VER}/SHA256SUMS" -o "$SUMS"
grep "linux-x86_64/en-US/firefox-${VER}.tar.xz" "$SUMS" | sed "s|linux-x86_64/en-US/||" > "$SUMS.one" || {
  echo "fetch: ENTRY NOT FOUND in SHA256SUMS"; exit 1
}
(cd "$ROOT/sources" && sha256sum -c "$SUMS.one")
rm -f "$SUMS" "$SUMS.one"
echo "fetch: OK"
