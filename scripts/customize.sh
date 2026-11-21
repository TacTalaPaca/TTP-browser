#!/bin/sh
# Unpack clean ESR and apply Firegila branding and configs. Linux only.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PRODUCT="$(tr -d ' \n' < "$ROOT/VERSION")"
ESR="$(tr -d ' \n' < "$ROOT/ESR_VERSION")"
SRC_TAR="$ROOT/sources/firefox-${ESR}.tar.xz"
BUILD="$ROOT/build/firefox"

[ -f "$SRC_TAR" ] || { echo "customize: missing $SRC_TAR (run fetch-esr.sh)"; exit 1; }

echo "customize: unpacking fresh $ESR..."
rm -rf "$BUILD"
mkdir -p "$ROOT/build"
tar -xf "$SRC_TAR" -C "$ROOT/build"

# application.ini rebrand. Keeps Version and BuildID.
INI="$BUILD/application.ini"
sed -i 's/^Vendor=.*/Vendor=Firegila/' "$INI"
sed -i 's/^Name=.*/Name=Firegila/' "$INI"
sed -i 's/^RemotingName=.*/RemotingName=firegila-esr/' "$INI"
grep -E '^(Vendor|Name|RemotingName)=' "$INI"

# distribution identity and policies
sed "s/@PRODUCT@/$PRODUCT/g" "$ROOT/configs/distribution.ini" \
  > "$BUILD/distribution/distribution.ini"
grep -q "@PRODUCT@" "$BUILD/distribution/distribution.ini" \
  && { echo "customize: version placeholder left in distribution.ini"; exit 1; }
cp "$ROOT/configs/policies.json" "$BUILD/distribution/policies.json"
python3 -c "import json;json.load(open('$BUILD/distribution/policies.json'));print('policies.json: valid JSON')"

# default prefs. Product version and base ESR come from the two version files.
sed "s/@PRODUCT@/$PRODUCT/g; s/@ESR@/$ESR/g" "$ROOT/configs/firegila.js" \
  > "$BUILD/defaults/pref/firegila.js"
grep -q "@PRODUCT@\|@ESR@" "$BUILD/defaults/pref/firegila.js" \
  && { echo "customize: version placeholder left in firegila.js"; exit 1; }
echo "customize: firegila.js version $PRODUCT, base $ESR"

# autoconfig. Grants the bundled uBlock Origin private window access.
cp "$ROOT/configs/autoconfig.js" "$BUILD/defaults/pref/autoconfig.js"
cp "$ROOT/configs/firegila.cfg" "$BUILD/firegila.cfg"

# bundled extensions (installed on first run)
if [ -d "$ROOT/extensions" ] && ls "$ROOT"/extensions/*.xpi >/dev/null 2>&1; then
  mkdir -p "$BUILD/distribution/extensions"
  cp "$ROOT"/extensions/*.xpi "$BUILD/distribution/extensions/"
  echo "customize: bundled extensions -> $(ls "$BUILD/distribution/extensions" | tr '\n' ' ')"
fi

# product brand inside omni.ja
python3 "$ROOT/scripts/patch-omni-branding.py" "$ROOT" "$BUILD"

# neutral theme inside both omni jars
python3 "$ROOT/scripts/patch-omni-theme.py" "$ROOT" "$BUILD"

# window icons (generate 16/32/48/64/128 from 2048 master)
python3 - "$ROOT" "$BUILD" <<'EOF'
import sys
from PIL import Image
from pathlib import Path
root, build = Path(sys.argv[1]), Path(sys.argv[2])
master = Image.open(root / "app-icons" / "firegila-2048.png").convert("RGBA")
d = build / "browser" / "chrome" / "icons" / "default"
d.mkdir(parents=True, exist_ok=True)
for s in (16, 32, 48, 64, 128):
    master.resize((s, s), Image.LANCZOS).save(d / f"default{s}.png", optimize=True)
print("icons: replaced", sorted(p.name for p in d.glob("default*.png")))
EOF

# launcher
cp "$ROOT/branding/firegila-launcher.sh" "$BUILD/firegila"
chmod +x "$BUILD/firegila"

echo "customize: done -> $BUILD"
