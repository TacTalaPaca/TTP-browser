#!/usr/bin/env python3
# Headless UI checks for Firegila.
# Runs the built browser, drives chrome state and synthetic drag events, and
# checks drag, groups, pinned tabs, workspaces, session restore, app windows,
# Sync locks and removed UI. Prints PASS or FAIL for each check.
import http.server
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "build" / "firefox" / "firefox"
HOST = "127.0.0.1"
PORT = 2828
TAB = "application/x-moz-tabbrowser-tab"
UBLOCK_VERSION = "1.77.0"

FAILURES = []


RESIDUAL_IDS = [
    "sidebar-switcher-tabs",
    "sync-tabs-menuitem",
    "allTabsMenu-syncedTabs",
    "menu_openFirefoxView",
    "BMB_viewBookmarksToolbar",
    "BMB_bookmarksToolbar",
    "BMB_unsortedBookmarks",
    "bookmarksToolbarFolderMenu",
    "bookmarksToolbarSeparator",
    "PersonalToolbar",
    "context_reopenInContainer",
    "context-openlinkincontainertab",
    "context-openlinkinusercontext-menu",
    "placesContext_open:newcontainertab",
    "menu_newUserContext",
    "urlbarView-context-menu-open-in-container-tab",
    "PanelUI-fxa-menu-services",
    "PanelUI-fxa-cta-menu",
    "PanelUI-fxa-remotetabs-deck",
    "syncEngineBookmarks",
    "syncEngineTabs",
]


def check(name, ok, detail=""):
    if ok:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name} {detail}")
        FAILURES.append(name)


def check_static_css():
    jar = ROOT / "build" / "firefox" / "browser" / "omni.ja"
    if not jar.exists():
        return
    with zipfile.ZipFile(jar) as bundle:
        css = bundle.read(
            "chrome/browser/skin/classic/browser/browser-shared.css"
        ).decode()
        tabs = bundle.read(
            "chrome/browser/skin/classic/browser/tabbrowser/tabs.css"
        ).decode()
        newtab = [
            bundle.read(name).decode()
            for name in (
                "chrome/browser/builtin-addons/newtab/data/css/activity-stream.css",
                "chrome/browser/builtin-addons/newtab/data/css/nova/activity-stream.css",
            )
        ]
    for name in RESIDUAL_IDS:
        rule = f"#{name}" in css or f'[id="{name}"]' in css
        check(f"css hides {name}", rule)
    check("css tab drag motion", "transform var(--fg-tab-drag-motion)" in tabs)
    for index, text in enumerate(newtab):
        check(f"newtab {index} panel motion", "--fg-motion-panel: 180ms" in text)
        check(
            f"newtab {index} customize motion",
            "transform var(--fg-motion-panel) var(--fg-ease)" in text,
        )

    root = ROOT / "build" / "firefox" / "omni.ja"
    if not root.exists():
        return
    with zipfile.ZipFile(root) as bundle:
        tokens = bundle.read(
            "chrome/toolkit/skin/classic/global/design-system/tokens-shared.css"
        ).decode()
    check("css panel motion token", "--fg-motion-panel: 180ms" in tokens)
    version_file = ROOT / "build" / "firefox" / "firegila.version"
    check(
        "installed version marker",
        version_file.exists()
        and version_file.read_text().strip() == (ROOT / "VERSION").read_text().strip(),
        str(version_file),
    )


def check_bundled_extension():
    asset = ROOT / "assets" / "uBlock0@raymondhill.net.xpi"
    built = (
        ROOT
        / "build"
        / "firefox"
        / "distribution"
        / "extensions"
        / "uBlock0@raymondhill.net.xpi"
    )
    if not asset.exists() or not built.exists():
        check("uBlock extension present", False, f"{asset} or {built}")
        return
    with zipfile.ZipFile(asset) as bundle:
        asset_manifest = json.loads(bundle.read("manifest.json"))
    with zipfile.ZipFile(built) as bundle:
        built_manifest = json.loads(bundle.read("manifest.json"))
    version = asset_manifest.get("version")
    check("uBlock extension current", version == UBLOCK_VERSION, str(version))
    check(
        "uBlock extension bundled",
        built_manifest.get("version") == version
        and built_manifest.get("name") == asset_manifest.get("name"),
        f"{built_manifest.get('version')} {built_manifest.get('name')}",
    )


def wait_port(timeout=40):
    end = time.time() + timeout
    while time.time() < end:
        try:
            socket.create_connection((HOST, PORT), 1).close()
            return True
        except OSError:
            time.sleep(0.25)
    return False


class Marionette:
    def __init__(self):
        self.sock = socket.create_connection((HOST, PORT), 20)
        self.sock.settimeout(90)
        self.seq = 0

    def recv(self):
        buf = b""
        while b":" not in buf:
            chunk = self.sock.recv(1)
            if not chunk:
                raise RuntimeError("marionette closed")
            buf += chunk
        size = int(buf.split(b":")[0])
        data = b""
        while len(data) < size:
            data += self.sock.recv(size - len(data))
        return json.loads(data)

    def send(self, msg):
        data = json.dumps(msg).encode()
        self.sock.sendall(str(len(data)).encode() + b":" + data)

    def call(self, name, params):
        self.seq += 1
        self.send([0, self.seq, name, params])
        while True:
            msg = self.recv()
            if msg[1] == self.seq:
                if msg[2]:
                    raise RuntimeError(msg[2])
                return msg[3]

    def init(self):
        self.recv()
        self.call("WebDriver:NewSession", {"capabilities": {}})
        self.call("Marionette:SetContext", {"value": "chrome"})

    def js(self, body, timeout=60000):
        script = (
            "const done=arguments[arguments.length-1];(async()=>{try{"
            + body
            + "}catch(e){done(JSON.stringify({error:String(e),stack:e.stack}));}})();"
        )
        return self.call(
            "WebDriver:ExecuteAsyncScript",
            {
                "script": script,
                "args": [],
                "scriptTimeout": timeout,
                "sandbox": "system",
            },
        )

    def value(self, body, timeout=60000):
        result = self.js(body, timeout)
        if isinstance(result, dict):
            value = result.get("value", result)
        else:
            value = result
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass


class Browser:
    def __init__(self, prefs, tag):
        self.tag = tag
        self.temp = Path(tempfile.mkdtemp(prefix=f"firegila-{tag}-"))
        self.profile = self.temp / "profile"
        self.home = self.temp / "home"
        self.profile.mkdir()
        self.home.mkdir()
        self.log = self.temp / "browser.log"
        with open(self.profile / "user.js", "w") as handle:
            for name, value in prefs.items():
                if isinstance(value, bool):
                    handle.write(
                        f"user_pref({json.dumps(name)}, {'true' if value else 'false'});\n"
                    )
                elif isinstance(value, int):
                    handle.write(f"user_pref({json.dumps(name)}, {value});\n")
                else:
                    handle.write(f"user_pref({json.dumps(name)}, {json.dumps(value)});\n")
        self.proc = None
        self.m = None

    def start(self):
        env = dict(os.environ)
        env["HOME"] = str(self.home)
        env["MOZ_HEADLESS"] = "1"
        log = open(self.log, "ab")
        self.proc = subprocess.Popen(
            [
                str(BIN),
                "--no-remote",
                "--profile",
                str(self.profile),
                "--marionette",
                "--remote-allow-system-access",
                "--new-instance",
            ],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        if not wait_port():
            raise RuntimeError(f"{self.tag}: marionette did not start")
        self.m = Marionette()
        self.m.init()
        return self.m

    def stop(self):
        if self.m:
            try:
                self.m.js("Services.startup.quit(Ci.nsIAppStartup.eAttemptQuit); done('bye');", 10000)
            except Exception:
                pass
            self.m.close()
        if self.proc:
            try:
                self.proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=10)
        self.scan_log()

    def scan_log(self):
        if not self.log.exists():
            return
        ignored = (
            "Certificates.sys.mjs",
            "sourceWin is undefined",
            "Node.contains: Argument 1 does not implement interface Node",
            "ConduitsChild",
            "PortDisconnect",
        )
        errors = []
        for line in self.log.read_text(errors="replace").splitlines():
            if "JavaScript error" not in line and "TypeError" not in line:
                continue
            if any(text in line for text in ignored):
                continue
            errors.append(line)
        check(f"{self.tag} log clean", not errors, " | ".join(errors[:3]))

    def cleanup(self):
        shutil.rmtree(self.temp, ignore_errors=True)


COMMON_PREFS = {
    "browser.startup.page": 1,
    "firegila.workspaces.enabled": False,
}


def drag_body(dragged, target_x, target_y, check_during=""):
    return f"""
    const dragged = {dragged};
    const dr = dragged.getBoundingClientRect();
    const dt = new DataTransfer();
    dt.mozSetDataAt({json.dumps(TAB)}, dragged, 0);
    dt.effectAllowed = "move";
    dragged._dragData = {{
      movingTabs: [dragged],
      movingTabsSet: new Set([dragged]),
      fromTabList: false,
      offsetX: 0,
      offsetY: 0,
      screenX: dr.left + dr.width / 2,
      screenY: dr.top + dr.height / 2,
    }};
    const ev = (type, x, y) => new DragEvent(type, {{
      bubbles: true,
      cancelable: true,
      clientX: x,
      clientY: y,
      screenX: x,
      screenY: y,
      dataTransfer: dt,
    }});
    gBrowser.tabContainer.dispatchEvent(ev("dragstart", dr.left + dr.width / 2, dr.top + dr.height / 2));
    await new Promise(r => setTimeout(r, 80));
    {check_during}
    """


def test_launcher_cache():
    temp = Path(tempfile.mkdtemp(prefix="firegila launcher "))
    try:
        launcher = temp / "firegila"
        shutil.copy(ROOT / "assets" / "firegila-launcher.sh", launcher)
        launcher.chmod(0o755)
        (temp / "firegila.version").write_text("1.4\n")
        fake = temp / "firefox"
        fake.write_text("#!/bin/sh\nexit 0\n")
        fake.chmod(0o755)

        first = temp / "first"
        (first / "startupCache").mkdir(parents=True)
        (first / ".firegila-version").write_text("1.3\n")
        subprocess.run(
            [str(launcher), "--profile", str(first)],
            check=True,
            timeout=20,
        )
        check(
            "launcher purges cache on update",
            not (first / "startupCache").exists()
            and (first / ".firegila-version").read_text().strip() == "1.4",
            str(first),
        )

        second = temp / "second"
        (second / "startupCache").mkdir(parents=True)
        (second / ".firegila-version").write_text("1.4\n")
        subprocess.run(
            [str(launcher), "--profile", str(second)],
            check=True,
            timeout=20,
        )
        check(
            "launcher keeps cache on same version",
            (second / "startupCache").exists()
            and (second / ".firegila-version").read_text().strip() == "1.4",
            str(second),
        )

        third = temp / "third"
        (third / "startupCache").mkdir(parents=True)
        subprocess.run(
            [str(launcher), "--profile", str(third)],
            check=True,
            timeout=20,
        )
        check(
            "launcher purges cache without marker",
            not (third / "startupCache").exists()
            and (third / ".firegila-version").read_text().strip() == "1.4",
            str(third),
        )
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def test_horizontal():
    b = Browser(COMMON_PREFS, "horizontal")
    try:
        m = b.start()
        m.js("await new Promise(r => setTimeout(r, 1800)); done('ok');", 30000)

        state = m.value(r"""
        const principal = Services.scriptSecurityManager.getSystemPrincipal();
        const mk = (u) => gBrowser.addTab(u, { triggeringPrincipal: principal, skipAnimation: true });
        const tabs = [];
        for (let i = 0; i < 4; i++) tabs.push(mk("about:blank?h" + i));
        await new Promise(r => setTimeout(r, 500));
        window.FiregilaTabDrag.testMode = true;
        done(JSON.stringify({ controller: !!window.FiregilaTabDrag, bookmarks: !!window.FiregilaBookmarks }));
        """)
        check("horizontal controller", state.get("controller") is True)
        check("bookmarks controller", state.get("bookmarks") is True)

        prefs = m.value(r"""
        const names = [
          "services.sync.engine.bookmarks",
          "services.sync.engine.tabs",
          "services.sync.prefs.sync.browser.newtabpage.pinned",
          "services.sync.engine.passwords",
          "browser.toolbars.bookmarks.visibility",
        ];
        const out = {};
        for (const name of names) {
          let value;
          try { value = Services.prefs.getBoolPref(name); }
          catch (e) { try { value = Services.prefs.getStringPref(name); } catch (e2) { value = null; } }
          out[name] = { value, locked: Services.prefs.prefIsLocked(name) };
        }
        done(JSON.stringify(out));
        """)
        check(
            "sync bookmarks locked off",
            prefs["services.sync.engine.bookmarks"] == {"value": False, "locked": True},
            str(prefs.get("services.sync.engine.bookmarks")),
        )
        check(
            "sync tabs locked off",
            prefs["services.sync.engine.tabs"] == {"value": False, "locked": True},
            str(prefs.get("services.sync.engine.tabs")),
        )
        check(
            "pinned pref locked",
            prefs["services.sync.prefs.sync.browser.newtabpage.pinned"]
            == {"value": False, "locked": True},
            str(prefs.get("services.sync.prefs.sync.browser.newtabpage.pinned")),
        )
        check(
            "passwords sync on",
            prefs["services.sync.engine.passwords"] == {"value": True, "locked": False},
            str(prefs.get("services.sync.engine.passwords")),
        )
        check(
            "bookmarks toolbar locked off",
            prefs["browser.toolbars.bookmarks.visibility"]
            == {"value": "never", "locked": True},
            str(prefs.get("browser.toolbars.bookmarks.visibility")),
        )

        residual = m.value(r"""
        const ids = [
          "sync-tabs-menuitem",
          "menu_openFirefoxView",
          "bookmarksToolbarFolderMenu",
          "bookmarksToolbarSeparator",
          "PersonalToolbar",
          "context_reopenInContainer",
          "context-openlinkincontainertab",
          "context-openlinkinusercontext-menu",
          "placesContext_open:newcontainertab",
          "menu_newUserContext",
          "urlbarView-context-menu-open-in-container-tab",
        ];
        const hidden = {};
        for (const id of ids) {
          const el = document.getElementById(id);
          const rect = el?.getBoundingClientRect();
          hidden[id] = !el || getComputedStyle(el).display === "none" ||
            (!rect.width && !rect.height);
        }
        const key = document.getElementById("viewBookmarksToolbarKb");
        done(JSON.stringify({ hidden, key: !!key }));
        """)
        for name, value in residual.get("hidden", {}).items():
            check(f"hidden {name}", value is True)
        check("bookmarks toolbar key removed", residual.get("key") is False)

        dialog = m.value(r"""
        let win = window.openDialog(
          "chrome://browser/content/preferences/dialogs/syncChooseWhatToSync.xhtml",
          "",
          "chrome,centerscreen,resizable",
          {}
        );
        await new Promise(r => setTimeout(r, 500));
        const out = {
          bookmarks: !!win.document.querySelector(".sync-engine-bookmarks"),
          tabs: !!win.document.querySelector(".sync-engine-tabs"),
          passwords: !!win.document.querySelector(".sync-engine-passwords"),
        };
        win.close();
        done(JSON.stringify(out));
        """)
        check("sync dialog no bookmarks row", dialog.get("bookmarks") is False)
        check("sync dialog no tabs row", dialog.get("tabs") is False)
        check("sync dialog keeps passwords", dialog.get("passwords") is True)

        drag = m.value(r"""
        const principal = Services.scriptSecurityManager.getSystemPrincipal();
        const mk = (u) => gBrowser.addTab(u, { triggeringPrincipal: principal, skipAnimation: true });
        const tabs = Array.from(gBrowser.tabs).filter(t => t.linkedBrowser?.currentURI?.spec?.includes("about:blank?h"));
        const dragged = tabs[1];
        const target = tabs[3];
        const tr = target.getBoundingClientRect();
        const before = Array.from(gBrowser.tabs).map(t => t.linkedBrowser?.currentURI?.spec);
        const dt = new DataTransfer();
        dt.mozSetDataAt("application/x-moz-tabbrowser-tab", dragged, 0);
        dt.effectAllowed = "move";
        const dr = dragged.getBoundingClientRect();
        dragged._dragData = {
          movingTabs: [dragged], movingTabsSet: new Set([dragged]), fromTabList: false,
          offsetX: 0, offsetY: 0, screenX: dr.left + dr.width / 2, screenY: dr.top + dr.height / 2,
        };
        const ev = (type, x, y) => new DragEvent(type, {
          bubbles: true, cancelable: true, clientX: x, clientY: y, screenX: x, screenY: y, dataTransfer: dt,
        });
        gBrowser.tabContainer.dispatchEvent(ev("dragstart", dr.left + dr.width / 2, dr.top + dr.height / 2));
        await new Promise(r => setTimeout(r, 80));
        const button = document.getElementById("tabs-newtab-button");
        const buttonHidden = getComputedStyle(button).visibility === "hidden";
        const go = { x: tr.left + 6, y: tr.top + tr.height / 2 };
        for (let i = 0; i < 5; i++) {
          window.dispatchEvent(ev("dragover", go.x, go.y));
          await new Promise(r => setTimeout(r, 30));
        }
        const placeholder = document.getElementById("firegila-tab-drop-placeholder");
        const placeholderHidden = !placeholder || placeholder.hidden;
        const ghost = window.FiregilaTabDrag.dragImage;
        const ghostRect = ghost?.getBoundingClientRect();
        const toolbarRect = document.getElementById("TabsToolbar").getBoundingClientRect();
        const ghostStuck = !!ghostRect
          && getComputedStyle(ghost).visibility !== "hidden"
          && ghostRect.top >= toolbarRect.top - 1
          && ghostRect.bottom <= toolbarRect.bottom + 1;
        window.dispatchEvent(ev("drop", go.x, go.y));
        await new Promise(r => setTimeout(r, 200));
        const after = Array.from(gBrowser.tabs).map(t => t.linkedBrowser?.currentURI?.spec);
        done(JSON.stringify({
          before, after, buttonHidden, placeholderHidden, ghostStuck,
          active: window.FiregilaTabDrag.active,
        }));
        """)
        check("new tab button hidden", drag.get("buttonHidden") is True)
        check("horizontal local placeholder hidden", drag.get("placeholderHidden") is True)
        check("drag ghost sticks to tab bar", drag.get("ghostStuck") is True, str(drag))
        after = drag.get("after", [])
        check(
            "horizontal drag order",
            "about:blank?h1" in str(after)
            and "about:blank?h3" in str(after)
            and after.index("about:blank?h1") < after.index("about:blank?h3"),
            str(after),
        )
        check("horizontal drag cleanup", drag.get("active") is False)

        cue = m.value(r"""
        const principal = Services.scriptSecurityManager.getSystemPrincipal();
        const tabs = Array.from(gBrowser.tabs).filter(t => t.linkedBrowser?.currentURI?.spec?.includes("about:blank?h"));
        const dragged = tabs[0];
        const target = tabs[2];
        const dr = dragged.getBoundingClientRect();
        const tr = target.getBoundingClientRect();
        const dt = new DataTransfer();
        dt.mozSetDataAt("application/x-moz-tabbrowser-tab", dragged, 0);
        dt.effectAllowed = "move";
        dragged._dragData = {
          movingTabs: [dragged], movingTabsSet: new Set([dragged]), fromTabList: false,
          offsetX: 0, offsetY: 0, screenX: dr.left + dr.width / 2, screenY: dr.top + dr.height / 2,
        };
        const ev = (type, x, y) => new DragEvent(type, {
          bubbles: true, cancelable: true, clientX: x, clientY: y, screenX: x, screenY: y, dataTransfer: dt,
        });
        gBrowser.tabContainer.dispatchEvent(ev("dragstart", dr.left + dr.width / 2, dr.top + dr.height / 2));
        await new Promise(r => setTimeout(r, 80));
        const go = { x: tr.left + tr.width / 2, y: tr.top + tr.height / 2 };
        for (let i = 0; i < 3; i++) {
          window.dispatchEvent(ev("dragover", go.x, go.y));
          await new Promise(r => setTimeout(r, 25));
        }
        await new Promise(r => setTimeout(r, 600));
        const placeholder = document.getElementById("firegila-tab-drop-placeholder");
        const earlyCandidate = document.querySelector("[fg-group-candidate]");
        const earlyBackground = earlyCandidate?.querySelector(".tab-background");
        const earlyStyle = earlyBackground ? getComputedStyle(earlyBackground) : null;
        const selectedStyle = getComputedStyle(gBrowser.selectedTab.querySelector(".tab-background"));
        const early = {
          candidate: !!earlyCandidate,
          placeholderHidden: placeholder?.hidden,
          groupActive: window.FiregilaTabDrag.groupActive,
          shifts: window.FiregilaTabDrag.shifts.size,
          borderColor: earlyStyle?.borderTopColor,
          borderStyle: earlyStyle?.borderTopStyle,
          outlineStyle: earlyStyle?.outlineStyle,
          selectedOutline: selectedStyle.outlineStyle,
          shadow: earlyStyle?.boxShadow,
        };
        window.dispatchEvent(ev("dragover", go.x + 8, go.y));
        await new Promise(r => setTimeout(r, 150));
        const moved = {
          candidate: !!document.querySelector("[fg-group-candidate]"),
          placeholderHidden: placeholder?.hidden,
          groupActive: window.FiregilaTabDrag.groupActive,
        };
        window.dispatchEvent(ev("drop", go.x, go.y));
        await new Promise(r => setTimeout(r, 200));
        done(JSON.stringify({ early, moved }));
        """)
        check("group pre cue", cue.get("early", {}).get("candidate") is True)
        check("group cue active", cue.get("early", {}).get("groupActive") is True, str(cue.get("early")))
        check("group cue hides placeholder", cue.get("early", {}).get("placeholderHidden") is True)
        check("group cue clears shifts", cue.get("early", {}).get("shifts") == 0, str(cue.get("early")))
        check(
            "group cue removes focus outline",
            cue.get("early", {}).get("selectedOutline") == "none",
            str(cue.get("early")),
        )
        check(
            "group cue cancels on move",
            cue.get("moved", {}).get("candidate") is False
            and cue.get("moved", {}).get("groupActive") is False,
            str(cue.get("moved")),
        )
        check(
            "group cue single border",
            cue.get("early", {}).get("borderStyle") == "solid"
            and cue.get("early", {}).get("outlineStyle") == "none"
            and cue.get("early", {}).get("shadow") in ("none", ""),
            str(cue.get("early")),
        )

        group_drop = m.value(r"""
        const principal = Services.scriptSecurityManager.getSystemPrincipal();
        const mk = (u) => gBrowser.addTab(u, { triggeringPrincipal: principal, skipAnimation: true });
        const dragged = mk("about:blank?gdrag");
        const target = mk("about:blank?gtarget");
        await new Promise(r => setTimeout(r, 400));
        gBrowser.selectedTab = dragged;
        await new Promise(r => setTimeout(r, 100));
        const dr = dragged.getBoundingClientRect();
        const tr = target.getBoundingClientRect();
        const dt = new DataTransfer();
        dt.mozSetDataAt("application/x-moz-tabbrowser-tab", dragged, 0);
        dt.effectAllowed = "move";
        dragged._dragData = {
          movingTabs: [dragged], movingTabsSet: new Set([dragged]), fromTabList: false,
          offsetX: 0, offsetY: 0, screenX: dr.left + dr.width / 2, screenY: dr.top + dr.height / 2,
        };
        const ev = (type, x, y) => new DragEvent(type, {
          bubbles: true, cancelable: true, clientX: x, clientY: y,
          screenX: x, screenY: y, dataTransfer: dt,
        });
        gBrowser.tabContainer.dispatchEvent(
          ev("dragstart", dr.left + dr.width / 2, dr.top + dr.height / 2)
        );
        await new Promise(r => setTimeout(r, 80));
        for (let i = 0; i < 4; i++) {
          window.dispatchEvent(ev("dragover", tr.left + tr.width / 2, tr.top + tr.height / 2));
          await new Promise(r => setTimeout(r, 30));
        }
        await new Promise(r => setTimeout(r, 600));
        const candidate = !!document.querySelector("[fg-group-candidate]");
        window.dispatchEvent(ev("drop", tr.left + tr.width / 2, tr.top + tr.height / 2));
        await new Promise(r => setTimeout(r, 350));
        gBrowser.tabContainer.dispatchEvent(
          ev("dragend", tr.left + tr.width / 2, tr.top + tr.height / 2)
        );
        await new Promise(r => setTimeout(r, 150));
        const groups = Array.from(document.querySelectorAll("tab-group")).map(group => ({
          tabs: group.tabs.map(tab => tab.linkedBrowser?.currentURI?.spec),
        }));
        done(JSON.stringify({ candidate, groups, active: window.FiregilaTabDrag.active }));
        """)
        check("group drop candidate", group_drop.get("candidate") is True, str(group_drop))
        groups = group_drop.get("groups", [])
        check(
            "group drop creates group",
            any(
                "about:blank?gdrag" in group.get("tabs", [])
                and "about:blank?gtarget" in group.get("tabs", [])
                for group in groups
            ),
            str(groups),
        )
        check("group drop cleanup", group_drop.get("active") is False, str(group_drop))

        group_label = m.value(r"""
        const principal = Services.scriptSecurityManager.getSystemPrincipal();
        const mk = (u) => gBrowser.addTab(u, { triggeringPrincipal: principal, skipAnimation: true });
        const before = mk("about:blank?glbefore");
        const target = mk("about:blank?gltarget");
        const g0 = mk("about:blank?gl0");
        const g1 = mk("about:blank?gl1");
        await new Promise(r => setTimeout(r, 400));
        const group = gBrowser.addTabGroup([g0, g1], { label: "LabelCheck", color: "blue" });
        await new Promise(r => setTimeout(r, 400));
        const label = group.labelElement;
        const lr = label.getBoundingClientRect();
        const tr = target.getBoundingClientRect();
        const dt = new DataTransfer();
        dt.mozSetDataAt("application/x-moz-tabbrowser-tab", label, 0);
        dt.effectAllowed = "move";
        label._dragData = {
          movingTabs: [label], movingTabsSet: new Set([label]), fromTabList: false,
          offsetX: 0, offsetY: 0, screenX: lr.left + lr.width / 2, screenY: lr.top + lr.height / 2,
        };
        const ev = (type, x, y) => new DragEvent(type, {
          bubbles: true, cancelable: true, clientX: x, clientY: y, screenX: x, screenY: y, dataTransfer: dt,
        });
        gBrowser.tabContainer.dispatchEvent(ev("dragstart", lr.left + lr.width / 2, lr.top + lr.height / 2));
        await new Promise(r => setTimeout(r, 80));
        const during = {
          active: window.FiregilaTabDrag.active,
          block: window.FiregilaTabDrag.block,
          dragging: group.isBeingDragged,
          collapsed: group.collapsed,
          moving: group.hasAttribute("movingtabgroup"),
          tabRects: group.tabs.map(t => {
            const r = t.getBoundingClientRect();
            const c = getComputedStyle(t);
            return { w: r.width, h: r.height, display: c.display, visibility: c.visibility };
          }),
        };
        const go = { x: tr.left + 6, y: tr.top + tr.height / 2 };
        for (let i = 0; i < 5; i++) {
          window.dispatchEvent(ev("dragover", go.x, go.y));
          await new Promise(r => setTimeout(r, 30));
        }
        window.dispatchEvent(ev("drop", go.x, go.y));
        await new Promise(r => setTimeout(r, 200));
        label.dispatchEvent(ev("dragend", go.x, go.y));
        await new Promise(r => setTimeout(r, 120));
        const order = Array.from(gBrowser.tabs).map(t => t.linkedBrowser?.currentURI?.spec);
        done(JSON.stringify({
          during,
          order,
          dragging: group.isBeingDragged,
          active: window.FiregilaTabDrag.active,
          collapsed: group.collapsed,
          groupTabs: group.tabs.map(t => t.linkedBrowser?.currentURI?.spec),
          visibleTabs: group.tabs.filter(t => {
            const r = t.getBoundingClientRect();
            return r.width > 0 && r.height > 0;
          }).length,
        }));
        """)
        check("group label drag active", group_label.get("during", {}).get("active") is True)
        check("group label drag block", group_label.get("during", {}).get("block") is True)
        check("group label drag state", group_label.get("during", {}).get("dragging") is True)
        check("expanded group hides tabs", group_label.get("during", {}).get("collapsed") is True)
        check("expanded group moving state", group_label.get("during", {}).get("moving") is True)
        check(
            "expanded group tab rects hidden",
            all(
                item.get("w", 0) == 0 or item.get("h", 0) == 0
                for item in group_label.get("during", {}).get("tabRects", [])
            ),
            str(group_label.get("during", {}).get("tabRects")),
        )
        order = group_label.get("order", [])
        check(
            "group label moved",
            "about:blank?gl0" in str(order)
            and "about:blank?gltarget" in str(order)
            and order.index("about:blank?gl0") < order.index("about:blank?gltarget"),
            str(order),
        )
        check("group label cleanup", group_label.get("dragging") is False)
        check("group label controller cleanup", group_label.get("active") is False)
        check("group label restored expanded", group_label.get("collapsed") is False)
        check("group label tabs restored", group_label.get("visibleTabs") == 2)

        split = m.value(r"""
        const principal = Services.scriptSecurityManager.getSystemPrincipal();
        const mk = (u) => gBrowser.addTab(u, { triggeringPrincipal: principal, skipAnimation: true });
        const target = mk("about:blank?sp0");
        const s1 = mk("about:blank?sp1");
        const s2 = mk("about:blank?sp2");
        const s3 = mk("about:blank?sp3");
        await new Promise(r => setTimeout(r, 400));
        const wrapper = gBrowser.addTabSplitView([s1, s2]);
        await new Promise(r => setTimeout(r, 400));
        const wr = wrapper.getBoundingClientRect();
        const tr = target.getBoundingClientRect();
        const dt = new DataTransfer();
        dt.mozSetDataAt("application/x-moz-tabbrowser-tab", wrapper, 0);
        dt.effectAllowed = "move";
        wrapper._dragData = {
          movingTabs: [wrapper], movingTabsSet: new Set([wrapper]), fromTabList: false,
          offsetX: 0, offsetY: 0, screenX: wr.left + wr.width / 2, screenY: wr.top + wr.height / 2,
        };
        const ev = (type, x, y) => new DragEvent(type, {
          bubbles: true, cancelable: true, clientX: x, clientY: y, screenX: x, screenY: y, dataTransfer: dt,
        });
        gBrowser.tabContainer.dispatchEvent(ev("dragstart", wr.left + wr.width / 2, wr.top + wr.height / 2));
        await new Promise(r => setTimeout(r, 80));
        const during = {
          active: window.FiregilaTabDrag.active,
          block: window.FiregilaTabDrag.block,
          full: window.FiregilaTabDrag.placeholderFull,
        };
        const go = { x: tr.left + 6, y: tr.top + tr.height / 2 };
        for (let i = 0; i < 5; i++) {
          window.dispatchEvent(ev("dragover", go.x, go.y));
          await new Promise(r => setTimeout(r, 30));
        }
        const placeholder = document.getElementById("firegila-tab-drop-placeholder");
        const placeholderHidden = !placeholder || placeholder.hidden;
        window.dispatchEvent(ev("drop", go.x, go.y));
        await new Promise(r => setTimeout(r, 200));
        wrapper.dispatchEvent(ev("dragend", go.x, go.y));
        await new Promise(r => setTimeout(r, 120));
        const order = Array.from(gBrowser.tabs).map(t => t.linkedBrowser?.currentURI?.spec);
        done(JSON.stringify({
          during, order, active: window.FiregilaTabDrag.active,
          placeholderHidden,
          wrapperVisible: wrapper.style.visibility,
          split: wrapper.tabs.map(t => t.linkedBrowser?.currentURI?.spec),
        }));
        """)
        check("split drag active", split.get("during", {}).get("active") is True)
        check("split drag block", split.get("during", {}).get("block") is True)
        check("split drag full placeholder", split.get("during", {}).get("full") is True)
        check("split local placeholder hidden", split.get("placeholderHidden") is True)
        order = split.get("order", [])
        check(
            "split moved",
            "about:blank?sp1" in str(order)
            and "about:blank?sp0" in str(order)
            and order.index("about:blank?sp1") < order.index("about:blank?sp0"),
            str(order),
        )
        check("split cleanup", split.get("active") is False)
        check("split visible", split.get("wrapperVisible") == "")

        motion = m.value(r"""
        const root = getComputedStyle(document.documentElement);
        done(JSON.stringify({
          panelMotion: root.getPropertyValue("--fg-motion-panel").trim(),
          tabsMotion: root.getPropertyValue("--fg-tabs-motion").trim(),
          sidebarMotion: window.__fgMotion?.duration,
        }));
        """)
        check("panel motion token", motion.get("panelMotion") == "180ms", str(motion))
        check("tabs motion token", motion.get("tabsMotion") == "180ms", str(motion))
        check("sidebar panel motion", motion.get("sidebarMotion") == 180, str(motion))

    finally:
        b.stop()
        b.cleanup()


def test_horizontal_geometry():
    b = Browser(COMMON_PREFS, "hgeometry")
    try:
        m = b.start()
        m.js("await new Promise(r => setTimeout(r, 1800)); done('ok');", 30000)

        geometry = m.value(r"""
        const principal = Services.scriptSecurityManager.getSystemPrincipal();
        const mk = (u) => gBrowser.addTab(u, { triggeringPrincipal: principal, skipAnimation: true });
        for (let i = 0; i < 20; i++) mk("about:blank?g" + i);
        await new Promise(r => setTimeout(r, 700));
        const tabs = Array.from(gBrowser.tabs).filter(t => t.linkedBrowser?.currentURI?.spec?.includes("about:blank?g"));
        const dragged = tabs[10];
        const target = tabs[2];
        gBrowser.selectedTab = dragged;
        const dr = dragged.getBoundingClientRect();
        const dt = new DataTransfer();
        dt.mozSetDataAt("application/x-moz-tabbrowser-tab", dragged, 0);
        dt.effectAllowed = "move";
        dragged._dragData = {
          movingTabs: [dragged], movingTabsSet: new Set([dragged]), fromTabList: false,
          offsetX: 0, offsetY: 0, screenX: dr.left + dr.width / 2, screenY: dr.top + dr.height / 2,
        };
        const ev = (type, x, y) => new DragEvent(type, {
          bubbles: true, cancelable: true, clientX: x, clientY: y, screenX: x, screenY: y, dataTransfer: dt,
        });
        gBrowser.tabContainer.dispatchEvent(ev("dragstart", dr.left + dr.width / 2, dr.top + dr.height / 2));
        const placeholder = document.getElementById("firegila-tab-drop-placeholder");
        const started = {
          active: window.FiregilaTabDrag.active,
          dragSize: window.FiregilaTabDrag.dragSize,
          tabWidth: dragged.getBoundingClientRect().width,
          tabTransition: getComputedStyle(dragged).transition,
        };
        for (let i = 0; i < 8; i++) {
          const tr = target.getBoundingClientRect();
          window.dispatchEvent(ev("dragover", tr.left + 2, tr.top + tr.height / 2));
          await new Promise(r => setTimeout(r, 35));
        }
        await new Promise(r => setTimeout(r, 260));
        const ph = placeholder.getBoundingClientRect();
        const visible = tabs
          .filter(t => t !== dragged)
          .map(t => ({ left: t.getBoundingClientRect().left, right: t.getBoundingClientRect().right }))
          .sort((a, b) => a.left - b.left);
        const gaps = [];
        for (let i = 1; i < visible.length; i++) {
          const size = visible[i].left - visible[i - 1].right;
          if (Math.abs(size) > 0.05) {
            gaps.push({ size, start: visible[i - 1].right, end: visible[i].left });
          }
        }
        const over = {
          insert: window.FiregilaTabDrag.insertIndex,
          placeholderHidden: placeholder.hidden,
          placeholderLeft: ph.left,
          placeholderRight: ph.right,
          placeholderWidth: ph.width,
          gaps,
        };
        gBrowser.tabContainer.arrowScrollbox.scrollByPixels(60);
        await new Promise(r => setTimeout(r, 700));
        const phScroll = placeholder.getBoundingClientRect();
        const visibleScroll = tabs
          .filter(t => t !== dragged)
          .map(t => ({ left: t.getBoundingClientRect().left, right: t.getBoundingClientRect().right }))
          .sort((a, b) => a.left - b.left);
        const gapsScroll = [];
        for (let i = 1; i < visibleScroll.length; i++) {
          const size = visibleScroll[i].left - visibleScroll[i - 1].right;
          if (Math.abs(size) > 0.05) {
            gapsScroll.push({ size, start: visibleScroll[i - 1].right, end: visibleScroll[i].left });
          }
        }
        const scrolled = {
          placeholderHidden: placeholder.hidden,
          placeholderLeft: phScroll.left,
          placeholderRight: phScroll.right,
          placeholderWidth: phScroll.width,
          gaps: gapsScroll,
        };
        const tr = target.getBoundingClientRect();
        window.dispatchEvent(ev("drop", tr.left + 2, tr.top + tr.height / 2));
        await new Promise(r => setTimeout(r, 220));
        gBrowser.tabContainer.dispatchEvent(ev("dragend", tr.left + 2, tr.top + tr.height / 2));
        await new Promise(r => setTimeout(r, 180));
        done(JSON.stringify({
          started,
          over,
          scrolled,
          after: {
            active: window.FiregilaTabDrag.active,
            order: Array.from(gBrowser.tabs).map(t => t.linkedBrowser?.currentURI?.spec),
            selected: gBrowser.selectedTab?.linkedBrowser?.currentURI?.spec,
          },
        }));
        """)
        started = geometry.get("started", {})
        over = geometry.get("over", {})
        gaps = over.get("gaps", [])
        gap = gaps[0] if len(gaps) == 1 else {}
        check("drag starts active", started.get("active") is True, str(started))
        check(
            "drag width measured",
            abs(started.get("dragSize", 0) - started.get("tabWidth", 0)) < 0.1,
            str(started),
        )
        check(
            "drag motion",
            "0.08s" in started.get("tabTransition", ""),
            str(started),
        )
        check("drag one slot gap", len(gaps) == 1, str(gaps))
        check(
            "drag gap matches width",
            abs(gap.get("size", 0) - started.get("dragSize", 0)) < 0.1,
            str(gap),
        )
        check("drag local placeholder hidden", over.get("placeholderHidden") is True, str(over))
        scrolled = geometry.get("scrolled", {})
        scroll_gaps = scrolled.get("gaps", [])
        scroll_gap = scroll_gaps[0] if len(scroll_gaps) == 1 else {}
        check("drag scroll one slot gap", len(scroll_gaps) == 1, str(scroll_gaps))
        check(
            "drag scroll slot",
            abs(scroll_gap.get("size", 0) - started.get("dragSize", 0)) < 0.1,
            str(scrolled),
        )
        after = geometry.get("after", {})
        order = after.get("order", [])
        check("drag geometry cleanup", after.get("active") is False, str(after))
        check(
            "drag geometry order",
            "about:blank?g10" in order
            and "about:blank?g2" in order
            and order.index("about:blank?g10") < order.index("about:blank?g2"),
            str(order),
        )
        check("drag geometry selection", after.get("selected") == "about:blank?g10", str(after))
    finally:
        b.stop()
        b.cleanup()


def test_pinned():
    b = Browser(
        {
            **COMMON_PREFS,
            "browser.tabs.dragDrop.createGroup.delayMS": 10000,
        },
        "pinned",
    )
    try:
        m = b.start()
        m.js("await new Promise(r => setTimeout(r, 1800)); done('ok');", 30000)
        result = m.value(r"""
        const principal = Services.scriptSecurityManager.getSystemPrincipal();
        const mk = u => gBrowser.addTab(u, { triggeringPrincipal: principal, skipAnimation: true });
        const tabs = [];
        for (let i = 0; i < 5; i++) tabs.push(mk("about:blank?pin" + i));
        await new Promise(r => setTimeout(r, 500));
        for (let i = 0; i < 3; i++) {
          gBrowser.pinTab(tabs[i]);
          await new Promise(r => setTimeout(r, 80));
        }
        await new Promise(r => setTimeout(r, 300));
        window.FiregilaTabDrag.testMode = true;

        const drag = async (dragged, target, x, y) => {
          gBrowser.selectedTab = dragged;
          await new Promise(r => setTimeout(r, 100));
          const dt = new DataTransfer();
          dt.mozSetDataAt("application/x-moz-tabbrowser-tab", dragged, 0);
          dt.effectAllowed = "move";
          const dr = dragged.getBoundingClientRect();
          dragged._dragData = {
            movingTabs: [dragged], movingTabsSet: new Set([dragged]), fromTabList: false,
            offsetX: 0, offsetY: 0, screenX: dr.left + dr.width / 2, screenY: dr.top + dr.height / 2,
          };
          const ev = (type, px, py) => new DragEvent(type, {
            bubbles: true, cancelable: true, clientX: px, clientY: py,
            screenX: px, screenY: py, dataTransfer: dt,
          });
          gBrowser.tabContainer.dispatchEvent(
            ev("dragstart", dr.left + dr.width / 2, dr.top + dr.height / 2)
          );
          await new Promise(r => setTimeout(r, 80));
          for (let i = 0; i < 5; i++) {
            window.dispatchEvent(ev("dragover", x, y));
            await new Promise(r => setTimeout(r, 30));
          }
          const during = {
            insert: window.FiregilaTabDrag.insertIndex,
            beyond: window.FiregilaTabDrag.pointerBeyondPinned(),
            active: window.FiregilaTabDrag.active,
          };
          window.dispatchEvent(ev("drop", x, y));
          await new Promise(r => setTimeout(r, 300));
          gBrowser.tabContainer.dispatchEvent(ev("dragend", x, y));
          await new Promise(r => setTimeout(r, 200));
          return { during, active: window.FiregilaTabDrag.active };
        };

        let pinned = Array.from(gBrowser.tabs).filter(t => t.pinned);
        const reorder = await drag(
          pinned[0],
          pinned[2],
          pinned[2].getBoundingClientRect().right - 4,
          pinned[2].getBoundingClientRect().top + pinned[2].getBoundingClientRect().height / 2
        );
        const reorderOrder = Array.from(gBrowser.tabs).map(t => t.linkedBrowser?.currentURI?.spec);
        const reorderPinned = gBrowser.pinnedTabCount;

        pinned = Array.from(gBrowser.tabs).filter(t => t.pinned);
        const unpinned = Array.from(gBrowser.tabs).filter(t => !t.pinned);
        const unpinTarget = unpinned[1];
        const targetRect = unpinTarget.getBoundingClientRect();
        const unpin = await drag(
          pinned[0],
          unpinTarget,
          targetRect.left + targetRect.width / 2,
          targetRect.top + targetRect.height / 2
        );
        const unpinOrder = Array.from(gBrowser.tabs).map(t => t.linkedBrowser?.currentURI?.spec);
        done(JSON.stringify({
          reorder,
          reorderOrder,
          reorderPinned,
          unpin,
          unpinOrder,
          unpinPinned: gBrowser.pinnedTabCount,
        }));
        """)
        check("pinned drag active", result.get("reorder", {}).get("during", {}).get("active") is True, str(result))
        check("pinned drag stays pinned", result.get("reorderPinned") == 3, str(result))
        order = result.get("reorderOrder", [])
        check(
            "pinned drag order",
            "about:blank?pin1" in order
            and "about:blank?pin2" in order
            and "about:blank?pin0" in order
            and order.index("about:blank?pin1") < order.index("about:blank?pin2")
            < order.index("about:blank?pin0"),
            str(order),
        )
        check("pinned reorder cleanup", result.get("reorder", {}).get("active") is False, str(result))
        check(
            "pinned unpin target",
            result.get("unpin", {}).get("during", {}).get("beyond") is True,
            str(result),
        )
        check("pinned unpin count", result.get("unpinPinned") == 2, str(result))
        check(
            "pinned unpin order",
            "about:blank?pin1" in result.get("unpinOrder", [])
            and result.get("unpinOrder").index("about:blank?pin1")
            >= result.get("unpinPinned", 0),
            str(result.get("unpinOrder")),
        )
        check("pinned unpin cleanup", result.get("unpin", {}).get("active") is False, str(result))
    finally:
        b.stop()
        b.cleanup()


def test_cross_window():
    b = Browser(
        {
            **COMMON_PREFS,
            "browser.tabs.dragDrop.createGroup.delayMS": 10000,
        },
        "crosswindow",
    )
    try:
        m = b.start()
        m.js("await new Promise(r => setTimeout(r, 1800)); done('ok');", 30000)

        result = m.value(r"""
        const principal = Services.scriptSecurityManager.getSystemPrincipal();
        const mk = (gb, url) => gb.addTab(url, { triggeringPrincipal: principal, skipAnimation: true });
        for (let i = 0; i < 4; i++) mk(gBrowser, "about:blank?src" + i);
        await new Promise(r => setTimeout(r, 600));
        let srcTabs = Array.from(gBrowser.tabs).filter(t => t.linkedBrowser?.currentURI?.spec?.includes("about:blank?src"));
        gBrowser.selectedTab = srcTabs[1];
        await new Promise(r => setTimeout(r, 300));

        const w2 = window.OpenBrowserWindow({ private: false });
        await new Promise(r => setTimeout(r, 1600));
        for (let i = 0; i < 20; i++) mk(w2.gBrowser, "about:blank?dst" + i);
        await new Promise(r => setTimeout(r, 800));
        w2.gBrowser.tabContainer.arrowScrollbox.scrollByPixels(-100000);
        w2.gBrowser.selectedTab = w2.gBrowser.tabs[0];
        await new Promise(r => setTimeout(r, 300));

        const evFor = (win, type, x, y, dt) => new win.DragEvent(type, {
          bubbles: true, cancelable: true, clientX: x, clientY: y,
          screenX: x, screenY: y, dataTransfer: dt,
        });
        const makeDT = tabs => {
          const dt = new DataTransfer();
          dt.mozSetDataAt("application/x-moz-tabbrowser-tab", tabs[0], 0);
          dt.effectAllowed = "move";
          tabs[0]._dragData = {
            movingTabs: tabs, movingTabsSet: new Set(tabs), fromTabList: false,
            offsetX: 0, offsetY: 0, screenX: 0, screenY: 0,
          };
          return dt;
        };
        const run = async (tabs, targetIndex) => {
          const dt = makeDT(tabs);
          const dr = tabs[0].getBoundingClientRect();
          tabs[0]._dragData.screenX = dr.left + dr.width / 2;
          tabs[0]._dragData.screenY = dr.top + dr.height / 2;
          gBrowser.tabContainer.dispatchEvent(
            evFor(window, "dragstart", dr.left + dr.width / 2, dr.top + dr.height / 2, dt)
          );
          await new Promise(r => setTimeout(r, 80));
          const dstTabs = Array.from(w2.gBrowser.tabs)
            .filter(t => t.linkedBrowser?.currentURI?.spec?.includes("about:blank?dst"));
          const target = dstTabs[targetIndex];
          const tr0 = target.getBoundingClientRect();
          w2.dispatchEvent(evFor(w2, "dragenter", tr0.left + 2, tr0.top + tr0.height / 2, dt));
          for (let i = 0; i < 6; i++) {
            const tr = target.getBoundingClientRect();
            w2.dispatchEvent(evFor(w2, "dragover", tr.left + 2, tr.top + tr.height / 2, dt));
            await new Promise(r => setTimeout(r, 40));
          }
          await new Promise(r => setTimeout(r, 400));
          const c = w2.FiregilaTabDrag;
          const ph = w2.document.getElementById("firegila-tab-drop-placeholder");
          const pr = ph.getBoundingClientRect();
          const visible = Array.from(w2.gBrowser.tabs)
            .map(t => {
              const rect = t.getBoundingClientRect();
              return { left: rect.left, right: rect.right, width: rect.width };
            })
            .filter(t => t.width > 0)
            .sort((a, b) => a.left - b.left);
          const gaps = [];
          for (let i = 1; i < visible.length; i++) {
            const size = visible[i].left - visible[i - 1].right;
            if (Math.abs(size) > 0.05) {
              gaps.push({ size, start: visible[i - 1].right, end: visible[i].left });
            }
          }
          const before = {
            mode: c.mode,
            count: c.movingCount,
            dragSize: c.dragSize,
            sourceWidth: tabs[0].getBoundingClientRect().width,
            dstWidth: dstTabs[0].getBoundingClientRect().width,
            full: c.placeholderFull,
            placeholderHidden: ph.hidden,
            placeholderLeft: pr.left,
            placeholderRight: pr.right,
            placeholderWidth: pr.width,
            placeholderHeight: pr.height,
            gaps,
          };
          const tr = target.getBoundingClientRect();
          w2.dispatchEvent(evFor(w2, "drop", tr.left + 2, tr.top + tr.height / 2, dt));
          await new Promise(r => setTimeout(r, 500));
          gBrowser.tabContainer.dispatchEvent(
            evFor(window, "dragend", tr.left + 2, tr.top + tr.height / 2, dt)
          );
          await new Promise(r => setTimeout(r, 300));
          before.after = {
            srcActive: window.FiregilaTabDrag.active,
            dstActive: w2.FiregilaTabDrag.active,
            order: Array.from(w2.gBrowser.tabs).map(t => t.linkedBrowser?.currentURI?.spec),
          };
          return before;
        };

        const single = await run([srcTabs[1]], 2);
        srcTabs = Array.from(gBrowser.tabs).filter(t => t.linkedBrowser?.currentURI?.spec?.includes("about:blank?src"));
        gBrowser.selectedTab = srcTabs[0];
        gBrowser.addToMultiSelectedTabs(srcTabs[2]);
        await new Promise(r => setTimeout(r, 200));
        const multi = await run([srcTabs[0], srcTabs[2]], 5);
        const split0 = mk(gBrowser, "about:blank?spl0");
        const split1 = mk(gBrowser, "about:blank?spl1");
        await new Promise(r => setTimeout(r, 500));
        const split = gBrowser.addTabSplitView([split0, split1], { trigger: "menu_add" });
        await new Promise(r => setTimeout(r, 500));
        const crossSplit = await run([split], 7);
        done(JSON.stringify({ single, multi, split: crossSplit }));
        """)
        single = result.get("single", {})
        single_before = single
        single_gaps = single_before.get("gaps", [])
        single_gap = single_gaps[0] if len(single_gaps) == 1 else {}
        check("cross window target mode", single_before.get("mode") == "target", str(single_before))
        check(
            "cross window single target width",
            abs(single_before.get("dragSize", 0) - single_before.get("dstWidth", 0)) < 0.1
            and single_before.get("sourceWidth", 0) > single_before.get("dstWidth", 0) + 50,
            str(single_before),
        )
        check("cross window single slot", len(single_gaps) == 1, str(single_gaps))
        check(
            "cross window single placeholder",
            single_before.get("placeholderHidden") is False
            and abs(single_before.get("placeholderWidth", 0) - single_before.get("dragSize", 0) + 4) < 0.75
            and abs(single_before.get("placeholderLeft", 0) - single_gap.get("start", 0) - 2) < 0.75,
            str(single_before),
        )
        single_order = single.get("after", {}).get("order", [])
        check(
            "cross window single order",
            "about:blank?src1" in single_order
            and "about:blank?dst2" in single_order
            and single_order.index("about:blank?src1") < single_order.index("about:blank?dst2"),
            str(single_order),
        )
        check(
            "cross window single cleanup",
            single.get("after", {}).get("srcActive") is False
            and single.get("after", {}).get("dstActive") is False,
            str(single.get("after", {})),
        )

        multi = result.get("multi", {})
        multi_gaps = multi.get("gaps", [])
        multi_gap = multi_gaps[0] if len(multi_gaps) == 1 else {}
        check("cross window multi count", multi.get("count") == 2, str(multi))
        check(
            "cross window multi target width",
            abs(multi.get("dragSize", 0) - multi.get("dstWidth", 0) * 2) < 0.1,
            str(multi),
        )
        check("cross window multi slot", len(multi_gaps) == 1, str(multi_gaps))
        check(
            "cross window multi placeholder",
            multi.get("full") is True
            and multi.get("placeholderHidden") is False
            and abs(multi.get("placeholderWidth", 0) - multi.get("dragSize", 0)) < 0.75
            and abs(multi.get("placeholderLeft", 0) - multi_gap.get("start", 0)) < 0.75,
            str(multi),
        )
        multi_order = multi.get("after", {}).get("order", [])
        check(
            "cross window multi order",
            "about:blank?src0" in multi_order
            and "about:blank?src3" in multi_order
            and "about:blank?dst5" in multi_order
            and max(multi_order.index("about:blank?src0"), multi_order.index("about:blank?src3"))
            < multi_order.index("about:blank?dst5"),
            str(multi_order),
        )
        check(
            "cross window multi cleanup",
            multi.get("after", {}).get("srcActive") is False
            and multi.get("after", {}).get("dstActive") is False,
            str(multi.get("after", {})),
        )

        cross_split = result.get("split", {})
        split_gaps = cross_split.get("gaps", [])
        split_gap = split_gaps[0] if len(split_gaps) == 1 else {}
        check("cross window split count", cross_split.get("count") == 1, str(cross_split))
        check(
            "cross window split target width",
            abs(cross_split.get("dragSize", 0) - cross_split.get("dstWidth", 0) * 2) < 0.1,
            str(cross_split),
        )
        check("cross window split slot", len(split_gaps) == 1, str(split_gaps))
        check(
            "cross window split placeholder",
            cross_split.get("full") is True
            and cross_split.get("placeholderHidden") is False
            and abs(cross_split.get("placeholderWidth", 0) - cross_split.get("dragSize", 0)) < 0.75
            and abs(cross_split.get("placeholderLeft", 0) - split_gap.get("start", 0)) < 0.75,
            str(cross_split),
        )
        split_order = cross_split.get("after", {}).get("order", [])
        check(
            "cross window split order",
            "about:blank?spl0" in split_order
            and "about:blank?spl1" in split_order
            and "about:blank?dst7" in split_order
            and max(split_order.index("about:blank?spl0"), split_order.index("about:blank?spl1"))
            < split_order.index("about:blank?dst7"),
            str(split_order),
        )
    finally:
        b.stop()
        b.cleanup()


def test_cross_window_edge():
    b = Browser(
        {
            **COMMON_PREFS,
            "browser.tabs.dragDrop.createGroup.delayMS": 10000,
        },
        "crossedge",
    )
    try:
        m = b.start()
        m.js("await new Promise(r => setTimeout(r, 1800)); done('ok');", 30000)

        result = m.value(r"""
        const principal = Services.scriptSecurityManager.getSystemPrincipal();
        const mk = (gb, url) => gb.addTab(url, { triggeringPrincipal: principal, skipAnimation: true });
        for (let i = 0; i < 4; i++) mk(gBrowser, "about:blank?src" + i);
        await new Promise(r => setTimeout(r, 600));
        const srcTabs = Array.from(gBrowser.tabs)
          .filter(t => t.linkedBrowser?.currentURI?.spec?.includes("about:blank?src"));
        gBrowser.selectedTab = srcTabs[1];
        await new Promise(r => setTimeout(r, 250));

        const w2 = window.OpenBrowserWindow({ private: false });
        await new Promise(r => setTimeout(r, 1600));
        for (let i = 0; i < 10; i++) mk(w2.gBrowser, "about:blank?dst" + i);
        await new Promise(r => setTimeout(r, 800));
        w2.gBrowser.tabContainer.arrowScrollbox.scrollByPixels(-100000);
        w2.gBrowser.selectedTab = w2.gBrowser.tabs[0];
        await new Promise(r => setTimeout(r, 300));

        window.FiregilaTabDrag.testMode = true;
        w2.FiregilaTabDrag.testMode = true;
        const dstTabs = Array.from(w2.gBrowser.tabs)
          .filter(t => t.linkedBrowser?.currentURI?.spec?.includes("about:blank?dst"));
        const originalWidth = dstTabs[0].getBoundingClientRect().width;

        const dt = new DataTransfer();
        dt.mozSetDataAt("application/x-moz-tabbrowser-tab", srcTabs[1], 0);
        dt.effectAllowed = "move";
        const dr = srcTabs[1].getBoundingClientRect();
        srcTabs[1]._dragData = {
          movingTabs: [srcTabs[1]], movingTabsSet: new Set([srcTabs[1]]), fromTabList: false,
          offsetX: 0, offsetY: 0, screenX: dr.left + dr.width / 2, screenY: dr.top + dr.height / 2,
        };
        const ev = (win, type, x, y) => new win.DragEvent(type, {
          bubbles: true, cancelable: true, clientX: x, clientY: y,
          screenX: x, screenY: y, dataTransfer: dt,
        });
        gBrowser.tabContainer.dispatchEvent(
          ev(window, "dragstart", dr.left + dr.width / 2, dr.top + dr.height / 2)
        );
        await new Promise(r => setTimeout(r, 80));

        const target = dstTabs[4];
        const tr0 = target.getBoundingClientRect();
        w2.dispatchEvent(ev(w2, "dragenter", tr0.left + 2, tr0.top + tr0.height / 2));
        for (let i = 0; i < 5; i++) {
          const tr = target.getBoundingClientRect();
          w2.dispatchEvent(ev(w2, "dragover", tr.left + 2, tr.top + tr.height / 2));
          await new Promise(r => setTimeout(r, 30));
        }
        const last = dstTabs[dstTabs.length - 1];
        for (let i = 0; i < 6; i++) {
          const lr = last.getBoundingClientRect();
          w2.dispatchEvent(ev(w2, "dragover", lr.right - 2, lr.top + lr.height / 2));
          await new Promise(r => setTimeout(r, 30));
        }
        await new Promise(r => setTimeout(r, 350));

        const ph = w2.document.getElementById("firegila-tab-drop-placeholder");
        const placeholder = ph.getBoundingClientRect();
        const spacer = w2.document.querySelector(".firegila-tab-drag-spacer");
        const spacerRect = spacer ? spacer.getBoundingClientRect() : null;
        const box = w2.gBrowser.tabContainer.arrowScrollbox.getBoundingClientRect();
        const visibleTabs = Array.from(w2.gBrowser.tabs)
          .map(t => {
            const rect = t.getBoundingClientRect();
            return { left: rect.left, right: rect.right, width: rect.width };
          })
          .filter(t => t.width > 0);
        const overlaps = visibleTabs.filter(
          t => placeholder.left < t.right - 0.5 && placeholder.right > t.left + 0.5
        ).length;
        const ghost = w2.FiregilaTabDrag.dragImage;
        const ghostRect = ghost?.getBoundingClientRect();
        const dragGhost = ghostRect
          ? {
              visible: getComputedStyle(ghost).visibility !== "hidden",
              width: ghostRect.width,
              height: ghostRect.height,
              centerX: ghostRect.left + ghostRect.width / 2,
              centerY: ghostRect.top + ghostRect.height / 2,
            }
          : null;
        const over = {
          mode: w2.FiregilaTabDrag.mode,
          insert: w2.FiregilaTabDrag.insertIndex,
          count: visibleTabs.length,
          originalWidth,
          dragSize: w2.FiregilaTabDrag.dragSize,
          placeholderHidden: ph.hidden,
          placeholder: {
            left: placeholder.left,
            right: placeholder.right,
            width: placeholder.width,
          },
          spacer: spacerRect
            ? { left: spacerRect.left, right: spacerRect.right, width: spacerRect.width }
            : null,
          box: { left: box.left, right: box.right },
          overlaps,
          dragGhost,
          pointer: { x: w2.FiregilaTabDrag.pointerX, y: w2.FiregilaTabDrag.pointerY },
          shrunkWidth: visibleTabs[visibleTabs.length - 1].width,
        };

        const hoverTab = dstTabs[2];
        for (let i = 0; i < 4; i++) {
          const hr = hoverTab.getBoundingClientRect();
          w2.dispatchEvent(ev(w2, "dragover", hr.left + hr.width / 2, hr.top + hr.height / 2));
          await new Promise(r => setTimeout(r, 40));
        }
        await new Promise(r => setTimeout(r, 600));
        const stationary = {
          candidate: !!w2.document.querySelector("[fg-group-candidate]"),
          groupActive: w2.FiregilaTabDrag.groupActive,
          placeholderHidden: ph.hidden,
        };
        const hr = hoverTab.getBoundingClientRect();
        w2.dispatchEvent(ev(w2, "dragover", hr.left + hr.width / 2 + 8, hr.top + hr.height / 2));
        await new Promise(r => setTimeout(r, 150));
        const moved = {
          candidate: !!w2.document.querySelector("[fg-group-candidate]"),
          groupActive: w2.FiregilaTabDrag.groupActive,
          placeholderHidden: ph.hidden,
          spacer: !!w2.document.querySelector(".firegila-tab-drag-spacer"),
        };

        w2.dispatchEvent(ev(w2, "dragover", w2.innerWidth / 2, w2.innerHeight / 2));
        await new Promise(r => setTimeout(r, 200));
        const outside = {
          placeholderHidden: ph.hidden,
          spacer: !!w2.document.querySelector(".firegila-tab-drag-spacer"),
        };

        w2.dispatchEvent(ev(w2, "dragleave", w2.innerWidth / 2, w2.innerHeight / 2));
        await new Promise(r => setTimeout(r, 250));
        gBrowser.tabContainer.dispatchEvent(
          ev(window, "dragend", w2.innerWidth / 2, w2.innerHeight / 2)
        );
        await new Promise(r => setTimeout(r, 250));
        done(JSON.stringify({
          over,
          stationary,
          moved,
          outside,
          cleanup: {
            srcActive: window.FiregilaTabDrag.active,
            dstActive: w2.FiregilaTabDrag.active,
            spacer: !!w2.document.querySelector(".firegila-tab-drag-spacer"),
            placeholder: !!w2.document.getElementById("firegila-tab-drop-placeholder"),
          },
        }));
        """)
        over = result.get("over", {})
        stationary = result.get("stationary", {})
        moved = result.get("moved", {})
        outside = result.get("outside", {})
        cleanup = result.get("cleanup", {})
        check("cross edge target mode", over.get("mode") == "target", str(over))
        check("cross edge end slot", over.get("insert") == over.get("count"), str(over))
        check(
            "cross edge tabs shrink",
            over.get("shrunkWidth", 0) < over.get("originalWidth", 0) - 4,
            str(over),
        )
        check(
            "cross edge slot width",
            abs(over.get("dragSize", 0) - over.get("shrunkWidth", 0)) < 1,
            str(over),
        )
        check("cross edge placeholder visible", over.get("placeholderHidden") is False, str(over))
        check("cross edge spacer visible", (over.get("spacer") or {}).get("width", 0) > 0, str(over))
        check(
            "cross edge placeholder in strip",
            (over.get("placeholder") or {}).get("right", 0) <= over.get("box", {}).get("right", 0) + 1,
            str(over),
        )
        check(
            "cross edge spacer in strip",
            (over.get("spacer") or {}).get("right", 0) <= over.get("box", {}).get("right", 0) + 1,
            str(over),
        )
        check("cross edge no tab overlap", over.get("overlaps") == 0, str(over))
        ghost = over.get("dragGhost") or {}
        pointer = over.get("pointer") or {}
        check(
            "cross edge drag ghost visible",
            ghost.get("visible") is True
            and ghost.get("width", 0) > 0
            and abs(ghost.get("centerX", 0) - pointer.get("x", 0)) < 2
            and abs(ghost.get("centerY", 0) - pointer.get("y", 0)) < 2,
            str(over.get("dragGhost")) + " " + str(pointer),
        )
        check(
            "cross edge no group cue",
            stationary.get("candidate") is False
            and stationary.get("groupActive") is False
            and stationary.get("placeholderHidden") is False,
            str(stationary),
        )
        check(
            "cross edge placeholder stays",
            moved.get("candidate") is False
            and moved.get("groupActive") is False
            and moved.get("placeholderHidden") is False
            and moved.get("spacer") is True,
            str(moved),
        )
        check(
            "cross edge page hides placeholder",
            outside.get("placeholderHidden") is True and outside.get("spacer") is False,
            str(outside),
        )
        check(
            "cross edge cleanup",
            cleanup.get("srcActive") is False
            and cleanup.get("dstActive") is False
            and cleanup.get("spacer") is False
            and cleanup.get("placeholder") is False,
            str(cleanup),
        )
    finally:
        b.stop()
        b.cleanup()


def test_multi():
    b = Browser(COMMON_PREFS, "multi")
    try:
        m = b.start()
        m.js("await new Promise(r => setTimeout(r, 1800)); done('ok');", 30000)
        multi = m.value(r"""
        window.FiregilaTabDrag.testMode = true;
        const principal = Services.scriptSecurityManager.getSystemPrincipal();
        const mk = (u) => gBrowser.addTab(u, { triggeringPrincipal: principal, skipAnimation: true });
        const tabs = [];
        for (let i = 0; i < 5; i++) tabs.push(mk("about:blank?mu" + i));
        await new Promise(r => setTimeout(r, 500));
        const target = tabs[4];
        gBrowser.clearMultiSelectedTabs();
        gBrowser.selectedTab = tabs[1];
        gBrowser.addToMultiSelectedTabs(tabs[2]);
        const dr = tabs[1].getBoundingClientRect();
        const tr = target.getBoundingClientRect();
        const dt = new DataTransfer();
        dt.mozSetDataAt("application/x-moz-tabbrowser-tab", tabs[1], 0);
        dt.effectAllowed = "move";
        tabs[1]._dragData = {
          movingTabs: [tabs[1], tabs[2]],
          movingTabsSet: new Set([tabs[1], tabs[2]]),
          fromTabList: false,
          offsetX: 0, offsetY: 0,
          screenX: dr.left + dr.width / 2, screenY: dr.top + dr.height / 2,
        };
        const ev = (type, x, y) => new DragEvent(type, {
          bubbles: true, cancelable: true, clientX: x, clientY: y, screenX: x, screenY: y, dataTransfer: dt,
        });
        gBrowser.tabContainer.dispatchEvent(ev("dragstart", dr.left + dr.width / 2, dr.top + dr.height / 2));
        await new Promise(r => setTimeout(r, 80));
        const during = {
          active: window.FiregilaTabDrag.active,
          count: window.FiregilaTabDrag.movingCount,
          block: window.FiregilaTabDrag.block,
        };
        const go = { x: tr.left + 6, y: tr.top + tr.height / 2 };
        for (let i = 0; i < 5; i++) {
          window.dispatchEvent(ev("dragover", go.x, go.y));
          await new Promise(r => setTimeout(r, 30));
        }
        const placeholder = document.getElementById("firegila-tab-drop-placeholder");
        const placeholderHidden = !placeholder || placeholder.hidden;
        window.dispatchEvent(ev("drop", go.x, go.y));
        await new Promise(r => setTimeout(r, 200));
        gBrowser.tabContainer.dispatchEvent(ev("dragend", go.x, go.y));
        await new Promise(r => setTimeout(r, 120));
        const order = Array.from(gBrowser.tabs).map(t => t.linkedBrowser?.currentURI?.spec);
        const visible = [tabs[1].style.visibility, tabs[2].style.visibility];
        gBrowser.clearMultiSelectedTabs();
        done(JSON.stringify({
          during, order, active: window.FiregilaTabDrag.active,
          placeholderHidden,
          visible,
        }));
        """)
        check("multi drag active", multi.get("during", {}).get("active") is True, str(multi))
        check("multi drag count", multi.get("during", {}).get("count") == 2, str(multi))
        check("multi drag block", multi.get("during", {}).get("block") is True, str(multi))
        check("multi local placeholder hidden", multi.get("placeholderHidden") is True, str(multi))
        order = multi.get("order", [])
        check(
            "multi moved",
            "about:blank?mu1" in str(order)
            and "about:blank?mu2" in str(order)
            and "about:blank?mu4" in str(order)
            and order.index("about:blank?mu1") < order.index("about:blank?mu4")
            and order.index("about:blank?mu2") < order.index("about:blank?mu4"),
            str(order),
        )
        check("multi cleanup", multi.get("active") is False, str(multi))
        check("multi visible", multi.get("visible") == ["", ""], str(multi))
    finally:
        b.stop()
        b.cleanup()


def test_vertical():
    prefs = dict(COMMON_PREFS)
    prefs["sidebar.verticalTabs"] = True
    prefs["firegila.sidebar.autoCollapseTabs"] = True
    b = Browser(prefs, "vertical")
    try:
        m = b.start()
        m.js("await new Promise(r => setTimeout(r, 1800)); done('ok');", 30000)
        result = m.value(r"""
        const principal = Services.scriptSecurityManager.getSystemPrincipal();
        const mk = (u) => gBrowser.addTab(u, { triggeringPrincipal: principal, skipAnimation: true });
        const tabs = [];
        for (let i = 0; i < 4; i++) tabs.push(mk("about:blank?v" + i));
        await new Promise(r => setTimeout(r, 500));
        window.FiregilaTabDrag.testMode = true;
        const dragged = tabs[1], target = tabs[3];
        const dr = dragged.getBoundingClientRect(), tr = target.getBoundingClientRect();
        const dt = new DataTransfer();
        dt.mozSetDataAt("application/x-moz-tabbrowser-tab", dragged, 0);
        dt.effectAllowed = "move";
        dragged._dragData = {
          movingTabs: [dragged], movingTabsSet: new Set([dragged]), fromTabList: false,
          offsetX: 0, offsetY: 0, screenX: dr.left + dr.width / 2, screenY: dr.top + dr.height / 2,
        };
        const ev = (type, x, y) => new DragEvent(type, {
          bubbles: true, cancelable: true, clientX: x, clientY: y, screenX: x, screenY: y, dataTransfer: dt,
        });
        gBrowser.tabContainer.dispatchEvent(ev("dragstart", dr.left + dr.width / 2, dr.top + dr.height / 2));
        await new Promise(r => setTimeout(r, 80));
        const go = { x: tr.left + tr.width / 2, y: tr.top + 6 };
        for (let i = 0; i < 5; i++) {
          window.dispatchEvent(ev("dragover", go.x, go.y));
          await new Promise(r => setTimeout(r, 30));
        }
        const columnHit = document.elementFromPoint(100, 300);
        const pageHit = document.elementFromPoint(400, 300);
        const button = document.getElementById("vertical-tabs-newtab-button");
        const buttonHidden = getComputedStyle(button).visibility === "hidden";
        window.dispatchEvent(ev("drop", go.x, go.y));
        await new Promise(r => setTimeout(r, 250));
        const order = Array.from(gBrowser.tabs).map(t => t.linkedBrowser?.currentURI?.spec);
        done(JSON.stringify({
          order,
          buttonHidden,
          columnInside: !!columnHit?.closest?.("#vertical-tabs-container"),
          pageShield: pageHit?.id,
        }));
        """)
        order = result.get("order", [])
        check(
            "vertical drag order",
            "about:blank?v1" in str(order)
            and order.index("about:blank?v1") < order.index("about:blank?v3"),
            str(order),
        )
        check("vertical new tab button hidden", result.get("buttonHidden") is True)
        check("tabs column receives pointer", result.get("columnInside") is True)
        check("page shield excludes tabs column", result.get("pageShield") == "firegila-tab-drag-shield")
    finally:
        b.stop()
        b.cleanup()


def test_chrome_layout():
    b = Browser({**COMMON_PREFS, "firegila.workspaces.enabled": True}, "layout")
    try:
        m = b.start()
        layout = m.value(r"""
        await new Promise(r => setTimeout(r, 2600));
        const root = document.documentElement;
        root.setAttribute("customtitlebar", "true");
        root.setAttribute("sizemode", "normal");
        await new Promise(r => setTimeout(r, 100));
        const spacers = [];
        for (const el of document.querySelectorAll(".titlebar-spacer")) {
          const rect = el.getBoundingClientRect();
          spacers.push({
            parent: el.parentElement.id,
            type: el.getAttribute("type"),
            display: getComputedStyle(el).display,
            width: rect.width,
          });
        }
        const buttons = [];
        for (const el of document.querySelectorAll("#nav-bar toolbarbutton")) {
          const rect = el.getBoundingClientRect();
          if (!rect.width || !rect.height) continue;
          const icon = el.querySelector(".toolbarbutton-icon, .toolbarbutton-badge-stack, image");
          const iconRect = icon ? icon.getBoundingClientRect() : null;
          buttons.push({
            id: el.id,
            width: rect.width,
            leftGap: iconRect ? iconRect.left - rect.left : null,
            rightGap: iconRect ? rect.right - iconRect.right : null,
          });
        }
        const principal = Services.scriptSecurityManager.getSystemPrincipal();
        const motionTab = gBrowser.addTab("about:blank?motion", {
          triggeringPrincipal: principal,
          skipAnimation: false,
        });
        const motionStart = motionTab.getBoundingClientRect().width;
        const motionTransition = getComputedStyle(motionTab).transition;
        await new Promise(r => setTimeout(r, 180));
        const motionEnd = motionTab.getBoundingClientRect().width;
        gBrowser.removeTab(motionTab);
        await new Promise(r => setTimeout(r, 250));
        const tabMotion = {
          start: motionStart,
          end: motionEnd,
          transition: motionTransition,
          closed: !motionTab.isConnected,
        };

        const menu = document.getElementById("firegila-workspace-menu");
        const menuIcons = {};
        try {
          menu.openPopupAtScreen(20, 20, true);
          await new Promise(r => setTimeout(r, 150));
          for (const id of ["firegila-workspace-new", "firegila-workspace-rename", "firegila-workspace-delete"]) {
            const item = document.getElementById(id);
            const icon = item.querySelector(".menu-icon");
            const rect = item.getBoundingClientRect();
            const iconRect = icon.getBoundingClientRect();
            menuIcons[id] = {
              iconic: item.classList.contains("menuitem-iconic"),
              content: getComputedStyle(icon).content,
              display: getComputedStyle(icon).display,
              iconWidth: iconRect.width,
              iconHeight: iconRect.height,
              width: rect.width,
              height: rect.height,
            };
          }
        } finally {
          menu.hidePopup();
        }
        const stripMargins = {};
        for (const id of ["firegila-workspaces", "tabs-newtab-button"]) {
          const el = document.getElementById(id);
          if (!el) continue;
          const style = getComputedStyle(el);
          stripMargins[id] = {
            top: style.marginTop,
            right: style.marginRight,
            bottom: style.marginBottom,
            left: style.marginLeft,
          };
        }
        const ublock = WebExtensionPolicy.getByID("uBlock0@raymondhill.net");
        done(JSON.stringify({
          spacers,
          buttons,
          menuIcons,
          stripMargins,
          tabMotion,
          ublock: ublock
            ? { active: ublock.active, version: ublock.extension?.version }
            : null,
          devtoolsHost: Services.prefs.getStringPref("devtools.toolbox.host"),
          devtoolsPrevious: Services.prefs.getStringPref("devtools.toolbox.previousHost"),
          profileSchema: Services.prefs.getIntPref("firegila.schema", -1),
          devtoolsGuard: Services.prefs.prefHasUserValue("firegila.migration.devtoolsHost.v1"),
        }));
        """)
        left_spacers = [
            item
            for item in layout.get("spacers", [])
            if item.get("type") == "pre-tabs"
            and item.get("parent") in ("TabsToolbar", "nav-bar")
        ]
        check(
            "titlebar left spacer hidden",
            left_spacers
            and all(item.get("display") == "none" for item in left_spacers),
            str(left_spacers),
        )
        buttons = layout.get("buttons", [])
        check("toolbar buttons found", len(buttons) >= 5, str(buttons))
        check(
            "toolbar button sides equal",
            buttons
            and all(
                abs(item.get("leftGap", 0) - item.get("rightGap", 0)) < 0.75
                for item in buttons
            ),
            str(buttons),
        )
        check(
            "toolbar button widths equal",
            buttons and len({round(item.get("width", 0), 2) for item in buttons}) == 1,
            str(buttons),
        )
        menu_icons = layout.get("menuIcons", {})
        check(
            "workspace action icons",
            len(menu_icons) == 3
            and all(
                item.get("iconic") is True
                and "url(" in item.get("content", "")
                and item.get("display") != "none"
                and item.get("iconWidth", 0) > 0
                and item.get("iconHeight", 0) > 0
                and item.get("width", 0) > 0
                for item in menu_icons.values()
            ),
            str(menu_icons),
        )
        strip_margins = layout.get("stripMargins", {})
        tab_motion = layout.get("tabMotion", {})
        check(
            "tab open animation",
            tab_motion.get("end", 0) > tab_motion.get("start", 0) + 50
            and "min-width" in tab_motion.get("transition", ""),
            str(tab_motion),
        )
        check("tab close cleanup", tab_motion.get("closed") is True, str(tab_motion))
        check(
            "tab strip button margins",
            len(strip_margins) == 2
            and all(
                set(item.values()) == {"4px"} for item in strip_margins.values()
            ),
            str(strip_margins),
        )
        ublock = layout.get("ublock") or {}
        check(
            "uBlock extension loaded",
            ublock.get("active") is True and ublock.get("version") == UBLOCK_VERSION,
            str(ublock),
        )
        check("devtools dock right", layout.get("devtoolsHost") == "right", str(layout))
        check(
            "devtools previous host",
            layout.get("devtoolsPrevious") == "bottom",
            str(layout),
        )
        check("profile schema", layout.get("profileSchema") == 2, str(layout))
        check("devtools guard removed", layout.get("devtoolsGuard") is False, str(layout))
    finally:
        b.stop()
        b.cleanup()


def test_profile_migration():
    b = Browser(COMMON_PREFS, "migration")
    try:
        m = b.start()
        m.js("await new Promise(r => setTimeout(r, 3000)); done('ok');", 30000)
        first = m.value(r"""
        done(JSON.stringify({
          schema: Services.prefs.getIntPref("firegila.schema", -1),
        }));
        """)
        check("profile schema current", first.get("schema") == 2, str(first))

        m.value(r"""
        Services.prefs.setIntPref("firegila.schema", 0);
        Services.prefs.setBoolPref("firegila.migration.strictTracking", true);
        Services.prefs.setBoolPref("firegila.migration.strictTracking.v2", true);
        Services.prefs.setBoolPref("firegila.migration.globalPrivacyControl", true);
        Services.prefs.setBoolPref("firegila.migration.devtoolsHost.v1", true);
        Services.prefs.setBoolPref("firegila.migration.defaultBookmarks", true);
        Services.prefs.setBoolPref("firegila.migration.webappDesktopEntries.v1", true);
        Services.prefs.setIntPref("firegila.sidebar.width", 640);
        done('ok');
        """)
        b.stop()

        m = b.start()
        m.js("await new Promise(r => setTimeout(r, 3200)); done('ok');", 30000)
        result = m.value(r"""
        const guards = [
          "firegila.migration.strictTracking",
          "firegila.migration.strictTracking.v2",
          "firegila.migration.globalPrivacyControl",
          "firegila.migration.devtoolsHost.v1",
          "firegila.migration.defaultBookmarks",
          "firegila.migration.webappDesktopEntries.v1",
        ];
        done(JSON.stringify({
          schema: Services.prefs.getIntPref("firegila.schema", -1),
          guards: guards.map(name => Services.prefs.prefHasUserValue(name)),
          width: Services.prefs.getIntPref("firegila.sidebar.width", 0),
        }));
        """)
        check("profile schema after upgrade", result.get("schema") == 2, str(result))
        check(
            "legacy migration guards removed",
            result.get("guards") and not any(result.get("guards")),
            str(result),
        )
        check("user setting preserved", result.get("width") == 640, str(result))
        b.stop()

        m = b.start()
        m.js("await new Promise(r => setTimeout(r, 2600)); done('ok');", 30000)
        third = m.value(r"""
        done(JSON.stringify({
          schema: Services.prefs.getIntPref("firegila.schema", -1),
          width: Services.prefs.getIntPref("firegila.sidebar.width", 0),
        }));
        """)
        check("profile schema stable", third.get("schema") == 2, str(third))
        check("user setting stable", third.get("width") == 640, str(third))
    finally:
        b.stop()
        b.cleanup()


def test_session():
    prefs = {
        "browser.startup.page": 3,
        "browser.sessionstore.resume_from_crash": True,
        "browser.sessionstore.restore_hidden_tabs": True,
        "firegila.workspaces.enabled": True,
        "firegila.workspaces.list": '[{"id":"ws-a","name":"Default"},{"id":"ws-b","name":"Work"}]',
    }
    b = Browser(prefs, "session")
    try:
        m = b.start()
        m.js("await new Promise(r => setTimeout(r, 1600)); done('ok');", 30000)
        create = m.value(r"""
        const { SessionStore } = ChromeUtils.importESModule("resource:///modules/sessionstore/SessionStore.sys.mjs");
        const principal = Services.scriptSecurityManager.getSystemPrincipal();
        const mk = (u) => gBrowser.addTab(u, { triggeringPrincipal: principal, skipAnimation: true });
        const setWs = (t, id) => { t.setAttribute("firegila.workspace", id); SessionStore.setCustomTabValue(t, "firegila.workspace", id); };
        const a1 = mk("about:blank?sa1"), a2 = mk("about:blank?sa2");
        const ga = gBrowser.addTabGroup([a1, a2], { label: "Alpha", color: "blue" });
        setWs(a1, "ws-a"); setWs(a2, "ws-a");
        const b1 = mk("about:blank?sb1"), b2 = mk("about:blank?sb2");
        const gb = gBrowser.addTabGroup([b1, b2], { label: "Beta", color: "orange" });
        setWs(b1, "ws-b"); setWs(b2, "ws-b");
        gb.collapsed = true;
        gBrowser.selectedTab = b1;
        await new Promise(r => setTimeout(r, 1200));
        done(JSON.stringify({
          groups: Array.from(document.querySelectorAll("tab-group")).map(g => ({ label: g.label, collapsed: g.collapsed, display: g.style.display })),
          selected: gBrowser.selectedTab?.linkedBrowser?.currentURI?.spec,
        }));
        """)
        check("session create", create.get("selected") == "about:blank?sb1", str(create))
        b.stop()
        b.m = None
        b.proc = None

        for round in (1, 2):
            b.start()
            restored = b.m.value(r"""
            await new Promise(r => setTimeout(r, 4500));
            const tabs = Array.from(gBrowser.tabs).map(t => ({
              url: t.linkedBrowser?.currentURI?.spec,
              ws: t.getAttribute("firegila.workspace"),
              hidden: t.hidden,
              selected: t.selected,
              group: t.group?.label || "",
            }));
            const groups = Array.from(document.querySelectorAll("tab-group")).map(g => ({
              label: g.label,
              collapsed: g.collapsed,
              display: g.style.display,
            }));
            done(JSON.stringify({
              tabs,
              groups,
              selected: gBrowser.selectedTab?.linkedBrowser?.currentURI?.spec,
              workspace: document.querySelector("#firegila-workspaces")?.getAttribute("label"),
            }));
            """)
            groups = {g["label"]: g for g in restored.get("groups", [])}
            check(f"session {round} Beta visible", groups.get("Beta", {}).get("display") == "")
            check(f"session {round} Alpha hidden", groups.get("Alpha", {}).get("display") == "none")
            check(f"session {round} Beta collapsed", groups.get("Beta", {}).get("collapsed") is True)
            check(f"session {round} selected", restored.get("selected") == "about:blank?sb1")
            check(f"session {round} workspace", restored.get("workspace") == "Work")
            check(f"session {round} active tab visible", any(
                t for t in restored.get("tabs", [])
                if t.get("url") == "about:blank?sb1" and not t.get("hidden")
            ))
            b.stop()
            b.m = None
            b.proc = None
    finally:
        b.stop()
        b.cleanup()


def test_app():
    prefs = {
        "browser.startup.page": 1,
        "sidebar.verticalTabs": True,
        "browser.taskbarTabs.enabled": True,
    }
    handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    b = Browser(prefs, "app")
    try:
        m = b.start()
        m.js("await new Promise(r => setTimeout(r, 1800)); done('ok');", 30000)
        result = m.value(r"""
        const principal = Services.scriptSecurityManager.getSystemPrincipal();
        const { TaskbarTabs } = ChromeUtils.importESModule("resource:///modules/taskbartabs/TaskbarTabs.sys.mjs");
        const tab = gBrowser.addTab("http://localhost:%d/", { triggeringPrincipal: principal });
        gBrowser.selectedTab = tab;
        await new Promise(r => setTimeout(r, 500));
        await TaskbarTabs.moveTabIntoTaskbarTab(tab);
        await new Promise(r => setTimeout(r, 2000));
        let win = null;
        for (const w of Services.wm.getEnumerator("navigator:browser")) {
          if (w.document.documentElement.hasAttribute("taskbartab")) { win = w; break; }
        }
        if (!win) { done(JSON.stringify({ error: "no app window" })); }
        else {
          const doc = win.document;
          const read = id => {
            const e = doc.getElementById(id);
            if (!e) return null;
            const c = win.getComputedStyle(e);
            const r = e.getBoundingClientRect();
            return { display: c.display, w: r.width, h: r.height };
          };
          done(JSON.stringify({
            tabs: read("tabbrowser-tabs"),
            vertical: read("vertical-tabs-container"),
            sidebar: read("sidebar-container"),
            toolbox: read("navigator-toolbox"),
          }));
        }
        """ % port)
        check("app window exists", result.get("error") != "no app window", str(result))
        check("app window no tab strip", result.get("tabs", {}).get("display") == "none")
        check("app window no tabs column", result.get("vertical", {}).get("display") == "none")
        check("app window no sidebar", result.get("sidebar", {}).get("display") == "none")
        check("app window one top bar", result.get("toolbox", {}).get("h") == 40, str(result.get("toolbox")))
        apps = b.home / ".local" / "share" / "applications"
        entries = list(apps.glob("firegila.webapp-*.desktop")) if apps.exists() else []
        text = entries[0].read_text() if entries else ""
        check("app desktop entry present", bool(entries))
        check("app desktop entry hidden", "NoDisplay=true" in text)
        check("app desktop entry category", "Categories=Network;WebBrowser;" in text)
    finally:
        b.stop()
        httpd.shutdown()
        b.cleanup()


def main():
    if not BIN.exists():
        print(f"missing {BIN}")
        print("run scripts/customize.sh first")
        return 1
    check_static_css()
    check_bundled_extension()
    test_launcher_cache()
    test_horizontal()
    test_horizontal_geometry()
    test_pinned()
    test_cross_window()
    test_cross_window_edge()
    test_multi()
    test_vertical()
    test_chrome_layout()
    test_profile_migration()
    test_session()
    test_app()
    print()
    if FAILURES:
        print(f"FAIL {len(FAILURES)} check(s)")
        for name in FAILURES:
            print(f"  {name}")
        return 1
    print("PASS all UI checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
