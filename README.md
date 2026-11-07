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
  LICENSE                  # MPL-2.0
  DEV.md                   # commands for working on the project
  app-icons/               # firegila-512/1024/2048.png (transparent masters)
  branding/                # firegila.desktop, launcher script
  configs/                 # policies.json, firegila.js, distribution.ini
  packaging/               # deb, rpm, arch, appimage and metainfo templates
  scripts/
    fetch-esr.sh           # download + SHA256 verify
    customize.sh           # unpack + rebrand + icons + configs
    omnijar.py             # shared omni jar extract and repack
    patch-omni-branding.py # names and logos inside browser omni
    patch-omni-theme.py    # neutral theme inside both omni jars
    package.sh             # build every package format
    packages/              # one script per format
    check-commit.sh        # git hygiene before a commit
    install.sh             # install a packaged tarball
  dev                      # dev only, fresh profile run, never shipped
  sources/                 # upstream tarball (gitignored)
  build/firefox            # customized tree (gitignored)
  packages/<version>/      # release packages (gitignored)
```

Quick start:

```sh
./scripts/fetch-esr.sh
./scripts/customize.sh
./build/firefox/firegila --no-remote --profile /tmp/firegila-check
./scripts/package.sh
./scripts/install.sh packages/<version>/firegila-<version>-linux-x86_64.tar.xz
firegila
```

Notes:
- `DEV.md` has every build, test, packaging and upgrade command.
- Releases are built into `packages/<version>/`: deb, rpm, Arch package,
  AppImage, portable tarball, `SHA256SUMS` and `BUILDINFO`.
- `VERSION` is the Firegila release. `ESR_VERSION` is the Firefox base. They
  move independently.
- `application.ini`: `Name=Firegila`, `Vendor=Firegila`, `RemotingName=firegila-esr`
  so profiles and locks stay separate from Firefox.
- Enterprise policy lives at `distribution/policies.json` (`about:policies` to verify).
- Default prefs live at `defaults/pref/firegila.js` (overridable by the user).
- Window icons regenerated from `app-icons/firegila-2048.png`.
- Theme: neutral palette in Dark, Light and System themes, system accent, no brand colors.
  System follows the OS scheme with the same styles. Content pages follow the same palette.
- Source is MPL-2.0, see `LICENSE`. The bundled Firefox binary keeps its own
  MPL notice.

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
  `app-icons/firegila-2048.png`.
- Ships its own `.desktop` entry and launcher. Default profile is
  `$HOME/.firegila`. The launcher never deletes profiles.
- `firegila.version` records the Firegila release. `firegila.build` records the
  base ESR (`153.5.1esr`).

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
  hides and shows strip, tabs and panel together. Tabs are 32px in both
  orientations. The 16px icon and the 16px close button box sit on the same
  8px margin on all sides, with an 8px gap between icon and label. The New
  Tab button is a 32px square in the horizontal strip and a 32px row in the
  vertical one.
- The sidebar settings offer Auto-hide tabs. With it on the tabs column floats
  over the strip and panel and slides in with a transform, so nothing reflows
  and the surface moves with its content. It stays collapsed until the pointer
  reaches the window edge, and a 3px sensor there keeps the reveal working over
  a page or its scrollbar. It replaces the stock expand on hover setting, which
  reflowed the whole sidebar.
- The sidebar settings also offer Tabs on the opposite side. It puts the tabs
  column at the far edge, away from the strip and panel. Works with auto-hide
  on or off, and follows the sidebar when it is moved to the right. The column
  keeps the tab bar surface there.
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
- Motion for the whole browser comes from one set of tokens (180ms base,
  120ms fast, plain ease), shared by CSS transitions and every sidebar
  animation, including the panel and customize view open and close. Honors
  `sidebar.animation.enabled` and reduced motion.

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
- Audio from another workspace marks the switcher with a 6px system accent
  dot. The same dot marks the sidebar button and a website button when audio
  plays there.
- Settings > Tabs and browsing has the workspace switches and both scroll
  switches.

### New tab

- Shortcuts grid is manual only. No history fill, no sponsored tiles, no
  default sites. Add, edit, drag and remove work as stock. Eight per row,
  centered, fluid width between 300px and 720px.
- Search bar is fluid between the same bounds instead of stepping at layout
  breakpoints. The tabs grid underneath keeps its fixed columns.
- Logo stays centered at any row count. All slots stay visible, so the add
  tile is never hidden on narrow windows. Weather widget on with explicit
  endpoints. No stories, highlights or shopping content.
- Wallpapers offer only the custom upload from the PC. The stock Firefox
  wallpaper list and the solid color picker are dropped. Uploads appear in a
  scrollable grid inside the Wallpapers panel. Up to 100 are kept, and a new
  upload drops the oldest. Removing the active wallpaper switches to the next
  one; the Wallpapers toggle turns off only when none are left.
- Add and edit shortcut dialogs fade and scale in on open and out on close.
- Settings loses the sponsored shortcuts, sponsored stories, support promo
  and recent activity sections.
- Default bookmarks ship empty, so new profiles start clean. Profiles made
  before 0.1.1 lose the four stock Mozilla defaults once on first start;
  user bookmarks are left alone. Added bookmarks suggest and sync normally.

### Theme

- Neutral gray ramp in every theme, system accent color instead of brand
  colors, 8px radius on controls, 6px on menu rows, no shadows. Forced colors
  and user installed themes are left alone. Light and dark use the same
  contrast steps for chrome, cards, borders and dim text. The section divider
  is a separate token, so it stays visible without reading as a hard line.
- Background tabs carry a 1px border on their fill. The selected tab keeps
  the 1px accent border. The rule is the same for vertical and horizontal
  tabs. The close button box is 16px on every tab, on the same 8px margin as
  the tab icon.
- Design system buttons and the tab close button shrink their glyph while
  pressed. XUL toolbar buttons keep their box and use the stock background
  press, so the button face never shrinks on click.
- Popup panels fade in over the fast token, with no slide. The extensions
  panel used the stock 70px slide, which read as a bounce.
- The page content area is flat. No outline around it, no rounded corner next
  to the sidebar.
- The tab strip has no list all tabs button and no Firefox View button by
  default. Both are out of the default layout.
- Selected and inactive tabs share one neutral border color. The system
  accent stays on focus rings and controls, not on tab borders.
- Urlbar row hover and selected states follow the neutral ramp. Text fields,
  selects and dropdowns get a single border, accent on focus.

### Convenience

- Scroll over the tab strip switches tabs, and over the workspace switcher
  switches workspaces. Middle click starts autoscroll. All on by default.
- Session restore is on by default. The next start reopens the same windows
  and tabs, including tabs hidden in other workspaces, and loads them all.
  Users can still choose a fresh start in settings.

### Privacy, AI and content defaults

- Telemetry, studies, crash reporting, Normandy and health report off, locked
  by policy where possible. Nothing is cleared on exit, cookies, history,
  passwords and sessions persist.
- Pocket, VPN UI, shopping, microsurveys, MoreFromMozilla and addon
  recommendations off. Firefox Home keeps top sites only, no sponsored rows.
  QuickSuggest on and off both locked off.
- Generative AI, chat, page assist, smart tab groups, link previews and the AI
  settings section off, locked by policy.
- Containers are off and locked. No menu entry, no settings page and no
  creation path.
- HTTPS only mode on, query stripping on. First run and post update pages
  blank. Onboarding and feature recommendations skipped.
- Updates off, Mozilla builds would replace this package.
- Search: DuckDuckGo default, Ecosia added, Bing, Wikipedia and Perplexity
  removed.
- Bookmark toolbar off by default, user can turn it on.
- uBlock Origin bundled, pinned to the toolbar, allowed in private windows.
- Page load flash color follows the palette in light and dark.
