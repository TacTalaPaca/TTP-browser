# Firegila
Linux only. Firefox ESR rebrand. Phase 1 is a binary repackage.

Base: the Firefox ESR release in `ESR_VERSION`, linux-x86_64, en-US.
Release: the Firegila version in `VERSION`.
Method: unpack official tarball, overlay branding + policies + prefs, repack.
No source build. Telemetry, VPN, Pocket and sponsored items are
disabled in policy and prefs. Cookies, history and passwords are kept.
Nothing is cleared on exit.

```
Firegila/
  VERSION                  # Firegila release version
  ESR_VERSION              # ESR version pin
  CHANGELOG.md             # release history
  LICENSE                  # MPL-2.0
  DEV.md                   # commands for working on the project
  assets/                  # desktop entry, launcher, newtab pattern, uBlock
  assets/icons/            # firegila-512/1024/2048.png (transparent masters)
  configs/                 # policies.json, firegila.js, distribution.ini
  packaging/               # declarative package templates and metadata
    common/                # shared metadata for every format
    deb/ rpm/ arch/        # format templates
    appimage/              # AppImage template and pinned tool
  scripts/
    fetch-esr.sh           # download + SHA256 verify
    customize.sh           # unpack + rebrand + icons + configs
    omnijar.py             # shared omni jar extract and repack
    patch-omni-branding.py # names and logos inside browser omni
    patch-omni-theme.py    # neutral theme inside both omni jars
    package.sh             # build every package format
    packages/              # one script per format
    check-commit.sh        # git hygiene before a commit
    check-ui.py            # headless UI checks on the built browser
    install.sh             # install a packaged tarball
  dev                      # dev only, fresh profile run, never shipped
  sources/                 # upstream tarball (gitignored)
  build/firefox            # customized tree (gitignored)
  dist/                    # release packages (gitignored)
```

Quick start:

```sh
./scripts/fetch-esr.sh
./scripts/customize.sh
./build/firefox/firegila --no-remote --profile /tmp/firegila-check
./scripts/package.sh
./scripts/install.sh dist/firegila-<version>-linux-x86_64.tar.xz
firegila
```

Notes:
- `DEV.md` has every build, test, packaging and upgrade command.
- Releases are built into `dist/`: deb, rpm, Arch package, AppImage,
  portable tarball and `SHA256SUMS`.
- `VERSION` is the Firegila release. `ESR_VERSION` is the Firefox base. They
  move independently.
- `application.ini`: `Name=Firegila`, `Vendor=Firegila`, `RemotingName=firegila-esr`
  so profiles and locks stay separate from Firefox.
- Enterprise policy lives at `distribution/policies.json` (`about:policies` to verify).
- Default prefs live at `defaults/pref/firegila.js` (overridable by the user).
- Window icons regenerated from `assets/icons/firegila-2048.png`.
- Theme: neutral palette in Dark, Light and System themes, system accent, no brand colors.
  System follows the OS scheme with the same styles. Content pages follow the same palette.
- Source is MPL-2.0, see `LICENSE`. The bundled Firefox binary keeps its own
  MPL notice. The bundled uBlock Origin extension keeps its GPL-3.0-or-later
  license.

## Changes from stock Firefox ESR

Everything below is a difference between this package and the official
linux-x86_64 en-US build of the release in `ESR_VERSION`. No source build, all
changes are overlays on the unpacked tarball, applied by
`scripts/customize.sh`.

### Branding

- Name, vendor and remote name are Firegila, so profiles, locks and window
  classes stay separate from Firefox (`application.ini`, `distribution.ini`).
- Product strings say Firegila where a name is shown. Feature names the user
  looks up in help articles (Firefox Account, Firefox View, Pocket) keep
  their stock names.
- Icons, about page logo and wordmark are generated from
  `assets/icons/firegila-2048.png`.
- Ships its own `.desktop` entry and launcher. Default profile is
  `$HOME/.firegila`. The launcher never deletes profiles.
- `firegila.version` records the Firegila release. `firegila.build` records the
  base ESR (`153.7.0esr`).

### Sidebar

- New sidebar on by default, strip visible, hide/show button first in the nav
  bar. Strip is 40px wide with 32px button faces, matching the nav bar.
- Tool list is history and bookmarks. Passwords and tabs from other devices
  stay available in the customize dialog but are not pinned.
- Strip, vertical tabs column and panel resize continuously on every state
  change instead of sliding. Panel content is revealed at resting size and
  fades with the panel.
- Panel width is remembered across sessions. Fresh profiles start at 500px.
  Dragging the splitter still resizes freely.
- With vertical tabs the strip and the tabs column share the tab bar surface.
  Without them the strip matches the nav bar. The panel uses the page surface.
  The only section divider is the 1px line on the strip side of the panel, so
  strip and tabs read as one chrome section. The panel-to-page boundary keeps
  the resize bar, so it stays visible and draggable.
- History, bookmarks, open tabs, tabs from other devices and the customizer
  use one card surface: `--fg-bg-3` fill, `--fg-border` border, 8px radius.
  The updated bookmarks list is on by default and wraps its content in the
  same card as history, so the tools read as one set.
- Passwords uses the same header, panel padding and search field as the other
  sidebar tools.
- Vertical tabs live in their own 220px column after the strip, next to the
  panel, so the order is strip, tabs, panel. The strip keeps its buttons
  and layout either way, never expands, never resizes. The hide/show button
  hides and shows the strip and panel only, the tabs column stays visible.
  Tabs are 32px in both orientations. The 16px icon and the 16px close button
  box sit on the same 8px margin on all sides, with an 8px gap between icon
  and label. The New Tab button is a 32px square in the horizontal strip and
  a 32px row in the vertical one.
- The sidebar settings offer Auto-hide tabs. With it on the tabs column floats
  over the strip and panel and slides in with a transform, so nothing reflows
  and the surface moves with its content. It stays collapsed until the pointer
  reaches the window edge, and a 3px sensor there keeps the reveal working over
  a page or its scrollbar. It replaces the stock expand on hover setting, which
  reflowed the whole sidebar.
- Auto-collapse tabs keeps the column in layout at the sidebar strip width,
  showing tab icons only. Hovering it expands the full vertical tab bar and
  leaving it collapses back. Auto-hide and auto-collapse are mutually
  exclusive.
- Pinned tabs sit in a four-column grid at the top of the column, 32px tall
  with the same 4px gaps and margins. A collapsed strip shows one column.
  Opening the bar slides the grid to the full layout, so the selected pin
  stays in view and its row and order do not change.
- Tab groups use a folder label tinted with the group color in both tab
  orientations. A chevron shows open or closed. Grouped tabs take a matching
  border and tint and stay aligned with the strip. An unnamed horizontal group
  is a 32px folder tile. A collapsed strip shows a 32px folder tile.
- The sidebar settings also offer Tabs on the opposite side. It puts the tabs
  column at the far edge, away from the strip and panel. Works with auto-hide
  or auto-collapse, and follows the sidebar when it is moved to the right. The
  column keeps the tab bar surface there.
- Add websites to sidebar puts a divider, one button per saved site and a plus
  button in the strip. The add form starts with the current page URL filled
  in when that page is http or https. A saved site opens as a web panel with
  its own icon, back and forward, reload and close. Eight sites at most, http
  and https only, kept in prefs across restarts. A site keeps its page when
  the panel is closed and reopened. Right click a site button to reload, open
  it in a tab or remove it.
- The settings button stays at the bottom of the strip.
- The divider stock draws above the tool buttons in vertical tabs mode is
  gone. It was the drag handle for the tools section, which is not resizable
  here.
- Right click opens the sidebar menu on the strip and on the tabs column
  background. Tab items keep the tab menu.
- Vertical tabs no longer flip the sidebar to always-show, which is what stock
  does on every startup. The visibility setting is pinned to hide-sidebar, so
  the toolbar button stays a hide/show button in both tab orientations. The
  sidebar settings no longer offer the visibility switch.
- Motion for the whole browser comes from one set of tokens (180ms panels,
  140ms base, 80ms fast, plain ease), shared by CSS transitions and every
  sliding panel, including the sidebar, the tabs column and the New Tab
  customize view. Honors `sidebar.animation.enabled` and reduced motion.

### Workspaces

- One workspace switcher in the tab bar, left of the horizontal tabs, and
  above the vertical tabs column. The menu lists the workspaces, marks the
  current one with a check, and offers New, Rename and Delete. Delete asks
  first and closes the tabs of that workspace. On by default.
- Workspaces use the native tab hide and show API. Tabs of the other
  workspaces are hidden, not closed, and keep title, history and scroll.
  Membership is a `firegila.workspace` custom tab value, kept by SessionStore
  across restarts.
- Pinned tabs and tabs that use a camera or a microphone stay visible in
  every workspace, because the API cannot hide them safely.
- An empty workspace opens one new tab on switch. Names are 24 characters at
  most, 12 workspaces at most.
- Audio from another workspace marks the switcher with a 6px neutral dot.
  The same dot marks the sidebar button and a website button when audio
  plays there.
- Settings > Tabs and browsing has the workspace switches and both scroll
  switches.

### New tab

- Shortcuts grid comes from the Shortcuts bookmark folder. No history fill,
  no sponsored tiles, no default sites. Add and drag write to the folder.
  Eight per row, centered, fluid width between 300px and 720px.
- Shortcut menu has Open in New Window, Open in New Private Window and Delete
  shortcut. No pin, unpin, edit, dismiss or history deletion. The pin badge is
  gone.
- Search bar is fluid between the same bounds instead of stepping at layout
  breakpoints. The tabs grid underneath keeps its fixed columns.
- Logo stays centered at any row count. All slots stay visible, so the add
  tile is never hidden on narrow windows. Weather widget is off by default and
  opt-in from the customize menu. The card fills the stock right column and
  keeps a stable height. No stories, highlights or shopping content.
- The plain new tab shows a subtle topography pattern in the divider color.
  A wallpaper replaces it.
- Wallpapers offer only the custom upload from the PC. The stock Firefox
  wallpaper list and the solid color picker are dropped. Uploads appear in a
  scrollable grid inside the Wallpapers panel. Up to 100 are kept, and a new
  upload drops the oldest. Removing the active wallpaper switches to the next
  one; the Wallpapers toggle turns off only when none are left.
- The add shortcut dialog fades and scales in on open and out on close.
- Settings loses the sponsored shortcuts, sponsored stories, support promo
  and recent activity sections.
- Default bookmarks ship empty, so new profiles start clean. Stock Mozilla
  defaults are removed once. User bookmarks are moved into the Bookmarks
  folder.

### Theme

- Neutral gray ramp in every theme, system UI font, system accent color instead
  of brand colors, 8px radius on controls, no shadows. Forced colors and user
  installed themes are left alone. Light and dark use the same contrast steps
  for chrome, cards, borders and dim text. The section divider is a separate
  token, so it stays visible without reading as a hard line.
- Right click menus use stock Firefox menu styling. No custom menu background,
  border, padding or radius. The rest of the browser keeps the Firegila theme.
- Background tabs carry a 1px border on their fill. The selected tab keeps
  the 1px accent border. The rule is the same for vertical and horizontal
  tabs. The close button box is 16px on every tab, on the same 8px margin as
  the tab icon.
- Hover and selected fills fade on the fast token across tabs, toolbar
  buttons, sidebar buttons and new tab tiles.
- Audio indicators use the shared neutral token. Tab audio and mute indicators
  use the native compact overlay in the collapsed strip.
- Design system buttons and the tab close button shrink their glyph while
  pressed. Nav bar buttons keep the stock square icon face and hover fill. On
  press the face scales, except for menu buttons, whose panels need a fixed
  anchor.
- Popup panels fade in over the fast token, with no slide. The extensions
  panel used the stock 70px slide, which read as a bounce.
- The page content area has square corners and a subtle 1px border. No
  outline around it. The sidebar panel has no divider on the strip side.
- The tab strip has no list all tabs button and no Firefox View button by
  default. Both are out of the default layout.
- Urlbar row hover and selected states follow the neutral ramp. Text fields,
  selects and dropdowns get a single border, accent on focus.

### Convenience

- Scroll over the tab strip switches tabs, and over the workspace switcher
  switches workspaces. Middle click starts autoscroll. All on by default.
- Dragging a tab inside its window keeps the drag ghost in the tab bar. The
  row glides to the new order and uses no placeholder.
- Dragging a tab from another window shows the tab ghost at the cursor and a
  rounded placeholder in the destination strip. The target row resizes and
  the placeholder stays inside the strip.
- Holding a tab being reordered over another tab for half a second shows one
  solid accent group cue. Moving again hides the cue. Drop to add the tab to
  that group or create a new group with both tabs. Group creation is only
  available when reordering inside one window.
- Dropping on the page shows a New window overlay and opens the tab in a new
  window. Dropping on another Firegila window moves the tab into that window.
  Vertical mode still shows the Split view and New window drop targets.
- Pinned tabs stay in the pinned area. In horizontal and vertical list modes,
  dragging a pinned tab to the unpinned strip unpins it. The vertical pinned
  grid reorders inside the grid.
- Group labels, split view wrappers, multi-selected tabs and tab list drags use
  the same group and cross-window handling. Local reorders stay placeholder
  free.
- A cross-window drop reserves the destination slot, so the row shrinks and
  the placeholder stays inside the strip. Over the page it shows only the
  window hint.
- The row width settles before the drag is measured, so the placeholder and
  the shifted tabs share one geometry. The placeholder follows strip scroll.
- New tab buttons hide during a drag.
- Settings > Shortcuts lists common browser shortcuts by category, with a
  filter and a reset for each entry. Each one can be rebound, and the choice
  is stored per profile.
- F12 opens Developer Tools docked on the right. The dock can still be moved
  from the toolbox menu.
- Copy Page Link sits in the page context menu and on Ctrl+Shift+L.
- Session restore is on by default. The next start reopens the same windows
  and tabs, including tabs hidden in other workspaces, and loads them all.
  Tab groups keep their workspace, order and collapsed state.
  Users can still choose a fresh start in settings.

### App windows

- Firefox Taskbar Tabs is enabled on Linux. The URL bar page action and the
  hamburger menu install the current site as an app window.
- The app window reads the site manifest for the name and icon, opens one tab,
  and uses `display-mode: minimal-ui`.
- App windows keep one top bar. The tab strip, the tabs column and the sidebar
  are hidden, and the page fills the rest of the window.
- Compact chrome hides the URL text and keeps the identity chip. Ctrl+L shows
  the full address bar. Escape or clicking the page collapses it again.
- Back, forward and reload sit together. The identity chip follows them. The
  toolbar has no page title. Extensions, the menu and the window controls
  group on the right.
- App windows use the same profile, so cookies, history, logins, tabs and
  workspaces stay. Uninstalling an app removes the desktop entry and registry
  entry only. Site data is not touched.
- The desktop entry is named `firegila.webapp-*` and sets `StartupWMClass` so
  the taskbar matches the app icon. It sets `NoDisplay` and a Web Browser
  category, so it never appears in the Linux application menu or in Lost and
  Found. Existing entries are updated once on the next start.

### Sync

- Firefox Accounts and Sync stay on.
- Passwords, history, addons, addresses and settings sync.
- Bookmarks, Shortcuts, tabs and workspaces stay local. Their sync engines
  are off and locked.
- The Sync settings and sidebar show no Bookmarks, Tabs or Synced Tabs
  entries.

### Fullscreen

- F11 hides the sidebar. The toolbar and vertical tabs become overlays that
  slide away with the same motion.
- The toolbar auto-hides and reveals at the top. It does not push the page.
- Vertical tabs switch to auto-hide for the duration of F11. The previous tabs
  mode returns on exit.
- A page fullscreen video hides the toolbar, sidebar and tabs column. Top and
  edge reveals stay off until the page leaves fullscreen.

### Bookmarks

- Two folders only: Bookmarks and Shortcuts. Bookmarks Toolbar, Bookmarks
  Menu, Other Bookmarks and Mobile Bookmarks are hidden.
- Bookmarks can hold folders and subfolders. Shortcuts is a flat list and
  cannot hold folders.
- Both folders appear in the save panel, bookmark sidebar, bookmarks menu
  panel, library and Alt Bookmarks menu. The Bookmarks Toolbar is removed
  completely.
- Existing user bookmarks move into Bookmarks once. Pinned New Tab entries
  move into Shortcuts once. Nothing is deleted.
- Saving a bookmark to Shortcuts adds a New Tab shortcut. Deleting the
  shortcut removes the bookmark only. History stays.
- The save panel folder picker lists Bookmarks subfolders. New Folder stays in
  the library. Shortcuts has no expander and no empty folder area.
- Bookmark menus drop Cut, Copy, Paste and Add Separator. Add actions target
  the selected folder. The two roots cannot be renamed, deleted or moved.
- The shortcut grid, the sidebar and the library stay in sync through one
  bookmark sync layer.

### Settings

- Classic settings layout, so every pane is complete and the Home pane is not
  empty.
- The Shortcuts page groups shortcuts by category, has a filter, and shows a
  reset only for changed shortcuts.
- The data promise sits in General > Startup.
- VA-API is an opt-in row under Performance.

### Privacy, AI and content defaults

- Telemetry, studies, crash reporting, Normandy and health report off, locked
  by policy where possible. Nothing is cleared on exit, cookies, history,
  passwords and sessions persist.
- Pocket, VPN UI, shopping, microsurveys, MoreFromMozilla and addon
  recommendations off. Firefox Home keeps top sites only, no sponsored rows.
  QuickSuggest on and off both locked off.
- Generative AI, chat, page assist, smart tab groups, link previews and the AI
  settings section off, locked by policy. Local translations stay on. They run
  on device and send nothing to a server.
- Containers are off and locked. No menu entry, no settings page and no
  creation path.
- HTTPS only mode on, query stripping on. First run and post update pages
  blank. Onboarding and feature recommendations skipped.
- Strict tracking protection by default and marked Strict (default) in
  settings. Existing Standard profiles move once to Strict. Tell sites not to
  sell or share data is on by default.
- DRM is on by default. Widevine downloads on first play. The stock General
  checkbox can turn it off.
- Cookie banners reject optional cookies in normal and private windows.
  Audible autoplay is blocked. Payment method autofill is off, address
  autofill stays available. TLS 0-RTT is off.
- Hardware video decoding (VA-API) is an opt-in under Performance. Off by
  default, restart required. It needs a supported GPU driver.
- Clear-on-shutdown categories are off, including the v2 prefs. The master
  switch is off as well. Cookies, history, tabs and passwords stay.
- Updates off, Mozilla builds would replace this package.
- Search: DuckDuckGo default, Ecosia added, Bing, Wikipedia and Perplexity
  removed.
- Bookmark toolbar off by default, user can turn it on.
- uBlock Origin bundled, pinned to the toolbar, allowed in private windows.
- Page load flash color follows the palette in light and dark.
