/* Firegila defaults.
 * Cookies, history, passwords and sessions are kept.
 * No clear on exit. Unknown prefs are ignored.
 * Locked telemetry prefs are in policies.json.
 */

// Telemetry and reporting
pref("toolkit.telemetry.enabled", false);
pref("toolkit.telemetry.unified", false);
pref("toolkit.telemetry.archive.enabled", false);
pref("datareporting.healthreport.uploadEnabled", false);
pref("datareporting.policy.dataSubmissionEnabled", false);
pref("app.normandy.enabled", false);
pref("app.shield.optoutstudies.enabled", false);
pref("browser.crashReports.unsubmittedCheck.enabled", false);
pref("browser.tabs.crashReporting.sendReport", false);

// Pocket, VPN and extras
pref("extensions.pocket.enabled", false);
pref("browser.privatebrowsing.vpn.ui.enabled", false);
pref("browser.contentblocking.report.hide_vpn_banner", true);
pref("browser.vpn_promo.enabled", false);
// Firegila starts every profile on Strict tracking protection.
pref("browser.contentblocking.category", "strict");
pref("privacy.globalprivacycontrol.enabled", true);
pref("privacy.globalprivacycontrol.functionality.enabled", true);
pref("browser.shopping.experience2023.enabled", false);
pref("browser.microsurvey.enabled", false);
pref("browser.preferences.moreFromMozilla", false);
pref("extensions.getAddons.showPane", false);
pref("extensions.htmlaboutaddons.recommendations.enabled", false);

// New tab
// Shortcuts section stays for manual pins. All auto sources off.
// Empty defaults are locked through the policy. Remote tiles stay on so
// the locked empty list takes effect. Sponsored fetch stays off.
pref("browser.newtabpage.activity-stream.feeds.topsites", true);
pref("browser.newtabpage.activity-stream.default.sites", "");
pref("browser.newtabpage.activity-stream.improvesearch.noDefaultSearchTile", true);
pref("browser.newtabpage.activity-stream.improvesearch.topSiteSearchShortcuts", false);
pref("browser.topsites.useRemoteSetting", false);
pref("browser.newtabpage.activity-stream.feeds.section.highlights", false);
pref("browser.newtabpage.activity-stream.feeds.section.topstories", false);
pref("browser.newtabpage.activity-stream.feeds.system.topstories", false);
pref("browser.newtabpage.activity-stream.discoverystream.enabled", false);
pref("browser.newtabpage.activity-stream.discoverystream.shortcuts.personalization.enabled", false);
pref("browser.topsites.contile.enabled", false);
// Wallpapers. Only the custom upload from the PC is offered. The stock
// wallpaper list is dropped in the WallpaperFeed patch.
pref("browser.newtabpage.activity-stream.newtabWallpapers.enabled", true);
pref("browser.newtabpage.activity-stream.newtabWallpapers.customWallpaper.enabled", true);
pref("browser.newtabpage.activity-stream.newtabWallpapers.customColor.enabled", false);
// Sync
// Firefox Accounts stay on. Passwords, history, addons, addresses and
// settings sync. Bookmarks, Shortcuts and tabs stay local. The New Tab
// pinned list is not synced as a preference.
pref("services.sync.engine.bookmarks", false);
pref("services.sync.engine.tabs", false);
pref("services.sync.prefs.sync.browser.newtabpage.pinned", false);

// Weather widget. Off by default, opt-in from the New Tab customize menu.
pref("browser.newtabpage.activity-stream.showWeather", false);
pref("browser.newtabpage.activity-stream.system.showWeather", true);
pref("browser.newtabpage.activity-stream.widgets.system.weather.enabled", true);
pref("browser.newtabpage.activity-stream.widgets.weather.enabled", false);
// Endpoints are set explicitly. The widget falls back to the urlbar Merino
// endpoint when these are empty, so leaving them unset breaks the fetch.
pref("browser.newtabpage.activity-stream.weather.reportEndpoint", "https://merino.services.mozilla.com/api/v1/suggest");
pref("browser.newtabpage.activity-stream.weather.hourlyEndpoint", "https://merino.services.mozilla.com/api/v1/weather/hourly-forecasts");

// Sponsored content off
pref("browser.newtabpage.activity-stream.showSponsored", false);
pref("browser.newtabpage.activity-stream.showSponsoredTopSites", false);

// AI
// GenerativeAI policy locks the same switches.
// Local translations stay on. They run on device. The AIControls policy
// sets Translations available and keeps the other AI features blocked.
pref("browser.ml.enabled", false);
pref("browser.ml.chat.enabled", false);
pref("browser.ml.pageAssist.enabled", false);
pref("browser.preferences.aiControls", false);
pref("browser.preferences.experimental.hidden", true);
pref("browser.tabs.groups.smart.enabled", false);
pref("browser.tabs.groups.smart.userEnabled", false);

// Page load flash
// Light and dark.
pref("browser.display.background_color", "#fafafa");
pref("browser.display.background_color.dark", "#171717");
pref("browser.display.use_system_colors", false);

// Bookmark toolbar
// Off by default. The user can turn it on any time.
pref("browser.toolbars.bookmarks.visibility", "never");

// Sidebar
// New sidebar on, strip visible, tool list is history and bookmarks.
// The hide/show button is in the nav bar. Passwords and tabs from other
// devices stay available in the sidebar customize dialog but are not on.
pref("sidebar.revamp", true);
// The updated bookmarks list. It uses the same cards and rows as history.
pref("sidebar.updatedBookmarks.enabled", true);
pref("sidebar.verticalTabs", false);
pref("sidebar.visibility", "hide-sidebar");
pref("sidebar.main.tools", "history,bookmarks");
pref("browser.toolbarbuttons.introduced.sidebar-button", true);
// Panel width. 0 means nothing stored yet, so the stock default is used as
// the starting size and not forced on later runs. Written by the theme patch
// when the splitter is dragged.
pref("firegila.sidebar.width", 0);
// Auto-hide tabs. The column floats at the window edge, collapsed until the
// pointer reaches the edge. Off by default.
pref("firegila.sidebar.autoHideTabs", false);
// Auto-collapse tabs. The column keeps the sidebar strip width, shows tab
// icons only, and expands to the full vertical bar on hover. Off by default.
pref("firegila.sidebar.autoCollapseTabs", false);
// Tabs on the opposite side. Works with auto-hide or auto-collapse on. Off by
// default, so tabs sit next to the strip.
pref("firegila.sidebar.tabsOpposite", false);
// Website panels
// The toggle adds a divider, one button per saved site and a plus button to
// the strip. The list is JSON, http and https only, eight entries at most.
// Off by default.
pref("firegila.sidebar.webPanelsEnabled", false);
pref("firegila.sidebar.webPanels", "[]");

// HTTPS only and query stripping
pref("dom.security.https_only_mode", true);
pref("privacy.query_stripping.enabled", true);
// 0-RTT replay risk. Off is safe and does not break sites.
pref("security.tls.enable_0rtt_data", false);

// DRM
// On by default so video sites play on first use. Widevine downloads from
// Google on the first DRM site. The stock General checkbox can turn it off.
pref("media.eme.enabled", true);

// Session restore
// Reopen the same windows, tabs and workspaces on the next start. Hidden
// workspace tabs are restored too, not skipped or loaded on demand. These
// are defaults, so the user can still choose a fresh start in settings.
pref("browser.startup.page", 3);
pref("browser.sessionstore.resume_from_crash", true);
pref("browser.sessionstore.newTabOnRestore", false);
pref("browser.sessionstore.restore_on_demand", false);
pref("browser.sessionstore.restore_hidden_tabs", true);
pref("browser.sessionstore.restore_pinned_tabs_on_demand", false);

// Keep data on exit
pref("browser.privatebrowsing.autostart", false);
pref("privacy.sanitize.sanitizeOnShutdown", false);
pref("privacy.clearOnShutdown.cookies", false);
pref("privacy.clearOnShutdown.history", false);
pref("privacy.clearOnShutdown.sessions", false);
pref("privacy.clearOnShutdown.formdata", false);
pref("privacy.clearOnShutdown.downloads", false);
pref("privacy.clearOnShutdown.offlineApps", false);
pref("privacy.clearOnShutdown.siteSettings", false);
// The clear-on-shutdown UI uses the v2 categories. The master switch is
// off, and every category is off too, so data stays even if it is turned on.
pref("privacy.clearOnShutdown_v2.historyFormDataAndDownloads", false);
pref("privacy.clearOnShutdown_v2.browsingHistoryAndDownloads", false);
pref("privacy.clearOnShutdown_v2.cookiesAndStorage", false);
pref("privacy.clearOnShutdown_v2.cache", false);
pref("privacy.clearOnShutdown_v2.siteSettings", false);
pref("privacy.clearOnShutdown_v2.formdata", false);
pref("browser.passwords.rememberPasswords", true);
pref("signon.rememberSignons", true);

// Compat
pref("privacy.resistFingerprinting", false);
pref("geo.enabled", true);
pref("webgl.disabled", false);

// Content defaults
// Cookie banners: reject optional cookies, normal and private windows.
pref("cookiebanners.service.mode", 1);
pref("cookiebanners.service.mode.privateBrowsing", 1);
pref("cookiebanners.ui.desktop.enabled", true);
// Autoplay: block audible media, allow muted.
pref("media.autoplay.default", 1);
// Payment autofill stays off. Address autofill stays available.
pref("extensions.formautofill.creditCards.enabled", false);

// Containers
// Not offered. No menu entry, no settings page, no creation path. The two
// enabling prefs are locked off in policies.json as well.
pref("privacy.userContext.enabled", false);
pref("privacy.userContext.ui.enabled", false);
pref("privacy.userContext.newTabContainerOnLeftClick.enabled", false);
pref("browser.discovery.containers.enabled", false);
pref("privacy.usercontext.about_newtab_segregation.enabled", false);

// Workspaces
// One switcher in the tab bar, tab hiding for the inactive sets, membership
// kept per tab by SessionStore.
pref("firegila.workspaces.enabled", true);
pref("firegila.workspaces.scrollSwitch", true);
pref("firegila.workspaces.list", "[{\"id\":\"ws-default\",\"name\":\"Default\"}]");

// DevTools
// F12 docks the toolbox on the right. The user can still change it.
pref("devtools.toolbox.host", "right");
pref("devtools.toolbox.previousHost", "bottom");

// Convenience
// Tab groups form after a short hold. The drag controller shows a dashed
// candidate outline before this delay, so the target does not need to be chased.
pref("browser.tabs.dragDrop.createGroup.delayMS", 180);
// Scroll over the tab strip switches tabs, middle click starts autoscroll.
// Stock ESR has both off.
pref("toolkit.tabbox.switchByScrolling", true);
pref("general.autoScroll", true);

// Settings
// Classic layout. The new settings redesign leaves the Home pane empty in
// this ESR base.
pref("browser.settings-redesign.enabled", false);

// App windows
// Firefox Taskbar Tabs on Linux. The URL bar page action installs the
// current site as an app window. The theme patch adds the menu entry and
// compact chrome.
pref("browser.taskbarTabs.enabled", true);

// uBlock Origin
// Bundled in distribution/extensions, pinned, private windows on. The UUID
// appears twice and has to stay equal. This file is parsed by the prefs
// parser, not evaluated as JavaScript, so no variables or JSON.stringify.
pref("extensions.allowPrivateBrowsingByDefault", true);
pref("extensions.webextensions.uuids", "{\"uBlock0@raymondhill.net\":\"d3f1c2b4-5a6e-4f7d-8c9b-0a1b2c3d4e5f\"}");
// Toolbar layout comes from the CustomizableUI defaults, patched in
// patch-omni-theme.py. Setting browser.uiCustomization.state here dropped the
// sidebar and home buttons and duplicated the uBlock button, so it is left to
// the defaults. Account button off, uBlock pinned by its manifest area.

// Profile schema
// Starts at 0 so the first run applies every migration. The runner raises it
// after the steps complete and removes deprecated migration guards.
pref("firegila.schema", 0);

// Branding
// @PRODUCT@ and @ESR@ are replaced by customize.sh from VERSION and
// ESR_VERSION.
pref("firegila.version", "@PRODUCT@");
pref("firegila.build", "@ESR@");
pref("startup.homepage_welcome_url", "");
pref("startup.homepage_override_url", "");
// Updates off. Mozilla builds would replace this package.
pref("app.update.auto", false);
