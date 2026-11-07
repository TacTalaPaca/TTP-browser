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
// Weather widget.
pref("browser.newtabpage.activity-stream.showWeather", true);
pref("browser.newtabpage.activity-stream.system.showWeather", true);
pref("browser.newtabpage.activity-stream.widgets.weather.enabled", true);
// Endpoints are set explicitly. The widget falls back to the urlbar Merino
// endpoint when these are empty, so leaving them unset breaks the fetch.
pref("browser.newtabpage.activity-stream.weather.reportEndpoint", "https://merino.services.mozilla.com/api/v1/suggest");
pref("browser.newtabpage.activity-stream.weather.hourlyEndpoint", "https://merino.services.mozilla.com/api/v1/weather/hourly-forecasts");

// Sponsored content off
pref("browser.newtabpage.activity-stream.showSponsored", false);
pref("browser.newtabpage.activity-stream.showSponsoredTopSites", false);

// AI
// GenerativeAI policy locks the same switches.
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
// Tabs on the opposite side. Works with auto-hide on or off. Off by default,
// so tabs sit next to the strip.
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
pref("browser.passwords.rememberPasswords", true);
pref("signon.rememberSignons", true);

// Compat
pref("privacy.resistFingerprinting", false);
pref("geo.enabled", true);
pref("webgl.disabled", false);

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

// Convenience
// Scroll over the tab strip switches tabs, middle click starts autoscroll.
// Stock ESR has both off.
pref("toolkit.tabbox.switchByScrolling", true);
pref("general.autoScroll", true);

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

// Branding
// @PRODUCT@ and @ESR@ are replaced by customize.sh from VERSION and
// ESR_VERSION.
pref("firegila.version", "@PRODUCT@");
pref("firegila.build", "@ESR@");
pref("startup.homepage_welcome_url", "");
pref("startup.homepage_override_url", "");
// Updates off. Mozilla builds would replace this package.
pref("app.update.auto", false);
