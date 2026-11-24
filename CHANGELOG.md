# Changelog

## 1.3

- Reworked tab dragging for horizontal, vertical, pinned, group, split and multi-selected tabs.
- Added one placeholder and row motion, group targets, cross-window drops and tab list drops.
- Fixed cross-window placeholder width when source and destination tab strips use different tab sizes.
- Cross-window drops reserve a destination slot, shrink the row and keep the placeholder inside the tab strip.
- The placeholder hides while the pointer is over the page and no longer covers the window controls.
- Fixed placeholder alignment when the tab strip is compressed or scrolled.
- Hid tabs inside an expanded group while its label is dragged.
- Local tab reorders glide without a placeholder. The placeholder is only used for cross-window drops.
- Holding a tab being reordered over another tab for half a second shows one solid accent group cue. Moving restores the row.
- Group creation stays local to one window. Cross-window drops only move the tab.
- Local tab drags keep the drag ghost in the tab bar. Cross-window drags keep the tab ghost at the cursor.
- Removed the extra active tab width. Every tab keeps the same width.
- Removed the hairline under the fixed New Tab row in an overflowing vertical strip.
- Sync now keeps passwords, history, addons, addresses and settings and locks bookmarks, tabs and the pinned list off.
- Removed Bookmarks Toolbar, Synced Tabs, Firefox View, container and promo entries from the visible UI.
- Improved session restore of workspaces, groups and windows. App windows use one top bar and hidden tabs.
- Shared motion tokens across the chrome, sidebar, tabs column and New Tab customize panel.
- Gave every nav bar button the same button box and 4px face margin.
- Removed the leading titlebar spacer on Linux when window controls are on the right.
- Added icons to the workspace New, Rename and Delete menu items.
- Updated the bundled uBlock Origin extension to 1.77.0.
- F12 opens Developer Tools docked on the right, with a one-time migration for existing profiles.
- Moved release packages to dist and added package archive and clean tree checks.

## 1.2

- Fixed the workspaces startup error and the saved workspace restore.
- Added a one-time Strict tracking protection migration and marked Strict as the default in settings.
- Enabled DRM by default through the stock General checkbox.
- Added Linux app windows with compact chrome, no page title, grouped toolbar controls, branded desktop entries, StartupWMClass and a menu entry.
- Added F11 fullscreen overlays with a hidden sidebar, a toolbar and URL bar over the page, and auto-hide vertical tabs until exit.
- Disabled the top and edge reveals during page fullscreen video.
- Added two bookmark folders, Bookmarks and Shortcuts, with a one-time migration and a flat Shortcuts list.
- Moved New Tab shortcuts to the Shortcuts folder, kept the folder and pinned entries in sync, simplified the shortcut menu and removed the pin badge.
- Removed the old bookmark roots, the Bookmarks Toolbar and the cut, copy, paste and add separator bookmark items.
- Locked the Bookmarks and Shortcuts roots against rename, delete and move.
- Fixed duplicate separators and the Shortcuts New Folder entry in bookmark context menus.
- Listed Bookmarks subfolders in the save panel folder picker, hid New Folder there and removed the dotted focus ring from folder trees.
- Made the weather widget opt-in and removed its fixed width.
- Reworked the Shortcuts page with categories, a filter, clearer names and compact reset controls.
- Switched Settings to the classic layout so every pane is complete.
- Added cookie banner rejection, audible autoplay blocking, payment autofill off, local translations on and TLS 0-RTT off.
- Added an opt-in VA-API row under Performance.
- Added the v2 clear-on-shutdown categories and a persistence guard.
- Fixed the distribution version shown in Settings.
- Fixed the README ESR version note.

## 1.1

- Updated the Firefox ESR base to 153.7.0.
- Fixed Arch package dependencies.
- Switched RPM dependencies to shared-library capabilities.
- Added shared package metadata for deb, rpm, Arch, AppImage and tarball.
- Added desktop search keywords.
- Reworked tab groups with folder labels, grouped tab tint, state chevrons and smooth expand and collapse.
- Removed the tab group overflow count and the pinned drop section.
- Fixed vertical tab drag, split view layout, cross-window drops and cleanup after every drag.
- Added Split view and New window drop targets.
- Added a vertical drop indicator that matches the horizontal pin.
- Added a Shortcuts page under Settings for every main browser shortcut.
- Added Copy Page Link to the page context menu and Ctrl+Shift+L.
- Switched audio indicators to the neutral shared token.
- Made Strict tracking protection and Global Privacy Control the defaults.

## 0.1.3

- Added release metadata.

## 0.1.2

- Restored open tabs and neutral tab borders.
- Bumped the product version.
- Added auto-collapse tabs and the four-column pinned grid.
- Kept the active pin visible while the grid slides.
- Added the New Tab topography pattern.
- Faded hover and selected fills across the chrome and New Tab.
- Kept pinned tabs across restarts.

## 0.1.1

- Updated the Firefox ESR base to 153.6.0.
- Removed the four stock Mozilla default bookmarks once from older profiles.
- Added the New Tab wallpaper grid, removal fallback and button polish.
- Documented the layout, builds and releases.
- Required approval before release packaging.

## 0.1.0

- Initial release based on Firefox ESR, Linux x86_64, binary repackage.
- Added Firegila branding, icons, desktop entry and launcher.
- Added the neutral theme, custom sidebar, vertical tabs, workspaces, auto-hide tabs and web panels.
- Added manual New Tab shortcuts, fluid search and grid, custom wallpapers and the weather widget.
- Disabled telemetry, VPN, Pocket and sponsored content. Cookies, history and passwords are kept.
- Bundled uBlock Origin.
- Added deb, rpm, Arch, AppImage and tarball packages.
