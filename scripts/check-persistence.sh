#!/bin/sh
# Fail if a default can clear cookies, history, tabs or passwords on exit.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PREFS="$ROOT/configs/firegila.js"

[ -f "$PREFS" ] || {
  echo "persistence: missing $PREFS" >&2
  exit 1
}

fail=0

require() {
  if ! grep -Fq "$1" "$PREFS"; then
    echo "persistence: missing $1"
    fail=1
  fi
}

require 'pref("browser.privatebrowsing.autostart", false);'
require 'pref("privacy.sanitize.sanitizeOnShutdown", false);'
require 'pref("privacy.clearOnShutdown.cookies", false);'
require 'pref("privacy.clearOnShutdown.history", false);'
require 'pref("privacy.clearOnShutdown.sessions", false);'
require 'pref("privacy.clearOnShutdown.formdata", false);'
require 'pref("privacy.clearOnShutdown.downloads", false);'
require 'pref("privacy.clearOnShutdown.offlineApps", false);'
require 'pref("privacy.clearOnShutdown.siteSettings", false);'
require 'pref("privacy.clearOnShutdown_v2.historyFormDataAndDownloads", false);'
require 'pref("privacy.clearOnShutdown_v2.browsingHistoryAndDownloads", false);'
require 'pref("privacy.clearOnShutdown_v2.cookiesAndStorage", false);'
require 'pref("privacy.clearOnShutdown_v2.cache", false);'
require 'pref("privacy.clearOnShutdown_v2.siteSettings", false);'
require 'pref("privacy.clearOnShutdown_v2.formdata", false);'
require 'pref("browser.startup.page", 3);'
require 'pref("browser.sessionstore.resume_from_crash", true);'
require 'pref("browser.sessionstore.restore_on_demand", false);'
require 'pref("browser.sessionstore.restore_hidden_tabs", true);'
require 'pref("browser.sessionstore.restore_pinned_tabs_on_demand", false);'
require 'pref("browser.passwords.rememberPasswords", true);'
require 'pref("signon.rememberSignons", true);'

if grep -Eq 'pref\("privacy\.(sanitize\.sanitizeOnShutdown|clearOnShutdown[^"]*)", true\)' "$PREFS"; then
  echo "persistence: a clear-on-shutdown pref is true"
  fail=1
fi

if [ "$fail" -ne 0 ]; then
  echo "persistence: FAILED"
  exit 1
fi
echo "persistence: OK"
