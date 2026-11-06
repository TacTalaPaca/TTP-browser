#!/usr/bin/env python3
# Neutral theme for both omni jars. Palette:
# dark 171717 1f1f1f 2b2b2b, light fafafa f2f2f2 e6e6e6 d9d9d9.
# Accent follows the system accent color. No hardcoded brand colors.
# Scope: every theme. System follows the OS scheme with the same styles.
# Only user installed themes and forced colors are left alone.
# Usage: patch-omni-theme.py ROOT BUILD
import base64
import io
import os
import shutil
from pathlib import Path

from PIL import Image

from omnijar import extract, replace, require_paths

ROOT, BUILD = require_paths()

# Our defaults, written by customize.sh. Appended at the browser patch call.
FIREGILA_PREFS = (BUILD / "defaults" / "pref" / "firegila.js").read_text()

GRAY = [
    ("--color-gray-0", "#fafafa"), ("--color-gray-10", "#f2f2f2"),
    ("--color-gray-15", "#e6e6e6"), ("--color-gray-20", "#d9d9d9"),
    ("--color-gray-25", "#cccccc"), ("--color-gray-30", "#b8b8b8"),
    ("--color-gray-35", "#a6a6a6"), ("--color-gray-40", "#949494"),
    ("--color-gray-45", "#828282"), ("--color-gray-50", "#6e6e6e"),
    ("--color-gray-55", "#5a5a5a"), ("--color-gray-60", "#4a4a4a"),
    ("--color-gray-65", "#434343"), ("--color-gray-70", "#3d3d3d"),
    ("--color-gray-75", "#333333"), ("--color-gray-80", "#2e2e2e"),
    ("--color-gray-85", "#262626"), ("--color-gray-90", "#1f1f1f"),
    ("--color-gray-100", "#1f1f1f"),
    # Violet primitives neutralized to the ramp. Components that use them
    # follow automatically, without per file edits.
    ("--color-violet-0", "#fafafa"), ("--color-violet-10", "#f2f2f2"),
    ("--color-violet-20", "#e6e6e6"), ("--color-violet-30", "#d9d9d9"),
    ("--color-violet-40", "#cccccc"), ("--color-violet-50", "#b8b8b8"),
    ("--color-violet-60", "#8f8f8f"), ("--color-violet-70", "#6e6e6e"),
    ("--color-violet-80", "#4a4a4a"), ("--color-violet-90", "#333333"),
    ("--color-violet-100", "#262626"), ("--color-violet-110", "#1f1f1f"),
    ("--color-violet-desaturated-0", "#f2f2f2"),
    ("--color-violet-desaturated-10", "#e6e6e6"),
    ("--color-violet-desaturated-20", "#d9d9d9"),
    ("--color-violet-desaturated-30", "#c4c4c4"),
    ("--color-violet-desaturated-40", "#a6a6a6"),
    ("--color-violet-desaturated-50", "#8f8f8f"),
    ("--color-violet-desaturated-60", "#6e6e6e"),
    ("--color-violet-desaturated-70", "#4a4a4a"),
    ("--color-violet-desaturated-80", "#333333"),
    ("--color-violet-desaturated-90", "#1f1f1f"),
    # Firegila palette variables. Change colors here and in
    # NEWTAB_PALETTE_CSS below.
    ("--fg-bg", "light-dark(#fafafa, #1f1f1f)"),
    ("--fg-bg-2", "light-dark(#f5f5f5, #1f1f1f)"),
    ("--fg-bg-3", "light-dark(#ececec, #262626)"),
    ("--fg-bg-4", "light-dark(#e0e0e0, #2e2e2e)"),
    ("--fg-tabbar", "light-dark(#f2f2f2, #1a1a1a)"),
    ("--fg-navbar", "light-dark(#f7f7f7, #262626)"),
    ("--fg-hover", "light-dark(#e0e0e0, #3d3d3d)"),
    ("--fg-active", "light-dark(#d4d4d4, #4a4a4a)"),
    ("--fg-border", "light-dark(#d0d0d0, #3d3d3d)"),
    ("--fg-divider", "light-dark(#e0e0e0, #2f2f2f)"),
    ("--fg-text", "light-dark(#171717, #fafafa)"),
    ("--fg-text-dim", "light-dark(#4a4a4a, #b8b8b8)"),
]

# Old Firefox palette literals swept to the neutral ramp and accent.
# Applied to every stylesheet so pages that hardcode them follow the theme.
OLD_GRAYS = [
    ("#2b2a33", "#1f1f1f"), ("#2B2A33", "#1f1f1f"),
    ("#42414d", "#2e2e2e"), ("#42414D", "#2e2e2e"),
    ("rgb(66, 65, 77)", "#2e2e2e"), ("rgb(66,65,77)", "#2e2e2e"),
    ("rgb(66, 65, 77,", "#2e2e2e"), ("rgb(66,65,77,", "#2e2e2e"),
    ("rgb(82, 82, 94)", "#4a4a4a"), ("rgb(82,82,94)", "#4a4a4a"),
    ("#52525e", "#4a4a4a"), ("#52525E", "#4a4a4a"),
    ("#5d5c66", "#4a4a4a"), ("#5D5C66", "#4a4a4a"),
    ("#15141a", "#171717"), ("#15141A", "#171717"),
    ("#23222b", "#262626"), ("#23222B", "#262626"),
    ("#1c1b22", "#1f1f1f"), ("#1C1B22", "#1f1f1f"),
    ("#fbfbfe", "#fafafa"), ("#FBFBFE", "#fafafa"),
    ("#f9f9fb", "#f2f2f2"), ("#F9F9FB", "#f2f2f2"),
    ("#deddde", "#d9d9d9"), ("#DEDDDE", "#d9d9d9"),
    ("#cfcfd8", "#cccccc"), ("#CFCFD8", "#cccccc"),
    ("#5b5b66", "#6e6e6e"), ("#5B5B66", "#6e6e6e"),
    ("#67676c", "#6e6e6e"), ("#67676C", "#6e6e6e"),
    ("#b1b1b3", "#b8b8b8"), ("#B1B1B3", "#b8b8b8"),
    ("rgb(43, 42, 51)", "#262626"), ("rgb(43,42,51)", "#262626"),
    ("rgb(58 57 68 / 0.2)", "rgb(0 0 0 / 0.2)"),
    ("ThreeDShadow", "light-dark(#d0d0d0, #1a1a1a)"),
]

OLD_ACCENTS = [
    ("#764edd", "AccentColor"), ("#764EDD", "AccentColor"),
    ("#9059ff", "AccentColor"), ("#9059FF", "AccentColor"),
    ("#0a84ff", "AccentColor"), ("#0A84FF", "AccentColor"),
    ("#0670cc", "AccentColor"), ("#0996f8", "AccentColor"),
    ("#005bab", "AccentColor"),
    ("#b89cff", "#cccccc"), ("#B89CFF", "#cccccc"),
]

# Token files keep violet primitives neutral instead of accent.
TOKEN_VIOLET = [
    ("#f5ecff", "#fafafa"), ("#eaddff", "#f2f2f2"), ("#d4c1ff", "#e6e6e6"),
    ("#b89cff", "#d9d9d9"), ("#9871ff", "#cccccc"), ("#764edd", "#b8b8b8"),
    ("#5939a8", "#8f8f8f"), ("#3e2976", "#6e6e6e"), ("#271c48", "#4a4a4a"),
    ("#161423", "#333333"),
    ("#f2f0f8", "#f2f2f2"), ("#e7e1f8", "#e6e6e6"), ("#d2c8ec", "#d9d9d9"),
    ("#b6aad9", "#c4c4c4"), ("#9687c0", "#a6a6a6"), ("#75669f", "#8f8f8f"),
    ("#584a7d", "#6e6e6e"), ("#3e315f", "#4a4a4a"),
    ("#f5ecff", "#fafafa"),
]

def is_token_file(rel):
    return rel.endswith("tokens-shared.css") or rel.endswith("tokens-platform.css")

# Unlayered block appended to tokens-shared.css. Unlayered beats the token
# layers. Forced colors are excluded so high contrast keeps working.
GLOBAL_OVERRIDE_CSS = (
    "\n/* Firegila neutral theme. Applied to every theme. */\n"
    "@media not (forced-colors) {\n"
    "  :root,\n"
    "  :host(.anonymous-content-host) {\n"
    + "".join(f"    {k}: {v};\n" for k, v in GRAY)
    + "    --background-color-information: light-dark(#e6e6e6, #333333);\n"
    + "    --text-color: light-dark(#171717, #fafafa);\n"
    + "    --text-color-disabled: light-dark(#9f9f9f, #777777);\n"
    + "    --text-color-deemphasized: light-dark(#5b5b5b, #b8b8b8);\n"
    + "    --text-color-accent-primary-selected: AccentColorText;\n"
    + "    --color-accent-primary: AccentColor;\n"
    + "    --color-accent-primary-hover: color-mix(in srgb, black 12%, AccentColor);\n"
    + "    --color-accent-primary-active: color-mix(in srgb, black 25%, AccentColor);\n"
    + "    --color-accent-primary-selected: color-mix(in srgb, black 25%, AccentColor);\n"
    + "    --color-accent-attention: AccentColor;\n"
    + "    --button-text-color-primary: AccentColorText;\n"
    + "    --link-color: AccentColor;\n"
    + "    --link-color-hover: color-mix(in srgb, black 12%, AccentColor);\n"
    + "    --link-color-active: color-mix(in srgb, black 25%, AccentColor);\n"
    + "    --button-text-color: light-dark(#171717, #fafafa);\n"
    + "    --input-text-background-color: light-dark(#ffffff, #333333);\n"
    + "    --input-text-color: light-dark(#171717, #fafafa);\n"
    + "    --toolbar-field-text-color: var(--text-color);\n"
    + "    --toolbarbutton-icon-fill: currentColor;\n"
    + "    --panel-background-color: light-dark(#ffffff, #2e2e2e);\n"
    + "    --panel-border-color: light-dark(#d9d9d9, #3d3d3d);\n"
    + "    --panel-text-color: light-dark(#171717, #fafafa);\n"
    # Motion. One set of timings and one curve for the whole browser. Anything
    # that animates reads these, so nothing drifts apart. The sidebar
    # animation reads them back out in JS, see SB_BOOTSTRAP_JS.
    + "    --fg-motion-fast: 120ms;\n"
    + "    --fg-motion-base: 180ms;\n"
    + "    --fg-motion-slow: 260ms;\n"
    + "    --fg-ease: ease;\n"
    + "    --toolbar-field-text-color-focus: light-dark(#171717, #fafafa);\n"
    # The system theme keeps these out of the override because the native
    # platform sets them. Pin them so both theme choices match.
    + "    --toolbar-text-color: light-dark(#171717, #fafafa);\n"
    + "    --button-background-color: var(--fg-bg-3);\n"
    + "    --button-background-color-ghost: transparent;\n"
    + "    --button-background-color-primary: AccentColor;\n"
    + "    --toolbarbutton-icon-fill-attention: AccentColor;\n"
    + "    --toolbarbutton-icon-fill-attention-text: AccentColorText;\n"
    + "    --background-color-canvas: var(--fg-bg);\n"
    + "    --background-color-box-info: color-mix(in srgb, currentColor 6%, transparent);\n"
    + "    --background-color-dimmed: var(--fg-bg-4);\n"
    + "    --background-color-dimmed-further: var(--fg-active);\n"
    + "    --background-color-list-item-hover: var(--fg-hover);\n"
    + "    --sidebar-background-color: var(--fg-bg);\n"
    + "    --sidebar-border-color: var(--fg-border);\n"
    + "    --sidebar-text-color: var(--fg-text);\n"
    + "    --table-header-text-color: var(--fg-text);\n"
    + "    --table-row-background-color-alternate: var(--fg-bg-2);\n"
    + "    --toolbox-background-color: var(--fg-tabbar);\n"
    + "    --toolbox-background-color-inactive: var(--fg-tabbar);\n"
    + "    --toolbox-text-color: light-dark(#171717, #fafafa);\n"
    + "    --toolbox-text-color-inactive: light-dark(#777777, #9f9f9f);\n"
    + "    --chrome-content-separator-color: var(--fg-border);\n"
    + "    --tabs-navbar-separator-color: var(--fg-border);\n"
    + "    --toolbarseparator-color: var(--fg-border);\n"
    + "    --theme-toolbar-separator: var(--fg-border);\n"
    + "    --toolbar-background-color: var(--fg-navbar);\n"
    + "    --toolbar-field-background-color-focus: var(--fg-bg-3);\n"
    + "    --button-background-color-hover: var(--fg-hover);\n"
    + "    --button-background-color-active: var(--fg-active);\n"
    + "    --button-background-color-ghost-hover: var(--fg-hover);\n"
    + "    --button-background-color-ghost-active: var(--fg-active);\n"
    + "    --button-background-color-selected: var(--fg-active);\n"
    + "    --toolbarbutton-background-color-hover: var(--fg-hover);\n"
    + "    --toolbarbutton-background-color-active: var(--fg-active);\n"
    + "    --button-background-color-toolbar-hover: var(--fg-hover);\n"
    + "    --button-background-color-toolbar-active: var(--fg-active);\n"
    # Urlbar result rows. Stock leaves selected on the same tone as the
    # plain row, so picking a result reads as no change at all. Map the
    # three states onto the same ramp the buttons use.
    + "    --urlbarview-background-color-hover: var(--fg-hover);\n"
    + "    --urlbarview-background-color-selected: var(--fg-active);\n"
    + "    --urlbarview-text-color-selected: var(--fg-text);\n"
    + "    --input-text-border: 1px solid light-dark(#c4c4c4, #4a4a4a);\n"
    + "    --input-text-border-color-disabled: transparent;\n"
    + "    --input-text-background-color-disabled: light-dark(#f2f2f2, #2e2e2e);\n"
    + "    --input-text-color-disabled: light-dark(#9f9f9f, #777777);\n"
    + "    --input-text-opacity-disabled: 1;\n"
    + "    --select-border: 1px solid light-dark(#c4c4c4, #4a4a4a);\n"
    + "    --select-border-color-hover: AccentColor;\n"
    + "    --select-background-color-hover: var(--select-background-color);\n"
    + "    --select-text-color-hover: var(--select-text-color);\n"
    + "    --select-border-color-disabled: transparent;\n"
    + "    --select-background-color-disabled: light-dark(#f2f2f2, #2e2e2e);\n"
    + "    --select-text-color-disabled: light-dark(#9f9f9f, #777777);\n"
    + "    --select-opacity-disabled: 1;\n"
    + "    --card-border-color: var(--fg-border);\n"
    + "    --border-color: var(--fg-border);\n"
    + "    --border-color-interactive: light-dark(#b8b8b8, #4a4a4a);\n"
    + "    --border-color-deemphasized: light-dark(#d9d9d9, #3a3a3a);\n"
    + "    --box-shadow-level-1: none;\n"
    + "    --box-shadow-level-2: none;\n"
    + "    --box-shadow-level-3: none;\n"
    + "    --box-shadow-level-4: none;\n"
    + "    --card-box-shadow: none;\n"
    + "    --popup-box-shadow: none;\n"
    + "    --tab-box-shadow: none;\n"
    + "    --card-box-shadow-hover: none;\n"
    + "    --panel-box-shadow: none;\n"
    + "    --panel-list-box-shadow: none;\n"
    + "    --content-area-shadow: none;\n"
    + "    --logins-dialog-shadow: none;\n"
    + "    --pip-box-shadow-default: none;\n"
    + "    --pip-box-shadow-hover: none;\n"
    + "    --smartwindow-shadow: none;\n"
    + "    --in-content-page-background: var(--fg-bg);\n"
    + "    --in-content-page-color: var(--fg-text);\n"
    + "    --in-content-box-background: var(--fg-bg-3);\n"
    + "    --in-content-box-background-odd: var(--fg-bg-2);\n"
    + "    --in-content-box-border-color: var(--fg-border);\n"
    + "    --in-content-border-color: var(--fg-border);\n"
    + "    --in-content-text-color: var(--fg-text);\n"
    + "    --in-content-deemphasized-text: var(--fg-text-dim);\n"
    + "    --focus-outline-width: 1px;\n"
    + "    --focus-outline-offset: 1px;\n"
    + "    --fg-radius: 8px;\n"
    + "    --fg-tabs-width: 220px;\n"
    + "    --border-radius-xsmall: 8px;\n"
    + "    --border-radius-small: 8px;\n"
    + "    --border-radius-medium: 8px;\n"
    + "    --border-radius-large: 8px;\n"
    + "    --border-radius-xlarge: 8px;\n"
    + "    --border-radius-xxlarge: 8px;\n"
    + "    --panel-border-radius: 8px;\n"
    + "    --panel-menuitem-border-radius: calc(8px - 4px);\n"
    + "    --menuitem-border-radius: calc(8px - 4px);\n"
    + "    --panel-list-border-radius: 8px;\n"
    + "    --button-border-radius: 8px;\n"
    + "    --toolbarbutton-border-radius: 8px;\n"
    + "    --urlbar-border-radius: 8px;\n"
    + "    --urlbarview-border-radius: 8px;\n"
    + "    --urlbar-inner-border-radius: calc(8px - 4px);\n"
    + "    --card-border-radius: 8px;\n"
    + "    --tab-border-radius: 8px;\n"
    + "    accent-color: AccentColor;\n"
    + "  }\n"
    + "  :root .toolbarbutton-1 {\n"
    + "    align-items: center !important;\n"
    + "  }\n"
    + "  :root .toolbarbutton-1 > .toolbarbutton-icon,\n"
    + "  :root .toolbarbutton-1 > .toolbarbutton-badge-stack {\n"
    + "    margin-block: auto !important;\n"
    + "  }\n"
    + "  :root #urlbar .searchmode-switcher {\n"
    + "    --button-border-radius: calc(var(--urlbar-border-radius) - 2px) !important;\n"
    + "    border-radius: calc(var(--urlbar-border-radius) - 2px) !important;\n"
    + "  }\n"
    + "  :root #urlbar :is([urlbar-slot], .urlbar-page-action) {\n"
    + "    border-radius: calc(var(--urlbar-border-radius) - 2px) !important;\n"
    + "  }\n"
    + "  @media (prefers-color-scheme: dark) {\n"
    + "    :root, :root #navigator-toolbox, :root toolbar, :root panel, :root menupopup {\n"
    + "      color-scheme: dark !important;\n"
    + "    }\n"
    + "  }\n"
    + "  @media (prefers-color-scheme: light) {\n"
    + "    :root, :root #navigator-toolbox, :root toolbar, :root panel, :root menupopup {\n"
    + "      color-scheme: light !important;\n"
    + "    }\n"
    + "  }\n"
    + "}\n"
)

# Single intended border on text fields, search fields and dropdowns.
# Focus swaps the border color. No extra ring.
WIDGET_CSS = """
/* Firegila single border inputs. */
#input:focus-visible {
  outline: none;
  border-color: AccentColor;
}
.select-wrapper:has(:focus-visible) {
  outline: none;
  border-color: AccentColor;
}
"""

# Opaque newtab dialog. Accent Add button, neutral Cancel button.
NEWTAB_DIALOG_CSS = """
/* Firegila newtab dialog. */
.edit-topsites-wrapper .modal {
  background-color: light-dark(#ffffff, #2e2e2e);
  color: light-dark(#171717, #fafafa);
}
.actions button.cancel {
  background-color: light-dark(#e6e6e6, #3d3d3d);
  border-color: light-dark(#c4c4c4, #4a4a4a);
  color: light-dark(#171717, #fafafa);
}
.actions button.cancel:hover {
  background-color: light-dark(#d9d9d9, #4a4a4a);
  box-shadow: none;
}
.actions button.done {
  background-color: var(--color-accent-primary);
  border-color: var(--color-accent-primary);
  color: AccentColorText;
}
.actions button.done:hover {
  background-color: var(--color-accent-primary-hover);
  border-color: var(--color-accent-primary-hover);
  box-shadow: none;
}
.actions button.done:active {
  background-color: var(--color-accent-primary-active);
  border-color: var(--color-accent-primary-active);
}
.topsite-form input[type="text"],
.topsite-form input[type="url"] {
  outline: none;
}
.topsite-form input[type="text"]:focus-visible,
.topsite-form input[type="url"]:focus-visible {
  outline: none;
  border-color: AccentColor;
}

/* Firegila newtab dialog transitions.
 *
 * Opening: the dialog is a real <dialog> opened with showModal() and React
 * mounts it in the same pass, so @starting-style covers the entry. The
 * allow-discrete parts keep it in the top layer while it fades, otherwise it
 * blinks out on the first frame.
 *
 * Closing: React unmounts the node the instant the state clears, so the bundle
 * is patched to hold that state back for one transition length and to put
 * .fg-closing on the dialog first. That is what this second half animates.
 */
@media not (prefers-reduced-motion: reduce) {
  .modalOverlayOuter {
    opacity: 0;
    transition:
      opacity var(--fg-motion-base) var(--fg-ease),
      overlay var(--fg-motion-base) allow-discrete,
      display var(--fg-motion-base) allow-discrete;
  }
  .modalOverlayOuter[open] {
    opacity: 1;
  }
  .modalOverlayOuter::backdrop {
    transition: background-color var(--fg-motion-base) var(--fg-ease);
  }
  .edit-topsites-wrapper .modal,
  .edit-search-shortcuts .modal {
    opacity: 0;
    scale: 0.98;
    transition:
      opacity var(--fg-motion-base) var(--fg-ease),
      scale var(--fg-motion-base) var(--fg-ease);
  }
  .modalOverlayOuter[open] .modal {
    opacity: 1;
    scale: 1;
  }
  .modalOverlayOuter.fg-closing {
    opacity: 0;
    pointer-events: none;
  }
  .modalOverlayOuter.fg-closing::backdrop {
    background-color: transparent;
  }
  .modalOverlayOuter.fg-closing .modal {
    opacity: 0;
    scale: 0.98;
  }
}
@starting-style {
  .modalOverlayOuter[open] {
    opacity: 0;
  }
  .modalOverlayOuter[open] .modal {
    opacity: 0;
    scale: 0.98;
  }
}
"""

TOKENS_SHARED = "chrome/toolkit/skin/classic/global/design-system/tokens-shared.css"
# Last stylesheet in the global import chain, so appends here win the cascade.
GLOBAL_SHARED = "chrome/toolkit/skin/classic/global/global-shared.css"
MAIN_EDITS = {
    # Always draw chrome ourselves instead of handing it to the native
    # platform theme. Without this the system theme skips the CSS that
    # colours the toolbox, urlbar and fields, so it renders differently
    # from the built in light and dark themes.
    "modules/LightweightThemeConsumer.sys.mjs": [
        ("    this._doc.forceNonNativeTheme = !!builtinThemeConfig?.nonNative;",
         "    this._doc.forceNonNativeTheme = true;"),
    ],
    # Sidebar strip shows on a fresh profile. Stock hides it whenever
    # vertical tabs are off, which is our case.
    "moz-src/browser/components/sidebar/SidebarState.sys.mjs": [
        ("const DEFAULT_LAUNCHER_VISIBLE = false;",
         "const DEFAULT_LAUNCHER_VISIBLE = true;"),
        # The launcher stays collapsed in hide-sidebar mode: the tabs live in
        # their own column now, so there is nothing to expand for.
        ("""      case "hide-sidebar":
        if (lazy.verticalTabsEnabled) {
          forceExpandValue = visible;
        }
        this.launcherVisible = visible;
        break;""",
         """      case "hide-sidebar":
        forceExpandValue = false;
        this.launcherVisible = visible;
        break;"""),
        # The tab strip is still marked expanded while vertical tabs are on,
        # or it renders icons only. The launcher above never expands, so this
        # is the only place the attribute comes from outside hover mode.
        ("""    tabContainer.toggleAttribute("expanded", expanded);""",
         """    tabContainer.toggleAttribute(
      "expanded",
      expanded ||
        (lazy.verticalTabsEnabled && this.revampVisibility === "hide-sidebar")
    );"""),
        # Same for startup: the launcher starts collapsed, the tabs do not
        # need it expanded for it.
        ("""    } else {
      if (lazy.verticalTabsEnabled) {
        this.#props.launcherExpanded = true;
      }
      this.launcherVisible = showLauncher;
    }""",
         """    } else {
      this.launcherVisible = showLauncher;
    }"""),
    ],
    # Stock flips the visibility pref to "always-show" as soon as vertical tabs
    # are on, and does it on every startup through this one function. That is
    # what turns the toolbar button into an expand/collapse toggle and lets the
    # strip widen. Firegila keeps the hide/show layout in both orientations, so
    # pin the pref here and the rest of stock follows.
    "moz-src/browser/components/sidebar/SidebarManager.sys.mjs": [
        ("""  handleVerticalTabsPrefChange(isEnabled, resetVisibility = true) {
    if (!isEnabled) {
      const currentVisibility = Services.prefs.getStringPref(
        VISIBILITY_SETTING_PREF,
        "always-show"
      );
      if (currentVisibility == "expand-on-hover") {
        this.#savedVisibility = currentVisibility;
      }
      Services.prefs.setStringPref(VISIBILITY_SETTING_PREF, "hide-sidebar");
    } else if (resetVisibility) {
      if (this.#savedVisibility) {
        Services.prefs.setStringPref(
          VISIBILITY_SETTING_PREF,
          this.#savedVisibility
        );
        this.#savedVisibility = null;
      } else {
        Services.prefs.setStringPref(VISIBILITY_SETTING_PREF, "always-show");
      }
    }
  }""",
         """  handleVerticalTabsPrefChange(isEnabled, resetVisibility = true) {
    Services.prefs.setStringPref(VISIBILITY_SETTING_PREF, "hide-sidebar");
  }"""),
    ],
    # Platform token values are covered by the appended block above.
    # Only files without token coverage get direct edits here.
    "chrome/toolkit/skin/classic/global/pictureinpicture/player.css": [
        ("#0060df", "AccentColor"),
        ("#00ddff", "AccentColor"),
    ],
    "chrome/toolkit/skin/classic/global/media/videocontrols.css": [
        ("#00ddff", "AccentColor"),
    ],
    "chrome/toolkit/skin/classic/global/media/pipToggle.css": [
        ("#0060df", "AccentColor"),
    ],
    "chrome/pdfjs/content/web/viewer.css": [
        ("#0060df", "AccentColor"), ("#0250bb", "AccentColor"),
    ],
    "localization/en-US/toolkit/branding/brandings.ftl": [
        ("-firefox-home-brand-name = Firefox Home",
         "-firefox-home-brand-name = Firegila Home"),
    ],
    "chrome/en-US/locale/en-US/global/appstrings.properties": [
        ("Firefox", "Firegila"),
    ],
    "localization/en-US/toolkit/about/aboutAddons.ftl": [
        ("a selection Firefox <a",
         "a selection Firegila <a"),
        (".title = Firefox only recommends extensions",
         ".title = Firegila only recommends extensions"),
    ],
    # Default toolbar layout. Nav bar order and no Firefox View in the tab bar.
    "moz-src/browser/components/customizableui/CustomizableUI.sys.mjs": [
        ('''    // Add firefox-view if not present
    if (currentVersion < 18) {
      let tabstripPlacements =
        gSavedState.placements[CustomizableUI.AREA_TABSTRIP];
      if (
        tabstripPlacements &&
        !tabstripPlacements.includes("firefox-view-button")
      ) {
        tabstripPlacements.unshift("firefox-view-button");
      }
    }''',
         '''    // Firegila does not auto add the Firefox View button.'''),
        ('''      "back-button",
      "forward-button",
      "stop-reload-button",
      Services.policies.isAllowed("removeHomeButtonByDefault")
        ? null
        : "home-button",''',
         '''      "back-button",
      "stop-reload-button",
      "forward-button",
      "home-button",'''),
        ('''        defaultPlacements: [
          "firefox-view-button",
          "tabbrowser-tabs",
          "new-tab-button",
          "alltabs-button",
        ],''',
         '''        defaultPlacements: [
          "tabbrowser-tabs",
          "new-tab-button",
        ],'''),
        ('''        verticalTabsDefaultPlacements: [
          "firefox-view-button",
          "alltabs-button",
        ],''',
         '''        verticalTabsDefaultPlacements: [
          "firefox-view-button",
        ],'''),
        ('''      lazy.ippEnabled ? "ipprotection-button" : null,
      "fxa-toolbar-menu-button",
      lazy.resetPBMToolbarButtonEnabled ? "reset-pbm-toolbar-button" : null,''',
         '''      lazy.ippEnabled ? "ipprotection-button" : null,
      lazy.resetPBMToolbarButtonEnabled ? "reset-pbm-toolbar-button" : null,'''),
        ('''    // Add the FxA toolbar menu as the right most button item
    if (currentVersion < 16) {
      let navbarPlacements = gSavedState.placements[CustomizableUI.AREA_NAVBAR];
      // Place the menu item as the first item to the left of the hamburger menu
      if (navbarPlacements) {
        navbarPlacements.push("fxa-toolbar-menu-button");
      }
    }''',
         '''    // Firegila does not auto add the account button.'''),
        ('''      let index = navbarPlacements.indexOf("fxa-toolbar-menu-button");
      navbarPlacements.splice(index, 0, "ipprotection-button");''',
         '''      navbarPlacements.push("ipprotection-button");'''),
        ('''    Services.prefs.clearUserPref(kPrefSidebarPositionStartEnabled);
    gDefaultTheme.enable();
    gNewElementCount = 0;''',
         '''    Services.prefs.clearUserPref(kPrefSidebarPositionStartEnabled);
    // Firegila keeps the current theme on reset.
    gNewElementCount = 0;'''),
        ('''    this.registerArea(
      CustomizableUI.AREA_BOOKMARKS,
      {
        type: CustomizableUI.TYPE_TOOLBAR,
        defaultPlacements: ["personal-bookmarks"],
        defaultCollapsed: "newtab",
      },
      true
    );''',
         '''    this.registerArea(
      CustomizableUI.AREA_BOOKMARKS,
      {
        type: CustomizableUI.TYPE_TOOLBAR,
        defaultPlacements: ["personal-bookmarks"],
        defaultCollapsed: "never",
      },
      true
    );'''),
    ],
}

# New tab explicit hex values that are not palette tokens.
NEWTAB_TOKEN_PAIRS = [
    ("--button-text-color-primary: light-dark(var(--color-white), var(--color-gray-70));",
     "--button-text-color-primary: AccentColorText;"),
    ("#FCFBFF", "#fafafa"), ("#EFEDF2", "#f2f2f2"), ("#E3E2E7", "#e6e6e6"),
    ("#D6D5DA", "#d9d9d9"), ("#C7C6CB", "#cccccc"), ("#B7B6BA", "#b8b8b8"),
    ("#A6A4A9", "#a6a6a6"), ("#949297", "#949494"), ("#817F84", "#828282"),
    ("#67666A", "#6e6e6e"), ("#515054", "#5a5a5a"), ("#3F3E42", "#4a4a4a"),
    ("#312F33", "#434343"), ("#252428", "#3d3d3d"), ("#1D1B1F", "#333333"),
    ("#171519", "#2e2e2e"), ("#131215", "#262626"), ("#121114", "#1f1f1f"),
    ("rgba(66, 65, 77, 85%)", "#2c2c2c"),
    ("rgba(66, 65, 77, 0.85)", "#2c2c2c"),
    ("--newtab-background-color-secondary: #42414d;",
     "--newtab-background-color-secondary: #2e2e2e;"),
    ("#F0F0F4", "#f2f2f2"), ("#E0E0E6", "#e6e6e6"), ("#52525E", "#454545"),
    ("#CFCFD8", "#d9d9d9"), ("#5B5B66", "#555555"),
    ("--newtab-overlay-color: color-mix(in srgb, var(--newtab-background-color) 85%, transparent);",
     "--newtab-overlay-color: var(--newtab-background-color);"),
]

# Nova file only. The classic copy inherits box from the toolkit.
NEWTAB_NOVA_ONLY = [
    ("--background-color-box: light-dark(var(--color-white), var(--color-gray-70));",
     "--background-color-box: light-dark(#ffffff, #2e2e2e);"),
]

# Newtab palette. Accent from the system, violet neutralized. One block
# covers toggles, selects, buttons and cards.
NEWTAB_PALETTE_CSS = """
/* Firegila neutral palette for newtab. Keep in sync with the Firegila palette
 * list near the top of this script. */
:root, :root.nova-tokens, .nova-tokens {
  --color-accent-primary: AccentColor;
  --color-accent-primary-hover: color-mix(in srgb, black 12%, AccentColor);
  --color-accent-primary-active: color-mix(in srgb, black 25%, AccentColor);
  --color-accent-primary-selected: color-mix(in srgb, black 25%, AccentColor);
  --color-accent-attention: AccentColor;
  --color-violet-0: #fafafa;
  --color-violet-10: #f2f2f2;
  --color-violet-20: #e6e6e6;
  --color-violet-30: #d9d9d9;
  --color-violet-40: #cccccc;
  --color-violet-50: #b8b8b8;
  --color-violet-60: #8f8f8f;
  --color-violet-70: #6e6e6e;
  --color-violet-80: #4a4a4a;
  --color-violet-90: #333333;
  --color-violet-100: #262626;
  --color-violet-110: #1f1f1f;
  --color-violet-desaturated-0: #f2f2f2;
  --color-violet-desaturated-10: #e6e6e6;
  --color-violet-desaturated-20: #d9d9d9;
  --color-violet-desaturated-30: #c4c4c4;
  --color-violet-desaturated-40: #a6a6a6;
  --color-violet-desaturated-50: #8f8f8f;
  --color-violet-desaturated-60: #6e6e6e;
  --color-violet-desaturated-70: #4a4a4a;
  --color-violet-desaturated-80: #333333;
  --color-violet-desaturated-90: #1f1f1f;
  --fg-bg: light-dark(#fafafa, #1f1f1f);
  --fg-bg-2: light-dark(#f5f5f5, #1f1f1f);
  --fg-bg-3: light-dark(#ececec, #262626);
  --fg-bg-4: light-dark(#e0e0e0, #2e2e2e);
  --fg-tabbar: light-dark(#f2f2f2, #1a1a1a);
  --fg-navbar: light-dark(#f7f7f7, #262626);
  --fg-hover: light-dark(#e0e0e0, #3d3d3d);
  --fg-active: light-dark(#d4d4d4, #4a4a4a);
  --fg-border: light-dark(#d0d0d0, #3d3d3d);
  --fg-divider: light-dark(#e0e0e0, #2f2f2f);
  --fg-text: light-dark(#171717, #fafafa);
  --fg-text-dim: light-dark(#4a4a4a, #b8b8b8);
  --button-background-color-hover: var(--fg-hover);
  --button-background-color-active: var(--fg-active);
  --newtab-button-static-hover-background: var(--fg-hover);
  --newtab-button-static-active-background: var(--fg-active);
  --fg-search-min: 300px;
  --fg-search-max: 720px;
  --fg-search-gap: 24px;
  --fg-radius: 8px;
  --border-radius-small: 8px;
  --border-radius-medium: 8px;
  --border-radius-large: 8px;
  --panel-border-radius: 8px;
  --panel-menuitem-border-radius: calc(8px - 4px);
  --button-border-radius: 8px;
  --card-border-radius: 8px;
  --box-shadow-level-1: none;
  --box-shadow-level-2: none;
  --box-shadow-level-3: none;
  --box-shadow-level-4: none;
  --card-box-shadow: none;
  --card-box-shadow-hover: none;
  --popup-box-shadow: none;
  --panel-box-shadow: none;
  --text-color: var(--fg-text);
  --icon-color: var(--fg-text);
  --newtab-background-card: var(--fg-bg-3);
}
"""


# Solid accent for newtab action buttons. Appended to both newtab files.
NEWTAB_BUTTONS_CSS = """
/* Firegila newtab action buttons. Darker neutral fill in dark mode. */
.personalize-button,
.lightWallpaper .personalize-button,
.darkWallpaper .personalize-button {
  background-color: var(--fg-bg-3) !important;
  color: var(--fg-text) !important;
  fill: currentColor;
  border: 0;
}
.personalize-button:hover {
  background-color: var(--fg-hover) !important;
  color: var(--fg-text) !important;
}
.personalize-button:active,
.personalize-button:focus-visible,
.personalize-button:focus-within {
  background-color: var(--fg-active) !important;
  color: var(--fg-text) !important;
}
.personalize-button:focus-visible {
  outline: 1px solid AccentColor !important;
  outline-offset: 1px;
}
.personalize-button > label,
.personalize-button > div {
  color: var(--fg-text) !important;
  fill: currentColor;
}
.top-site-outer .context-menu-button:hover {
  background-color: var(--color-accent-primary) !important;
  fill: AccentColorText;
}
.top-site-outer .context-menu-button:hover:active {
  background-color: var(--color-accent-primary-active) !important;
}
"""

BROWSER_EDITS = {
    # Vertical tabs get their own column after the strip, so the order is
    # strip, tabs, panel. The box moves out of the sidebar-main tabstrip slot
    # into a plain sibling. Stock finds it by ID everywhere it matters, and
    # the empty slot renders nothing. Auto-hide floats the column over the
    # edge, so the DOM order does not move it there.
    # Neither the pinned tabs nor the tools section is resizable. Both size to
    # their content. Without resize attributes a splitter is only a divider
    # and drags do nothing.
    "chrome/browser/content/browser/browser.xhtml": [
        ('<splitter orient="vertical" id="vertical-pinned-tabs-splitter" resizebefore="sibling" resizeafter="none" hidden="true"/>',
         '<splitter orient="vertical" id="vertical-pinned-tabs-splitter" hidden="true"/>'),
        ("""  <box context="sidebar-context-menu" id="sidebar-container" class="chrome-block" hidden="true">
    <html:sidebar-main flex="1">
      <box id="vertical-tabs" slot="tabstrip" customizable="true" contextmenu="toolbar-context-menu"></box>
    </html:sidebar-main>
  </box>
  <splitter id="sidebar-launcher-splitter" class="chromeclass-extrachrome sidebar-splitter" resizebefore="sibling" resizeafter="none" hidden="true"/>
""",
         """  <box context="sidebar-context-menu" id="sidebar-container" class="chrome-block" hidden="true">
    <html:sidebar-main flex="1">
    </html:sidebar-main>
  </box>
  <splitter id="sidebar-launcher-splitter" class="chromeclass-extrachrome sidebar-splitter" resizebefore="sibling" resizeafter="none" hidden="true"/>
  <box id="firegila-tabs-sensor"/>
  <box id="vertical-tabs-container">
    <box id="vertical-tabs" customizable="true" contextmenu="toolbar-context-menu"></box>
  </box>
"""),
        # Website panels get a header and their own content browser next to the
        # stock sidebar browser. The stock browser keeps chrome panel pages.
        ("""    <stack class="sidebar-browser-stack">
      <browser id="sidebar" autoscroll="false" disablehistory="true" disablefullscreen="true" tooltip="aHTMLTooltip"/>
    </stack>
""",
         """    <hbox id="firegila-webpanel-header" align="center" hidden="true">
      <label id="firegila-webpanel-title" crop="end" flex="1"/>
      <toolbarbutton id="firegila-webpanel-back" class="tabbable" data-l10n-id="firegila-webpanel-back"/>
      <toolbarbutton id="firegila-webpanel-forward" class="tabbable" data-l10n-id="firegila-webpanel-forward"/>
      <toolbarbutton id="firegila-webpanel-reload" class="tabbable" data-l10n-id="firegila-webpanel-reload"/>
      <toolbarbutton id="firegila-webpanel-close" class="tabbable" data-l10n-id="sidebar-panel-header-close-button"/>
    </hbox>
    <stack class="sidebar-browser-stack">
      <browser id="sidebar" autoscroll="false" disablehistory="true" disablefullscreen="true" tooltip="aHTMLTooltip"/>
    </stack>
"""),
        # Add popup and the panel button menu.
        ("""  <script src="chrome://browser/content/main-popupset.js" />
""",
         """  <script src="chrome://browser/content/main-popupset.js" />

  <panel id="firegila-webpanel-add-popup" type="arrow" orient="vertical" hidden="true">
    <vbox class="fg-webpanel-form">
      <label data-l10n-id="firegila-webpanel-add-heading"/>
      <html:input id="firegila-webpanel-url" type="text" data-l10n-id="firegila-webpanel-url-field"/>
      <html:input id="firegila-webpanel-name" type="text" data-l10n-id="firegila-webpanel-name-field"/>
      <label id="firegila-webpanel-error" class="fg-webpanel-error" hidden="true"/>
      <hbox class="fg-webpanel-buttons">
        <button id="firegila-webpanel-cancel" data-l10n-id="firegila-webpanel-cancel"/>
        <button id="firegila-webpanel-ok" class="primary" data-l10n-id="firegila-webpanel-add"/>
      </hbox>
    </vbox>
  </panel>

  <menupopup id="firegila-webpanel-menu">
    <menuitem id="firegila-webpanel-menu-reload" data-l10n-id="firegila-webpanel-menu-reload"/>
    <menuitem id="firegila-webpanel-menu-open-tab" data-l10n-id="firegila-webpanel-menu-open-tab"/>
    <menuseparator/>
    <menuitem id="firegila-webpanel-menu-remove" data-l10n-id="firegila-webpanel-menu-remove"/>
  </menupopup>

  <panel id="firegila-workspace-name-popup" type="arrow" orient="vertical" hidden="true">
    <vbox class="fg-webpanel-form">
      <label id="firegila-workspace-name-heading"/>
      <html:input id="firegila-workspace-name-input" type="text" maxlength="24"/>
      <label id="firegila-workspace-name-error" class="fg-webpanel-error" hidden="true"/>
      <hbox class="fg-webpanel-buttons">
        <button id="firegila-workspace-name-cancel" data-l10n-id="firegila-webpanel-cancel"/>
        <button id="firegila-workspace-name-ok" class="primary" data-l10n-id="firegila-workspace-save"/>
      </hbox>
    </vbox>
  </panel>

  <panel id="firegila-workspace-confirm-popup" type="arrow" orient="vertical" hidden="true">
    <vbox class="fg-webpanel-form">
      <label id="firegila-workspace-confirm-text"/>
      <hbox class="fg-webpanel-buttons">
        <button id="firegila-workspace-confirm-cancel" data-l10n-id="firegila-webpanel-cancel"/>
        <button id="firegila-workspace-confirm-ok" class="primary" data-l10n-id="firegila-workspace-delete-button"/>
      </hbox>
    </vbox>
  </panel>
"""),
        # Workspace switcher at the left of the tabs. The module moves it to
        # the top of the vertical tabs column when vertical tabs are on.
        ("""    <hbox flex="1" align="end" class="toolbar-items">
      <toolbartabstop/>
""",
         """    <hbox flex="1" align="end" class="toolbar-items">
      <toolbartabstop/>
      <toolbarbutton id="firegila-workspaces" type="menu" class="firegila-workspace-switcher" hidden="true">
        <box class="firegila-workspace-arrow-box">
          <box class="firegila-workspace-audio"/>
          <image class="firegila-workspace-arrow"/>
        </box>
        <menupopup id="firegila-workspace-menu">
          <menuseparator id="firegila-workspace-separator"/>
          <menuitem id="firegila-workspace-new" data-l10n-id="firegila-workspace-new"/>
          <menuitem id="firegila-workspace-rename" data-l10n-id="firegila-workspace-rename"/>
          <menuitem id="firegila-workspace-delete" data-l10n-id="firegila-workspace-delete"/>
        </menupopup>
      </toolbarbutton>
"""),
    ],
    # The sidebar menu belongs to the strip in vertical tabs mode too. Stock
    # only updates the items when vertical tabs are off and then cancels the
    # default menu, so the strip had no right click menu at all.
    "chrome/browser/content/browser/sidebar/sidebar-main.mjs": [
        # Saved websites get their own strip block: divider, buttons, add.
        ("""            ${when(!this.isToolsOverflowing(), () =>
              repeat(
                this.getToolsAndExtensions().values(),
                action => action.view,
                action => this.entrypointTemplate(action)
              )
            )}
""",
         """            ${when(!this.isToolsOverflowing(), () =>
              repeat(
                this.getToolsAndExtensions().values(),
                action => action.view,
                action => this.entrypointTemplate(action)
              )
            )}
            ${this.webPanelActions()}
"""),
        # The customize button moves out of the tools group so it can sit at
        # the bottom of the strip, below the saved websites.
        ("""            ${this.webPanelActions()}
            ${when(window.SidebarController.sidebarVerticalTabsEnabled, () =>
              repeat(
                this.bottomActions,
                action => action.view,
                action => this.entrypointTemplate(action)
              )
            )}
            ${when(this.isToolsOverflowing(), () =>
""",
         """            ${this.webPanelActions()}
            ${when(this.isToolsOverflowing(), () =>
"""),
        ("""          ${when(
            !window.SidebarController.sidebarVerticalTabsEnabled,
            () =>
              html` <div class="bottom-actions actions-list">
                ${repeat(
                  this.bottomActions,
                  action => action.view,
                  action => this.entrypointTemplate(action)
                )}
              </div>`
          )}
""",
         """          <div class="bottom-actions actions-list">
            ${repeat(
              this.bottomActions,
              action => action.view,
              action => this.entrypointTemplate(action)
            )}
          </div>
"""),
        ("""  render() {
    /* Add 1 to tools and extensions count for "Customize sidebar" option */
""",
         """  webPanelActions() {
    const panels = window.FiregilaWebPanels;
    if (!panels?.enabled) {
      return nothing;
    }
    return html`
      <div class="fg-webpanel-divider" role="separator"></div>
      <div
        class="fg-webpanel-list actions-list"
        @contextmenu=${event => panels.onContextMenu(event)}
      >
        ${repeat(
          panels.actions,
          action => action.view,
          action => this.entrypointTemplate(action)
        )}
        <moz-button
          class="fg-webpanel-add"
          type="icon ghost"
          .iconSrc=${"chrome://global/skin/icons/plus.svg"}
          title=${panels.addTooltip}
          @click=${event => panels.openAdd(event.currentTarget)}
        ></moz-button>
      </div>
    `;
  }

  render() {
    /* Add 1 to tools and extensions count for "Customize sidebar" option */
"""),
        ("""    if (
      this.contextMenuTarget?.localName === "sidebar-main" &&
      !window.SidebarController.sidebarVerticalTabsEnabled
    ) {
      this.updateSidebarContextMenuItems();
      return;
    }""",
         """    if (this.contextMenuTarget?.localName === "sidebar-main") {
      this.updateSidebarContextMenuItems();
      return;
    }"""),
        ("""    toolsSplitter.setAttribute("id", "sidebar-tools-and-extensions-splitter");
    toolsSplitter.setAttribute("resizebefore", "none");
    toolsSplitter.setAttribute("resizeafter", "sibling");
""",
         """    toolsSplitter.setAttribute("id", "sidebar-tools-and-extensions-splitter");
"""),
    ],
    # The visibility setting is pinned to hide-sidebar, so this checkbox would
    # only be able to break the layout. Drop the control. The expand on hover
    # control becomes the auto-hide tabs switch, which only touches the tabs
    # column and never writes sidebar.visibility.
    "chrome/browser/content/browser/sidebar/sidebar-customize.mjs": [
        ("""                <moz-checkbox
                  slot="nested"
                  type="checkbox"
                  id="hide-sidebar"
                  name="hideSidebar"
                  data-l10n-id="sidebar-hide-tabs-and-sidebar"
                  @change=${this.#handleVisibilityChange}
                  ?checked=${this.visibility == "hide-sidebar"}
                  ?disabled=${this.getWindow().SidebarController._state
                    .revampVisibility === "expand-on-hover"}
                ></moz-checkbox>
""", ""),
        ("""                ${when(
                  this.expandOnHoverEnabled,
                  () => html`
                    <moz-checkbox
                      slot="nested"
                      type="checkbox"
                      id="expand-on-hover"
                      name="expand-on-hover"
                      data-l10n-id="expand-sidebar-on-hover"
                      @change=${this.#toggleExpandOnHover}
                      ?checked=${this.getWindow().SidebarController._state
                        .revampVisibility === "expand-on-hover"}
                      ?disabled=${this.visibility == "hide-sidebar"}
                    ></moz-checkbox>
                  `
                )}
""",
         """                <moz-checkbox
                  slot="nested"
                  type="checkbox"
                  id="auto-hide-tabs"
                  name="autoHideTabs"
                  data-l10n-id="firegila-auto-hide-tabs"
                  @change=${this.#toggleAutoHideTabs}
                  ?checked=${Services.prefs.getBoolPref(
                    "firegila.sidebar.autoHideTabs",
                    false
                  )}
                ></moz-checkbox>
                <moz-checkbox
                  slot="nested"
                  type="checkbox"
                  id="tabs-opposite"
                  name="tabsOpposite"
                  data-l10n-id="firegila-tabs-opposite"
                  @change=${this.#toggleTabsOpposite}
                  ?checked=${Services.prefs.getBoolPref(
                    "firegila.sidebar.tabsOpposite",
                    false
                  )}
                ></moz-checkbox>
"""),
        # Website panels sit next to the position switch in the same group.
        ("""              ?checked=${!this.isPositionStart}
          ></moz-checkbox>
          </moz-fieldset>
""",
         """              ?checked=${!this.isPositionStart}
          ></moz-checkbox>
            <moz-checkbox
              type="checkbox"
              id="web-panels-enabled"
              name="webPanelsEnabled"
              data-l10n-id="firegila-webpanels-toggle"
              @change=${this.#toggleWebPanels}
              ?checked=${Services.prefs.getBoolPref(
                "firegila.sidebar.webPanelsEnabled",
                false
              )}
            ></moz-checkbox>
          </moz-fieldset>
"""),
        ("""  #toggleExpandOnHover(e) {
    e.stopPropagation();
    if (e.target.checked) {
      Services.prefs.setStringPref("sidebar.visibility", "expand-on-hover");
      Glean.sidebarCustomize.expandOnHoverEnabled.record({
        checked: true,
      });
    } else {
      Services.prefs.setStringPref("sidebar.visibility", "always-show");
    }
  }
""",
         """  #toggleAutoHideTabs(e) {
    e.stopPropagation();
    Services.prefs.setBoolPref(
      "firegila.sidebar.autoHideTabs",
      e.target.checked
    );
  }

  #toggleTabsOpposite(e) {
    e.stopPropagation();
    Services.prefs.setBoolPref(
      "firegila.sidebar.tabsOpposite",
      e.target.checked
    );
  }

  #toggleWebPanels(e) {
    e.stopPropagation();
    Services.prefs.setBoolPref(
      "firegila.sidebar.webPanelsEnabled",
      e.target.checked
    );
  }
"""),
    ],
    # The expand on hover control becomes the two tabs switches. Website
    # panel strings live here too, the add popup and strip read them.
    "localization/en-US/browser/sidebar.ftl": [
        ("expand-sidebar-on-hover =\n  .label = Expand sidebar on hover",
         "firegila-auto-hide-tabs =\n  .label = Auto-hide tabs\n\n"
         "firegila-tabs-opposite =\n  .label = Tabs on the opposite side\n\n"
         "firegila-webpanels-toggle =\n  .label = Add websites to sidebar\n\n"
         "firegila-webpanel-add-heading = Add website to sidebar\n\n"
         "firegila-webpanel-url-field =\n  .placeholder = https://example.com\n\n"
         "firegila-webpanel-name-field =\n  .placeholder = Name (optional)\n\n"
         "firegila-webpanel-add =\n  .label = Add\n\n"
         "firegila-webpanel-cancel =\n  .label = Cancel\n\n"
         "firegila-webpanel-menu-reload =\n  .label = Reload\n\n"
         "firegila-webpanel-menu-open-tab =\n  .label = Open in a new tab\n\n"
         "firegila-webpanel-menu-remove =\n  .label = Remove website\n\n"
         "firegila-webpanel-error-invalid = Enter a website address that starts with http or https.\n\n"
         "firegila-webpanel-error-limit = You can add up to 8 websites.\n\n"
         "firegila-webpanel-add-tooltip = Add website\n\n"
         "firegila-webpanel-back =\n  .tooltiptext = Back\n\n"
         "firegila-webpanel-forward =\n  .tooltiptext = Forward\n\n"
         "firegila-webpanel-reload =\n  .tooltiptext = Reload\n\n"
         "firegila-workspace-new =\n  .label = New\n\n"
         "firegila-workspace-rename =\n  .label = Rename\n\n"
         "firegila-workspace-delete =\n  .label = Delete\n\n"
         "firegila-workspace-delete-button =\n  .label = Delete\n\n"
         "firegila-workspace-save =\n  .label = Save\n\n"
         "firegila-workspace-new-heading = New workspace\n\n"
         "firegila-workspace-rename-heading = Rename workspace\n\n"
         "firegila-workspace-name-empty = Enter a name.\n\n"
         "firegila-workspace-name-taken = That name is already used.\n\n"
         "firegila-workspace-limit = You can add up to 12 workspaces.\n\n"
         "firegila-workspace-delete-text = Delete \"{ $name }\" and close its { $count } tabs?"),
    ],
    # Bookmarks use the same card surface as history, open tabs and the
    # customizer. The stock page drops the list straight into the panel.
    "chrome/browser/content/browser/sidebar/sidebar-bookmarks.mjs": [
        ("""    return html`
      <h3
        data-l10n-id="firefoxview-search-results-header"
        data-l10n-args=${JSON.stringify({
          query: escapeHtmlEntities(this.searchQuery),
        })}
      ></h3>
      <span
        data-l10n-id="firefoxview-search-results-count"
        data-l10n-args=${JSON.stringify({ count: this.searchResults.length })}
      ></span>
      <sidebar-bookmark-list
        maxTabsLength="-1"
        secondaryActionClass="delete-button"
        .tabItems=${this.searchResults}
        @fxview-tab-list-primary-action=${this.onPrimaryAction}
        @fxview-tab-list-secondary-action=${this.onSecondaryAction}
        @fxview-tab-list-middleclick-action=${this.onPrimaryAction}
      ></sidebar-bookmark-list>
    `;""",
         """    return html`<moz-card
      data-l10n-id="firefoxview-search-results-header"
      data-l10n-args=${JSON.stringify({
        query: escapeHtmlEntities(this.searchQuery),
      })}
    >
      <span
        slot="secondary-header"
        data-l10n-id="firefoxview-search-results-count"
        data-l10n-args=${JSON.stringify({ count: this.searchResults.length })}
      ></span>
      <sidebar-bookmark-list
        maxTabsLength="-1"
        secondaryActionClass="delete-button"
        .tabItems=${this.searchResults}
        @fxview-tab-list-primary-action=${this.onPrimaryAction}
        @fxview-tab-list-secondary-action=${this.onSecondaryAction}
        @fxview-tab-list-middleclick-action=${this.onPrimaryAction}
      ></sidebar-bookmark-list>
    </moz-card>`;"""),
        ("""            () =>
              html`<sidebar-bookmark-list
                maxTabsLength="-1"
                secondaryActionClass="delete-button"
                .tabItems=${this.bookmarks.children?.filter(
                  b =>
                    b.children &&
                    (b.children.length ||
                      b.guid !== lazy.PlacesUtils.bookmarks.mobileGuid)
                ) ?? []}
                .expandedFolderGuids=${this.#expandedFolderGuids}
                @fxview-tab-list-primary-action=${this.onPrimaryAction}
                @fxview-tab-list-secondary-action=${this.onSecondaryAction}
                @fxview-tab-list-middleclick-action=${this.onPrimaryAction}
                @bookmark-folder-toggle=${this.#onFolderToggle}
                @bookmark-folder-middleclick=${({ detail }) =>
                  this.#openBookmarks([detail])}
              ></sidebar-bookmark-list>`
""",
         """            () =>
              html`<moz-card><sidebar-bookmark-list
                maxTabsLength="-1"
                secondaryActionClass="delete-button"
                .tabItems=${this.bookmarks.children?.filter(
                  b =>
                    b.children &&
                    (b.children.length ||
                      b.guid !== lazy.PlacesUtils.bookmarks.mobileGuid)
                ) ?? []}
                .expandedFolderGuids=${this.#expandedFolderGuids}
                @fxview-tab-list-primary-action=${this.onPrimaryAction}
                @fxview-tab-list-secondary-action=${this.onSecondaryAction}
                @fxview-tab-list-middleclick-action=${this.onPrimaryAction}
                @bookmark-folder-toggle=${this.#onFolderToggle}
                @bookmark-folder-middleclick=${({ detail }) =>
                  this.#openBookmarks([detail])}
              ></sidebar-bookmark-list></moz-card>`
"""),
    ],
    # Every sidebar page imports SidebarPage, so one import here registers the
    # card element for history, bookmarks, synced tabs and open tabs.
    "chrome/browser/content/browser/sidebar/sidebar-page.mjs": [
        ('// eslint-disable-next-line import/no-unassigned-import\n'
         'import "chrome://browser/content/sidebar/sidebar-panel-header.mjs";',
         '// eslint-disable-next-line import/no-unassigned-import\n'
         'import "chrome://browser/content/sidebar/sidebar-panel-header.mjs";\n'
         '// eslint-disable-next-line import/no-unassigned-import\n'
         'import "chrome://global/content/elements/moz-card.mjs";'),
    ],
    # The shared import above replaces this one.
    "chrome/browser/content/browser/sidebar/sidebar-syncedtabs.html": [
        ("""    <script
      type="module"
      src="chrome://global/content/elements/moz-card.mjs"
    ></script>
""", ""),
    ],
    # Workspace toggles in the Tabs and browsing pane. Containers are removed
    # from the UI here: pref entry, settings, group and subpage.
    "chrome/browser/content/browser/preferences/config/tabs-browsing.mjs": [
        ('  { id: "browser.tabs.groups.smart.enabled", type: "bool" },\n'
         '  { id: "privacy.userContext.ui.enabled", type: "bool" },\n\n'
         '  { id: "privacy.userContext.enabled", type: "bool" },\n\n',
         '  { id: "browser.tabs.groups.smart.enabled", type: "bool" },\n'
         '  { id: "firegila.workspaces.enabled", type: "bool" },\n'
         '  { id: "firegila.workspaces.scrollSwitch", type: "bool" },\n'
         '  { id: "toolkit.tabbox.switchByScrolling", type: "bool" },\n\n'),
        ("""// "Containers" tabs settings
Preferences.addSetting({
  id: "privacyUserContextUI",
  pref: "privacy.userContext.ui.enabled",
});
Preferences.addSetting({
  id: "browserContainersbox",
  deps: ["privacyUserContextUI"],
  visible: ({ privacyUserContextUI }) => !!privacyUserContextUI.value,
});
Preferences.addSetting({
  id: "browserContainersCheckbox",
  pref: "privacy.userContext.enabled",
  controllingExtensionInfo: {
    storeId: "privacy.containers",
    l10nId: "extension-controlling-privacy-containers",
  },
  async promptToCloseTabsAndDisable(count, setting) {
    let [title, message, okButton, cancelButton] =
      await document.l10n.formatValues([
        { id: "containers-disable-alert-title" },
        { id: "containers-disable-alert-desc", args: { tabCount: count } },
        { id: "containers-disable-alert-ok-button", args: { tabCount: count } },
        { id: "containers-disable-alert-cancel-button" },
      ]);

    let buttonFlags =
      Ci.nsIPrompt.BUTTON_TITLE_IS_STRING * Ci.nsIPrompt.BUTTON_POS_0 +
      Ci.nsIPrompt.BUTTON_TITLE_IS_STRING * Ci.nsIPrompt.BUTTON_POS_1;

    let rv = Services.prompt.confirmEx(
      window,
      title,
      message,
      buttonFlags,
      okButton,
      cancelButton,
      null,
      null,
      {}
    );

    // User confirmed - disable containers and close container tabs.
    if (rv == 0) {
      await lazy.ContextualIdentityService.closeContainerTabs();
      setting.pref.value = false;
    }

    // Keep the checkbox checked when the user opts not to close tabs.
    return true;
  },
  set(val, _, setting) {
    // When enabling container tabs, just set the pref value.
    if (val) {
      return val;
    }

    // When disabling container tabs, check if there are container tabs currently
    // open. If there aren't, then proceed with disabling.
    let count = lazy.ContextualIdentityService.countContainerTabs();
    if (count == 0) {
      return false;
    }

    // When disabling container tabs with container tabs currently open show a
    // dialog to determine whether or not the tabs should be closed.
    return this.promptToCloseTabsAndDisable(count, setting);
  },
});
Preferences.addSetting({
  id: "browserContainersSettings",
  deps: ["browserContainersCheckbox"],
  /**
   * Displays container panel for customising and adding containers.
   */
  onUserClick: () => {
    window.gotoPref("containers");
  },
  disabled: ({ browserContainersCheckbox }) => !browserContainersCheckbox.value,
});

""", ""),
        ('  ContextualIdentityService:\n'
         '    "resource://gre/modules/ContextualIdentityService.sys.mjs",\n', ""),
        ("""      {
        id: "browserContainersbox",
        control: "moz-fieldset",
        l10nId: "tabs-containers-heading",
        headingLevel: 3,
        items: [
          {
            id: "browserContainersCheckbox",
            l10nId: "browser-containers-enabled-2",
            supportPage: "containers",
          },
          {
            id: "browserContainersSettings",
            loadPane: "containers",
            l10nId: "browser-containers-settings-2",
            control: "moz-box-button",
          },
        ],
      },
""", ""),
        ("""SettingGroupManager.registerGroups({
""",
         """Preferences.addSetting({
  id: "firegilaWorkspaces",
});
Preferences.addSetting({
  id: "firegilaWorkspacesEnabled",
  pref: "firegila.workspaces.enabled",
});
Preferences.addSetting({
  id: "firegilaWorkspaceScroll",
  pref: "firegila.workspaces.scrollSwitch",
  deps: ["firegilaWorkspacesEnabled"],
  disabled: ({ firegilaWorkspacesEnabled }) => !firegilaWorkspacesEnabled.value,
});
Preferences.addSetting({
  id: "firegilaTabScroll",
  pref: "toolkit.tabbox.switchByScrolling",
});

SettingGroupManager.registerGroups({
"""),
        ("""          {
            id: "warnOnQuitKey",
            l10nId: "ask-on-quit-with-key",
          },
        ],
      },
    ],
""",
         """          {
            id: "warnOnQuitKey",
            l10nId: "ask-on-quit-with-key",
          },
        ],
      },
      {
        id: "firegilaWorkspaces",
        control: "moz-fieldset",
        l10nId: "firegila-workspaces-heading",
        headingLevel: 3,
        items: [
          {
            id: "firegilaWorkspacesEnabled",
            l10nId: "firegila-workspaces-enabled",
          },
          {
            id: "firegilaWorkspaceScroll",
            l10nId: "firegila-workspaces-scroll",
          },
          {
            id: "firegilaTabScroll",
            l10nId: "firegila-tabs-scroll",
          },
        ],
      },
    ],
"""),
    ],
    "chrome/browser/content/browser/preferences/preferences.js": [
        ("""  containers: {
    parent: srdSectionEnabled("tabsBrowsing") ? "tabsBrowsing" : "general",
    l10nId: "containers-section-header2",
    groupIds: ["containers"],
    module: "chrome://browser/content/preferences/config/containers.mjs",
  },
""", ""),
    ],
    # Panel open and close transitions like every other sidebar state change.
    # Stock flips the box on and off with no animation at all. The call is
    # left un-awaited on purpose: it reads the from rects first, yields, then
    # reads the to rects once the toggle below has landed.
    "chrome/browser/content/browser/sidebar/browser-sidebar.js": [
        ("      this.selectMenuItem(commandID);\n"
         "      this._box.hidden = this._splitter.hidden = false;",
         "      this.selectMenuItem(commandID);\n"
         "      if (this._animationEnabled && !window.gReduceMotion) {\n"
         "        this._animateSidebarContainer();\n"
         "      }\n"
         "      this._box.hidden = this._splitter.hidden = false;"),
        # Panels keep their page when the sidebar hides. Stock unloads to
        # about:blank, which loses state and forces a reload on reopen.
        ("    // Replace the document currently displayed in the sidebar with about:blank\n"
         "    // so that we can free memory by unloading the page. We need to explicitly\n"
         "    // create a new content viewer because the old one doesn't get destroyed\n"
         "    // until about:blank has loaded (which does not happen as long as the\n"
         "    // element is hidden).\n"
         "    this.browser.setAttribute(\"src\", \"about:blank\");\n"
         "    this.browser.docShell?.createAboutBlankDocumentViewer(null, null);\n"
         "\n"
         "    this._box.removeAttribute(\"checked\");\n"
         "    this._box.removeAttribute(\"context\");\n"
         "    this._box.hidden = this._splitter.hidden = true;",
         "    if (this._animationEnabled && !window.gReduceMotion) {\n"
         "      this._animateSidebarContainer();\n"
         "    }\n"
         "    this._box.removeAttribute(\"checked\");\n"
         "    this._box.removeAttribute(\"context\");\n"
         "    this._box.hidden = this._splitter.hidden = true;"),
    ],
    "chrome/browser/content/branding/aboutDialog.css": [
        ("#20123a", "#262626"),
        ("hsla(235, 43%, 10%, 0.5)", "#2e2e2e"),
    ],
    "chrome/browser/content/browser/contentSearchHandoffUI.css": [
        ("--content-search-handoff-ui-border-radius: var(--border-radius-circle);",
         "--content-search-handoff-ui-border-radius: 8px;"),
    ],
    "chrome/browser/content/browser/firefoxview/firefoxview.css": [
        ("#0061e0", "AccentColor"), ("#00ddff", "AccentColor"),
        ("--newtab-background-color: light-dark(#f9f9fb, #2b2a33);",
         "--newtab-background-color: light-dark(#fafafa, #1f1f1f);"),
    ],
    "chrome/browser/content/browser/aboutwelcome/aboutwelcome.css": [
        ("#0061E0", "AccentColor"), ("#00DDFF", "AccentColor"), ("#9059FF", "AccentColor"),
    ],
    "chrome/browser/content/browser/protections.css": [
        ("#0250bb", "AccentColor"), ("#9059ff", "AccentColor"),
    ],
    "chrome/browser/content/browser/backup/archive.css": [
        ("#0060df", "AccentColor"), ("#0250bb", "AccentColor"),
    ],
    "chrome/browser/builtin-addons/webcompat/about-compat/aboutCompat.css": [
        ("#0061e0", "AccentColor"), ("#00ddff", "AccentColor"),
    ],
    "chrome/browser/builtin-addons/newtab/data/css/activity-stream.css": [
        ("#20123A", "#171717"), ("#fbfbfe", "#fafafa"),
        ("#F9F9FB", "#fafafa"), ("#2B2A33", "#1f1f1f"),
    ] + NEWTAB_TOKEN_PAIRS,
    "chrome/browser/builtin-addons/newtab/data/css/nova/activity-stream.css": [
        ("#20123A", "#171717"), ("#fbfbfe", "#fafafa"),
        ("#F9F9FB", "#fafafa"), ("#2B2A33", "#1f1f1f"),
    ] + NEWTAB_TOKEN_PAIRS + NEWTAB_NOVA_ONLY,
    "chrome/browser/builtin-addons/newtab/data/content/activity-stream.bundle.js": [
        # Logo stays centered at any row count. Stock moves it aside past 2 rows.
        ("const logoShouldBeCentered = !pocketEnabled && !hasContentWidgets && !hasManyTopSitesRows;",
         "const logoShouldBeCentered = true;"),
        # Slot count ignores the experiment config and uses the plain default.
        ("TopSitesMaxSitesPerRow: prefs.trainhopConfig?.topSites?.maxSitesPerRow ?? prefs.topSitesMaxSitesPerRow ?? TOP_SITES_MAX_SITES_PER_ROW",
         "TopSitesMaxSitesPerRow: prefs.topSitesMaxSitesPerRow ?? TOP_SITES_MAX_SITES_PER_ROW"),
        # Add tile starts in the first free slot. Stock starts it at the last
        # slot when the grid is empty, so the first shortcut pins there and
        # the add tile has nowhere left to go.
        ("    let targetPosition = topSites.length - 1;",
         "    let targetPosition = 0;"),
        # Hold a newtab dialog on screen long enough to fade out. React unmounts
        # the node the instant the edit state clears, which leaves nothing for a
        # close transition to animate. fgDeferDialogClose puts .fg-closing on
        # the dialog, waits for the transition, and only then lets the state go.
        ("class _TopSites extends (external_React_default()).PureComponent {",
         """// Firegila. Hold a newtab dialog on screen long enough to fade out.
function fgDeferDialogClose(selector, done) {
  var dialog = globalThis.document?.querySelector(selector);
  if (!dialog || dialog.fgClosing) {
    done();
    return;
  }
  dialog.fgClosing = true;
  dialog.classList.add("fg-closing");
  var settled = false;
  var finish = () => {
    if (settled) {
      return;
    }
    settled = true;
    dialog.removeEventListener("transitionend", finish);
    dialog.classList.remove("fg-closing");
    dialog.fgClosing = false;
    done();
  };
  dialog.addEventListener("transitionend", finish);
  // Fallback for reduced motion, where nothing transitions at all.
  globalThis.setTimeout(finish, 400);
}
class _TopSites extends (external_React_default()).PureComponent {"""),
        ("""  onEditFormClose() {
    this.props.dispatch(actionCreators.UserEvent({
      source: TOP_SITES_SOURCE,
      event: "TOP_SITES_EDIT_CLOSE"
    }));
    this.props.dispatch({
      type: actionTypes.TOP_SITES_CANCEL_EDIT
    });
  }""",
         """  onEditFormClose() {
    fgDeferDialogClose(".edit-topsites-wrapper .modalOverlayOuter", () => {
      this.props.dispatch(actionCreators.UserEvent({
        source: TOP_SITES_SOURCE,
        event: "TOP_SITES_EDIT_CLOSE"
      }));
      this.props.dispatch({
        type: actionTypes.TOP_SITES_CANCEL_EDIT
      });
    });
  }"""),
        ("""  onSearchShortcutsFormClose() {
    this.props.dispatch(actionCreators.UserEvent({
      source: TOP_SITES_SOURCE,
      event: "SEARCH_EDIT_CLOSE"
    }));
    this.props.dispatch({
      type: actionTypes.TOP_SITES_CLOSE_SEARCH_SHORTCUTS_MODAL
    });
  }""",
         """  onSearchShortcutsFormClose() {
    fgDeferDialogClose(".edit-search-shortcuts .modalOverlayOuter", () => {
      this.props.dispatch(actionCreators.UserEvent({
        source: TOP_SITES_SOURCE,
        event: "SEARCH_EDIT_CLOSE"
      }));
      this.props.dispatch({
        type: actionTypes.TOP_SITES_CLOSE_SEARCH_SHORTCUTS_MODAL
      });
    });
  }"""),
        # Every slot stays visible. Stock caps rows at 6 and 8 per viewport
        # width, which hides the add tile on narrower windows. Row length
        # is fixed at 8 by CSS instead.
        ("""      if (novaEnabled) {
        if (i >= maxSmallVisibleIndex) {
          slotProps.className = "nova-hide-for-s";
        } else if (i >= maxNarrowVisibleIndex) {
          slotProps.className = "nova-hide-for-xs";
        }
      } else if (i >= maxSmallVisibleIndex) {
        slotProps.className = "hide-for-small";
      } else if (i >= maxNarrowVisibleIndex) {
        slotProps.className = "hide-for-narrow";
      }""",
         """      if (false) {
        slotProps.className = "nova-hide-for-s";
      }"""),
    ],
    # New tab wallpapers. Firegila offers only the custom upload from the PC,
    # so the stock wallpaper records are not read. The category dispatch below
    # the removed block still runs, and that is what adds the upload entry.
    "chrome/browser/builtin-addons/newtab/lib/Wallpapers/WallpaperFeed.sys.mjs": [
        ('''    // retrieving all records in collection
    const records = await this.wallpaperClient.get();
    if (!records?.length) {
      return;
    }

    const customWallpaperEnabled = Services.prefs.getBoolPref(
      PREF_WALLPAPERS_CUSTOM_WALLPAPER_ENABLED
    );

    let baseAttachmentURL = RS_FALLBACK_BASE_URL;
    try {
      baseAttachmentURL = await lazy.Utils.baseAttachmentsURL();
    } catch (error) {
      console.error(
        `Error fetching remote settings base url from CDN. Falling back to ${RS_FALLBACK_BASE_URL}`,
        error
      );
    }

    const wallpapers = [
      ...records.map(record => {
        return {
          ...record,
          ...(record.attachment
            ? {
                wallpaperUrl: `${baseAttachmentURL}${record.attachment.location}`,
              }
            : {}),
          background_position: record.background_position || "center",
          category: record.category || "",
          order: record.order || 0,
          thumbnail: record.thumbnail || null,
        };
      }),
    ];
''',
         '''    const customWallpaperEnabled = Services.prefs.getBoolPref(
      PREF_WALLPAPERS_CUSTOM_WALLPAPER_ENABLED
    );

    const wallpapers = [];
'''),
    ],
    "chrome/browser/builtin-addons/newtab/lib/TopSitesFeed.sys.mjs": [
        ('''function getTopSitesCount(prefValues) {
  return (
    prefValues[ROWS_PREF] *
    (prefValues.trainhopConfig?.topSites?.maxSitesPerRow ??
      prefValues[PREF_MAX_SITES_PER_ROW] ??
      TOP_SITES_MAX_SITES_PER_ROW)
  );
}''',
         '''function getTopSitesCount(prefValues) {
  return (
    prefValues[ROWS_PREF] *
    (prefValues[PREF_MAX_SITES_PER_ROW] ?? TOP_SITES_MAX_SITES_PER_ROW)
  );
}'''),
        # Manual shortcuts only. History never fills the grid. Pinned
        # links still merge through insertPinned, so add, edit, drag and
        # remove keep working exactly as stock.
        ("    // Remove any duplicates from frecent and default sites\n",
         "    // Manual shortcuts only. History never fills the grid.\n    frecent = [];\n\n    // Remove any duplicates from frecent and default sites\n"),
    ],
    # Home settings sections. Sponsored content and recent activity rows
    # are removed from Settings and the new tab customize panel.
    "chrome/en-US/locale/browser/appstrings.properties": [
        ("Firefox", "Firegila"),
    ],
    "localization/en-US/browser/preferences/preferences.ftl": [
        (".tooltiptext = Extensions and themes for Firefox desktop",
         ".tooltiptext = Extensions and themes for Firegila desktop"),
        ("tabs-group-header2 =\n  .label = Tabs",
         "tabs-group-header2 =\n  .label = Tabs\n\n"
         "firegila-workspaces-heading =\n  .label = Workspaces\n\n"
         "firegila-workspaces-enabled =\n  .label = Enable workspaces\n\n"
         "firegila-workspaces-scroll =\n  .label = Switch workspaces by scrolling\n\n"
         "firegila-tabs-scroll =\n  .label = Switch tabs by scrolling"),
    ],
    "localization/en-US/browser/profile/default-bookmarks.ftl": [
        ("default-bookmarks-firefox-heading = Mozilla Firefox",
         "default-bookmarks-firefox-heading = Firegila"),
        ("default-bookmarks-firefox-customize = Customize Firefox",
         "default-bookmarks-firefox-customize = Customize Firegila"),
    ],
    "localization/en-US/devtools/client/application.ftl": [
        ("manifest-loaded-devtools-error = Firefox DevTools error",
         "manifest-loaded-devtools-error = Firegila DevTools error"),
    ],
    "chrome/browser/builtin-addons/newtab/lib/AboutPreferences.sys.mjs": [
        ('''    const allSections = [...PREFS_FOR_SETTINGS(), highlights];''',
         '''    const allSections = PREFS_FOR_SETTINGS();'''),
        ('''        {
          id: "supportFirefox",
          subcategory: "support-firefox",
          l10nId: "home-prefs-support-firefox-header-srd",
          control: "moz-toggle",
          items: [
            {
              id: "sponsoredShortcuts",
              l10nId: "home-prefs-shortcuts-by-option-sponsored-srd",
            },
            {
              id: "sponsoredStories",
              l10nId: "home-prefs-recommended-by-option-sponsored-stories-srd",
            },
            {
              id: "supportFirefoxPromo",
              l10nId: "home-prefs-mission-message2",
              control: "moz-promo",
              options: [
                {
                  control: "a",
                  l10nId: "home-prefs-mission-message-learn-more-link-srd",
                  slot: "support-link",
                  controlAttrs: {
                    is: "moz-support-link",
                    "support-page": "sponsor-privacy",
                    "utm-content": "inproduct",
                  },
                },
              ],
            },
          ],
        },
''',
         ''''''),
        ('''        {
          id: "recentActivity",
          subcategory: "highlights",
          l10nId: "home-prefs-recent-activity-header-srd",
          control: "moz-toggle",
          items: [
            {
              id: "recentActivityRows",
              l10nId: "home-prefs-recent-activity-select",
              control: "moz-select",
              options: [
                {
                  value: 1,
                  l10nId: "home-prefs-sections-rows-option-srd",
                  l10nArgs: { num: 1 },
                },
                {
                  value: 2,
                  l10nId: "home-prefs-sections-rows-option-srd",
                  l10nArgs: { num: 2 },
                },
                {
                  value: 3,
                  l10nId: "home-prefs-sections-rows-option-srd",
                  l10nArgs: { num: 3 },
                },
                {
                  value: 4,
                  l10nId: "home-prefs-sections-rows-option-srd",
                  l10nArgs: { num: 4 },
                },
              ],
            },
            {
              id: "recentActivityVisited",
              l10nId: "home-prefs-highlights-option-visited-pages-srd",
            },
            {
              id: "recentActivityBookmarks",
              l10nId: "home-prefs-highlights-options-bookmarks-srd",
            },
            {
              id: "recentActivityDownloads",
              l10nId: "home-prefs-highlights-option-most-recent-download-srd",
            },
          ],
        },
''',
         ''''''),
        ('''    // Support Firefox: sponsored content
    Preferences.addSetting({
      id: "supportFirefox",
      pref: "browser.newtabpage.activity-stream.showSponsoredCheckboxes",
      deps: ["sponsoredShortcuts", "sponsoredStories", ...firefoxHomeDeps],
      disabled: deps => !firefoxHomeActive(deps),
      onUserChange(value, { sponsoredShortcuts, sponsoredStories }) {
        // When supportFirefox changes, automatically update child preferences to match
        sponsoredShortcuts.value = !!value;
        sponsoredStories.value = !!value;
      },
    });
''',
         ''''''),
        ('''    Preferences.addSetting({
      id: "sponsoredShortcuts",
      pref: "browser.newtabpage.activity-stream.showSponsoredTopSites",
      deps: ["topsitesEnabled"],
      disabled: ({ topsitesEnabled }) => !topsitesEnabled.value,
    });
''',
         ''''''),
        ('''    Preferences.addSetting({
      id: "sponsoredStories",
      pref: "browser.newtabpage.activity-stream.showSponsored",
      deps: ["systemTopstories", "stories"],
      visible: ({ systemTopstories }) => !!systemTopstories.value,
      disabled: ({ stories }) => !stories.value,
    });
''',
         ''''''),
        ('''    Preferences.addSetting({
      id: "supportFirefoxPromo",
      deps: ["supportFirefox"],
    });
''',
         ''''''),
        ('''    // Recent activity
    Preferences.addSetting({
      id: "recentActivity",
      pref: "browser.newtabpage.activity-stream.feeds.section.highlights",
      deps: firefoxHomeDeps,
      disabled: deps => !firefoxHomeActive(deps),
    });
''',
         ''''''),
        ('''    Preferences.addSetting({
      id: "recentActivityRows",
      pref: "browser.newtabpage.activity-stream.section.highlights.rows",
    });
''',
         ''''''),
        ('''    Preferences.addSetting({
      id: "recentActivityVisited",
      pref: "browser.newtabpage.activity-stream.section.highlights.includeVisited",
    });
''',
         ''''''),
        ('''    Preferences.addSetting({
      id: "recentActivityBookmarks",
      pref: "browser.newtabpage.activity-stream.section.highlights.includeBookmarks",
    });
''',
         ''''''),
        ('''    Preferences.addSetting({
      id: "recentActivityDownloads",
      pref: "browser.newtabpage.activity-stream.section.highlights.includeDownloads",
    });
''',
         ''''''),
        ('''    {
      id: "support-firefox",
      pref: {
        feed: "showSponsoredCheckboxes",
        titleString: "home-prefs-support-firefox-header",
        nestedPrefs: [
          {
            name: "showSponsoredTopSites",
            titleString: "home-prefs-shortcuts-by-option-sponsored",
            eventSource: "SPONSORED_TOP_SITES",
          },
          {
            name: "showSponsored",
            titleString: "home-prefs-recommended-by-option-sponsored-stories",
            eventSource: "POCKET_SPOCS",
            shouldHidePref: !Services.prefs.getBoolPref(
              "browser.newtabpage.activity-stream.feeds.system.topstories",
              true
            ),
            shouldDisablePref: !Services.prefs.getBoolPref(
              "browser.newtabpage.activity-stream.feeds.section.topstories",
              true
            ),
          },
        ],
      },
    },
''',
         ''''''),
        ('''    // Special cases to like the nested prefs with another pref,
    // so we can disable it real time.
    if (id === "support-firefox") {
      function setupSupportFirefoxSubCheck(triggerPref, subPref) {
        const subCheckFullName = `browser.newtabpage.activity-stream.${triggerPref}`;
        const subCheckPref = Preferences.get(subCheckFullName);

        subCheckPref?.on("change", () => {
          const showSponsoredFullName = `browser.newtabpage.activity-stream.${subPref}`;
          const showSponsoredSubcheck = subChecks.find(
            subcheck =>
              subcheck.getAttribute("preference") === showSponsoredFullName
          );
          if (showSponsoredSubcheck) {
            showSponsoredSubcheck.disabled = !Services.prefs.getBoolPref(
              subCheckFullName,
              true
            );
          }
        });
      }

      setupSupportFirefoxSubCheck("feeds.section.topstories", "showSponsored");
      setupSupportFirefoxSubCheck("feeds.topsites", "showSponsoredTopSites");
    }
''',
         ''''''),
        ('''        // Update child preferences for the "Support Firefox" checkbox group
        // so that they're turned on and off at the same time.
        if (id === "support-firefox") {
          const subPref = Preferences.get(subcheck.getAttribute("preference"));
          subPref.value = pref.value;
        }

''',
         ''''''),
    ],
    "chrome/browser/skin/classic/browser/browser-colors.css": [
        ("--short-notification-background: #0250bb;",
         "--short-notification-background: AccentColor;"),
        ("--short-notification-gradient: #9059ff;",
         "--short-notification-gradient: AccentColor;"),
        ("--focus-outline-color: light-dark(#0061e0, #00ddff);",
         "--focus-outline-color: AccentColor;"),
        ("--chrome-content-separator-color: var(--card-border-color);",
         "--chrome-content-separator-color: var(--fg-border);"),
        ("--chrome-content-separator-color: light-dark(rgb(204, 204, 204), hsl(240, 5%, 5%));",
         "--chrome-content-separator-color: var(--fg-border);"),
        ("--chrome-content-separator-color: light-dark(rgb(201, 192, 227), rgb(16, 17, 24));",
         "--chrome-content-separator-color: var(--fg-border);"),
        ("--tabs-navbar-separator-color: light-dark(rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.3));",
         "--tabs-navbar-separator-color: var(--fg-border);"),
    ],
    "chrome/browser/skin/classic/browser/preferences/search.css": [
        ("fill: #0060df; /* Blue-60 */", "fill: AccentColor;"),
    ],
    "chrome/browser/skin/classic/browser/controlcenter/panel.css": [
        ("fill: light-dark(#0090ed, #80ebff);", "fill: AccentColor;"),
        ("--trustpanel-highlight-bg: light-dark(var(--color-violet-10), var(--color-violet-90));",
         "--trustpanel-highlight-bg: light-dark(#e6e6e6, #333333);"),
        ("--trustpanel-highlight-bg: light-dark(var(--color-violet-10), var(--color-violet-desaturated-70));",
         "--trustpanel-highlight-bg: light-dark(#e6e6e6, #333333);"),
        ("--trustpanel-inner-border: 1px solid var(--color-violet-20);",
         "--trustpanel-inner-border: 1px solid #c4c4c4;"),
    ],
    "chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css": [
        ("--panel-banner-item-info-icon-bgcolor: light-dark(#0090ed, #80ebff);",
         "--panel-banner-item-info-icon-bgcolor: AccentColor;"),
        ("  --panel-background-color: #0060df;\n  --panel-border-color: #0060df;\n  --panel-text-color: #fff;",
         "  --panel-background-color: AccentColor;\n  --panel-border-color: AccentColor;\n  --panel-text-color: AccentColorText;"),
        ("linear-gradient(90deg, #9059ff 0%, #ff4aa2 52.08%, #ffbd4f 100%)",
         "linear-gradient(90deg, #b3b3b3 0%, #8f8f8f 52.08%, #b3b3b3 100%)"),
        ("border: 4px solid light-dark(#177ee6, #00ddff);",
         "border: 4px solid AccentColor;"),
    ],
    "chrome/browser/content/browser/preferences/config/appearance.mjs": [
        ("""    /** @param {string} val */
    set(val) {
      return this.themeNames.indexOf(val);
    },""",
         """    /** @param {string} val */
    set(val) {
      // Firegila links website scheme to the browser theme.
      const themes = {
        dark: "firefox-compact-dark@mozilla.org",
        light: "firefox-compact-light@mozilla.org",
        auto: "default-theme@mozilla.org",
      };
      const id = themes[val];
      if (id) {
        const { AddonManager } = ChromeUtils.importESModule(
          "resource://gre/modules/AddonManager.sys.mjs"
        );
        AddonManager.getAddonByID(id).then(addon => addon && addon.enable());
      }
      return this.themeNames.indexOf(val);
    },"""),
    ],
    "chrome/browser/skin/classic/browser/preferences/preferences.css": [
        (".nav-separator {",
         "/* Firegila hides AI and Labs nav entries. Prefs gate the panes. */\n"
         "      #category-ai-features,\n"
         "      #category-experimental {\n"
         "        display: none;\n"
         "      }\n"
         "      .nav-separator {"),
    ],
    "chrome/browser/skin/classic/browser/urlbar-searchbar.css": [
        ("--cfr-active-color: #0060df;", "--cfr-active-color: AccentColor;"),
    ],
    "chrome/browser/skin/classic/browser/downloads/download-blockedStates.css": [
        ("fill: light-dark(#0090ed, #80ebff);", "fill: AccentColor;"),
    ],
    "chrome/browser/skin/classic/browser/smartbar.css": [
        ("--smartbar-border-color-gradient: linear-gradient(95deg, var(--color-violet-50) 1.22%, var(--color-pink-40) 49.98%, var(--color-yellow-30) 99.68%);",
         "--smartbar-border-color-gradient: AccentColor;"),
        ("--smartbar-outline-color: light-dark(var(--color-violet-30), var(--color-violet-50));",
         "--smartbar-outline-color: AccentColor;"),
        ("--link-color: light-dark(var(--color-violet-70), var(--color-violet-30));",
         "--link-color: AccentColor;"),
        ("--multiline-editor-selection-color: light-dark(var(--color-violet-0), var(--color-violet-60));",
         "--multiline-editor-selection-color: AccentColor;"),
        ("--smartbar-glow-color: color-mix(in srgb, var(--color-violet-40) 50%, transparent);",
         "--smartbar-glow-color: AccentColor;"),
    ],
    "chrome/browser/skin/classic/browser/syncedtabs/sidebar.css": [
        ("  background-color: #0060df;\n  color: white;",
         "  background-color: AccentColor;\n  color: AccentColorText;"),
    ],
    "chrome/browser/skin/classic/browser/toolbarbuttons.css": [
        ("--smartwindow-toggle-shadow-color: light-dark(\n    color-mix(in srgb, var(--color-violet-60) 20%, transparent),\n    color-mix(in srgb, var(--color-violet-40) 20%, transparent)\n  );",
         "--smartwindow-toggle-shadow-color: #8f8f8f;"),
        ("--smartwindow-ask-btn-bg-opened-dark: #321342;",
         "--smartwindow-ask-btn-bg-opened-dark: #333333;"),
        ("--smartwindow-ask-btn-bg-opened-hover: var(--color-violet-20);",
         "--smartwindow-ask-btn-bg-opened-hover: #e6e6e6;"),
        ("--smartwindow-ask-btn-text-color: light-dark(var(--color-violet-80), var(--color-white));",
         "--smartwindow-ask-btn-text-color: light-dark(#171717, #fafafa);"),
        ("--smartwindow-ask-btn-text-color-opened: light-dark(var(--color-violet-80), var(--color-violet-10));",
         "--smartwindow-ask-btn-text-color-opened: light-dark(#171717, #fafafa);"),
        ("--smartwindow-ask-btn-border-color-opened: light-dark(var(--color-violet-80), transparent);",
         "--smartwindow-ask-btn-border-color-opened: light-dark(#8f8f8f, transparent);"),
        ("--smartwindow-ask-btn-border-color-hover: light-dark(var(--color-violet-80), var(--color-white));",
         "--smartwindow-ask-btn-border-color-hover: AccentColor;"),
        ("--smartwindow-ask-btn-icon-stroke-color: light-dark(#ecbcea, var(--color-violet-40));",
         "--smartwindow-ask-btn-icon-stroke-color: currentColor;"),
        ("--smartwindow-ask-btn-gradient: linear-gradient(83deg, #5119dc 0.73%, var(--color-violet-30) 98.05%);",
         "--smartwindow-ask-btn-gradient: AccentColor;"),
    ],
    "chrome/browser/skin/classic/browser/toolbarbutton-icons.css": [
        ("fill: #0060df;", "fill: AccentColor;"),
        ("background-color: #0060df33;", "background-color: AccentColor;"),
        ("background-color: #0060df22;", "background-color: AccentColor;"),
    ],
    "chrome/browser/skin/classic/browser/privatebrowsing/aboutPrivateBrowsing.css": [
        ("--background-color-canvas: #25003e;",
         "--background-color-canvas: #1f1f1f;"),
        ("--content-search-handoff-ui-background-color: #321c64;",
         "--content-search-handoff-ui-background-color: #262626;"),
        ("--content-search-handoff-ui-unfocused-border-color: rgb(149, 43, 185);",
         "--content-search-handoff-ui-unfocused-border-color: #4a4a4a;"),
        ("#0060df", "AccentColor"),
        ("rgba(149, 43, 185, 0.5)", "#333333"),
    ],
    "chrome/browser/content/browser/privacy-metrics-card.css": [
        ("fill: var(--color-violet-50);", "fill: AccentColor;"),
    ],
    "chrome/browser/content/browser/sidebar/sidebar-pins-promo.css": [
        ("/* This Source Code Form is subject to the terms of the Mozilla Public",
         ":host { display: none !important; }\n\n/* This Source Code Form is subject to the terms of the Mozilla Public"),
        ("#9059ff", "#8f8f8f"), ("#f4f0ff", "#f2f2f2"), ("#c7b2ff", "#c4c4c4"),
        ("#623ac3", "#666666"), ("#7844f0", "#7d7d7d"),
    ],
    "modules/BuiltInThemeConfig.sys.mjs": [
        ("""  [
    "firefox-alpenglow@mozilla.org",
    {
      version: "1.5.3",
      path: "resource://builtin-themes/alpenglow/",
    },
  ],
""", ""),
    ],
    "chrome/browser/content/builtin-themes/privatewindow/manifest.json": [
        ('"name": "Firefox Nova Private Window"', '"name": "Firegila Private Window"'),
        ("#180e30", "#1f1f1f"), ("#281d44", "#262626"), ("#584a7d", "#3d3d3d"),
        ("#9687c0", "#454545"), ("#75669f", "#333333"), ("#d4c1ff", "#fafafa"),
        ("#e7e1f8", "#fafafa"), ("#1d1b1f", "#333333"), ("#131215", "#1f1f1f"),
        ("#d6d5da", "#454545"), ("rgba(182, 170, 217, 0.4)", "#4a4a4a"),
        ("rgba(54,53,57,0.9)", "#1f1f1f"),
        ("rgba(251, 251, 254, 0.7)", "#9f9f9f"),
    ],
}

REMOVE_DIRS_BROWSER = [
    "chrome/browser/content/builtin-themes/alpenglow",
]

# Layered tabs for every theme. Inactive tabs sit above the toolbar,
# the active tab sits above them with a full accent border.
# Unlayered beats token layers.
TAB_CSS = """
:root:not([lwtheme]) {
  --tab-background-color-selected: light-dark(#ffffff, #333333);
  --tab-background-color-hover: light-dark(#d9d9d9, #383838);
  --tab-selected-textcolor: light-dark(#171717, #fafafa);
  --tab-border-color-accent: AccentColor;
  --tab-selected-shadow: none;
}
.tabbrowser-tab:not([selected], [multiselected]) > .tab-stack > .tab-background {
  background-color: light-dark(#ededed, #1d1d1d);
  border: 1px solid light-dark(#d0d0d0, #232323);
}
.tabbrowser-tab[selected] > .tab-stack > .tab-background {
  border: 1px solid AccentColor;
}
#tabbrowser-tabs[orient="horizontal"]::before {
  display: none !important;
}

/* The stock button is still in the markup, but the tab strip has no tab
 * pickup entry here. Hide it so the workspace switcher sits beside the first
 * tab. Vertical tabs collapse the strip, so it is out of sight there too. */
#TabsToolbar-customization-target > #firefox-view-button {
  display: none !important;
}
:root {
  --chrome-content-separator-color: var(--fg-border);
  --tabs-navbar-separator-color: var(--fg-border);
  --toolbarseparator-color: var(--fg-border);
  --theme-toolbar-separator: var(--fg-border);
}
#tabbrowser-arrowscrollbox::part(overflow-start-indicator),
#tabbrowser-arrowscrollbox::part(overflow-end-indicator) {
  display: none !important;
}
/* Both strips use a 32px tab. The vertical column keeps a 2px inset, so its
 * background is the same size as a horizontal tab. The icon gap and the tab
 * inset are one value in both orientations. */
:root {
  --tab-min-height: 32px !important;
  --tab-icon-end-margin: 8px !important;
}

#tabbrowser-tabs[orient="vertical"] .tabbrowser-tab {
  padding: 2px !important;
}
#tabbrowser-tabs[orient="vertical"] .tabbrowser-tab > .tab-stack > .tab-background {
  margin-inline: 0 !important;
  margin-block: 0 !important;
  min-height: 32px !important;
}

/* Expanded vertical tabs use the same 8px inline inset as horizontal ones.
 * The stock value is derived from the collapsed width, which leaves a 18.5px
 * inset in the expanded column. */
#tabbrowser-tabs[orient="vertical"][expanded] {
  --tab-inline-padding: 8px !important;
  --tab-icon-end-margin: 8px !important;
}

/* The close button is a 16px square on every tab, the same box as the tab
 * icon, with the same 8px margin on all sides. The stock 24px box left a
 * wider gap on the right than the icon has on the left. */
#tabbrowser-tabs[orient="horizontal"] .tabbrowser-tab > .tab-stack > .tab-content > .tab-close-button,
#tabbrowser-tabs[orient="vertical"][expanded] .tabbrowser-tab > .tab-stack > .tab-content > .tab-close-button {
  width: 16px !important;
  min-width: 16px !important;
  height: 16px !important;
  min-height: 16px !important;
  margin-inline-end: 0 !important;
  padding: 2px !important;
}

/* The New Tab button is a 32px square in the horizontal strip and a full
 * width 32px row in the vertical one. */
#tabs-newtab-button {
  width: 32px !important;
  min-width: 32px !important;
  height: 32px !important;
  min-height: 32px !important;
  margin: 4px 2px !important;
  padding: 0 !important;
}

/* No list all tabs button. It is static markup, so it stays in the document
 * even when it is not part of the tab strip placement. Hide it and keep it
 * out of the vertical tab strip defaults as well. */
#alltabs-button {
  display: none !important;
}

#tabbrowser-tabs[orient="vertical"] > #vertical-tabs-newtab-button,
#tabbrowser-arrowscrollbox[orient="vertical"] > #tabbrowser-arrowscrollbox-periphery > #tabs-newtab-button {
  width: calc(100% - 4px) !important;
  min-width: 0 !important;
  margin: 2px !important;
  padding-inline: 8px !important;
  height: 32px !important;
  min-height: 32px !important;
  justify-content: start !important;
}
"""

# Flat content area. Stock draws a hairline outline around the page and rounds
# the corner next to the sidebar. Firegila keeps it square and borderless.
CONTENT_AREA_CSS = """
.browserContainer {
  outline: none;
  border-radius: 0 !important;
}
"""

# Shared card surface for the sidebar content pages. History, bookmarks,
# synced tabs, open tabs and the customizer use one card.
SIDEBAR_PAGE_CSS = """
:root {
  --card-background-color: var(--fg-bg-3);
  --card-border-color: var(--fg-border);
  --sidebar-box-background: var(--fg-bg-3);
  --sidebar-box-border-color: var(--fg-border);
}

/* Cards and the search bar share one inline edge. */
.sidebar-panel .sidebar-panel-scrollable-content {
  padding-inline: 0;
}
"""

# The password panel keeps the sidebar panel padding and the same search
# field as the other tools.
MEGALIST_CSS = """
.container.sidebar-panel {
  padding: var(--space-large);
}

.sidebar-panel .search-container {
  min-height: 32px;
  padding-inline: 8px;
  border: 1px solid var(--fg-border);
  border-radius: var(--border-radius-medium);
  background-color: var(--fg-bg-3);
  color: var(--fg-text);
}
"""

# Newtab layout tweaks. No shadows, framed menu, stacked logo, hover labels.
# Visual only, stock layout and behavior.
NEWTAB_TWEAKS_CSS = """
/* No shadows on the new tab. Stock paints over a hundred of them on cards,
   menus, tiles and widgets. Flat everywhere. */
*, *::before, *::after {
  box-shadow: none !important;
  text-shadow: none !important;
}
/* Graph paper grid on the plain new tab background. Only when no wallpaper
   is set, so a chosen image stays clean. Centered so the pattern reads as
   deliberate rather than as an off screen edge. */
body:not(.lightWallpaper):not(.darkWallpaper) {
  background-image:
    linear-gradient(to right, light-dark(color-mix(in srgb, var(--fg-text) 8%, transparent), color-mix(in srgb, var(--fg-text) 4%, transparent)) 1px, transparent 1px),
    linear-gradient(to bottom, light-dark(color-mix(in srgb, var(--fg-text) 8%, transparent), color-mix(in srgb, var(--fg-text) 4%, transparent)) 1px, transparent 1px);
  background-size: 24px 24px;
  background-position: center center;
  background-repeat: repeat;
}
.customize-menu {
  border-radius: var(--fg-radius) !important;
  border: 1px solid var(--fg-border) !important;
  box-shadow: none !important;
  background-color: var(--newtab-background-color-secondary) !important;
}
.customize-menu.nova-enabled {
  --customize-menu-bg: var(--newtab-background-color-secondary);
  top: 8px !important;
  bottom: auto !important;
  height: calc(100vh - 16px) !important;
  max-height: calc(100vh - 16px) !important;
  min-height: 0 !important;
  margin: 0 !important;
  box-sizing: border-box !important;
  inset-inline-end: 8px !important;
}
.customize-menu-content {
  padding: 8px 8px 48px !important;
}
.customize-menu-content .manage-settings-footer {
  padding: 8px !important;
}
/* Wrapping rows center each row on its own, so the add tile starts
   centered when it opens a new row. The row is pinned to exactly 8 slots
   and never shrinks while there is room for them, so a wide window always
   lays out 8. On a narrow window the box is capped to the space available
   instead of overflowing it, because an overflowing box cannot be centered
   by auto margins and the tiles then drift off to the right. Fewer tiles
   per row, still 8 at most. Row gap matches the column gap. */
.top-sites-list {
  display: flex !important;
  flex-wrap: wrap;
  justify-content: center !important;
  align-content: center;
  grid-template-columns: none !important;
  column-gap: var(--space-medium) !important;
  row-gap: var(--space-medium) !important;
  inline-size: min(calc(8 * var(--col-width, 75px) + 7 * var(--space-medium)), 100%);
  margin-inline: auto;
}
.top-sites-list > .top-site-outer {
  flex: none;
  margin-inline: 0;
}
.top-site-outer .tile,
.top-site-outer.add-button .tile,
.nova-enabled .top-site-outer .tile,
.nova-enabled .top-site-outer.add-button .tile {
  box-shadow: none !important;
  border: 1px solid var(--fg-border) !important;
  border-radius: var(--fg-radius) !important;
  background: var(--fg-bg-3) !important;
}
.top-site-outer .tile:active,
.top-site-outer.add-button .tile:active {
  box-shadow: none !important;
  border: 1px solid var(--fg-border) !important;
}
.top-site-outer .top-site-button:focus-visible,
.top-site-outer .tile:focus-visible {
  outline: 1px solid AccentColor !important;
  outline-offset: 1px;
}
.top-site-outer.add-button .tile .icon-wrapper {
  fill: var(--fg-text) !important;
  color: var(--fg-text) !important;
}
.personalize-button,
.context-menu,
.panel-list,
.card-outer,
.collapsible-section,
.section-top-bar {
  box-shadow: none !important;
}
.search-wrapper content-search-handoff-ui {
  --content-search-handoff-ui-unfocused-border-color: var(--fg-border);
}
/* The search bar steps between fixed widths at the layout breakpoints, so it
   jumps the moment the window crosses one. One max, one min, and the gap it
   keeps from the edges as the window closes in.

   Nova lays the page out on a grid of fixed 75px columns, so anything
   spanning all of them jumps by a whole column, around 86px, whenever one is
   added. Flexible columns fill the content box exactly, so everything spanning
   them tracks the window smoothly. The tiles keep their fixed size from the
   wrapping flex rule below. */
.nova-enabled .content {
  grid-template-columns: repeat(auto-fill, minmax(var(--col-width), 1fr));
  justify-content: normal;
}
.activity-stream .search-wrapper .search-inner-wrapper,
.nova-enabled .search-inner-wrapper {
  width: clamp(
    var(--fg-search-min),
    calc(100% - 2 * var(--fg-search-gap)),
    var(--fg-search-max)
  );
}
.top-site-outer .title {
  opacity: 0;
  transition: opacity var(--fg-motion-fast) var(--fg-ease);
  position: absolute;
  top: calc(100% + 2px);
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
  pointer-events: none;
  text-align: center;
}
.top-site-outer .title .title-label {
  display: block !important;
  background: var(--fg-bg-3);
  border: 1px solid var(--fg-border) !important;
  border-radius: var(--fg-radius) !important;
  padding: 3px 8px !important;
  min-height: 0 !important;
  height: auto;
  width: max-content !important;
  max-width: 150px;
  text-align: center !important;
  line-height: 1.35;
  white-space: normal;
  overflow: visible;
  text-overflow: clip;
}
.top-site-outer {
  position: relative;
}
.top-site-outer:hover .title,
.top-site-outer:focus-within .title {
  opacity: 1;
}
.top-site-outer.add-button .title {
  display: none !important;
}
.logo-and-wordmark {
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  width: max-content !important;
}
.logo-and-wordmark .logo {
  width: 150px !important;
  height: 150px !important;
  background-size: 150px 150px !important;
}
.logo-and-wordmark .wordmark {
  display: none !important;
}
.nova-enabled .weather-widget {
  background: var(--fg-bg-3) !important;
  border: 1px solid var(--fg-border) !important;
  border-radius: var(--fg-radius) !important;
  box-shadow: none !important;
  /* Stock states drop the inline padding, leaving top and right unequal. */
  padding: var(--space-medium) !important;
  box-sizing: border-box;
  /* Fixed width. The card grew after use location, which shrank the right
     inset and made the padding look wrong. Same width in every state. */
  inline-size: 170px;
}
.nova-enabled .weather-widget.weather-search-active.small-widget {
  inline-size: 170px;
}
/* The right sidebar column is 150px, so a 170px card overflowed it and
   ate the page padding on that side. Widen the column to fit the card. */
.nova-enabled.container {
  grid-template-columns: var(--side-col-width) var(--content-col-width) 170px;
}
/* Once real data renders, the conditions row can push past the padding box
   and the right gap shrinks. Keep the content inside the padding box so the
   right inset always matches the top inset. */
.nova-enabled .weather-widget .weather-container,
.nova-enabled .weather-widget .weather-conditions-view,
.nova-enabled .weather-widget .weather-info-link {
  max-width: 100% !important;
  margin: 0 !important;
  box-sizing: border-box;
}
.nova-enabled .weather-widget:hover,
.nova-enabled .weather-widget:focus-within {
  background: var(--fg-bg-3) !important;
  outline: none !important;
  box-shadow: none !important;
}
.nova-enabled .weather-widget .weather-conditions-view .weather-icon-column {
  border-radius: calc(var(--fg-radius) - var(--space-small)) !important;
}
.nova-enabled .weather-widget .forecast-row .forecast-row-items li {
  border-radius: calc(var(--fg-radius) - var(--space-small)) !important;
}
.nova-enabled .weather-widget .forecast-footer {
  inset-inline: 0 !important;
  left: 0 !important;
  right: 0 !important;
  display: block !important;
  text-align: center !important;
}
.nova-enabled .weather-widget.large-widget .forecast-footer {
  justify-content: center !important;
}
.nova-enabled .weather-widget .forecast-footer .sponsored-text {
  opacity: 0;
  visibility: visible !important;
  transition: opacity var(--fg-motion-fast) var(--fg-ease);
}
.nova-enabled .weather-widget:hover .forecast-footer .sponsored-text,
.nova-enabled .weather-widget:focus-within .forecast-footer .sponsored-text {
  opacity: 1;
  visibility: visible !important;
}
"""

# Fox mascot art stays. Only the Mozilla mark is replaced.
ART_SVG_BROWSER = [
    "chrome/browser/skin/classic/browser/preferences/mozilla-logo.svg",
]


def patch_jar(jar, edits, remove_dirs=(), art=(), appends=(), sweep=False,
              overwrites=()):
    work = BUILD / "theme-work"
    extract(jar, work)
    for rel, pairs in edits.items():
        p = work / rel
        text = p.read_text()
        for old, new in pairs:
            n = text.count(old)
            assert n >= 1, f"theme: not found in {rel}: {old[:70]}"
            text = text.replace(old, new)
            print(f"{jar.name} {rel} {n}x")
        p.write_text(text)
    for rel, block in appends:
        p = work / rel
        with p.open("a") as f:
            f.write(block)
        print(f"{jar.name} appended {rel}")
    if sweep:
        n_swept = 0
        for dirpath, dirnames, filenames in os.walk(work):
            for fn in sorted(filenames):
                if not fn.endswith(".css"):
                    continue
                full = Path(dirpath) / fn
                rel = full.relative_to(work).as_posix()
                text = full.read_text()
                pairs = OLD_GRAYS + (TOKEN_VIOLET if is_token_file(rel) else OLD_ACCENTS)
                new_text = text
                for old, new in pairs:
                    if old in new_text:
                        new_text = new_text.replace(old, new)
                if new_text != text:
                    full.write_text(new_text)
                    n_swept += 1
        print(f"{jar.name} swept {n_swept} stylesheets")
    for d in remove_dirs:
        shutil.rmtree(work / d, ignore_errors=True)
        print(f"{jar.name} removed {d}")
    if art:
        master = Image.open(ROOT / "app-icons" / "firegila-2048.png").convert("RGBA")
        buf = io.BytesIO()
        master.resize((256, 256), Image.LANCZOS).save(buf, "PNG", optimize=True)
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256">'
            '<image width="256" height="256" href="data:image/png;base64,'
            + base64.b64encode(buf.getvalue()).decode()
            + '"/></svg>'
        )
        for rel in art:
            (work / rel).write_text(svg)
            print(f"{jar.name} art {rel}")
    for rel, content in overwrites:
        (work / rel).write_text(content)
        print(f"{jar.name} overwrote {rel}")
    replace(jar, work)
    print(f"theme: patched {jar.name}")


SB_CHROME_CSS = """
/* Strip width is the nav bar height. Neither measure has a token, the
 * bootstrap reads both off #nav-bar. */

#sidebar-container {
  inline-size: var(--fg-navbar-height, var(--tab-min-height));
  min-inline-size: var(--fg-navbar-height, var(--tab-min-height));
  background-color: var(--fg-navbar);
}

/* With vertical tabs the strip joins the tabs column, so it takes the tab bar
 * surface. Without them it is a plain launcher and follows the nav bar. */
@media -moz-pref("sidebar.verticalTabs") {
  #sidebar-container {
    background-color: var(--fg-tabbar);
  }
}

/* The panel-to-page boundary is the resize bar: wide grab area, one divider
 * line. */

#sidebar-splitter {
  width: var(--space-small);
  border-inline: calc((var(--space-small) - 1px) / 2) solid transparent;
  background-color: var(--fg-border);
  background-clip: content-box;
  margin-block-end: 0;
  transition: background-color var(--fg-motion-fast) var(--fg-ease);
}

#sidebar-splitter:hover {
  background-color: var(--focus-outline-color);
}

/* Panel: plain full height section, no radius. Width is the stored drag size
 * when there is one, else 500px. The 1px border is the section divider on the
 * strip side, so the panel reads as its own surface even when the tones are
 * close. */

#sidebar-box {
  box-sizing: border-box;
  padding-block-end: 0;
  margin-block-end: 0;
  overflow: clip;
  background-color: var(--fg-bg);
  border-inline-start: 1px solid var(--fg-divider);
  border-radius: 0;
  outline: none;
  width: var(--fg-panel-width, 500px);
}

:root:has(#sidebar-container[sidebar-positionend]) #sidebar-box {
  border-inline-start: 0;
  border-inline-end: 1px solid var(--fg-divider);
}

#sidebar {
  border-radius: 0;
  box-shadow: none;
  outline: none;
}

/* The launcher splitter would resize the strip, which this sheet overrides.
 * Hide it, a dead handle is worse than none. */

#sidebar-launcher-splitter {
  display: none;
}

/* Vertical tabs column. Auto width collapses to zero because the tab strip is
 * a scroll container, so the width is explicit, same as stock. Hidden with the
 * strip. Inline display during a transition beats this, so the fade-out still
 * plays. The column carries the strip surface, so strip and tabs form one
 * chrome section. The panel border is the only section divider. */

#vertical-tabs-container {
  display: flex;
  flex-direction: column;
  background-color: var(--fg-tabbar);
}

#vertical-tabs {
  flex-grow: 1;
  min-height: 0;
}

@media -moz-pref("sidebar.verticalTabs") {
  #vertical-tabs-container {
    width: var(--fg-tabs-width);
  }
}

:root:has(#sidebar-container[hidden]) #vertical-tabs-container {
  display: none;
}

/* Auto-hide tabs. The column keeps its full width and slides over the edge
 * with a transform, so nothing reflows and no frame is spent on layout. The
 * background and the tabs move as one surface.
 * A separate 3px chrome sensor at the edge keeps mousemove reachable when the
 * column sits over the page or its scrollbar. The sensor is earlier in the
 * DOM, so the revealed column paints above it and takes the clicks. */

@media -moz-pref("sidebar.verticalTabs") {
  :root[fg-autohide-tabs] #vertical-tabs-container {
    position: absolute;
    inset-block: 0;
    inset-inline-start: 0;
    z-index: var(--browser-area-z-index-sidebar-expand-on-hover);
    width: var(--fg-tabs-width);
    transform: translateX(-100%);
    transition: transform var(--fg-motion-base) var(--fg-ease);
  }

  :root[fg-autohide-tabs]:has(#sidebar-container[sidebar-positionend]) #vertical-tabs-container {
    inset-inline-start: auto;
    inset-inline-end: 0;
    transform: translateX(100%);
  }

  :root[fg-autohide-tabs][fg-tabs-opposite] #vertical-tabs-container {
    inset-inline-start: auto;
    inset-inline-end: 0;
    transform: translateX(100%);
  }

  :root[fg-autohide-tabs][fg-tabs-opposite]:has(#sidebar-container[sidebar-positionend]) #vertical-tabs-container {
    inset-inline-start: 0;
    inset-inline-end: auto;
    transform: translateX(-100%);
  }

  :root[fg-autohide-tabs][fg-tabs-revealed] #vertical-tabs-container {
    transform: translateX(0);
  }

  :root[fg-autohide-tabs] #vertical-tabs {
    min-inline-size: var(--fg-tabs-width);
  }

  :root[fg-autohide-tabs] #firegila-tabs-sensor {
    display: block;
    position: absolute;
    inset-block: 0;
    inset-inline-start: 0;
    width: 3px;
    z-index: var(--browser-area-z-index-sidebar-expand-on-hover);
  }

  :root[fg-autohide-tabs]:has(#sidebar-container[sidebar-positionend]) #firegila-tabs-sensor {
    inset-inline-start: auto;
    inset-inline-end: 0;
  }

  :root[fg-autohide-tabs][fg-tabs-opposite] #firegila-tabs-sensor {
    inset-inline-start: auto;
    inset-inline-end: 0;
  }

  :root[fg-autohide-tabs][fg-tabs-opposite]:has(#sidebar-container[sidebar-positionend]) #firegila-tabs-sensor {
    inset-inline-start: 0;
    inset-inline-end: auto;
  }

  :root:has(#sidebar-container[hidden]) #firegila-tabs-sensor {
    display: none;
  }
}

/* Tabs on the opposite side of the sidebar. Stock writes order inline as
 * 1..N on every child, so the values here sit outside that range and important
 * beats the inline style. Auto-hide only needs the inset flipped. */

/* The column carries the strip surface in every mode now, so the tab fill and
 * border keep the same separation as before. */

:root[fg-tabs-opposite] .tabbrowser-tab:not([selected], [multiselected]) > .tab-stack > .tab-background {
  border-color: light-dark(#c4c4c4, #2e2e2e);
}

/* Not on hover, so the stock hover rule still wins. */

:root[fg-tabs-opposite] .tabbrowser-tab:not([selected], [multiselected]):not(:hover) > .tab-stack > .tab-background {
  background-color: light-dark(#ededed, #1f1f1f);
}

@media -moz-pref("sidebar.verticalTabs") {
  :root[fg-tabs-opposite]:not([lwtheme]) {
    --tab-background-color-hover: light-dark(#cccccc, #383838);
  }
}

:root[fg-tabs-opposite]:not(:has(#sidebar-container[sidebar-positionend])) #vertical-tabs-container {
  order: 9999 !important;
}

:root[fg-tabs-opposite]:has(#sidebar-container[sidebar-positionend]) #vertical-tabs-container {
  order: -1 !important;
}

:root[fg-autohide-tabs][fg-tabs-opposite] #vertical-tabs-container {
  inset-inline-start: auto;
  inset-inline-end: 0;
}

:root[fg-autohide-tabs][fg-tabs-opposite]:has(#sidebar-container[sidebar-positionend]) #vertical-tabs-container {
  inset-inline-start: 0;
  inset-inline-end: auto;
}

/* Website panels. Header above the panel browser, plus the add popup. The
 * header only shows for saved sites. Built in panels bring their own. */

#sidebar-box > .sidebar-browser-stack {
  flex: 1;
  min-height: 0;
}

#firegila-webpanel-header {
  display: flex;
  align-items: center;
  gap: var(--space-small);
  padding-inline: var(--space-large);
  padding-block: var(--space-small);
  -moz-context-properties: fill;
  fill: currentColor;
}

#firegila-webpanel-header[hidden],
.firegila-webpanel-browser[hidden] {
  display: none;
}

#firegila-webpanel-title {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 15px;
  font-weight: 600;
}

#firegila-webpanel-header > toolbarbutton {
  appearance: none;
  min-width: 24px;
  min-height: 24px;
  padding: 4px;
  border: 0;
  border-radius: var(--border-radius-medium);
  -moz-context-properties: fill;
  fill: currentColor;
}

#firegila-webpanel-header > toolbarbutton:hover:not([disabled]) {
  background-color: var(--fg-hover);
}

#firegila-webpanel-header > toolbarbutton:hover:active:not([disabled]) {
  background-color: var(--fg-active);
}

#firegila-webpanel-header > toolbarbutton[disabled] {
  opacity: 0.5;
}

#firegila-webpanel-back {
  list-style-image: url("chrome://browser/skin/back.svg");
}

#firegila-webpanel-forward {
  list-style-image: url("chrome://browser/skin/forward.svg");
}

#firegila-webpanel-reload {
  list-style-image: url("chrome://global/skin/icons/reload.svg");
}

#firegila-webpanel-close {
  list-style-image: url("chrome://global/skin/icons/close.svg");
}

/* Pressed feedback. XUL toolbarbuttons paint the face and the glyph in one
 * box, so a scale would shrink the whole button. They keep the stock
 * background press. Only the close button and design system icons scale. */

@media (prefers-reduced-motion: no-preference) {
  .tab-close-button,
  .button-icon {
    transition: transform 120ms cubic-bezier(0.3, 0, 0.2, 1);
  }

  .tab-close-button:active,
  button:active > .button-icon {
    transform: scale(0.93);
  }
}

.firegila-webpanel-browser {
  flex: 1;
}

#firegila-webpanel-add-popup,
#firegila-workspace-name-popup,
#firegila-workspace-confirm-popup {
  --panel-padding: 12px;
  --panel-background-color: var(--fg-bg);
  --panel-border-color: var(--fg-border);
}

.fg-webpanel-form {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 8px;
  width: 16em;
}

.fg-webpanel-form > label:first-child {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

#firegila-webpanel-url,
#firegila-webpanel-name,
#firegila-workspace-name-input {
  box-sizing: border-box;
  height: 32px;
  min-height: 32px;
  margin: 0;
  padding: 2px 10px;
  border: 1px solid var(--fg-border);
  border-radius: var(--border-radius-medium);
  background-color: var(--fg-bg-3);
  color: var(--fg-text);
}

#firegila-webpanel-url:focus,
#firegila-webpanel-name:focus,
#firegila-workspace-name-input:focus {
  border-color: AccentColor;
  outline: none;
}

#firegila-webpanel-url::placeholder,
#firegila-webpanel-name::placeholder,
#firegila-workspace-name-input::placeholder {
  color: var(--fg-text-dim);
}

/* The stock panel buttons use the native widget colors. Paint them from the
 * palette so the popups match the rest of the browser. Both buttons share the
 * row width, so the pair spans the form. */

.fg-webpanel-form button {
  appearance: none;
  flex: 1 1 0;
  min-width: 0;
  height: 32px;
  margin: 0;
  padding: 0 12px;
  border: 1px solid var(--fg-border);
  border-radius: var(--border-radius-medium);
  background-color: var(--fg-bg-3);
  color: var(--fg-text);
  font: inherit;
  font-weight: 500;
}

.fg-webpanel-form button:not(.primary):hover {
  background-color: var(--fg-hover);
}

.fg-webpanel-form button:not(.primary):active {
  background-color: var(--fg-active);
}

.fg-webpanel-form button.primary {
  border-color: AccentColor;
  background-color: AccentColor;
  color: AccentColorText;
}

.fg-webpanel-form button.primary:hover {
  border-color: color-mix(in srgb, AccentColor 85%, black);
  background-color: color-mix(in srgb, AccentColor 85%, black);
}

.fg-webpanel-form button.primary:active {
  border-color: color-mix(in srgb, AccentColor 72%, black);
  background-color: color-mix(in srgb, AccentColor 72%, black);
}

.fg-webpanel-form button:focus-visible {
  outline: 1px solid AccentColor;
  outline-offset: 1px;
}

.fg-webpanel-error {
  margin: 0;
  color: light-dark(#b3261e, #ffb4ab);
}

.fg-webpanel-buttons {
  display: flex;
  flex: 0 0 auto;
  align-items: stretch;
  gap: 8px;
  width: 100%;
  margin: 0;
}

/* Workspace switcher. A tab sized pill in the tab bar, a full width row above
 * the vertical tabs. The fill, border and radius are the background tab set,
 * so the two controls read as one row. */

#firegila-workspaces {
  appearance: none;
  -moz-appearance: none;
  -moz-box-orient: horizontal;
  box-orient: horizontal;
  align-items: center;
  flex: 0 0 auto;
  box-sizing: border-box;
  width: 120px;
  height: 32px;
  min-height: 32px;
  margin-block: 4px;
  margin-inline: 4px 2px;
  padding: 0 8px;
  border: 1px solid light-dark(#d0d0d0, #232323);
  border-radius: 8px;
  background-color: light-dark(#ededed, #1d1d1d);
  color: var(--fg-text);
}

#firegila-workspaces:hover {
  background-color: light-dark(#d9d9d9, #383838);
}

/* Same shift as the background tabs when the strip sits on the other side. */

:root[fg-tabs-opposite] .toolbar-items > #firegila-workspaces {
  background-color: light-dark(#ededed, #1f1f1f);
}

:root[fg-tabs-opposite] .toolbar-items > #firegila-workspaces:hover {
  background-color: light-dark(#d9d9d9, #383838);
}

/* The stock icon slot is empty here. Hide it so the label and the chevron sit
 * between the two paddings without an extra leading gap. */

#firegila-workspaces > .toolbarbutton-icon {
  display: none;
}

#firegila-workspaces > .toolbarbutton-text {
  display: block;
  flex: 1 1 auto;
  min-width: 0;
  margin: 0;
  padding: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: start;
}

/* Chevron. A real image in currentColor, so it follows the text in both
 * modes. The box is ordered after the label. */

#firegila-workspaces > .firegila-workspace-arrow-box {
  order: 1;
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  margin-inline-start: 6px;
}

/* One audio dot style everywhere: 6px, accent color, round. On the button it
 * sits in the row before the chevron, centered with the label. */

#firegila-workspaces .firegila-workspace-audio {
  display: none;
  flex: 0 0 auto;
  width: 6px;
  height: 6px;
  margin-inline-end: 6px;
  border-radius: 50%;
  background-color: AccentColor;
}

#firegila-workspaces[firegila-audio] .firegila-workspace-audio {
  display: block;
}

#firegila-workspaces .firegila-workspace-arrow {
  width: 12px;
  height: 12px;
  -moz-context-properties: fill;
  fill: currentColor;
  opacity: 0.65;
  list-style-image: url("chrome://global/skin/icons/arrow-down.svg");
}

#vertical-tabs-container > #firegila-workspaces {
  flex: 0 0 auto;
  width: calc(100% - 4px);
  max-width: none;
  margin: 2px;
  padding-inline: 8px;
  border: 1px solid light-dark(#d0d0d0, #232323);
  border-radius: 8px;
  background-color: light-dark(#ededed, #1d1d1d);
}

#vertical-tabs-container > #firegila-workspaces:hover {
  background-color: light-dark(#d9d9d9, #383838);
}

/* The workspace list uses the app surfaces, not the GTK menu colors, so it
 * matches the popups that belong to Firegila. */

#firegila-workspace-menu {
  --panel-padding: 4px;
  --panel-background-color: var(--fg-bg);
  --panel-border-color: var(--fg-border);
  --panel-text-color: var(--fg-text);
  /* Script replaces this with the live button width, so the list is exactly
   * as wide as the button in both tab modes. */
  --panel-width: 120px;
  --menuitem-border-radius: 6px;
  --menuitem-padding: 5px 10px;
}

/* No gutter. The radio marker and the icon slot are not drawn, so names and
 * commands all start at the same padding. */

#firegila-workspace-menu > menuitem > .menu-icon {
  display: none;
}

#firegila-workspace-menu > menuitem {
  min-height: 32px;
}

#firegila-workspace-menu > menuitem[_moz-menuactive]:not([disabled]) {
  background-color: var(--fg-hover);
  color: var(--fg-text);
}

#firegila-workspace-menu > menuseparator {
  margin-block: 4px;
}

/* Current workspace: bold text and a check at the end. The accent stays on the
 * check only, because accent text on a menu surface can be too low contrast. */

#firegila-workspace-menu .firegila-workspace-item[checked] {
  font-weight: 600;
}

#firegila-workspace-menu .firegila-workspace-item[checked]::after {
  content: "";
  order: 3;
  flex: 0 0 auto;
  width: 14px;
  height: 14px;
  margin-inline-start: 6px;
  -moz-context-properties: fill;
  fill: AccentColor;
  background-image: url("chrome://global/skin/icons/check.svg");
  background-position: center;
  background-repeat: no-repeat;
  background-size: 14px 14px;
}

/* Audio dot in a row, same size and color as the button and the sidebar. */

#firegila-workspace-menu .firegila-workspace-item[firegila-audio]::before {
  content: "";
  order: 2;
  flex: 0 0 auto;
  width: 6px;
  height: 6px;
  margin-inline-start: 6px;
  border-radius: 50%;
  background-color: AccentColor;
}

/* Sidebar audio dot. Same 6px accent circle as the workspace button and the
 * website list, so audio reads the same wherever it is shown. */

#sidebar-button {
  position: relative;
}

#sidebar-button[firegila-audio]::after {
  content: "";
  position: absolute;
  inset-block-start: 5px;
  inset-inline-end: 5px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: AccentColor;
  pointer-events: none;
}

.fg-webpanel-list moz-button[attention] {
  --button-attention-dot-color: AccentColor;
  --button-badge-size: 6px;
}

/* The unified extensions panel is a plain fade. Stock slides it 70px with the
 * toolbar curve, which reads as a bounce next to the other menus. */
#unified-extensions-panel {
  transition-property: opacity !important;
  transition-duration: var(--fg-motion-fast, 120ms) !important;
  transition-timing-function: var(--fg-ease, ease) !important;
  transform: none !important;
}
"""

SB_MAIN_CSS = """
/* Strip buttons are the same square as a nav bar button. The pad is whatever
 * is left between strip and face, so they stay in step at any density. */

:host {
  --fg-sb-button-pad: calc((var(--fg-navbar-height, var(--tab-min-height))
    - var(--fg-navbar-button-size, 32px)) / 2);
}

.actions-list > moz-button:not(.tools-overflow),
.actions-list > moz-button:not(.tools-overflow):first-of-type,
.actions-list > moz-button:not(.tools-overflow):last-of-type {
  --button-outer-padding-inline: var(--fg-sb-button-pad);
  --button-outer-padding-block: var(--fg-sb-button-pad);
  --button-outer-padding-block-start: var(--fg-sb-button-pad);
  --button-outer-padding-block-end: var(--fg-sb-button-pad);
}

/* Divider above the tool buttons. It was the drag handle for a section that is
 * not resizable here, so remove it. */

#sidebar-tools-and-extensions-splitter {
  display: none !important;
}

/* Website panels. A divider, one button per saved site, then the add button.
 * The list reuses .actions-list, so the strip padding and hover come free. */

.fg-webpanel-divider {
  align-self: stretch;
  flex-shrink: 0;
  border-top: 1px solid var(--fg-border);
  margin-inline: var(--space-small);
  margin-block: var(--space-xxsmall);
}

/* The tools fill the strip height and the customize button stays at the
 * bottom, below the saved websites. */

.buttons-wrapper {
  flex: 1 1 auto;
  min-height: 0;
}

.buttons-wrapper > .actions-list:not(.bottom-actions):not(.overflow-button) {
  flex: 1 1 auto;
  min-height: 0;
}

.bottom-actions {
  flex-shrink: 0;
}

.wrapper {
  grid-template-rows: 1fr;
}
"""

SB_BOOTSTRAP_JS = """
// Reads the nav bar height, button size and motion tokens off the live page
// and publishes them for the sidebar CSS and animation. Neither metric has a
// token, so ResizeObserver covers density and window changes.
(function () {
  const PANEL_WIDTH_PREF = "firegila.sidebar.width";
  const AUTO_HIDE_PREF = "firegila.sidebar.autoHideTabs";
  const OPPOSITE_PREF = "firegila.sidebar.tabsOpposite";
  const DEFAULT_BOOKMARKS_PREF = "firegila.migration.defaultBookmarks";
  const STOCK_DEFAULT_BOOKMARKS = [
    ["Get Help", "https://support.mozilla.org/products/firefox"],
    [
      "Customize Firefox",
      "https://support.mozilla.org/kb/customize-firefox-controls-buttons-and-toolbars",
    ],
    ["Get Involved", "https://www.mozilla.org/contribute/"],
    ["About Us", "https://www.mozilla.org/about/"],
  ];

  // Profiles made before the default bookmarks patch still carry the four
  // Mozilla defaults in a "Mozilla Firefox" folder under the bookmarks menu.
  // Remove exactly those once, so upgrades match a fresh install. User
  // bookmarks are left alone, the folder is dropped only when it ends empty.
  async function migrateDefaultBookmarks() {
    if (Services.prefs.getBoolPref(DEFAULT_BOOKMARKS_PREF, false)) {
      return;
    }
    try {
      const { PlacesUtils } = ChromeUtils.importESModule(
        "resource://gre/modules/PlacesUtils.sys.mjs"
      );
      const bookmarks = PlacesUtils.bookmarks;

      const children = async guid => {
        const nodes = [];
        await bookmarks.fetch({ parentGuid: guid }, node => nodes.push(node));
        return nodes;
      };

      const stockFolders = [];
      const removeStock = async guid => {
        for (const node of await children(guid)) {
          if (node.type === bookmarks.TYPE_FOLDER) {
            if (node.title === "Mozilla Firefox") {
              stockFolders.push(node.guid);
            }
            if (!(await removeStock(node.guid))) {
              return false;
            }
            continue;
          }
          if (node.type !== bookmarks.TYPE_BOOKMARK || !node.url) {
            continue;
          }
          const stock = STOCK_DEFAULT_BOOKMARKS.some(
            ([title, url]) =>
              node.title === title && node.url.href.startsWith(url)
          );
          if (!stock) {
            continue;
          }
          try {
            await bookmarks.remove(node.guid);
          } catch (e) {
            // Places is busy. Retry on the next start.
            return false;
          }
        }
        return true;
      };

      for (const guid of [bookmarks.menuGuid, bookmarks.toolbarGuid]) {
        if (!(await removeStock(guid))) {
          return;
        }
      }
      for (const guid of stockFolders) {
        if ((await children(guid)).length) {
          continue;
        }
        try {
          await bookmarks.remove(guid);
        } catch (e) {
          return;
        }
      }
      Services.prefs.setBoolPref(DEFAULT_BOOKMARKS_PREF, true);
    } catch (e) {
      // Places is not ready yet. Retry on the next start.
    }
  }

  function publishMotion() {
    const computed = getComputedStyle(document.documentElement);
    const read = (name, fallback) =>
      computed.getPropertyValue(name).trim() || fallback;
    window.__fgMotion = {
      duration: parseFloat(read("--fg-motion-base", "180ms")) || 180,
      easing: read("--fg-ease", "ease"),
    };
  }

  // Stock does not persist the panel width, restore it here. With nothing
  // stored nothing is applied, so the default stays a starting point.
  function persistPanelWidth() {
    const box = document.getElementById("sidebar-box");
    const splitter = document.getElementById("sidebar-splitter");
    if (!box || !splitter) {
      return;
    }
    const stored = Services.prefs.getIntPref(PANEL_WIDTH_PREF, 0);
    if (stored > 0) {
      box.style.setProperty("--fg-panel-width", `${stored}px`);
    }
    // command fires only at the end of a real drag. The transitions change the
    // box width every frame, so watching the box instead would store those.
    // The property is the live value from here on, so the stylesheet falls
    // back to it instead of the default.
    splitter.addEventListener("command", () => {
      const width = Math.round(box.getBoundingClientRect().width);
      if (width > 0) {
        box.style.setProperty("--fg-panel-width", `${width}px`);
        Services.prefs.setIntPref(PANEL_WIDTH_PREF, width);
      }
    });
  }

  function publishNavbarMetrics() {
    const navBar = document.getElementById("nav-bar");
    // The face users see, from a real toolbar button rather than a plain icon.
    const navIcon = [
      "back-button",
      "home-button",
      "stop-reload-button",
      "unified-extensions-button",
      "sidebar-button",
    ]
      .map(id => document.getElementById(id))
      .filter(Boolean)
      .map(button => button.querySelector(".toolbarbutton-icon"))
      .find(icon => icon && icon.getBoundingClientRect().width > 0);
    if (!navBar) {
      return;
    }
    const style = document.documentElement.style;
    const sync = () => {
      style.setProperty(
        "--fg-navbar-height",
        `${navBar.getBoundingClientRect().height}px`
      );
      if (navIcon) {
        style.setProperty(
          "--fg-navbar-button-size",
          `${navIcon.getBoundingClientRect().width}px`
        );
      }
    };
    sync();
    new ResizeObserver(sync).observe(navBar);
  }
  // The launcher never expands here, so the tab strip would render collapsed
  // icons. Mark it expanded directly while vertical tabs are on, which covers
  // startup and flipping the mode at runtime.
  function syncTabStripExpanded() {
    const tabs = document.getElementById("tabbrowser-tabs");
    if (!tabs) {
      return;
    }
    tabs.toggleAttribute(
      "expanded",
      Services.prefs.getBoolPref("sidebar.verticalTabs", false)
    );
  }

  function start() {
    publishMotion();
    publishNavbarMetrics();
    persistPanelWidth();
    syncTabStripExpanded();
    migrateDefaultBookmarks();
    watchSidebarHidden();
    watchRevealLeave();
    watchEdgeSensor();
    watchTabsContextMenu();
    Services.prefs.addObserver("sidebar.verticalTabs", syncTabStripExpanded);
  }

  // Auto-hide tabs. The column floats at the window edge, so a reveal is one
  // attribute flip and the stylesheet animates the width. The state is set
  // before the sidebar renders, so the first frame is already collapsed.
  function syncAutoHide() {
    const on = Services.prefs.getBoolPref(AUTO_HIDE_PREF, false);
    document.documentElement.toggleAttribute("fg-autohide-tabs", on);
    if (!on) {
      document.documentElement.removeAttribute("fg-tabs-revealed");
    }
  }

  // The column switches sides by attribute. The order and the edge checks read
  // it, so a change also drops a reveal left over from the old side.
  function syncTabsSide() {
    document.documentElement.toggleAttribute(
      "fg-tabs-opposite",
      Services.prefs.getBoolPref(OPPOSITE_PREF, false)
    );
    setRevealed(false);
  }

  function sidebarOnTheRight() {
    const strip = document.getElementById("sidebar-container");
    return strip ? strip.hasAttribute("sidebar-positionend") : false;
  }

  function tabsOnTheRight() {
    const opposite = document.documentElement.hasAttribute("fg-tabs-opposite");
    return sidebarOnTheRight() !== opposite;
  }

  function setRevealed(on) {
    document.documentElement.toggleAttribute("fg-tabs-revealed", on);
  }

  // Cached so the pointer handler never forces a layout. The width is a fixed
  // token, the same one the stylesheet uses.
  let tabsWidth = 220;

  function readTabsWidth() {
    tabsWidth =
      parseFloat(
        getComputedStyle(document.documentElement).getPropertyValue(
          "--fg-tabs-width"
        )
      ) || 220;
  }

  function onPointerMove(event) {
    const root = document.documentElement;
    if (
      !root.hasAttribute("fg-autohide-tabs") ||
      !root.hasAttribute("fg-tabs-revealed")
    ) {
      return;
    }
    const strip = document.getElementById("sidebar-container");
    // Hidden sidebar takes the tabs with it.
    if (!strip || strip.hidden) {
      return;
    }
    const target = event.originalTarget || event.target;
    if (target?.ownerDocument && target.ownerDocument !== document) {
      return;
    }
    const x = pointerX(event);
    const onRight = tabsOnTheRight();
    const past = onRight ? x < window.innerWidth - tabsWidth : x > tabsWidth;
    if (past) {
      setRevealed(false);
    }
  }

  // Screen coordinates are global, so they are the same no matter which
  // document produced the event. Stock sidebar panels are chrome pages and
  // report mousemove with panel relative clientX, which made the old edge
  // test fire at the strip. Normalize against the window origin instead.
  function pointerX(event) {
    const inner = window.mozInnerScreenX;
    if (typeof inner === "number" && Number.isFinite(event.screenX)) {
      return event.screenX - inner;
    }
    return event.clientX;
  }

  // The edge sensor is the only reveal trigger. It is a chrome element in the
  // outer 3px of the window, so events from an open sidebar panel cannot
  // reach it.
  function watchEdgeSensor() {
    const sensor = document.getElementById("firegila-tabs-sensor");
    if (!sensor) {
      return;
    }
    sensor.addEventListener("mousemove", () => {
      const root = document.documentElement;
      if (!root.hasAttribute("fg-autohide-tabs")) {
        return;
      }
      const strip = document.getElementById("sidebar-container");
      if (strip && !strip.hidden) {
        setRevealed(true);
      }
    });
  }

  // Hiding the sidebar clears the reveal, so showing it again starts collapsed.
  function watchSidebarHidden() {
    const strip = document.getElementById("sidebar-container");
    if (!strip) {
      return;
    }
    new MutationObserver(() => {
      if (strip.hidden) {
        setRevealed(false);
      }
    }).observe(strip, { attributes: true, attributeFilter: ["hidden"] });
    new MutationObserver(() => setRevealed(false)).observe(strip, {
      attributes: true,
      attributeFilter: ["sidebar-positionend"],
    });
  }

  // Leaving the column hides it. A content document does not report mousemove
  // to this window, so the edge sensor alone would leave the column open while
  // the pointer sits in the page or in an open panel.
  function watchRevealLeave() {
    const tabs = document.getElementById("vertical-tabs-container");
    if (tabs) {
      tabs.addEventListener("mouseleave", () => setRevealed(false));
    }
  }

  // The sidebar menu on the tabs column background. Tab items carry their own
  // menu, so those are left alone. Stock only wires the strip.
  function watchTabsContextMenu() {
    const container = document.getElementById("vertical-tabs-container");
    if (!container) {
      return;
    }
    container.addEventListener("contextmenu", event => {
      let node = event.explicitOriginalTarget || event.target;
      while (node && node !== container) {
        if (
          node.classList?.contains("tabbrowser-tab") ||
          node.id === "vertical-tabs-newtab-button" ||
          node.id === "tabs-newtab-button"
        ) {
          return;
        }
        node = node.parentNode;
      }
      const main = document.querySelector("sidebar-main");
      const menu = document.getElementById("sidebar-context-menu");
      if (
        !main ||
        !menu ||
        typeof main.updateSidebarContextMenuItems !== "function"
      ) {
        return;
      }
      event.preventDefault();
      main.updateSidebarContextMenuItems();
      menu.openPopupAtScreen(event.screenX, event.screenY, true);
    });
  }

  syncAutoHide();
  syncTabsSide();
  readTabsWidth();
  Services.prefs.addObserver(AUTO_HIDE_PREF, syncAutoHide);
  Services.prefs.addObserver(OPPOSITE_PREF, syncTabsSide);
  window.addEventListener("mousemove", onPointerMove);

  if (document.readyState === "complete") {
    start();
  } else {
    window.addEventListener("load", start, { once: true });
  }
})();
"""


SB_ANIM_JS = """
// Sidebar transitions animate widths, so the page reflows every frame. Stock
// pins elements and translates them, which slides and then jumps.
// Timing comes from window.__fgMotion, the same tokens the CSS uses.
(function () {
  const stockAnimateSidebarContainer =
    SidebarController._animateSidebarContainer;

  function snapshot(el) {
    return el.getBoundingClientRect().width;
  }

  // Holds the element in layout while it animates. Display is set even when it
  // is not hidden yet, because stock flips hidden right after calling us and
  // the toggle would otherwise drop it to display none for a frame.
  function hold(el) {
    el.style.display = "flex";
    el.style.minWidth = "0";
    el.style.maxWidth = "none";
    el.style.overflow = "clip";
    el.style.contain = "layout paint";
  }

  function release(el) {
    el.style.display = "";
    el.style.width = "";
    el.style.minWidth = "";
    el.style.maxWidth = "";
    el.style.overflow = "";
    el.style.contain = "";
  }

  // The panel content is held at its resting width so it is revealed, not
  // squashed. Splitter drags still reflow, this only runs during transitions.
  function holdContent(box, width) {
    if (!box) {
      return;
    }
    for (const el of box.children) {
      el.style.minInlineSize = `${width}px`;
    }
  }

  function releaseContent(box) {
    if (!box) {
      return;
    }
    for (const el of box.children) {
      el.style.minInlineSize = "";
      el.style.opacity = "";
    }
  }

  async function runTransition(ctrl) {
    const tabbox = document.getElementById("tabbrowser-tabbox");
    const tabs = document.getElementById("vertical-tabs-container");
    const elements = [ctrl.sidebarContainer, tabs, ctrl._box, ctrl._splitter].filter(
      Boolean
    );

    // These four carry the attribute stock CSS hangs its own transitions off.
    const marked = [
      ctrl.sidebarContainer,
      ctrl.sidebarMain,
      ctrl._box,
      tabbox,
    ];
    const mark = on => {
      for (const el of marked) {
        el?.toggleAttribute("sidebar-ongoing-animations", on);
      }
    };

    const clear = () => {
      elements.forEach(release);
      releaseContent(ctrl._box);
      releaseContent(tabs);
      mark(false);
    };

    // Read the visual truth first, while any running transition still applies.
    // A quick second toggle then starts from where the eye is, not from a
    // stylesheet value, so reversals do not jump.
    const from = elements.map(snapshot);

    // Whatever is still running is stale. Drop it now that its geometry
    // is captured.
    ctrl._ongoingAnimations.forEach(a => a.cancel());
    ctrl._ongoingAnimations = [];
    clear();

    // Freeze everything at its pre-toggle width. The content freezes with the
    // box, or it snaps by the splitter width on the first frame.
    for (let i = 0; i < elements.length; ++i) {
      hold(elements[i]);
      elements[i].style.width = `${from[i]}px`;
      if (elements[i] === ctrl._box) {
        holdContent(ctrl._box, from[i]);
      }
      if (elements[i] === tabs && tabs) {
        holdContent(tabs, from[i]);
      }
    }

    // One microtask lets stock's toggles land. The destination widths are CSS
    // driven, so a forced layout reads them with no need to wait on lit, and
    // the animation starts on the next frame instead of after the render.
    await Promise.resolve();

    // The pin has to come off before reading the destination. A hidden box
    // still measures at its old width, so from and to come out equal and
    // there is nothing to animate. No paint happens in between.
    elements.forEach(release);
    releaseContent(ctrl._box);
    releaseContent(tabs);
    const to = elements.map(snapshot);

    // Geometry is settled. From here a call is a new transition.
    ctrl._fgReading = false;

    // Nothing changes, so there is nothing to animate. Skip the markers too,
    // so a no-op call leaves no trace on the page.
    if (from.every((width, i) => width === to[i])) {
      return;
    }

    const motion = window.__fgMotion || {};
    const options = {
      duration: motion.duration ?? 180,
      easing: motion.easing ?? "ease",
      fill: "both",
    };

    const animations = [];
    for (let i = 0; i < elements.length; ++i) {
      if (from[i] === to[i]) {
        continue;
      }
      hold(elements[i]);
      if (elements[i] === ctrl._box) {
        holdContent(ctrl._box, Math.max(from[i], to[i]));
        // Fade the content with the box, so text is never cut mid-word at
        // full opacity. The border lives on the box itself and stays visible.
        // Start is read live, so a reversal mid-fade continues from there.
        const end = to[i] === 0 ? 0 : 1;
        for (const child of ctrl._box.children) {
          if (!child.getClientRects().length) {
            continue;
          }
          const start = parseFloat(getComputedStyle(child).opacity) || 0;
          if (start !== end) {
            animations.push(
              child.animate([{ opacity: start }, { opacity: end }], options)
            );
          }
        }
      }
      if (elements[i] === tabs && tabs) {
        holdContent(tabs, Math.max(from[i], to[i]));
        // No border to preserve here, so the column itself fades.
        const end = to[i] === 0 ? 0 : 1;
        const start = parseFloat(getComputedStyle(tabs).opacity) || 0;
        if (start !== end) {
          animations.push(
            tabs.animate([{ opacity: start }, { opacity: end }], options)
          );
        }
      }
      animations.push(
        elements[i].animate(
          [{ width: `${from[i]}px` }, { width: `${to[i]}px` }],
          options
        )
      );
    }
    ctrl._ongoingAnimations = animations;

    mark(true);

    await Promise.allSettled(animations.map(a => a.finished));

    if (ctrl._ongoingAnimations === animations) {
      ctrl._ongoingAnimations = [];
      clear();
    }
    // Release before cancel, so each element falls back to its stylesheet
    // width. A finished animation with fill both would otherwise pin the
    // value it stopped at.
    animations.forEach(a => a.cancel());
  }

  SidebarController._animateSidebarContainer = function () {
    // show() and hide() call back in during the same tick. Fold those calls
    // into the running transition and hand back the same promise.
    if (this._fgReading) {
      return this._fgDone || Promise.resolve();
    }
    // Expand on hover floats over the page without changing layout, so stock
    // still handles it.
    if (document.documentElement.hasAttribute("sidebar-expand-on-hover")) {
      return stockAnimateSidebarContainer.call(this);
    }

    this._fgReading = true;
    const done = runTransition(this);
    this._fgDone = done;
    const settle = () => {
      this._fgReading = false;
      if (this._fgDone === done) {
        this._fgDone = null;
      }
    };
    done.then(settle, settle);
    return done;
  };
})();
"""


# Website panels. Saved sites get a strip button and their own content browser
# next to the stock sidebar browser. The strip block is rendered by
# sidebar-main through window.FiregilaWebPanels.
SB_WEBPANELS_JS = """
(function () {
  const ENABLED_PREF = "firegila.sidebar.webPanelsEnabled";
  const PANELS_PREF = "firegila.sidebar.webPanels";
  const MAX_PANELS = 8;
  const MAX_URL = 2048;
  const MAX_LABEL = 60;
  const MAX_ICON = 2048;
  const HEAD_LIMIT = 262144;
  const PANEL_PREFIX = "fg-panel-";
  const PANEL_ID_RE =
    /^fg-panel-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

  const icons = new Map();
  const triedIcons = new Set();
  const browsers = new Map();
  const audioPanels = new Set();
  const l10n = new Localization(["browser/sidebar.ftl"], true);
  let panels = [];
  let shownId = null;
  let contextId = null;
  let addTooltip = "";
  let wired = false;
  let navTimer = null;
  let hideTimer = null;
  let addAnchor = null;

  function controller() {
    return window.SidebarController;
  }

  function prefEnabled() {
    return Services.prefs.getBoolPref(ENABLED_PREF, false);
  }

  function message(id) {
    try {
      return l10n.formatValueSync(id) || "";
    } catch (e) {
      return "";
    }
  }

  function cleanLabel(raw) {
    return String(raw || "")
      .replace(/[\\u0000-\\u001f\\u007f]+/g, " ")
      .replace(/\\s+/g, " ")
      .trim()
      .slice(0, MAX_LABEL);
  }

  function hostLabel(url) {
    try {
      return new URL(url).hostname.replace(/^www\\./, "");
    } catch (e) {
      return url;
    }
  }

  // Accepts http and https only. A missing scheme is read as https.
  function normalize(raw) {
    let value = String(raw || "").trim();
    if (!value || value.length > MAX_URL) {
      return null;
    }
    if (!/^[a-z][a-z0-9+.-]*:/i.test(value)) {
      value = "https://" + value;
    }
    let url;
    try {
      url = new URL(value);
    } catch (e) {
      return null;
    }
    if (url.protocol !== "http:" && url.protocol !== "https:") {
      return null;
    }
    if (!url.hostname || url.username || url.password) {
      return null;
    }
    return { url: url.href, label: hostLabel(url.href) };
  }

  function readPanels() {
    let raw;
    try {
      raw = JSON.parse(Services.prefs.getStringPref(PANELS_PREF, "[]"));
    } catch (e) {
      return [];
    }
    if (!Array.isArray(raw)) {
      return [];
    }
    const list = [];
    const seen = new Set();
    const ids = new Set();
    for (const entry of raw) {
      const normalized = normalize(entry?.url);
      if (
        !normalized ||
        seen.has(normalized.url) ||
        list.length >= MAX_PANELS
      ) {
        continue;
      }
      seen.add(normalized.url);
      let id = entry.id;
      if (
        typeof id !== "string" ||
        !PANEL_ID_RE.test(id) ||
        ids.has(id)
      ) {
        id = PANEL_PREFIX + crypto.randomUUID();
      }
      ids.add(id);
      list.push({
        id,
        url: normalized.url,
        label: cleanLabel(entry.label) || normalized.label,
        icon: isIconUrl(entry.icon) ? entry.icon : "",
      });
    }
    return list;
  }

  function writePanels(list) {
    Services.prefs.setStringPref(PANELS_PREF, JSON.stringify(list));
  }

  function panelById(id) {
    return panels.find(panel => panel.id === id) || null;
  }

  function isIconUrl(value) {
    if (typeof value !== "string" || value.length > MAX_ICON) {
      return false;
    }
    return /^https?:\\/\\//i.test(value) || /^data:image\\//i.test(value);
  }

  function iconFor(panel) {
    return icons.get(panel.id) || panel.icon || `page-icon:${panel.url}`;
  }

  function actions() {
    return panels.map(panel => ({
      view: panel.id,
      tooltiptext: panel.label,
      iconUrl: iconFor(panel),
      attention: audioPanels.has(panel.id),
      webPanel: true,
    }));
  }

  // Rebuilds the controller entries from the pref. A panel that lost its
  // record, or the whole feature going off, closes the open panel.
  function applyPrefs() {
    const list = readPanels();
    const map = controller().sidebars;
    for (const [id, sidebar] of map) {
      if (sidebar.webPanel) {
        map.delete(id);
      }
    }
    panels = list;
    if (prefEnabled()) {
      for (const panel of panels) {
        map.set(panel.id, {
          webPanel: true,
          name: panel.id,
          label: panel.label,
          title: panel.label,
          url: "about:blank",
          iconUrl: iconFor(panel),
        });
      }
    }
    const current = controller().currentID;
    if (current && !map.has(current)) {
      controller().hide({ dismissPanel: true });
    }
    const keep = new Set(prefEnabled() ? panels.map(panel => panel.id) : []);
    for (const [id, browser] of browsers) {
      if (!keep.has(id)) {
        browser.remove();
        browsers.delete(id);
        audioPanels.delete(id);
      }
    }
    for (const id of icons.keys()) {
      if (!keep.has(id)) {
        icons.delete(id);
      }
    }
    for (const id of triedIcons) {
      if (!keep.has(id)) {
        triedIcons.delete(id);
      }
    }
    updateSidebarAudio();
    window.dispatchEvent(new CustomEvent("SidebarItemChanged"));
  }

  function updateSidebarAudio() {
    const button = document.getElementById("sidebar-button");
    if (button) {
      button.toggleAttribute("firegila-audio", audioPanels.size > 0);
    }
  }

  function setPanelAudio(id, on) {
    if (audioPanels.has(id) === on) {
      return;
    }
    if (on) {
      audioPanels.add(id);
    } else {
      audioPanels.delete(id);
    }
    updateSidebarAudio();
    window.dispatchEvent(new CustomEvent("SidebarItemChanged"));
  }

  function elements() {
    return {
      box: document.getElementById("sidebar-box"),
      header: document.getElementById("firegila-webpanel-header"),
      title: document.getElementById("firegila-webpanel-title"),
      back: document.getElementById("firegila-webpanel-back"),
      forward: document.getElementById("firegila-webpanel-forward"),
      reload: document.getElementById("firegila-webpanel-reload"),
      close: document.getElementById("firegila-webpanel-close"),
      stack: document.querySelector(".sidebar-browser-stack"),
      stock: document.getElementById("sidebar"),
    };
  }

  function activeBrowser() {
    return shownId ? browsers.get(shownId) || null : null;
  }

  // One content browser per panel, created on first open and kept loaded after
  // that. Closing the panel only hides it, so state, history and scroll stay.
  function browserFor(panel) {
    const existing = browsers.get(panel.id);
    if (existing) {
      return existing;
    }
    const stack = elements().stack;
    if (!stack) {
      return null;
    }
    const browser = document.createXULElement("browser");
    browser.className = "firegila-webpanel-browser";
    browser.setAttribute("type", "content");
    browser.setAttribute("remote", "true");
    browser.setAttribute("remoteType", "web");
    browser.setAttribute("maychangeremoteness", "true");
    browser.setAttribute("disablefullscreen", "true");
    browser.setAttribute("tooltip", "aHTMLTooltip");
    browser.setAttribute("context", "contentAreaContextMenu");
    browser.hidden = true;
    browser.addEventListener("load", onBrowserLoad, true);
    browser.addEventListener("pageshow", onBrowserLoad, true);
    browser.addEventListener("DOMAudioPlaybackStarted", () =>
      setPanelAudio(panel.id, true)
    );
    browser.addEventListener("DOMAudioPlaybackStopped", () =>
      setPanelAudio(panel.id, false)
    );
    stack.appendChild(browser);
    browsers.set(panel.id, browser);
    return browser;
  }

  function updateNav() {
    const el = elements();
    const browser = activeBrowser();
    if (!browser) {
      return;
    }
    let back = false;
    let forward = false;
    try {
      back = !!browser.canGoBack;
      forward = !!browser.canGoForward;
    } catch (e) {
      // No history yet.
    }
    if (el.back.disabled !== !back) {
      el.back.disabled = !back;
    }
    if (el.forward.disabled !== !forward) {
      el.forward.disabled = !forward;
    }
  }

  // A non tab content browser does not report load or progress to this
  // window, so the nav state is sampled while a panel is visible. Two
  // property reads, no layout.
  function startNavTimer() {
    if (navTimer) {
      return;
    }
    navTimer = setInterval(updateNav, 500);
  }

  function stopNavTimer() {
    if (navTimer) {
      clearInterval(navTimer);
      navTimer = null;
    }
  }

  function imageLoads(url) {
    return new Promise(resolve => {
      const img = new Image();
      const timer = setTimeout(() => resolve(false), 5000);
      img.onload = () => {
        clearTimeout(timer);
        resolve(img.naturalWidth > 0);
      };
      img.onerror = () => {
        clearTimeout(timer);
        resolve(false);
      };
      img.src = url;
    });
  }

  async function readHead(response, limit) {
    if (!response.body) {
      return (await response.text()).slice(0, limit);
    }
    const reader = response.body.getReader();
    const chunks = [];
    let size = 0;
    while (size < limit) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }
      chunks.push(value);
      size += value.length;
    }
    reader.cancel().catch(() => {});
    const all = new Uint8Array(size);
    let offset = 0;
    for (const chunk of chunks) {
      all.set(chunk, offset);
      offset += chunk.length;
    }
    return new TextDecoder().decode(all);
  }

  function storeIcon(id, icon) {
    icons.set(id, icon);
    const list = readPanels();
    const record = list.find(panel => panel.id === id);
    if (record) {
      record.icon = icon;
      writePanels(list);
    }
    const sidebar = controller().sidebars.get(id);
    if (sidebar) {
      sidebar.iconUrl = icon;
    }
    window.dispatchEvent(new CustomEvent("SidebarItemChanged"));
  }

  // The sidebar browser is not a tab, so the page favicon never reaches
  // Places. Read the page head, then probe the declared icons and
  // /favicon.ico. The first one that loads is kept with the record.
  async function discoverIcon(panel) {
    const id = panel.id;
    if (triedIcons.has(id) || icons.has(id) || panel.icon) {
      return;
    }
    triedIcons.add(id);
    const candidates = [];
    try {
      const response = await fetch(panel.url, {
        credentials: "omit",
        referrerPolicy: "no-referrer",
        redirect: "follow",
      });
      if (response.ok) {
        const html = await readHead(response, HEAD_LIMIT);
        for (const tag of html.match(/<link\\b[^>]*>/gi) || []) {
          if (!/\\brel\\s*=\\s*["']?[^"'>]*icon/i.test(tag)) {
            continue;
          }
          const href =
            tag.match(/\\bhref\\s*=\\s*["']([^"']+)["']/i)?.[1] ||
            tag.match(/\\bhref\\s*=\\s*([^\\s>]+)/i)?.[1];
          if (!href) {
            continue;
          }
          try {
            const absolute = new URL(href, panel.url);
            if (isIconUrl(absolute.href)) {
              candidates.push(absolute.href);
            }
          } catch (e) {
            // Skip a bad href.
          }
          if (candidates.length >= 3) {
            break;
          }
        }
      }
    } catch (e) {
      // Offline or blocked. The default icon stays.
    }
    try {
      candidates.push(new URL("/favicon.ico", panel.url).href);
    } catch (e) {
      return;
    }
    for (const candidate of candidates.slice(0, 4)) {
      if (!isIconUrl(candidate)) {
        continue;
      }
      if (await imageLoads(candidate)) {
        if (panelById(id)) {
          storeIcon(id, candidate);
        }
        return;
      }
    }
  }

  function showPanelChrome(panel) {
    const el = elements();
    shownId = panel.id;
    el.header.hidden = false;
    el.stock.hidden = true;
    for (const [id, browser] of browsers) {
      browser.hidden = id !== panel.id;
    }
    const browser = browserFor(panel);
    if (browser) {
      browser.hidden = false;
      if (browser.getAttribute("src") !== panel.url) {
        browser.setAttribute("src", panel.url);
      }
    }
    el.title.textContent = panel.label;
    el.title.setAttribute("tooltiptext", panel.label);
    updateNav();
    startNavTimer();
    discoverIcon(panel);
  }

  function swapToStock() {
    const el = elements();
    for (const browser of browsers.values()) {
      browser.hidden = true;
    }
    if (el.header) {
      el.header.hidden = true;
    }
    if (el.stock) {
      el.stock.hidden = false;
    }
  }

  function cancelDeferredSwap() {
    if (hideTimer) {
      clearTimeout(hideTimer);
      hideTimer = null;
    }
  }

  // Keep the web panel on screen until the box has finished closing, then show
  // the stock browser. Swapping at the start of the transition flashes the old
  // panel while the box is still shrinking.
  function hidePanelChrome(defer) {
    shownId = null;
    stopNavTimer();
    const box = elements().box;
    if (!defer || !box || box.hidden) {
      cancelDeferredSwap();
      swapToStock();
      return;
    }
    if (hideTimer) {
      return;
    }
    const motion = window.__fgMotion || {};
    hideTimer = setTimeout(() => {
      hideTimer = null;
      if (!shownId && elements().box?.hidden) {
        swapToStock();
      }
    }, (motion.duration ?? 180) + 40);
  }

  function onSidebarShow(event) {
    cancelDeferredSwap();
    const id = event.detail?.viewId;
    const panel = prefEnabled() && id ? panelById(id) : null;
    if (panel) {
      showPanelChrome(panel);
    } else {
      hidePanelChrome(false);
    }
  }

  function onBrowserLoad(event) {
    if (!shownId || event.target !== activeBrowser()) {
      return;
    }
    updateNav();
  }

  function addElements() {
    return {
      panel: document.getElementById("firegila-webpanel-add-popup"),
      url: document.getElementById("firegila-webpanel-url"),
      name: document.getElementById("firegila-webpanel-name"),
      error: document.getElementById("firegila-webpanel-error"),
      ok: document.getElementById("firegila-webpanel-ok"),
      cancel: document.getElementById("firegila-webpanel-cancel"),
    };
  }

  function showError(id) {
    const el = addElements();
    el.error.textContent = message(id);
    el.error.hidden = false;
  }

  function closeAdd() {
    const el = addElements();
    if (!el.panel) {
      return;
    }
    // Drop focus before hiding. Otherwise focus returns to the add button and
    // the Enter keyup can activate it again, which reopens this popup.
    const active = document.activeElement;
    if (active && el.panel.contains(active)) {
      active.blur();
    }
    if (el.panel.state !== "closed") {
      el.panel.hidePopup();
    }
  }

  // The plus button tooltip would sit over the popup. Drop it while the popup
  // is open and put it back after.
  function clearAnchorTooltip(anchor) {
    addAnchor = anchor;
    const inner = anchor.shadowRoot?.querySelector("#main-button");
    if (inner) {
      inner.removeAttribute("title");
    }
    for (const tip of document.querySelectorAll("tooltip")) {
      if (tip.state && tip.state !== "closed") {
        tip.hidePopup();
      }
    }
  }

  function restoreAnchorTooltip() {
    const inner = addAnchor?.shadowRoot?.querySelector("#main-button");
    if (inner && addTooltip) {
      inner.setAttribute("title", addTooltip);
    }
    addAnchor = null;
  }

  // The current page, when it is a normal web page. Used to prefill the add
  // form, so adding the site the user is on takes one click.
  function currentPageUrl() {
    const uri = window.gBrowser?.currentURI;
    if (!uri || (!uri.schemeIs("http") && !uri.schemeIs("https"))) {
      return "";
    }
    return uri.spec;
  }

  function openAdd(anchor) {
    const el = addElements();
    if (!el.panel || !anchor) {
      return;
    }
    if (el.panel.state === "open" || el.panel.state === "showing") {
      el.url.focus();
      return;
    }
    el.url.value = currentPageUrl();
    el.name.value = "";
    el.error.hidden = true;
    el.error.textContent = "";
    const start = controller()._positionStart;
    el.panel.hidden = false;
    clearAnchorTooltip(anchor);
    el.panel.openPopup(
      anchor,
      start ? "rightcenter leftcenter" : "leftcenter rightcenter",
      start ? 8 : -8,
      0
    );
    el.panel.addEventListener(
      "popupshown",
      () => {
        el.url.focus();
        if (el.url.value) {
          el.url.select();
        }
      },
      { once: true }
    );
  }

  function submitAdd() {
    const el = addElements();
    const normalized = normalize(el.url.value);
    if (!normalized) {
      showError("firegila-webpanel-error-invalid");
      return;
    }
    const list = readPanels();
    const existing = list.find(panel => panel.url === normalized.url);
    if (existing) {
      closeAdd();
      controller().show(existing.id);
      return;
    }
    if (list.length >= MAX_PANELS) {
      showError("firegila-webpanel-error-limit");
      return;
    }
    const panel = {
      id: PANEL_PREFIX + crypto.randomUUID(),
      url: normalized.url,
      label: cleanLabel(el.name.value) || normalized.label,
      icon: "",
    };
    writePanels([...list, panel]);
    applyPrefs();
    closeAdd();
    controller().show(panel.id);
  }

  function onContextMenu(event) {
    const button = event.target?.closest?.("moz-button[view]");
    if (!button) {
      return;
    }
    const id = button.getAttribute("view");
    if (!panels.some(panel => panel.id === id)) {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    contextId = id;
    const reload = document.getElementById("firegila-webpanel-menu-reload");
    reload.disabled = !(controller().isOpen && controller().currentID === id);
    document
      .getElementById("firegila-webpanel-menu")
      .openPopupAtScreen(event.screenX, event.screenY, true);
  }

  function reloadPanel() {
    if (!contextId) {
      return;
    }
    if (controller().isOpen && controller().currentID === contextId) {
      activeBrowser()?.reload();
    } else {
      controller().show(contextId);
    }
  }

  function openPanelTab() {
    const panel = contextId ? panelById(contextId) : null;
    if (!panel) {
      return;
    }
    if (typeof window.openTrustedLinkIn === "function") {
      window.openTrustedLinkIn(panel.url, "tab");
    } else {
      const principal = Services.scriptSecurityManager.getSystemPrincipal();
      window.gBrowser.addTab(panel.url, { triggeringPrincipal: principal });
    }
  }

  function removePanel() {
    if (!contextId) {
      return;
    }
    const id = contextId;
    contextId = null;
    writePanels(readPanels().filter(panel => panel.id !== id));
    applyPrefs();
  }

  function wire() {
    if (wired) {
      return true;
    }
    const el = elements();
    if (!el.box || !el.header || !el.stock || !el.stack) {
      return false;
    }
    el.box.addEventListener("sidebar-show", onSidebarShow);
    el.box.addEventListener("sidebar-hide", () => hidePanelChrome(true));
    el.back.addEventListener("command", () => activeBrowser()?.goBack());
    el.forward.addEventListener("command", () => activeBrowser()?.goForward());
    el.reload.addEventListener("command", () => activeBrowser()?.reload());
    el.close.addEventListener("command", () => controller().hide());

    const add = addElements();
    add.ok.addEventListener("command", submitAdd);
    add.cancel.addEventListener("command", closeAdd);
    add.panel.addEventListener("popuphidden", () => {
      add.panel.hidden = true;
      restoreAnchorTooltip();
    });
    add.url.addEventListener("keydown", event => {
      if (event.key === "Enter") {
        event.preventDefault();
        event.stopPropagation();
        submitAdd();
      }
    });
    add.name.addEventListener("keydown", event => {
      if (event.key === "Enter") {
        event.preventDefault();
        event.stopPropagation();
        submitAdd();
      }
    });

    document
      .getElementById("firegila-webpanel-menu-reload")
      .addEventListener("command", reloadPanel);
    document
      .getElementById("firegila-webpanel-menu-open-tab")
      .addEventListener("command", openPanelTab);
    document
      .getElementById("firegila-webpanel-menu-remove")
      .addEventListener("command", removePanel);

    Services.prefs.addObserver(ENABLED_PREF, applyPrefs);
    Services.prefs.addObserver(PANELS_PREF, applyPrefs);
    window.addEventListener("unload", () => {
      Services.prefs.removeObserver(ENABLED_PREF, applyPrefs);
      Services.prefs.removeObserver(PANELS_PREF, applyPrefs);
    });
    wired = true;
    return true;
  }

  window.FiregilaWebPanels = {
    get enabled() {
      return prefEnabled();
    },
    get actions() {
      return actions();
    },
    get addTooltip() {
      return addTooltip;
    },
    openAdd,
    onContextMenu,
  };

  function start() {
    panels = readPanels();
    addTooltip = message("firegila-webpanel-add-tooltip");
    if (!wire()) {
      window.addEventListener(
        "load",
        () => {
          wire();
          applyPrefs();
        },
        { once: true }
      );
    }
    applyPrefs();
  }

  if (window.SidebarController?.promiseInitialized) {
    window.SidebarController.promiseInitialized.then(start, start);
  } else {
    window.addEventListener("load", start, { once: true });
  }
})();
"""


# Workspaces. One switcher in the tab bar, tabs of the inactive workspaces are
# hidden with the native tab hiding API, membership is kept per tab with
# SessionStore custom values so it survives a restart.
SB_WORKSPACES_JS = """
(function () {
  const ENABLED_PREF = "firegila.workspaces.enabled";
  const SCROLL_PREF = "firegila.workspaces.scrollSwitch";
  const LIST_PREF = "firegila.workspaces.list";
  const TAB_VALUE = "firegila.workspace";
  const HIDDEN_SOURCE = "firegila-workspace";
  const MAX_WORKSPACES = 12;
  const MAX_NAME = 24;
  const SCROLL_DELAY = 160;

  const { SessionStore } = ChromeUtils.importESModule(
    "resource:///modules/sessionstore/SessionStore.sys.mjs"
  );
  const l10n = new Localization(["browser/sidebar.ftl"], true);

  let workspaces = [];
  let activeId = null;
  let nameMode = "new";
  let lastScroll = 0;
  let started = false;
  const lastTab = new Map();

  function tabsBrowser() {
    return window.gBrowser;
  }

  function message(id, args) {
    try {
      const value = args
        ? l10n.formatValueSync(id, args)
        : l10n.formatValueSync(id);
      return value || "";
    } catch (e) {
      return "";
    }
  }

  function cleanName(raw) {
    return String(raw || "")
      .replace(/[\\u0000-\\u001f\\u007f]+/g, " ")
      .replace(/\\s+/g, " ")
      .trim()
      .slice(0, MAX_NAME);
  }

  function readList() {
    let raw;
    try {
      raw = JSON.parse(Services.prefs.getStringPref(LIST_PREF, "[]"));
    } catch (e) {
      raw = [];
    }
    const list = [];
    const ids = new Set();
    const names = new Set();
    for (const entry of Array.isArray(raw) ? raw : []) {
      const name = cleanName(entry?.name);
      if (!name || names.has(name.toLowerCase())) {
        continue;
      }
      let id = entry?.id;
      if (
        typeof id !== "string" ||
        !/^ws-[a-z0-9-]+$/.test(id) ||
        ids.has(id)
      ) {
        id = "ws-" + crypto.randomUUID();
      }
      ids.add(id);
      names.add(name.toLowerCase());
      list.push({ id, name });
      if (list.length >= MAX_WORKSPACES) {
        break;
      }
    }
    if (!list.length) {
      list.push({ id: "ws-default", name: "Default" });
    }
    return list;
  }

  function writeList(list) {
    Services.prefs.setStringPref(LIST_PREF, JSON.stringify(list));
  }

  function enabled() {
    return Services.prefs.getBoolPref(ENABLED_PREF, true);
  }

  function workspace(id) {
    return workspaces.find(item => item.id === id) || null;
  }

  function active() {
    return workspace(activeId) || workspaces[0] || null;
  }

  function assignTab(tab, id) {
    if (!tab || !workspace(id)) {
      return;
    }
    tab.setAttribute(TAB_VALUE, id);
    SessionStore.setCustomTabValue(tab, TAB_VALUE, id);
  }

  function tabWorkspace(tab) {
    if (!tab) {
      return null;
    }
    let id = tab.getAttribute(TAB_VALUE);
    if (workspace(id)) {
      return id;
    }
    const saved = SessionStore.getCustomTabValue(tab, TAB_VALUE);
    if (workspace(saved)) {
      tab.setAttribute(TAB_VALUE, saved);
      return saved;
    }
    id = activeId || (workspaces[0] && workspaces[0].id);
    if (id) {
      assignTab(tab, id);
    }
    return id;
  }

  function claimUnknown() {
    for (const tab of tabsBrowser().tabs) {
      if (tab.closing) {
        continue;
      }
      if (!SessionStore.getCustomTabValue(tab, TAB_VALUE)) {
        assignTab(tab, activeId);
      }
    }
  }

  function tabsIn(id) {
    return Array.from(tabsBrowser().tabs).filter(
      tab => !tab.closing && tabWorkspace(tab) === id
    );
  }

  function hiddenByOther(tab) {
    const hiddenBy = SessionStore.getCustomTabValue(tab, "hiddenBy");
    return !!hiddenBy && hiddenBy !== HIDDEN_SOURCE;
  }

  function canShow(tab) {
    return !hiddenByOther(tab) && !tab.group?.collapsed;
  }

  function hideOthers(id) {
    const gb = tabsBrowser();
    for (const tab of gb.tabs) {
      if (tab.closing || tab.hidden) {
        continue;
      }
      if (tabWorkspace(tab) === id) {
        continue;
      }
      if (tab.pinned || tab.selected || tab.group?.collapsed) {
        continue;
      }
      gb.hideTab(tab, HIDDEN_SOURCE);
    }
    syncGroups();
  }

  // Native group labels are separate elements in the tab strip. Hide the ones
  // that belong to an inactive workspace, or they would float above the tabs
  // of the active one.
  function syncGroups() {
    for (const group of document.querySelectorAll("tab-group")) {
      const first = group.tabs && group.tabs[0];
      const id = first ? tabWorkspace(first) : null;
      const show = !enabled() || !id || id === activeId;
      group.style.display = show ? "" : "none";
    }
  }

  function rememberLast() {
    const tab = tabsBrowser().selectedTab;
    const id = tab ? tabWorkspace(tab) : null;
    if (id) {
      lastTab.set(id, tab);
    }
  }

  function switchTo(id) {
    if (!enabled() || !workspace(id) || id === activeId) {
      syncUI();
      return;
    }
    const gb = tabsBrowser();
    claimUnknown();
    activeId = id;
    const tabs = tabsIn(id);
    for (const tab of tabs) {
      if (tab.hidden && canShow(tab)) {
        gb.showTab(tab);
      }
    }
    const remembered = lastTab.get(id);
    const visible = tabs.filter(tab => canShow(tab));
    if (!visible.length) {
      const fresh = gb.addTab("about:newtab", {
        triggeringPrincipal: Services.scriptSecurityManager.getSystemPrincipal(),
      });
      assignTab(fresh, id);
      visible.push(fresh);
    }
    const pick =
      (remembered && !remembered.closing && visible.includes(remembered)
        ? remembered
        : null) || visible[0];
    if (pick) {
      gb.selectedTab = pick;
    }
    hideOthers(id);
    rememberLast();
    syncUI();
  }

  function tabHasAudio(tab) {
    return tab.hasAttribute("soundplaying") && !tab.hasAttribute("muted");
  }

  function workspaceHasAudio(id) {
    return Array.from(tabsBrowser().tabs).some(
      tab => !tab.closing && tabWorkspace(tab) === id && tabHasAudio(tab)
    );
  }

  function otherWorkspaceAudio() {
    return workspaces.some(
      item => item.id !== activeId && workspaceHasAudio(item.id)
    );
  }

  function syncUI() {
    const button = document.getElementById("firegila-workspaces");
    const current = active();
    if (!button || !current) {
      return;
    }
    button.hidden = !enabled();
    button.setAttribute("label", current.name);
    button.setAttribute("tooltiptext", current.name);
    button.toggleAttribute("firegila-audio", otherWorkspaceAudio());
  }

  function buildMenu() {
    const menu = document.getElementById("firegila-workspace-menu");
    const separator = document.getElementById("firegila-workspace-separator");
    if (!menu || !separator) {
      return;
    }
    for (const node of menu.querySelectorAll(".firegila-workspace-item")) {
      node.remove();
    }
    for (const item of workspaces) {
      const menuitem = document.createXULElement("menuitem");
      menuitem.className = "firegila-workspace-item";
      menuitem.setAttribute("type", "radio");
      menuitem.setAttribute("name", "firegila-workspace");
      menuitem.setAttribute("label", item.name);
      menuitem.setAttribute("value", item.id);
      menuitem.toggleAttribute(
        "firegila-audio",
        workspaceHasAudio(item.id)
      );
      menuitem.checked = item.id === activeId;
      // The property does not reflect to the attribute here, and the menu CSS
      // selects on the attribute, so set both.
      menuitem.toggleAttribute("checked", item.id === activeId);
      menuitem.addEventListener("command", () => switchTo(item.id));
      menu.insertBefore(menuitem, separator);
    }
    const remove = document.getElementById("firegila-workspace-delete");
    if (remove) {
      remove.disabled = workspaces.length <= 1;
    }
  }

  function placeSwitcher() {
    const button = document.getElementById("firegila-workspaces");
    if (!button) {
      return;
    }
    const vertical = Services.prefs.getBoolPref("sidebar.verticalTabs", false);
    if (vertical) {
      const container = document.getElementById("vertical-tabs-container");
      const tabs = document.getElementById("vertical-tabs");
      if (container && button.parentNode !== container) {
        container.insertBefore(button, tabs || container.firstChild);
      }
    } else {
      const items = document.querySelector("#TabsToolbar .toolbar-items");
      const target = document.getElementById("TabsToolbar-customization-target");
      if (items && button.parentNode !== items) {
        items.insertBefore(button, target || items.firstChild);
      }
    }
  }

  function nameElements() {
    return {
      panel: document.getElementById("firegila-workspace-name-popup"),
      heading: document.getElementById("firegila-workspace-name-heading"),
      input: document.getElementById("firegila-workspace-name-input"),
      error: document.getElementById("firegila-workspace-name-error"),
      cancel: document.getElementById("firegila-workspace-name-cancel"),
      ok: document.getElementById("firegila-workspace-name-ok"),
    };
  }

  function confirmElements() {
    return {
      panel: document.getElementById("firegila-workspace-confirm-popup"),
      text: document.getElementById("firegila-workspace-confirm-text"),
      cancel: document.getElementById("firegila-workspace-confirm-cancel"),
      ok: document.getElementById("firegila-workspace-confirm-ok"),
    };
  }

  function showNameError(id) {
    const el = nameElements();
    el.error.textContent = message(id);
    el.error.hidden = false;
  }

  function openNamePanel(mode) {
    nameMode = mode;
    const el = nameElements();
    const current = active();
    el.heading.textContent = message(
      mode === "new"
        ? "firegila-workspace-new-heading"
        : "firegila-workspace-rename-heading"
    );
    el.input.value = mode === "rename" && current ? current.name : "";
    el.error.hidden = true;
    el.error.textContent = "";
    el.panel.hidden = false;
    el.panel.openPopup(
      document.getElementById("firegila-workspaces"),
      "bottomleft topleft",
      0,
      4
    );
    el.panel.addEventListener(
      "popupshown",
      () => {
        el.input.focus();
        el.input.select();
      },
      { once: true }
    );
  }

  function closeNamePanel() {
    const el = nameElements();
    if (el.panel && el.panel.state !== "closed") {
      el.panel.hidePopup();
    }
  }

  function saveName() {
    const el = nameElements();
    const value = cleanName(el.input.value);
    if (!value) {
      showNameError("firegila-workspace-name-empty");
      return;
    }
    const current = active();
    const keepId = nameMode === "rename" && current ? current.id : null;
    if (
      workspaces.some(
        item => item.id !== keepId && item.name.toLowerCase() === value.toLowerCase()
      )
    ) {
      showNameError("firegila-workspace-name-taken");
      return;
    }
    if (nameMode === "new") {
      if (workspaces.length >= MAX_WORKSPACES) {
        showNameError("firegila-workspace-limit");
        return;
      }
      const item = { id: "ws-" + crypto.randomUUID(), name: value };
      workspaces.push(item);
      writeList(workspaces);
      closeNamePanel();
      switchTo(item.id);
      return;
    }
    if (current) {
      current.name = value;
      writeList(workspaces);
      closeNamePanel();
      syncUI();
    }
  }

  function openDeletePanel() {
    const current = active();
    if (!current || workspaces.length <= 1) {
      return;
    }
    const el = confirmElements();
    el.text.textContent = message("firegila-workspace-delete-text", {
      name: current.name,
      count: tabsIn(current.id).length,
    });
    el.panel.hidden = false;
    el.panel.openPopup(
      document.getElementById("firegila-workspaces"),
      "bottomleft topleft",
      0,
      4
    );
  }

  function closeDeletePanel() {
    const el = confirmElements();
    if (el.panel && el.panel.state !== "closed") {
      el.panel.hidePopup();
    }
  }

  function deleteWorkspace() {
    const current = active();
    if (!current || workspaces.length <= 1) {
      return;
    }
    const tabs = tabsIn(current.id);
    const other = workspaces.find(item => item.id !== current.id);
    closeDeletePanel();
    switchTo(other.id);
    for (const tab of tabs) {
      if (!tab.closing) {
        tabsBrowser().removeTab(tab);
      }
    }
    workspaces = workspaces.filter(item => item.id !== current.id);
    writeList(workspaces);
    syncUI();
  }

  function onTabOpen(event) {
    if (!enabled()) {
      return;
    }
    const tab = event.target;
    const saved = SessionStore.getCustomTabValue(tab, TAB_VALUE);
    if (workspace(saved)) {
      tab.setAttribute(TAB_VALUE, saved);
    } else if (activeId) {
      assignTab(tab, activeId);
    }
    syncGroups();
  }

  function onTabRestored(event) {
    const tab = event.target;
    const saved = SessionStore.getCustomTabValue(tab, TAB_VALUE);
    if (workspace(saved)) {
      tab.setAttribute(TAB_VALUE, saved);
    } else if (activeId) {
      assignTab(tab, activeId);
    }
    if (!enabled() || !activeId) {
      return;
    }
    if (tabWorkspace(tab) !== activeId) {
      if (!tab.hidden && !tab.pinned && tab !== tabsBrowser().selectedTab) {
        tabsBrowser().hideTab(tab, HIDDEN_SOURCE);
      }
    } else if (tab.hidden && canShow(tab)) {
      tabsBrowser().showTab(tab);
    }
    syncUI();
  }

  function onTabShow(event) {
    if (!enabled() || !activeId) {
      return;
    }
    const tab = event.target;
    if (tabWorkspace(tab) === activeId) {
      return;
    }
    if (tab === tabsBrowser().selectedTab || tab.pinned || tab.group?.collapsed) {
      return;
    }
    tabsBrowser().hideTab(tab, HIDDEN_SOURCE);
  }

  function onTabSelect() {
    if (!enabled() || !activeId) {
      return;
    }
    const tab = tabsBrowser().selectedTab;
    const id = tabWorkspace(tab);
    if (id && id !== activeId) {
      activeId = id;
      hideOthers(id);
      syncUI();
    }
    rememberLast();
  }

  function onTabClose(event) {
    for (const [id, tab] of lastTab) {
      if (tab === event.target) {
        lastTab.delete(id);
      }
    }
    syncUI();
  }

  function onTabAttr(event) {
    const changed = event.detail?.changed || [];
    if (changed.includes("soundplaying") || changed.includes("muted")) {
      syncUI();
    }
  }

  function onWheel(event) {
    if (!enabled() || workspaces.length < 2) {
      return;
    }
    if (!Services.prefs.getBoolPref(SCROLL_PREF, true)) {
      return;
    }
    event.preventDefault();
    const now = Date.now();
    if (now - lastScroll < SCROLL_DELAY) {
      return;
    }
    lastScroll = now;
    const index = workspaces.findIndex(item => item.id === activeId);
    const step = event.deltaY > 0 ? 1 : -1;
    const next = workspaces[(index + step + workspaces.length) % workspaces.length];
    switchTo(next.id);
  }

  function wire() {
    const gb = tabsBrowser();
    const button = document.getElementById("firegila-workspaces");
    if (!gb || !button) {
      return;
    }
    const container = gb.tabContainer;
    container.addEventListener("TabOpen", onTabOpen);
    container.addEventListener("TabClose", onTabClose);
    container.addEventListener("TabSelect", onTabSelect);
    container.addEventListener("TabShow", onTabShow);
    container.addEventListener("TabAttrModified", onTabAttr);
    window.addEventListener("SSTabRestored", onTabRestored);
    window.addEventListener("TabGrouped", syncGroups);
    window.addEventListener("TabUngrouped", syncGroups);
    window.addEventListener("TabGroupCollapse", syncGroups);
    window.addEventListener("TabGroupExpand", syncGroups);
    button.addEventListener("wheel", onWheel, { passive: false });

    const menu = document.getElementById("firegila-workspace-menu");
    menu.addEventListener("popupshowing", () => {
      menu.style.setProperty(
        "--panel-width",
        `${Math.round(button.getBoundingClientRect().width)}px`
      );
      buildMenu();
    });
    document
      .getElementById("firegila-workspace-new")
      .addEventListener("command", () => openNamePanel("new"));
    document
      .getElementById("firegila-workspace-rename")
      .addEventListener("command", () => openNamePanel("rename"));
    document
      .getElementById("firegila-workspace-delete")
      .addEventListener("command", openDeletePanel);

    const name = nameElements();
    name.ok.addEventListener("command", saveName);
    name.cancel.addEventListener("command", closeNamePanel);
    name.input.addEventListener("keydown", event => {
      if (event.key === "Enter") {
        event.preventDefault();
        event.stopPropagation();
        saveName();
      }
    });
    name.panel.addEventListener("popuphidden", () => {
      name.panel.hidden = true;
    });

    const confirm = confirmElements();
    confirm.ok.addEventListener("command", deleteWorkspace);
    confirm.cancel.addEventListener("command", closeDeletePanel);
    confirm.panel.addEventListener("popuphidden", () => {
      confirm.panel.hidden = true;
    });

    Services.prefs.addObserver(ENABLED_PREF, onPrefsChanged);
    Services.prefs.addObserver(LIST_PREF, onPrefsChanged);
    Services.prefs.addObserver("sidebar.verticalTabs", placeSwitcher);
    window.addEventListener("unload", () => {
      Services.prefs.removeObserver(ENABLED_PREF, onPrefsChanged);
      Services.prefs.removeObserver(LIST_PREF, onPrefsChanged);
      Services.prefs.removeObserver("sidebar.verticalTabs", placeSwitcher);
    });
  }

  function onPrefsChanged() {
    workspaces = readList();
    if (!workspace(activeId)) {
      activeId = workspaces[0].id;
    }
    if (enabled()) {
      for (const tab of tabsBrowser().tabs) {
        if (
          !tab.closing &&
          tabWorkspace(tab) === activeId &&
          tab.hidden &&
          canShow(tab)
        ) {
          tabsBrowser().showTab(tab);
        }
      }
      hideOthers(activeId);
    } else {
      for (const tab of tabsBrowser().tabs) {
        if (
          tab.hidden &&
          SessionStore.getCustomTabValue(tab, "hiddenBy") === HIDDEN_SOURCE
        ) {
          tabsBrowser().showTab(tab);
        }
      }
      syncGroups();
    }
    syncUI();
  }

  function start() {
    if (started) {
      return;
    }
    started = true;
    workspaces = readList();
    const selected = tabsBrowser().selectedTab;
    const saved = selected
      ? SessionStore.getCustomTabValue(selected, TAB_VALUE)
      : "";
    activeId = workspace(saved) ? saved : workspaces[0].id;
    claimUnknown();
    placeSwitcher();
    wire();
    if (enabled()) {
      for (const tab of tabsBrowser().tabs) {
        if (
          !tab.closing &&
          tabWorkspace(tab) === activeId &&
          tab.hidden &&
          canShow(tab)
        ) {
          tabsBrowser().showTab(tab);
        }
      }
      hideOthers(activeId);
    }
    syncUI();
    SessionStore.promiseAllWindowsRestored.then(restoreDone, restoreDone);
  }

  function restoreDone() {
    if (!enabled()) {
      syncUI();
      return;
    }
    const selected = tabsBrowser().selectedTab;
    const saved = selected
      ? SessionStore.getCustomTabValue(selected, TAB_VALUE)
      : "";
    if (workspace(saved)) {
      activeId = saved;
    }
    for (const tab of Array.from(tabsBrowser().tabs)) {
      if (tab.closing || tabWorkspace(tab) !== activeId) {
        continue;
      }
      if (tab.hidden && canShow(tab)) {
        tabsBrowser().showTab(tab);
      }
    }
    hideOthers(activeId);
    syncUI();
  }

  if (document.readyState === "complete") {
    start();
  } else {
    window.addEventListener("load", start, { once: true });
  }
})();
"""


# Pressed design system buttons shrink their icon, not the button box. The
# stylesheet lives in the moz-button shadow root, so the img is reachable here.
MOZ_BUTTON_PRESS_CSS = """
@media (prefers-reduced-motion: no-preference) {
  .button-background img {
    transition: transform 120ms cubic-bezier(0.3, 0, 0.2, 1);
  }

  #main-button:active .button-background img {
    transform: scale(0.93);
  }
}
"""


patch_jar(BUILD / "omni.ja", MAIN_EDITS, sweep=True,
          appends=[(TOKENS_SHARED, GLOBAL_OVERRIDE_CSS),
                   (GLOBAL_SHARED, GLOBAL_OVERRIDE_CSS),
                   ("chrome/toolkit/content/global/elements/moz-input-text.css", WIDGET_CSS),
                   ("chrome/toolkit/content/global/elements/moz-select.css", WIDGET_CSS),
                   ("chrome/toolkit/content/global/elements/moz-button.css", MOZ_BUTTON_PRESS_CSS),
                   ("chrome/toolkit/content/global/megalist/megalist.css", MEGALIST_CSS)])
# Both newtab stylesheets get the same four blocks. The dialog rules land in
# both because classic and nova each ship their own copy of the modal.
NEWTAB_CSS_FILES = [
    "chrome/browser/builtin-addons/newtab/data/css/activity-stream.css",
    "chrome/browser/builtin-addons/newtab/data/css/nova/activity-stream.css",
]
NEWTAB_CSS = NEWTAB_PALETTE_CSS + NEWTAB_BUTTONS_CSS + NEWTAB_DIALOG_CSS + NEWTAB_TWEAKS_CSS

# Default bookmarks ship Mozilla links that surface in the urlbar and add
# noise. An empty folder keeps new profiles clean, added bookmarks still
# suggest and sync normally.
DEFAULT_BOOKMARKS = """<!-- This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at http://mozilla.org/MPL/2.0/. -->
<!DOCTYPE NETSCAPE-Bookmark-file-1>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none';">
    <link rel="localization" href="branding/brand.ftl"/>
    <link rel="localization" href="browser/profile/default-bookmarks.ftl"/>
    <title data-l10n-id="default-bookmarks-title">default-bookmarks-title</title>
</head>
<body>
<h1 data-l10n-id="default-bookmarks-heading">default-bookmarks-heading</h1>

<dl><p>
</dl>
</body>
</html>
"""

patch_jar(BUILD / "browser/omni.ja", BROWSER_EDITS, REMOVE_DIRS_BROWSER, ART_SVG_BROWSER, sweep=True,
          appends=[(f, NEWTAB_CSS) for f in NEWTAB_CSS_FILES] + [
                   # The stock browser defaults file loads after the app level
                   # defaults/pref files, so stock wins on any pref both set.
                   # Appending our defaults here makes the intended value
                   # final. customize.sh writes the file before this runs.
                   ("defaults/preferences/firefox.js", "\n" + FIREGILA_PREFS),
                   ("chrome/browser/skin/classic/browser/tabbrowser/tab.tokens.css", TAB_CSS),
                   ("chrome/browser/content/browser/sidebar/sidebar.css", SIDEBAR_PAGE_CSS),
                   ("chrome/browser/skin/classic/browser/tabbrowser/content-area.css", CONTENT_AREA_CSS),
                   ("chrome/browser/skin/classic/browser/sidebar.css", SB_CHROME_CSS),
                   ("chrome/browser/content/browser/sidebar/sidebar-main.css", SB_MAIN_CSS),
                   ("chrome/browser/content/browser/sidebar/browser-sidebar.js", SB_BOOTSTRAP_JS),
                   ("chrome/browser/content/browser/sidebar/browser-sidebar.js", SB_ANIM_JS),
                   ("chrome/browser/content/browser/sidebar/browser-sidebar.js", SB_WEBPANELS_JS),
                   ("chrome/browser/content/browser/sidebar/browser-sidebar.js", SB_WORKSPACES_JS)],
          overwrites=[("chrome/browser/content/browser/default-bookmarks.html", DEFAULT_BOOKMARKS)])
