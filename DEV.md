# Developing Firegila

Commands for working on Firegila. What the project is, see `README.md`.
Rules the code follows, see `AGENTS.md`.

## All commands

### First build, once

| command | what it does |
|---|---|
| `./scripts/fetch-esr.sh` | download the ESR tarball and verify it |
| `./scripts/customize.sh` | unpack, brand, theme, configs, icons. Creates `build/firefox` |

### Daily loop

| command | what it does |
|---|---|
| `./dev` | run the browser on a fresh profile |
| `./dev --build` | rebuild first, then run on a fresh profile |
| `./dev /tmp/fg-testclear` | run on a fresh profile at that path |
| `./dev --keep` | run again on the same profile, keeps cookies and history |
| `./dev --keep /tmp/fg-testclear` | same, at that path |
| `./dev about:preferences` | run and open a page |
| `./dev --help` | list the flags |

`./dev` is the one you want. It deletes the profile before launching, so every
run starts the same. Anything after the flags goes to the browser.

`--build` exists because you almost always rebuild before testing, and
`customize.sh` takes a while.

| variable | default | what it is |
|---|---|---|
| `FG_PROFILE` | `/tmp/firegila-dev` | profile directory when you do not name one |

### Packaging and installing

| command | what it does |
|---|---|
| `./scripts/package.sh` | build every format into `packages/<version>/` |
| `./scripts/package.sh deb rpm` | build only the named formats |
| `./scripts/install.sh packages/<version>/firegila-<version>-linux-x86_64.tar.xz` | install the tarball to a prefix |
| `./scripts/check-commit.sh` | git hygiene before a commit |

Formats: `tarball`, `deb`, `rpm`, `arch`, `appimage`.

## Requirements

| need | used by |
|---|---|
| `python3` | the two patch scripts |
| Python `Pillow` | icon generation, both patch scripts |
| `curl`, `sha256sum` | `fetch-esr.sh`, AppImage tool download |
| `tar` with xz | unpack, tarball and rpm source |
| `unzip` | reading the omni jars |
| `dpkg-deb` | deb package |
| `rpmbuild` | rpm package |
| `makepkg`, `fakeroot` | Arch package |
| `bsdtar`, `zstd` | Arch package tools |
| `desktop-file-validate`, `appstreamcli` | package metadata checks |
| `sh` | every shell script |

```sh
python3 -m pip install --user Pillow
```

`update-desktop-database` and `gtk-update-icon-cache` are optional, used by
the deb and rpm scripts and by `install.sh`, and skipped when missing.

## Running the browser

`./dev` wraps `build/firefox/firegila`, which is the launcher that ships. The
launcher never deletes anything. It creates the profile directory you name,
and defaults to `$HOME/.firegila` when you name none. The wiping is done by
`./dev`, not by the launcher, so no profile is ever destroyed by accident.

For a run outside `./dev`:

```sh
./build/firefox/firegila --no-remote --profile /tmp/fg-test   # keeps data
./build/firefox/firegila -P                                    # profile manager
```

The real binary, with no wrapper at all. No profile defaulting, no window
class handling:

```sh
./build/firefox/firefox --no-remote --profile /tmp/probe
./build/firefox/firefox --version                              # the ESR in ESR_VERSION
```

Headless, for probing and screenshots:

```sh
MOZ_HEADLESS=1 MOZ_HEADLESS_WIDTH=1280 MOZ_HEADLESS_HEIGHT=800 \
  ./build/firefox/firefox --no-remote --profile /tmp/headless about:newtab
```

Headless follows the system scheme. To measure the dark branch of
`light-dark()`, set `ui.systemUsesDarkTheme=1` and
`layout.css.prefers-color-scheme.content-override=0` in the probe profile.

## Building

`customize.sh` deletes `build/firefox` and rebuilds it from the pristine ESR
every run. No incremental mode. That is deliberate, so a build can never
inherit something a previous one left behind.

Two consequences:

- Never edit files inside `build/firefox` expecting them to stick.
- Any change under `configs/` or `scripts/` needs a rebuild, `./dev --build`.

There is no source build. Both `omni.ja` archives are unpacked, edited as text,
and repacked: `build/firefox/omni.ja` for the platform, `build/firefox/browser/omni.ja`
for the browser. An edit that is not found fails the build loudly with the file
and the string.

## Packaging and installing

`VERSION` is the Firegila release, `ESR_VERSION` is the Firefox base. The
package version is `VERSION`, the release revision is 1.

`package.sh` refuses to run until `customize.sh` has. It stages one `/usr`
tree from `build/firefox` and passes that same tree to every format, so
`/usr/lib/firegila`, the launcher, desktop file, icons, metainfo and docs are
identical everywhere. Output goes to `packages/<version>/` with `SHA256SUMS`
and `BUILDINFO`. The whole `packages/` tree is gitignored.

`install.sh` removes and recreates `$PREFIX/lib/firegila`, then writes the
symlink, desktop entry and icon. Your real profile in `$HOME/.firegila` is not
touched. Pass a tarball path to install something other than the current
release:

```sh
./scripts/install.sh packages/<version>/firegila-<version>-linux-x86_64.tar.xz
```

The deb uses `dpkg-deb`, the rpm uses `rpmbuild`, Arch uses `makepkg`, and the
AppImage downloads the pinned `appimagetool` 1.9.1, checks its SHA256, and
falls back to an extracted tool when FUSE is unavailable. The AppImage tool
cache lives in `build/tools/`, also gitignored.

## Versions and releases

- `VERSION` is the Firegila release, currently `0.1.0`.
- `ESR_VERSION` is the Firefox base, currently `153.5.1esr`.
- Every release gets its own `packages/<VERSION>/` folder. A new product
  release is a new `VERSION`, a new folder, and a new `v<VERSION>` tag.
- `scripts/check-commit.sh` runs before a commit. It fails on tracked ignored
  files, staged files under `build/`, `packages/`, `sources/` or
  `scripts/__pycache__`, large staged files, and whitespace errors.

## Changing the theme

Theme blocks live in `scripts/patch-omni-theme.py` as string constants, each
appended to the file that wins the cascade for the thing being styled.

| constant | appended to |
|---|---|
| `GLOBAL_OVERRIDE_CSS` | `tokens-shared.css`, `global-shared.css` |
| `WIDGET_CSS` | toolkit text and select element styles |
| `NEWTAB_CSS` | both newtab stylesheets, one target list |
| `TAB_CSS` | `tab.tokens.css` |
| `SB_CHROME_CSS` | `sidebar.css` |
| `SB_MAIN_CSS` | `sidebar-main.css` |
| `SB_BOOTSTRAP_JS` | `browser-sidebar.js` |
| `SB_ANIM_JS` | `browser-sidebar.js` |
| `SB_WEBPANELS_JS` | `browser-sidebar.js` |
| `SB_WORKSPACES_JS` | `browser-sidebar.js` |
| `SIDEBAR_PAGE_CSS` | `sidebar/sidebar.css` |
| `MEGALIST_CSS` | `megalist/megalist.css` |

`NEWTAB_CSS` is the four newtab blocks concatenated once. `SB_BOOTSTRAP_JS`
runs before `SB_ANIM_JS` in the same file. The bootstrap reads the
real nav bar height and button size off the live toolbar into two custom
properties, and `SB_ANIM_JS` uses them, so the strip width is never hardcoded.
The tabs column width is the one fixed value, `--fg-tabs-width` in
`GLOBAL_OVERRIDE_CSS`, used by the stylesheet and by the auto-hide pointer
handler in `SB_BOOTSTRAP_JS`.

Which side the tabs sit on comes from the `fg-tabs-opposite` root attribute,
set from `firegila.sidebar.tabsOpposite`. Stock writes the sidebar order inline
on every `#browser` child, so the CSS rule that moves the column needs
`!important`. The auto-hide pointer handler reads the same attribute, so it
watches the opposite edge too.

Auto-hide does not animate the column width. The column keeps `--fg-tabs-width`
and slides with `transform: translateX`, so no frame touches layout and the
background and tabs move together. A separate 3px `#firegila-tabs-sensor`
element at the edge sits earlier in the DOM than the column, so it takes the
hover while the column is out and the column takes it once revealed. The
sensor is the only reveal trigger. Chrome sidebar panels report mousemove
with panel relative coordinates, so the window handler only collapses the
column and normalizes the pointer x against the window screen origin. A content
browser never reports mousemove to this window, so that sensor is what makes
the edge work over a page or a scrollbar.

The strip matches the nav bar surface when vertical tabs are off, and the tab
bar surface when they are on, so it joins the tabs column. The tabs column
carries the tab bar surface. The panel box and the stock sidebar browser use
`--fg-bg`. The only section divider is a 1px `--fg-divider` line on the strip
side of the panel. Light mode mirrors the dark contrast steps: chrome and page
about 1.07, card and page about 1.1, dim text about 8:1 in both. There is no
separate dark sidebar tone anymore, so a panel never matches the strip.

Bookmarks wraps its list in a `moz-card` like history and synced tabs.
`sidebar-page.mjs` imports the `moz-card` element once, so every page that
extends `SidebarPage` has it. The synced tabs page no longer carries its own
copy of that import. `SIDEBAR_PAGE_CSS`, appended to the content `sidebar.css`,
pins `--card-background-color`, `--card-border-color`,
`--sidebar-box-background` and `--sidebar-box-border-color` to the palette, so
every sidebar tool uses the same card fill, border, radius and padding.
`MEGALIST_CSS` gives the password panel the same panel padding and search
field. `sidebar.updatedBookmarks.enabled` is on by default in `firegila.js`, so
the sidebar loads `sidebar-bookmarks.html`. With the pref off, stock falls back
to the old `places/bookmarksSidebar.xhtml` tree, which none of this styling
touches.

The customize button is rendered in `.bottom-actions` in both tab modes, and
`.buttons-wrapper` fills the strip, so the button stays at the bottom under the
saved websites.

Button press feedback is CSS only. `SB_CHROME_CSS` scales the tab close
button and HTML button icons on `:active`. XUL toolbarbuttons are left out:
their icon element also paints the button face, so a scale would shrink the
whole button. `MOZ_BUTTON_PRESS_CSS`, appended to
`chrome/toolkit/content/global/elements/moz-button.css`, scales the icon inside
the moz-button shadow root. Both are 120ms and respect reduced motion.

`TAB_CSS` sets one tab shape for both strips: 32px tall, an 8px inline
inset, an 8px icon gap and a 16px close button box on the icon margin. The
list all tabs button is hidden there too. It stays in the markup after its
placement is dropped, so the rule is what keeps it out of the strip.

Website panels live in `SB_WEBPANELS_JS`, appended to `browser-sidebar.js` as
the third Firegila block. The strip block is rendered by `sidebar-main` from
`window.FiregilaWebPanels`, so the component only gained a template method.
The sites are stored in `firegila.sidebar.webPanels` as JSON, ids are
`fg-panel-` plus a uuid, eight entries at most, http and https only. Each site
is a plain entry in `SidebarController.sidebars`, opened in its own content
browser under `#sidebar-box`; the stock `#sidebar` browser keeps the chrome
panels. `about:blank` is the entry URL, the real site is loaded by the module
on `sidebar-show`. One browser is created per panel on first open and kept
loaded after that, so closing and reopening a panel keeps its page, history
and scroll. Removing a site or turning the feature off removes its browser,
its icon cache and its audio mark. The hide patch no longer unloads the stock
`#sidebar` either, so a chrome panel keeps its page when the sidebar closes.
The page favicon never reaches Places for a non tab browser, so
`discoverIcon()` reads the page head and probes the declared icons, then
`/favicon.ico`, and keeps the first one that loads. The add popup prefills
`gBrowser.currentURI` when it is http or https, and selects the text, so the
open page can be saved in one step. The add popup and the per site menu are in
`browser.xhtml`, styled from `SB_CHROME_CSS`, labels in `sidebar.ftl`.

Workspaces live in `SB_WORKSPACES_JS`, the fourth block in
`browser-sidebar.js`. The inactive sets are hidden with `gBrowser.hideTab`
under the `firegila-workspace` source, membership is the `firegila.workspace`
custom tab value, read back by SessionStore on restore. The list is
`firegila.workspaces.list`, JSON, `ws-` plus a uuid, 12 at most. The switcher
is static markup in `browser.xhtml` and is moved between `.toolbar-items` and
`#vertical-tabs-container` when the pref changes. The menu width is the live
button width, set from `popupshowing`. The current row is marked with a
check, not accent text, so the label keeps normal contrast on the menu
surface.

## Changing prefs

Most go in `configs/firegila.js`, under a short comment label. `@PRODUCT@`
and `@ESR@` come from `VERSION` and `ESR_VERSION`; `customize.sh` substitutes
them.

That file is **parsed, not evaluated**. Firefox reads `defaults/pref/*.js` with
a strict line parser, so only `pref("name", literal)` lines are accepted. No
variables, no `JSON.stringify`, no template literals, no helper functions. The
browser logs `prefs parse error: unknown keyword` and silently drops the rest
of the file when you get this wrong. Only `pref()` calls, comments and blank
lines. `node -c` it and you will still ship a broken build, so check the
browser log after any change here.

Locked settings belong in `configs/policies.json`, not in prefs. A policy lock
beats anything the user can set by hand. Some prefs cannot be set from a pref
file at all, `browser.newtabpage.activity-stream.topSitesMaxSitesPerRow` is
locked to 8 in the policy and that is what holds the shortcut grid to eight per
row.

Two default pref files load, in this order:

1. `defaults/pref/firegila.js`, from `configs/`
2. `defaults/preferences/firefox.js`, upstream

The second wins, so a pref both files set ends up at the stock value. The theme
patch appends `configs/firegila.js` to the end of the second file, which makes
the intended value final. Keep prefs in `configs/firegila.js` only, there is no
need for per pref edits in `BROWSER_EDITS`.

The policy `Preferences` list only accepts a fixed set of prefixes. `app.*`,
`toolkit.*` and `crashreporter.*` are rejected, so those cannot be locked and
have to go through the appended defaults.

Sync and Nimbus can rewrite toolbar layout at runtime. A layout that looks
wrong with an account attached may be right in a clean profile.

## Probing a running build

Read values out of a live build by appending a `console.log` probe to a file in
the browser jar, then reading it from a headless run.

`unzip` reads the jar, not Python `zipfile`. The pristine omni archives have a
binary prefix before the zip data, so `zipfile` cannot open them. `unzip`
warns about the central directory, the files still extract, ignore the warning.

Set the two values, then run the block as one paste:

```sh
JAR=build/firefox/browser/omni.ja
TARGET=chrome/browser/content/browser/sidebar/browser-sidebar.js
PROBE='setTimeout(function(){console.log("PROBE "+JSON.stringify({strip:document.getElementById("sidebar-container").getBoundingClientRect().width}))},4000);'

W=/tmp/probe-w; rm -rf "$W"; unzip -o -q "$JAR" -d "$W"
printf '\n%s\n' "$PROBE" >> "$W/$TARGET"
python3 - "$W" "$JAR" <<'PY'
import os, sys, zipfile
work, jar = sys.argv[1], sys.argv[2]
out = jar + ".new"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, dn, fn in os.walk(work):
        dn.sort()
        for f in sorted(fn):
            full = os.path.join(dp, f)
            z.write(full, os.path.relpath(full, work))
os.replace(out, jar)
PY
rm -rf "$W"

P=/tmp/probe-p; rm -rf "$P"; mkdir -p "$P"
printf 'user_pref("devtools.console.stdout.chrome", true);\n' > "$P/user.js"
MOZ_HEADLESS=1 MOZ_HEADLESS_WIDTH=1280 MOZ_HEADLESS_HEIGHT=800 \
  ./build/firefox/firefox --no-remote --profile "$P" about:newtab \
  > /tmp/probe.log 2>&1

python3 - <<'PY'
import json
key = '"PROBE '
decoder = json.JSONDecoder()
for line in open("/tmp/probe.log", "rb").read().decode("utf8", "replace").splitlines():
    i = line.find(key)
    if i < 0:
        continue
    message = decoder.raw_decode(line[i:])[0]
    print(json.loads(message.split("PROBE ", 1)[1]))
PY
```

Each console line looks like `console.log: "PROBE {...}"`, where the message is a
quoted JSON string with the payload escaped inside it. So decode the quoted
string first, then parse the payload. A regex on quotes will not work.

Two scope traps inside a probe. `Preferences` is not defined there, and
`Services.prefs.getDefaultPref` is gone, so read a default with:

```js
const { Preferences } =
  ChromeUtils.importESModule("resource://gre/modules/Preferences.sys.mjs");
const value = Preferences.get("firegila.build", true);
```

Always run `./dev --build` after probing, before packaging. A build tree with a
probe in it will ship if you forget, and nothing in the pipeline complains.

To sample an animated value, tick on a timer and count distinct results. A
transition that genuinely resizes gives many widths, a slide or snap gives two.

```js
const out = [];
const t0 = performance.now();
(function tick() {
  const t = Math.round(performance.now() - t0);
  out.push([t, document.getElementById("tabbrowser-tabbox")
    .getBoundingClientRect().width]);
  if (t < 300) {
    setTimeout(tick, 10);
  } else {
    console.log("PROBE " + JSON.stringify({
      samples: out,
      distinct: new Set(out.map((r) => r[1])).size,
    }));
  }
})();
```

## Upgrading the ESR

```sh
echo '154.0.0esr' > ESR_VERSION
./scripts/fetch-esr.sh
./scripts/customize.sh
./dev --build
./dev about:preferences
./dev about:addons
./scripts/package.sh
```

Expect theme patches to fail. They match exact strings from the ESR they were
written against. When one fails the build names the file and the string it
could not find. Read the fresh string out of the built jar and update the
table.

Things that move between ESR releases: stock default prefs, sidebar and tab
internals, the customization schema version `currentVersion` in
`configs/firegila.js`, and policy names.

`fetch-esr.sh` verifies the download against the SHA256SUMS published beside
the release. Same host, so it catches corruption, not a compromised mirror.

## Troubleshooting

| symptom | cause |
|---|---|
| `ModuleNotFoundError: No module named 'PIL'` | install Pillow into the interpreter running the scripts |
| `dev: run scripts/customize.sh first` | no `build/firefox`, run `./dev --build` |
| `customize: missing sources/firefox-...` | run `./scripts/fetch-esr.sh` |
| `theme: not found in <file>: <string>` | an exact string in a patch table no longer exists, expected on an upgrade |
| `theme: extract failed` | the jar did not unpack, re-run `customize.sh` |
| the theme looks half applied | interrupted run, `./dev --build` rebuilds from scratch |
| a sidebar width looks stuck | a probe is left in the tree, or an animation was not released. `./dev --build`, then check for `console.log` in the jar |
| `prefs parse error: unknown keyword` | `configs/firegila.js` used JavaScript. That file is parsed, not evaluated. Only `pref("name", literal)` lines |
| a change to `configs/` does nothing | rebuild, upstream `firefox.js` loads after it and wins |
| layout differs between a clean and a real profile | sync, Nimbus or an account rewriting the toolbar layout |
