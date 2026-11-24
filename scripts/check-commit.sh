#!/bin/sh
# Pre-commit hygiene. Run before staging a release.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VERSION="$(tr -d ' \n' < "$ROOT/VERSION")"

"$ROOT/scripts/check-persistence.sh"

fail=0

check_ignored() {
  path="$1"
  if ! git check-ignore -q --no-index "$path"; then
    echo "check: not ignored: $path"
    fail=1
  fi
}

check_ignored "build/.probe"
check_ignored "dist/.probe"
check_ignored "sources/.probe"
check_ignored "scripts/__pycache__/probe.pyc"

tracked="$(git ls-files -ci --exclude-standard || true)"
if [ -n "$tracked" ]; then
  echo "check: tracked files match .gitignore:"
  echo "$tracked"
  fail=1
fi

for file in $(git diff --cached --name-only); do
  if git check-ignore -q --no-index "$file"; then
    echo "check: staged ignored file: $file"
    fail=1
  fi
done

limit=10485760
for file in $(git diff --cached --name-only); do
  case "$file" in
    assets/icons/*|assets/*.xpi) continue ;;
  esac
  [ -f "$file" ] || continue
  size="$(git cat-file -s ":$file" 2>/dev/null || wc -c < "$file")"
  if [ "$size" -gt "$limit" ]; then
    echo "check: large staged file: $file ($size bytes)"
    fail=1
  fi
done

if ! git diff --cached --check; then
  fail=1
fi

echo "check: ignored paths"
git status --ignored --short | sed -n 's/^!! //p' | head -20

if [ "$fail" -ne 0 ]; then
  echo "check: FAILED"
  exit 1
fi
echo "check: OK"
