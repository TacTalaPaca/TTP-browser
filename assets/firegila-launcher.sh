#!/bin/sh
# Firegila launcher. Uses a separate profile from Firefox.
DIR="$(dirname "$(readlink -f "$0")")"
export MOZ_APP_LAUNCHER="$DIR/firegila"

# ESR requires the profile path to exist. Create it when given.
NEED_PATH=0
HAS_PROFILE=0
PROFILE_PATH=""
for a in "$@"; do
  if [ "$NEED_PATH" -eq 1 ]; then
    PROFILE_PATH="$a"
    mkdir -p "$PROFILE_PATH"
    HAS_PROFILE=1
    NEED_PATH=0
    continue
  fi
  case "$a" in
    --profile=*|-profile=*) PROFILE_PATH="${a#*=}"; mkdir -p "$PROFILE_PATH"; HAS_PROFILE=1 ;;
    --profile|-profile) NEED_PATH=1; HAS_PROFILE=1 ;;
    -P|-ProfileManager) HAS_PROFILE=1 ;;
  esac
done

# Default run. Keep data in HOME/.firegila, away from Firefox.
if [ "$HAS_PROFILE" -eq 0 ]; then
  mkdir -p "${HOME}/.firegila"
  set -- --profile "${HOME}/.firegila" "$@"
fi

exec "$DIR/firefox" --class Firegila --name Firegila "$@"
