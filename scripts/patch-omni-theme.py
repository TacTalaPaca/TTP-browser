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
from urllib.parse import quote

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
    ("--fg-separator", "light-dark(#d9d9d9, #333333)"),
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
    + "    --fg-audio: light-dark(#5b5b5b, #b8b8b8);\n"
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
    + "    --fg-motion-fast: 80ms;\n"
    + "    --fg-motion-base: 140ms;\n"
    + "    --fg-ease: ease;\n"
    + "    --fg-press-down: 90ms;\n"
    + "    --fg-press-up: 220ms;\n"
    + "    --fg-press-ease: cubic-bezier(0.2, 0, 0, 1);\n"
    + "    --fg-press-ease-down: cubic-bezier(0.3, 0, 0.2, 1);\n"
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
    + "    --panel-separator-color: var(--fg-separator);\n"
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
    + "    --fg-tabs-margin: 4px;\n"
    + "    --fg-tabs-inset: 8px;\n"
    + "    --border-radius-xsmall: 8px;\n"
    + "    --border-radius-small: 8px;\n"
    + "    --border-radius-medium: 8px;\n"
    + "    --border-radius-large: 8px;\n"
    + "    --border-radius-xlarge: 8px;\n"
    + "    --border-radius-xxlarge: 8px;\n"
    + "    --panel-menuitem-border-radius: calc(8px - 4px);\n"
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
    # Menus follow the platform geometry and colors. The rest of the chrome
    # stays on the Firegila theme.
    + "  menupopup {\n"
    + "    --border-radius-xsmall: 2px;\n"
    + "    --panel-box-shadow: 0 0 var(--panel-box-shadow-margin) hsla(0, 0%, 0%, 0.2);\n"
    + "    --panel-separator-color: color-mix(in srgb, currentColor 25%, transparent);\n"
    + "    --text-color-disabled: color-mix(in srgb, currentColor 40%, transparent);\n"
    + "    --text-color-deemphasized: color-mix(in srgb, currentColor 69%, transparent);\n"
    + "  }\n"
    + "  :root .toolbarbutton-1 {\n"
    + "    align-items: center !important;\n"
    + "  }\n"
    + "  :root .toolbarbutton-1 > .toolbarbutton-icon,\n"
    + "  :root .toolbarbutton-1 > .toolbarbutton-badge-stack {\n"
    + "    margin-block: auto !important;\n"
    + "  }\n"
    # Hover and selected fills fade in step on every button in the chrome.
    + "  :root :where(toolbarbutton, button) {\n"
    + "    transition:\n"
    + "      background-color var(--fg-motion-fast) var(--fg-ease),\n"
    + "      border-color var(--fg-motion-fast) var(--fg-ease);\n"
    + "  }\n"
    + "  :root .toolbarbutton-1 > :where(.toolbarbutton-icon, .toolbarbutton-text, .toolbarbutton-badge-stack) {\n"
    + "    transition:\n"
    + "      background-color var(--fg-motion-fast) var(--fg-ease),\n"
    + "      border-color var(--fg-motion-fast) var(--fg-ease);\n"
    + "  }\n"
    + "  :root #urlbar .searchmode-switcher {\n"
    + "    --button-border-radius: calc(var(--urlbar-border-radius) - 2px) !important;\n"
    + "    border-radius: calc(var(--urlbar-border-radius) - 2px) !important;\n"
    + "  }\n"
    + "  :root #urlbar :is([urlbar-slot], .urlbar-page-action) {\n"
    + "    border-radius: calc(var(--urlbar-border-radius) - 2px) !important;\n"
    + "  }\n"
    + "  @media (prefers-color-scheme: dark) {\n"
    + "    :root, :root #navigator-toolbox, :root toolbar, :root panel {\n"
    + "      color-scheme: dark !important;\n"
    + "    }\n"
    + "  }\n"
    + "  @media (prefers-color-scheme: light) {\n"
    + "    :root, :root #navigator-toolbox, :root toolbar, :root panel {\n"
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
  background-color: var(--fg-bg-3);
  border-color: var(--fg-border);
  color: var(--fg-text);
}
.actions button.cancel:hover {
  background-color: var(--fg-hover);
  border-color: var(--fg-border);
  box-shadow: none;
}
.actions button.cancel:active {
  background-color: var(--fg-active);
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
  --fg-separator: light-dark(#d9d9d9, #333333);
  --fg-text: light-dark(#171717, #fafafa);
  --fg-text-dim: light-dark(#4a4a4a, #b8b8b8);
  --button-background-color-hover: var(--fg-hover);
  --button-background-color-active: var(--fg-active);
  --newtab-button-static-hover-background: var(--fg-hover);
  --newtab-button-static-active-background: var(--fg-active);
  --newtab-element-hover-color: var(--fg-hover);
  --newtab-element-active-color: var(--fg-active);
  --newtab-element-secondary-hover-color: var(--fg-hover);
  --newtab-element-secondary-active-color: var(--fg-active);
  --newtab-primary-element-hover-color: var(--color-accent-primary-hover);
  --newtab-primary-element-active-color: var(--color-accent-primary-active);
  --fg-hover-brightness: 0.85;
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
/* Motion tokens. Same names and values as the chrome theme. */
:root {
  --fg-motion-fast: 80ms;
  --fg-motion-base: 140ms;
  --fg-ease: ease;
  --fg-press-down: 90ms;
  --fg-press-up: 220ms;
  --fg-press-ease: cubic-bezier(0.2, 0, 0, 1);
  --fg-press-ease-down: cubic-bezier(0.3, 0, 0.2, 1);
  --fg-fade-label: 120ms;
}
/* Firegila newtab action buttons. Darker neutral fill in dark mode. */
.personalize-button,
.lightWallpaper .personalize-button,
.darkWallpaper .personalize-button {
  background-color: var(--fg-bg-3) !important;
  color: var(--fg-text) !important;
  fill: currentColor;
  border: 0;
  transition: background-color var(--fg-motion-fast) var(--fg-ease);
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
/* Nova wraps the customize button in moz-button, so the fill lives in a
 * shadow part. Stock sets --button-background-color to transparent and the
 * button disappears over a wallpaper. The part is centered and fixed to the
 * same height in both states, so only the label width changes. */
.open-customization-button::part(button) {
  background-color: var(--fg-bg-3) !important;
  color: var(--fg-text) !important;
  fill: currentColor;
  border: 0;
  align-items: center;
  justify-content: center;
  padding: 0 var(--space-small) !important;
}
.open-customization-button::part(moz-button-label) {
  color: var(--fg-text) !important;
}
.open-customization-button:hover::part(button) {
  background-color: var(--fg-hover) !important;
}
.open-customization-button:active::part(button),
.open-customization-button:focus-visible::part(button),
.open-customization-button:focus-within::part(button) {
  background-color: var(--fg-active) !important;
}
.open-customization-button:focus-visible::part(button) {
  outline: 1px solid AccentColor !important;
  outline-offset: 1px;
}
/* Flat buttons keep a background hover. Stock drew a box-shadow ring, which
 * this theme removes. Primary actions keep their accent hover. */
.button,
.actions button {
  transition:
    background-color var(--fg-motion-fast) var(--fg-ease),
    border-color var(--fg-motion-fast) var(--fg-ease);
}
.button:hover:not(.dismiss, .done, .primary),
.button:focus-visible:not(.dismiss, .done, .primary),
.actions button:hover:not(.dismiss, .done, .primary),
.actions button:focus-visible:not(.dismiss, .done, .primary) {
  background-color: var(--fg-hover) !important;
  box-shadow: none !important;
}
.button:active:not(.dismiss, .done, .primary),
.actions button:active:not(.dismiss, .done, .primary) {
  background-color: var(--fg-active) !important;
}
/* One press curve for every button icon. The press is quick and the release
 * is slower, so a short click still plays the full scale down and back. */
@media (prefers-reduced-motion: no-preference) {
  .personalize-button > label {
    transition:
      opacity var(--fg-fade-label) var(--fg-press-ease),
      margin var(--fg-press-up) var(--fg-press-ease),
      max-width var(--fg-press-up) var(--fg-press-ease);
  }
  .personalize-button > div > img,
  .fg-wallpaper-remove::before {
    transition: transform var(--fg-press-up) var(--fg-press-ease);
  }
  .personalize-button:active > div > img,
  .fg-wallpaper-remove:active::before {
    transform: scale(0.9);
    transition-duration: var(--fg-press-down);
    transition-timing-function: var(--fg-press-ease-down);
  }
  .open-customization-button::part(button) {
    transition:
      max-width var(--fg-press-up) var(--fg-press-ease),
      gap var(--fg-press-up) var(--fg-press-ease),
      background-color var(--fg-motion-fast) var(--fg-ease);
  }
  .open-customization-button::part(moz-button-label) {
    transition:
      opacity var(--fg-fade-label) var(--fg-press-ease),
      max-width var(--fg-press-up) var(--fg-press-ease);
  }
  .wallpaper-input.theme-custom-wallpaper::after {
    transition: transform var(--fg-press-up) var(--fg-press-ease);
  }
  .wallpaper-input.theme-custom-wallpaper:active::after {
    transform: translate(-50%, -50%) scale(0.85);
    transition-duration: var(--fg-press-down);
    transition-timing-function: var(--fg-press-ease-down);
  }
}
/* Image tiles tint on hover. Stock darkened them hard, and the empty add
 * tile had no background change at all. */
.wallpaper-input {
  transition:
    filter var(--fg-motion-fast) var(--fg-ease),
    background-color var(--fg-motion-fast) var(--fg-ease);
}
.wallpaper-input:hover {
  filter: brightness(var(--fg-hover-brightness));
}
.wallpaper-input.theme-custom-wallpaper:hover {
  background-color: var(--fg-hover);
}
.wallpapers-reset {
  transition: background-color var(--fg-motion-fast) var(--fg-ease);
}
.wallpapers-reset:hover {
  background-color: var(--fg-hover);
  border-radius: var(--border-radius-small);
}
.top-site-outer .context-menu-button {
  transition: background-color var(--fg-motion-fast) var(--fg-ease);
}
.top-site-outer .context-menu-button:hover {
  background-color: var(--fg-hover) !important;
  fill: var(--fg-text);
  color: var(--fg-text);
}
.top-site-outer .context-menu-button:hover:active {
  background-color: var(--fg-active) !important;
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
  <box id="firegila-tabs-slot">
    <box id="vertical-tabs-container">
      <box id="vertical-tabs" customizable="true" contextmenu="toolbar-context-menu"></box>
    </box>
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
        # The pin drop section is removed completely. Dragging never creates
        # a pinned tab now, so the indicator and promo have no purpose.
        ("""          <div id="pinned-drop-indicator">
            <html:img id="pinned-drop-indicator-icon" src="chrome://browser/skin/pin.svg" role="presentation" loading="lazy"/>
            <span id="pinned-drop-indicator-text" data-l10n-id="pinned-tabs-drop-indicator"></span>
          </div>
          <html:sidebar-pins-promo id="drag-to-pin-promo-card"></html:sidebar-pins-promo>
""", ""),
        # Page link command, context menu item and shortcut.
        ("""    <command id="Browser:DuplicateTab" />
""",
         """    <command id="Browser:DuplicateTab" />
    <command id="firegila-cmd-copy-page-link" />
"""),
        ("""<key id="key_duplicateTab" command="Browser:DuplicateTab"/>
""",
         """<key id="key_duplicateTab" command="Browser:DuplicateTab"/>
<key id="key_firegilaCopyPageLink" data-l10n-id="firegila-copy-page-link" command="firegila-cmd-copy-page-link" key="L" modifiers="accel,shift"/>
"""),
        ("""      <menuitem id="context-selectall"
                data-l10n-id="text-action-select-all"
                command="cmd_selectAll"/>
""",
         """      <menuitem id="context-selectall"
                data-l10n-id="text-action-select-all"
                command="cmd_selectAll"/>
      <menuseparator id="firegila-context-sep-page-link"/>
      <menuitem id="firegila-context-copy-page-link"
                data-l10n-id="firegila-context-copy-page-link"
                command="firegila-cmd-copy-page-link"/>
"""),
    ],
    # Dragging never turns a tab into a pinned tab. The pin drop section is
    # hidden and the stock flag is forced off, so the drag stays under the
    # pointer instead of snapping to the pinned area.
    "chrome/browser/content/browser/tabbrowser/drag-and-drop.js": [
        ("""        let shouldPin =
          movingTabs.some(t => isTab(t)) &&
          !draggedTab.pinned &&
          (overPinnedDropIndicator ||
            dragToPinTargets.some(el => el.contains(event.target)));
""",
         """        let shouldPin = false;
"""),
        ("""      this._pinnedDropIndicator = document.getElementById(
        "pinned-drop-indicator"
      );
      this._dragToPinPromoCard = document.getElementById(
        "drag-to-pin-promo-card"
      );
""",
         """      this._pinnedDropIndicator =
        document.getElementById("pinned-drop-indicator") ||
        document.createXULElement("box");
      this._dragToPinPromoCard =
        document.getElementById("drag-to-pin-promo-card") ||
        document.createXULElement("box");
      this._dragToPinPromoCard.shouldRender = false;
"""),
        ("""      let pinnedDropIndicator = draggedTabDocument.getElementById(
        "pinned-drop-indicator"
      );
      let draggedTabContainer =
        draggedTabDocument.documentGlobal.gBrowser.tabContainer;
      pinnedDropIndicator.removeAttribute("visible");
      pinnedDropIndicator.removeAttribute("interactive");
""",
         """      let pinnedDropIndicator = draggedTabDocument.getElementById(
        "pinned-drop-indicator"
      );
      let draggedTabContainer =
        draggedTabDocument.documentGlobal.gBrowser.tabContainer;
      pinnedDropIndicator?.removeAttribute("visible");
      pinnedDropIndicator?.removeAttribute("interactive");
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
        ("""            ${when(
              this.verticalTabsEnabled,
              () => html`
                ${when(
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
                <moz-checkbox
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
              `
            )}
            </moz-checkbox>
          </moz-fieldset>
""",
         """            </moz-checkbox>
            ${when(
              this.verticalTabsEnabled,
              () => html`
                <moz-checkbox
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
                  type="checkbox"
                  id="auto-collapse-tabs"
                  name="autoCollapseTabs"
                  data-l10n-id="firegila-auto-collapse-tabs"
                  @change=${this.#toggleAutoCollapseTabs}
                  ?checked=${Services.prefs.getBoolPref(
                    "firegila.sidebar.autoCollapseTabs",
                    false
                  )}
                ></moz-checkbox>
              `
            )}
          </moz-fieldset>
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
              id="tabs-opposite"
              name="tabsOpposite"
              data-l10n-id="firegila-tabs-opposite"
              @change=${this.#toggleTabsOpposite}
              ?checked=${Services.prefs.getBoolPref(
                "firegila.sidebar.tabsOpposite",
                false
              )}
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
    if (e.target.checked) {
      Services.prefs.setBoolPref(
        "firegila.sidebar.autoCollapseTabs",
        false
      );
    }
    this.requestUpdate();
  }

  #toggleAutoCollapseTabs(e) {
    e.stopPropagation();
    Services.prefs.setBoolPref(
      "firegila.sidebar.autoCollapseTabs",
      e.target.checked
    );
    if (e.target.checked) {
      Services.prefs.setBoolPref(
        "firegila.sidebar.autoHideTabs",
        false
      );
    }
    this.requestUpdate();
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
         "firegila-auto-collapse-tabs =\n  .label = Auto-collapse tabs\n\n"
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
         "firegila-workspace-delete-text = Delete \"{ $name }\" and close its { $count } tabs?\n\n"
         "firegila-tab-drop-split = Split view\n\n"
         "firegila-tab-drop-window = New window"),
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
    "chrome/browser/content/browser/preferences/preferences.xhtml": [
        ("""      <html:moz-page-nav-button id="category-tabs-browsing"
        view="paneTabsBrowsing"
        iconsrc="chrome://global/skin/icons/cursor-arrow.svg"
        data-l10n-id="pane-tabs-browsing-title2">
      </html:moz-page-nav-button>
""",
         """      <html:moz-page-nav-button id="category-tabs-browsing"
        view="paneTabsBrowsing"
        iconsrc="chrome://global/skin/icons/cursor-arrow.svg"
        data-l10n-id="pane-tabs-browsing-title2">
      </html:moz-page-nav-button>
      <html:moz-page-nav-button id="category-shortcuts"
        view="paneShortcuts"
        iconsrc="chrome://global/skin/icons/settings.svg"
        data-l10n-id="firegila-shortcuts-section">
      </html:moz-page-nav-button>
"""),
    ],
    "chrome/browser/content/browser/preferences/preferences.js": [
        ("""  tabsBrowsing: {
    l10nId: "tabs-browsing-section",
""", """  shortcuts: {
    l10nId: "firegila-shortcuts-section",
    iconSrc: "chrome://global/skin/icons/settings.svg",
    groupIds: ["firegilaShortcuts"],
    module:
      "chrome://browser/content/preferences/config/firegila-shortcuts.mjs",
    visible: () => true,
  },
  tabsBrowsing: {
    l10nId: "tabs-browsing-section",
"""),
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
        # Wallpaper uploads. Stock keeps one custom image. The list pref keeps
        # several, shown as a grid in the custom wallpaper subpanel. The
        # subpanel already scrolls, so only the slots are added.
        ("""      case "firefox":
        fluent_id = "newtab-wallpaper-category-title-firefox";
        break;
    }
    this.setState({
      activeCategoryFluentID: fluent_id
    });""",
         """      case "firefox":
        fluent_id = "newtab-wallpaper-category-title-firefox";
        break;
      case "custom-wallpaper":
        fluent_id = "newtab-wallpaper-title";
        break;
    }
    this.setState({
      activeCategoryFluentID: fluent_id
    });"""),
        ("""  handleWallpaperListEntered() {
    this.arrowButtonRef.current?.focus();
  }

  // Record user interaction when changing wallpaper and reseting wallpaper to default""",
         """  handleWallpaperListEntered() {
    this.arrowButtonRef.current?.focus();
  }

  handleUploadedSelect(uuid, theme) {
    this.props.setPref("newtabWallpapers.customWallpaper.uuid", uuid);
    this.props.setPref(
      "newtabWallpapers.customWallpaper.theme",
      theme || "dark"
    );
    this.props.setPref("newtabWallpapers.wallpaper", "custom");
    this.props.setPref("newtabWallpapers.initialWallpaper", "");
    this.props.setPref("newtabWallpapers.user.enabled", true);
  }

  handleUploadedRemove(event, uuid) {
    event.preventDefault();
    event.stopPropagation();
    this.props.dispatch(
      actionCreators.OnlyToMain({
        type: actionTypes.WALLPAPER_REMOVE_UPLOAD,
        data: { uuid },
      })
    );
  }

  // Record user interaction when changing wallpaper and reseting wallpaper to default"""),
        ("""    const wallpapersUserEnabled = prefs["newtabWallpapers.user.enabled"];
    const selectedWallpaper = prefs["newtabWallpapers.wallpaper"];""",
         """    const wallpapersUserEnabled = prefs["newtabWallpapers.user.enabled"];
    const selectedWallpaper = prefs["newtabWallpapers.wallpaper"];
    let uploadedWallpapers = [];
    try {
      uploadedWallpapers = JSON.parse(
        prefs["newtabWallpapers.customWallpaper.list"] || "[]"
      );
    } catch (e) {
      uploadedWallpapers = [];
    }
    if (!Array.isArray(uploadedWallpapers)) {
      uploadedWallpapers = [];
    }
    uploadedWallpapers = uploadedWallpapers.filter(item => item && item.uuid);
    const activeUuid = prefs["newtabWallpapers.customWallpaper.uuid"];
    if (!uploadedWallpapers.length && activeUuid) {
      uploadedWallpapers = [
        {
          uuid: activeUuid,
          theme: prefs["newtabWallpapers.customWallpaper.theme"] || "dark",
        },
      ];
    }"""),
        ("""        const activeWallpaperObj = activeWallpaper && sortedList.find(wp => wp.title === activeWallpaper);
        // Detect custom solid color
        const isCustomSolidColor = category === "solid-colors" && activeWallpaper.startsWith("solid-color-picker");
        const thumbnail = activeWallpaperObj || sortedList[0];""",
         """        const activeWallpaperObj = activeWallpaper && sortedList.find(wp => wp.title === activeWallpaper);
        // Detect custom solid color
        const isCustomSolidColor = category === "solid-colors" && activeWallpaper.startsWith("solid-color-picker");
        const customWallpaper = category === "custom-wallpaper" ? uploadedWallpapers.find(item => item.uuid === activeUuid) || uploadedWallpapers[0] : null;
        const hasCustomWallpaper = !!customWallpaper;
        const thumbnail = activeWallpaperObj || sortedList[0];"""),
        ("""          case "custom-wallpaper":
            // @nova-cleanup(remove-conditional): Remove novaEnabled conditional and always use newtab-wallpaper-add-an-image
            fluent_id = novaEnabled ? "newtab-wallpaper-add-an-image" : "newtab-wallpaper-upload-image";
            break;""",
         """          case "custom-wallpaper":
            // @nova-cleanup(remove-conditional): Remove novaEnabled conditional and always use newtab-wallpaper-add-an-image
            fluent_id = hasCustomWallpaper ? "newtab-wallpaper-title" : novaEnabled ? "newtab-wallpaper-add-an-image" : "newtab-wallpaper-upload-image";
            break;"""),
        ("""        } else {
          style.backgroundColor = thumbnail?.solid_color || "";
        }""",
         """        } else {
          style.backgroundColor = thumbnail?.solid_color || "";
        }
        if (customWallpaper) {
          style.backgroundImage = `url(moz-newtab-wallpaper://${customWallpaper.uuid})`;
          style.backgroundPosition = "center";
          style.backgroundColor = "";
        }"""),
        ("""        const isCategorySelected = wallpapersUserEnabled && (activeWallpaperObj || isCustomSolidColor);""",
         """        const isCustomWallpaperActive = category === "custom-wallpaper" && selectedWallpaper === "custom";
        const isCategorySelected = wallpapersUserEnabled && (activeWallpaperObj || isCustomSolidColor || isCustomWallpaperActive);"""),
        ("""          className: `wallpaper-input
                      ${category === "custom-wallpaper" ? "theme-custom-wallpaper" : ""}
                      ${isCategorySelected ? "selected" : ""}`,""",
         """          className: `wallpaper-input
                      ${category === "custom-wallpaper" ? "theme-custom-wallpaper" : ""}
                      ${customWallpaper ? "fg-has-upload" : ""}
                      ${isCategorySelected ? "selected" : ""}`,"""),
        ("""            if (category !== "custom-wallpaper") {
              this.handleCategory(event);
            } else {
              this.handleUpload();
            }""",
         """            this.handleCategory(event);"""),
        ("""      }), colorPickerInput)))))""",
         """      }), activeCategory === "custom-wallpaper" ? [
        ...uploadedWallpapers.map(item => /*#__PURE__*/external_React_default().createElement("div", {
          className: "fg-wallpaper-slot",
          key: `upload-${item.uuid}`
        }, /*#__PURE__*/external_React_default().createElement("input", {
          type: "radio",
          name: `wallpaper-upload-${item.uuid}`,
          id: `wallpaper-upload-${item.uuid}`,
          className: "wallpaper-input fg-uploaded-wallpaper",
          style: {
            backgroundImage: `url(moz-newtab-wallpaper://${item.uuid})`
          },
          checked: selectedWallpaper === "custom" && item.uuid === activeUuid,
          onChange: () => this.handleUploadedSelect(item.uuid, item.theme),
          "aria-label": "Uploaded wallpaper"
        }), /*#__PURE__*/external_React_default().createElement("button", {
          type: "button",
          className: "fg-wallpaper-remove",
          title: "Remove wallpaper",
          "aria-label": "Remove wallpaper",
          onClick: event => this.handleUploadedRemove(event, item.uuid)
        }))),
        /*#__PURE__*/external_React_default().createElement("div", {
          className: "fg-wallpaper-slot fg-wallpaper-add-slot",
          key: "fg-add-wallpaper"
        }, /*#__PURE__*/external_React_default().createElement("button", {
          type: "button",
          className: "wallpaper-input theme-custom-wallpaper fg-wallpaper-add",
          title: "Add an image",
          "aria-label": "Add an image",
          onClick: this.handleUpload
        }))
      ] : colorPickerInput)))))"""),
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
        ('''const PREF_WALLPAPERS_CUSTOM_WALLPAPER_UUID =
  "browser.newtabpage.activity-stream.newtabWallpapers.customWallpaper.uuid";''',
         '''const PREF_WALLPAPERS_CUSTOM_WALLPAPER_UUID =
  "browser.newtabpage.activity-stream.newtabWallpapers.customWallpaper.uuid";

const PREF_WALLPAPERS_CUSTOM_WALLPAPER_THEME =
  "browser.newtabpage.activity-stream.newtabWallpapers.customWallpaper.theme";

const PREF_WALLPAPERS_CUSTOM_WALLPAPER_LIST =
  "browser.newtabpage.activity-stream.newtabWallpapers.customWallpaper.list";

const PREF_WALLPAPERS_CUSTOM_WALLPAPER_MAX =
  "browser.newtabpage.activity-stream.newtabWallpapers.customWallpaper.max";'''),
        ('''  // Constructs a moz-newtab-wallpaper:// URI for the given wallpaper UUID.
  getWallpaperURL(uuid) {
    return `moz-newtab-wallpaper://${uuid}`;
  }''',
         '''  // Constructs a moz-newtab-wallpaper:// URI for the given wallpaper UUID.
  getWallpaperURL(uuid) {
    return `moz-newtab-wallpaper://${uuid}`;
  }

  readUploadedWallpapers() {
    let list = [];
    try {
      list = JSON.parse(
        Services.prefs.getStringPref(PREF_WALLPAPERS_CUSTOM_WALLPAPER_LIST, "[]")
      );
    } catch (error) {
      list = [];
    }
    if (!Array.isArray(list)) {
      list = [];
    }
    list = list.filter(
      item => item && typeof item.uuid === "string" && item.uuid
    );
    const currentUuid = Services.prefs.getStringPref(
      PREF_WALLPAPERS_CUSTOM_WALLPAPER_UUID,
      ""
    );
    if (currentUuid && !list.some(item => item.uuid === currentUuid)) {
      list.push({
        uuid: currentUuid,
        theme:
          Services.prefs.getStringPref(
            PREF_WALLPAPERS_CUSTOM_WALLPAPER_THEME,
            ""
          ) || "dark",
      });
    }
    return list;
  }

  writeUploadedWallpapers(list) {
    Services.prefs.setStringPref(
      PREF_WALLPAPERS_CUSTOM_WALLPAPER_LIST,
      JSON.stringify(list)
    );
  }

  async removeWallpaperFile(uuid) {
    if (!uuid) {
      return;
    }
    const wallpaperDir = PathUtils.join(PathUtils.profileDir, "wallpaper");
    await IOUtils.remove(PathUtils.join(wallpaperDir, uuid), {
      ignoreAbsent: true,
    });
  }'''),
        ('''      let uuid = Services.uuid.generateUUID().toString().slice(1, -1);
      Services.prefs.setStringPref(PREF_WALLPAPERS_CUSTOM_WALLPAPER_UUID, uuid);

      const filePath = PathUtils.join(wallpaperDir, uuid);

      // convert to Uint8Array for IOUtils
      const arrayBuffer = await file.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);

      await IOUtils.write(filePath, uint8Array, { tmpPath: `${filePath}.tmp` });

      const wallpaperURI = this.getWallpaperURL(uuid);''',
         '''      let uuid = Services.uuid.generateUUID().toString().slice(1, -1);

      const filePath = PathUtils.join(wallpaperDir, uuid);

      // convert to Uint8Array for IOUtils
      const arrayBuffer = await file.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);

      await IOUtils.write(filePath, uint8Array, { tmpPath: `${filePath}.tmp` });

      const list = this.readUploadedWallpapers();
      list.unshift({ uuid, theme: wallpaperTheme });
      const max = Math.max(
        1,
        Services.prefs.getIntPref(PREF_WALLPAPERS_CUSTOM_WALLPAPER_MAX, 100)
      );
      while (list.length > max) {
        const oldest = list.pop();
        if (oldest.uuid !== uuid) {
          await this.removeWallpaperFile(oldest.uuid);
        }
      }
      this.writeUploadedWallpapers(list);
      Services.prefs.setStringPref(PREF_WALLPAPERS_CUSTOM_WALLPAPER_UUID, uuid);

      const wallpaperURI = this.getWallpaperURL(uuid);'''),
        ('''  async removeCustomWallpaper() {
    try {
      let uuid = Services.prefs.getStringPref(
        PREF_WALLPAPERS_CUSTOM_WALLPAPER_UUID,
        ""
      );

      if (!uuid) {
        return;
      }

      const wallpaperDir = PathUtils.join(PathUtils.profileDir, "wallpaper");
      const filePath = PathUtils.join(wallpaperDir, uuid);

      await IOUtils.remove(filePath, { ignoreAbsent: true });

      Services.prefs.clearUserPref(PREF_WALLPAPERS_CUSTOM_WALLPAPER_UUID);

      this.store.dispatch(
        ac.BroadcastToContent({
          type: at.WALLPAPERS_CUSTOM_SET,
          data: null,
        })
      );
    } catch (error) {
      console.error("Failed to remove custom wallpaper:", error);
    }
  }''',
         '''  async removeCustomWallpaper(uuid) {
    try {
      const currentUuid = Services.prefs.getStringPref(
        PREF_WALLPAPERS_CUSTOM_WALLPAPER_UUID,
        ""
      );
      const target = uuid || currentUuid;

      if (!target) {
        return;
      }

      const list = this.readUploadedWallpapers();
      const removedIndex = list.findIndex(item => item.uuid === target);
      const remaining = list.filter(item => item.uuid !== target);
      if (remaining.length !== list.length) {
        this.writeUploadedWallpapers(remaining);
      }

      await this.removeWallpaperFile(target);

      if (target !== currentUuid) {
        return;
      }

      if (remaining.length) {
        const next =
          remaining[Math.min(Math.max(removedIndex, 0), remaining.length - 1)];
        Services.prefs.setStringPref(
          PREF_WALLPAPERS_CUSTOM_WALLPAPER_UUID,
          next.uuid
        );
        Services.prefs.setStringPref(
          PREF_WALLPAPERS_CUSTOM_WALLPAPER_THEME,
          next.theme || "dark"
        );
        const userEnabled = Services.prefs.getBoolPref(
          "browser.newtabpage.activity-stream.newtabWallpapers.user.enabled",
          false
        );
        if (userEnabled) {
          this.store.dispatch(
            ac.SetPref("newtabWallpapers.wallpaper", "custom")
          );
          this.store.dispatch(
            ac.SetPref("newtabWallpapers.initialWallpaper", "")
          );
          this.store.dispatch(
            ac.SetPref("newtabWallpapers.user.enabled", true)
          );
        }
        this.store.dispatch(
          ac.BroadcastToContent({
            type: at.WALLPAPERS_CUSTOM_SET,
            data: this.getWallpaperURL(next.uuid),
          })
        );
        return;
      }

      if (
        Services.prefs.prefHasUserValue(PREF_WALLPAPERS_CUSTOM_WALLPAPER_UUID)
      ) {
        Services.prefs.clearUserPref(PREF_WALLPAPERS_CUSTOM_WALLPAPER_UUID);
      }
      if (
        Services.prefs.prefHasUserValue(PREF_WALLPAPERS_CUSTOM_WALLPAPER_THEME)
      ) {
        Services.prefs.clearUserPref(PREF_WALLPAPERS_CUSTOM_WALLPAPER_THEME);
      }

      this.store.dispatch(ac.SetPref("newtabWallpapers.wallpaper", ""));
      this.store.dispatch(ac.SetPref("newtabWallpapers.initialWallpaper", ""));
      this.store.dispatch(ac.SetPref("newtabWallpapers.user.enabled", false));

      this.store.dispatch(
        ac.BroadcastToContent({
          type: at.WALLPAPERS_CUSTOM_SET,
          data: null,
        })
      );
    } catch (error) {
      console.error("Failed to remove custom wallpaper:", error);
    }
  }'''),
        ('''        if (
          action.data.name === "newtabWallpapers.customColor.enabled" ||
          action.data.name === "newtabWallpapers.customWallpaper.enabled" ||
          action.data.name === "newtabWallpapers.enabled" ||
          action.data.name === "nova.enabled"
        ) {
          this.wallpaperTeardown();
          await this.wallpaperSetup(false /* isStartup */);
        }
        if (action.data.name === "newtabWallpapers.highlightSeenCounter") {''',
         '''        if (
          action.data.name === "newtabWallpapers.customColor.enabled" ||
          action.data.name === "newtabWallpapers.customWallpaper.enabled" ||
          action.data.name === "newtabWallpapers.enabled" ||
          action.data.name === "nova.enabled"
        ) {
          this.wallpaperTeardown();
          await this.wallpaperSetup(false /* isStartup */);
        }
        if (action.data.name === "newtabWallpapers.customWallpaper.uuid") {
          const uuid = action.data.value;
          this.store.dispatch(
            ac.BroadcastToContent({
              type: at.WALLPAPERS_CUSTOM_SET,
              data: uuid ? this.getWallpaperURL(uuid) : null,
            })
          );
        }
        if (action.data.name === "newtabWallpapers.highlightSeenCounter") {'''),
        ('''      case at.WALLPAPER_REMOVE_UPLOAD:
        await this.removeCustomWallpaper();
        break;''',
         '''      case at.WALLPAPER_REMOVE_UPLOAD:
        await this.removeCustomWallpaper(action.data?.uuid);
        break;'''),
    ],
    "chrome/browser/builtin-addons/newtab/lib/ActivityStream.sys.mjs": [
        ('''  [
    "newtabWallpapers.customWallpaper.theme",
    {
      title: "theme ('light' | 'dark') of user uploaded wallpaper",
      value: "",
    },
  ],''',
         '''  [
    "newtabWallpapers.customWallpaper.theme",
    {
      title: "theme ('light' | 'dark') of user uploaded wallpaper",
      value: "",
    },
  ],
  [
    "newtabWallpapers.customWallpaper.list",
    {
      title: "JSON list of user uploaded wallpapers",
      value: "[]",
    },
  ],
  [
    "newtabWallpapers.customWallpaper.max",
    {
      title: "Maximum number of user uploaded wallpapers",
      value: 100,
    },
  ],'''),
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
:root {
  --fg-tab-border: light-dark(#d0d0d0, #232323);
  --fg-tab-bg: light-dark(#ededed, #1d1d1d);
  --fg-tab-bg-hover: light-dark(#d9d9d9, #383838);
  --fg-tab-bg-opposite: light-dark(#ededed, #1f1f1f);
  --fg-tab-bg-opposite-hover: light-dark(#cccccc, #383838);
}
:root:not([lwtheme]) {
  --tab-background-color-selected: light-dark(#ffffff, #333333);
  --tab-background-color-hover: var(--fg-tab-bg-hover);
  --tab-selected-textcolor: light-dark(#171717, #fafafa);
  --tab-border-color-accent: AccentColor;
  --tab-selected-shadow: none;
}
.tabbrowser-tab:not([selected], [multiselected]) > .tab-stack > .tab-background {
  background-color: var(--fg-tab-bg);
  border: 1px solid var(--fg-tab-border);
}
.tabbrowser-tab[selected] > .tab-stack > .tab-background,
.tabbrowser-tab[multiselected] > .tab-stack > .tab-background {
  border: 1px solid AccentColor;
}
/* Hover and selected use the same fade as the buttons and tiles. The stock
 * drag transition below still wins while a tab moves. */
.tabbrowser-tab > .tab-stack > .tab-background {
  transition:
    background-color var(--fg-motion-fast) var(--fg-ease),
    border-color var(--fg-motion-fast) var(--fg-ease);
}
.tab-audio-button::part(button) {
  -moz-context-properties: fill;
  fill: var(--fg-audio);
}
.tab-icon-overlay:is([soundplaying], [muted], [activemedia-blocked]) {
  -moz-context-properties: fill;
  fill: var(--fg-audio);
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
  --tabs-navbar-separator-color: var(--fg-tab-border);
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
  padding: var(--fg-tabs-tab-padding) !important;
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
  width: calc(100% - 2 * var(--fg-tabs-margin)) !important;
  min-width: 0 !important;
  margin-block: 2px !important;
  margin-inline: var(--fg-tabs-margin) !important;
  padding-inline: var(--fg-tabs-inset) !important;
  height: 32px !important;
  min-height: 32px !important;
  justify-content: start !important;
}
"""

# Tab groups. Folder labels use the group color and grouped tabs use a tint.
TAB_GROUP_CSS = """
/* Tab groups. Folder labels use the group color and grouped tabs use a tint.
 * One set of tokens drives both orientations and every interaction state. */

:root {
  --fg-group-label-pad: 24px;
  --fg-group-label-max-width: 10em;
  --fg-group-icon-size: 14px;
  --fg-group-chevron-size: 12px;
  --fg-group-chevron-size-compact: 8px;
  --fg-group-border-width: 1px;
  --fg-group-border-mix: 55%;
  --fg-group-border-mix-strong: 75%;
  --fg-group-tint: 18%;
  --fg-group-tint-closed: 24%;
  --fg-group-tint-hover: 26%;
  --fg-group-tint-active: 32%;
  --fg-tab-row-height: calc(var(--tab-min-height) + 2 * var(--fg-tabs-tab-padding));
}

/* The stock group line and the overflow count are removed in both
 * orientations. The chevron on the folder label carries the state instead. */
.tab-group-line,
.tab-group-label-container::after,
.tab-group-overflow-count-container,
.tab-group-overflow-count {
  display: none !important;
}

tab-group {
  --fg-group-accent: var(
    --tab-group-background-color,
    var(--tab-group-color)
  );
  --fg-group-base: var(--fg-tab-bg);
  --fg-group-hover: var(--fg-tab-bg-hover);
}

:root[fg-tabs-opposite] tab-group {
  --fg-group-base: var(--fg-tab-bg-opposite);
  --fg-group-hover: var(--fg-tab-bg-opposite-hover);
}

/* Grouped tabs. The group color is only a tint on the tab surface. */
tab-group > .tabbrowser-tab > .tab-stack > .tab-background,
tab-group > tab-split-view-wrapper .tabbrowser-tab > .tab-stack > .tab-background {
  border-color: color-mix(in srgb, var(--fg-group-accent) var(--fg-group-border-mix), var(--fg-tab-border)) !important;
  background-color: color-mix(in srgb, var(--fg-group-accent) var(--fg-group-tint), var(--fg-group-base)) !important;
}

tab-group > .tabbrowser-tab:not([selected], [multiselected]):hover > .tab-stack > .tab-background,
tab-group > tab-split-view-wrapper .tabbrowser-tab:not([selected], [multiselected]):hover > .tab-stack > .tab-background {
  border-color: color-mix(in srgb, var(--fg-group-accent) var(--fg-group-border-mix-strong), var(--fg-tab-border)) !important;
  background-color: color-mix(in srgb, var(--fg-group-accent) var(--fg-group-tint-hover), var(--fg-group-hover)) !important;
}

tab-group > .tabbrowser-tab:not([selected], [multiselected]):active > .tab-stack > .tab-background,
tab-group > tab-split-view-wrapper .tabbrowser-tab:not([selected], [multiselected]):active > .tab-stack > .tab-background {
  background-color: color-mix(in srgb, var(--fg-group-accent) var(--fg-group-tint-active), var(--fg-group-hover)) !important;
}

tab-group > .tabbrowser-tab[selected] > .tab-stack > .tab-background,
tab-group > .tabbrowser-tab[multiselected] > .tab-stack > .tab-background,
tab-group > tab-split-view-wrapper .tabbrowser-tab[selected] > .tab-stack > .tab-background,
tab-group > tab-split-view-wrapper .tabbrowser-tab[multiselected] > .tab-stack > .tab-background {
  border-color: AccentColor !important;
  background-color: color-mix(in srgb, var(--fg-group-accent) var(--fg-group-tint-hover), var(--tab-background-color-selected)) !important;
}

#tabbrowser-tabs[orient="vertical"][expanded] tab-group > .tabbrowser-tab {
  margin-inline-start: 0 !important;
}

/* The label row uses the same outer box as a tab row. */
.tab-group-label-container {
  position: relative;
  contain: none !important;
}

#tabbrowser-tabs[orient="vertical"] .tab-group-label-container {
  box-sizing: border-box;
  flex: 0 0 auto;
  width: calc(100% - 2 * var(--fg-tabs-margin)) !important;
  margin: 0 var(--fg-tabs-margin) !important;
  padding: var(--fg-tabs-tab-padding) 0 !important;
}

#tabbrowser-tabs[orient="vertical"][expanded] tab-group > .tab-group-label-container {
  margin-inline: var(--fg-tabs-margin) !important;
}

#tabbrowser-tabs[orient="horizontal"] .tab-group-label-container {
  flex: 0 0 auto;
  margin: 0 var(--fg-tabs-tab-padding) !important;
  padding: 0 !important;
}

.tab-group-label-hover-highlight {
  box-sizing: border-box;
  align-self: stretch;
  width: 100% !important;
  max-width: none !important;
  margin: 0 !important;
  padding: 0 !important;
  background-color: transparent !important;
  box-shadow: none !important;
}

.tab-group-label {
  position: relative;
  box-sizing: border-box;
  display: block;
  width: 100%;
  min-width: var(--tab-min-height);
  height: var(--tab-min-height);
  min-height: var(--tab-min-height);
  margin: 0 !important;
  padding: 0 var(--fg-group-label-pad) !important;
  border: var(--fg-group-border-width) solid color-mix(in srgb, var(--fg-group-accent) var(--fg-group-border-mix), var(--fg-tab-border)) !important;
  border-radius: var(--fg-radius) !important;
  border-end-start-radius: var(--fg-radius) !important;
  background-color: color-mix(in srgb, var(--fg-group-accent) var(--fg-group-tint), var(--fg-group-base)) !important;
  color: var(--fg-group-accent) !important;
  font-weight: var(--font-weight-semibold) !important;
  line-height: calc(var(--tab-min-height) - 2 * var(--fg-group-border-width)) !important;
  text-align: center;
  text-shadow: none !important;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition:
    background-color var(--fg-motion-fast) var(--fg-ease),
    border-color var(--fg-motion-fast) var(--fg-ease);
}

.tab-group-label:not(.tablist-keyboard-focus) {
  outline: none !important;
}

/* Folder icon and state chevron. A down chevron means open, a side chevron
 * means closed. The transform uses the shared fast motion token. */
.tab-group-label::before,
.tab-group-label::after {
  content: "";
  position: absolute;
  inset-block-start: 50%;
  background-position: center;
  background-repeat: no-repeat;
  -moz-context-properties: fill;
  fill: currentColor;
  pointer-events: none;
}

.tab-group-label::before {
  inset-inline-start: var(--fg-tabs-inset);
  width: var(--fg-group-icon-size);
  height: var(--fg-group-icon-size);
  transform: translateY(-50%);
  background-image: url("chrome://global/skin/icons/folder.svg");
  background-size: var(--fg-group-icon-size);
}

.tab-group-label::after {
  inset-inline-end: var(--fg-tabs-inset);
  width: var(--fg-group-chevron-size);
  height: var(--fg-group-chevron-size);
  transform: translateY(-50%);
  background-image: url("chrome://global/skin/icons/arrow-down-12.svg");
  background-size: var(--fg-group-chevron-size);
  opacity: 0.7;
  transition:
    transform var(--fg-motion-fast) var(--fg-ease),
    opacity var(--fg-motion-fast) var(--fg-ease);
}

tab-group[collapsed] > .tab-group-label-container .tab-group-label::after {
  transform: translateY(-50%) rotate(-90deg);
  opacity: 1;
}

tab-group[collapsed] > .tab-group-label-container .tab-group-label:-moz-locale-dir(rtl)::after {
  transform: translateY(-50%) rotate(90deg);
}

/* A closed folder reads as a denser tint and a stronger border. */
tab-group[collapsed] > .tab-group-label-container .tab-group-label {
  background-color: color-mix(in srgb, var(--fg-group-accent) var(--fg-group-tint-closed), var(--fg-group-base)) !important;
  border-color: color-mix(in srgb, var(--fg-group-accent) var(--fg-group-border-mix-strong), var(--fg-tab-border)) !important;
}

tab-group .tab-group-label:hover,
tab-group[collapsed] > .tab-group-label-container .tab-group-label:hover {
  border-color: color-mix(in srgb, var(--fg-group-accent) var(--fg-group-border-mix-strong), var(--fg-tab-border)) !important;
  background-color: color-mix(in srgb, var(--fg-group-accent) var(--fg-group-tint-hover), var(--fg-group-hover)) !important;
}

tab-group .tab-group-label:hover::after {
  opacity: 1;
}

tab-group .tab-group-label:active,
tab-group[collapsed] > .tab-group-label-container .tab-group-label:active {
  background-color: color-mix(in srgb, var(--fg-group-accent) var(--fg-group-tint-active), var(--fg-group-hover)) !important;
  transition-duration: var(--fg-press-down);
}

tab-group[hasactivetab] > .tab-group-label-container .tab-group-label {
  border-color: color-mix(in srgb, var(--fg-group-accent) var(--fg-group-border-mix-strong), var(--fg-tab-border)) !important;
}

/* Vertical groups expand and collapse by animating each hidden tab row to
 * zero height. The row keeps its box, so the strip settles in one motion and
 * no other tab jumps. Stock hides these rows with display: none. */
#tabbrowser-arrowscrollbox[orient="vertical"] tab-group > .tabbrowser-tab {
  flex: 0 0 var(--fg-tab-row-height) !important;
  height: var(--fg-tab-row-height) !important;
  min-height: var(--fg-tab-row-height) !important;
  max-height: var(--fg-tab-row-height) !important;
  transition:
    flex-basis var(--fg-tabs-motion) var(--fg-ease),
    height var(--fg-tabs-motion) var(--fg-ease),
    min-height var(--fg-tabs-motion) var(--fg-ease),
    max-height var(--fg-tabs-motion) var(--fg-ease),
    padding-block var(--fg-tabs-motion) var(--fg-ease),
    opacity var(--fg-tabs-motion) var(--fg-ease);
}

#tabbrowser-tabs[orient="vertical"] #tabbrowser-arrowscrollbox[orient="vertical"] tab-group[collapsed]:not([movingtabgroup]) > .tabbrowser-tab:not([visuallyselected], [multiselected]) {
  display: flex !important;
  flex: 0 0 0 !important;
  height: 0 !important;
  min-height: 0 !important;
  max-height: 0 !important;
  padding-block: 0 !important;
  opacity: 0;
  overflow: clip !important;
  overflow-clip-margin: 0 !important;
  pointer-events: none;
}

/* Horizontal groups animate the same way: the hidden tabs collapse their
 * inline size and fade, instead of snapping out of the strip. */
#tabbrowser-tabs[orient="horizontal"] tab-group > .tabbrowser-tab {
  transition:
    min-width var(--fg-tabs-motion) var(--fg-ease),
    max-width var(--fg-tabs-motion) var(--fg-ease),
    padding-inline var(--fg-tabs-motion) var(--fg-ease),
    opacity var(--fg-tabs-motion) var(--fg-ease);
}

#tabbrowser-tabs[orient="horizontal"] tab-group[collapsed]:not([movingtabgroup]) > .tabbrowser-tab:not([visuallyselected], [multiselected]) {
  opacity: 0;
}

.tab-group-label[dragover-groupTarget] {
  outline: 1px solid AccentColor !important;
  outline-offset: -1px;
}

/* Horizontal label. The label padding reserves the chevron. */
#tabbrowser-tabs[orient="horizontal"] .tab-group-label {
  width: auto;
  max-width: var(--fg-group-label-max-width);
  min-width: var(--tab-min-height);
  padding-inline: var(--fg-group-label-pad) !important;
  height: var(--tab-min-height) !important;
  min-height: var(--tab-min-height) !important;
  line-height: calc(var(--tab-min-height) - 2 * var(--fg-group-border-width)) !important;
  margin: auto 0 !important;
}

/* An unnamed group is a square folder tile, the same box as a tab. */
#tabbrowser-tabs[orient="horizontal"] tab-group[label="\\200b"] .tab-group-label {
  width: var(--tab-min-height) !important;
  min-width: var(--tab-min-height) !important;
  max-width: var(--tab-min-height) !important;
  padding: 0 !important;
  font-size: 0;
}

#tabbrowser-tabs[orient="horizontal"] tab-group[label="\\200b"] .tab-group-label::before {
  inset-inline-start: 50%;
  transform: translate(calc(-50% - var(--fg-tabs-tab-padding)), -50%);
}

#tabbrowser-tabs[orient="horizontal"] tab-group[label="\\200b"] .tab-group-label:-moz-locale-dir(rtl)::before {
  transform: translate(calc(-50% + var(--fg-tabs-tab-padding)), -50%);
}

#tabbrowser-tabs[orient="horizontal"] tab-group[label="\\200b"] .tab-group-label::after {
  inset-inline-end: var(--fg-tabs-tab-padding);
  width: var(--fg-group-chevron-size-compact);
  height: var(--fg-group-chevron-size-compact);
  background-size: var(--fg-group-chevron-size-compact);
}

#tabbrowser-tabs[orient="vertical"] .tab-group-label {
  width: 100% !important;
  max-width: none !important;
  height: var(--tab-min-height) !important;
  min-height: var(--tab-min-height) !important;
  line-height: calc(var(--tab-min-height) - 2 * var(--fg-group-border-width)) !important;
}

/* Collapsed strip tile. Same box and spacing as a collapsed tab. */
@container fg-tabs-width (max-width: 48px) {
  #tabbrowser-tabs[orient="vertical"] .tab-group-label-container {
    width: var(--tab-min-height) !important;
    margin: 0 var(--fg-tabs-margin) !important;
  }

  #tabbrowser-tabs[orient="vertical"] .tab-group-label {
    width: var(--tab-min-height) !important;
    max-width: var(--tab-min-height) !important;
    min-width: var(--tab-min-height) !important;
    height: var(--tab-min-height) !important;
    min-height: var(--tab-min-height) !important;
    padding: 0 !important;
    font-size: 0;
    line-height: calc(var(--tab-min-height) - 2 * var(--fg-group-border-width)) !important;
  }

  #tabbrowser-tabs[orient="vertical"] .tab-group-label::before {
    inset-inline-start: 50%;
    transform: translate(calc(-50% - var(--fg-tabs-tab-padding)), -50%);
  }

  #tabbrowser-tabs[orient="vertical"] .tab-group-label:-moz-locale-dir(rtl)::before {
    transform: translate(calc(-50% + var(--fg-tabs-tab-padding)), -50%);
  }

  #tabbrowser-tabs[orient="vertical"] .tab-group-label::after {
    inset-inline-end: var(--fg-tabs-tab-padding);
    width: var(--fg-group-chevron-size-compact);
    height: var(--fg-group-chevron-size-compact);
    background-size: var(--fg-group-chevron-size-compact);
  }
}

/* Split view. One tab slot, two half tabs. The wrapper adds no surface,
 * padding, gap or divider of its own. */

#tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr;
  gap: 0 !important;
  box-sizing: border-box;
  flex: 0 0 auto !important;
  width: calc(100% - 2 * var(--fg-tabs-margin)) !important;
  height: var(--fg-tab-row-height) !important;
  margin: 0 var(--fg-tabs-margin) !important;
  padding: 0 !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  outline: none !important;
  box-shadow: none !important;
}

#tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper[hasactivetab],
#tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper:hover {
  background: transparent !important;
  outline: none !important;
}

#tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper .tabbrowser-tab {
  box-sizing: border-box;
  width: 100% !important;
  height: var(--fg-tab-row-height) !important;
  min-height: var(--fg-tab-row-height) !important;
  max-height: var(--fg-tab-row-height) !important;
  flex: 1 1 auto !important;
  margin: 0 !important;
  padding: var(--fg-tabs-tab-padding) 0 !important;
  border: 0 !important;
}

#tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper .tabbrowser-tab > .tab-stack > .tab-background {
  box-sizing: border-box;
  width: 100% !important;
  min-width: 0 !important;
  height: var(--tab-min-height) !important;
  min-height: var(--tab-min-height) !important;
  margin: 0 !important;
  border-radius: var(--fg-radius) !important;
}

#tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper .tabbrowser-tab:first-child > .tab-stack > .tab-background {
  border-start-end-radius: 0 !important;
  border-end-end-radius: 0 !important;
  border-inline-end: 0 !important;
}

#tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper .tabbrowser-tab:last-child > .tab-stack > .tab-background {
  border-start-start-radius: 0 !important;
  border-end-start-radius: 0 !important;
  border-inline-start: 0 !important;
}

#tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper .tabbrowser-tab:last-child {
  border-inline-start: 0 !important;
}

#tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper .tab-content {
  padding-inline: var(--fg-tabs-inset) !important;
}

/* Collapsed strip: one 32px tile split into two 16px rows. The inset border
 * belongs to the tile, not to either tab, so there is no middle divider. */
@container fg-tabs-width (max-width: 48px) {
  #tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr 1fr;
    width: var(--tab-min-height) !important;
    height: var(--tab-min-height) !important;
    margin: var(--fg-tabs-tab-padding) var(--fg-tabs-margin) !important;
    border: 0 !important;
    border-radius: var(--fg-radius) !important;
    box-shadow: inset 0 0 0 1px var(--fg-tab-border) !important;
    overflow: hidden;
  }

  #tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper[hasactivetab] {
    box-shadow: inset 0 0 0 1px AccentColor !important;
  }

  #tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper .tabbrowser-tab {
    height: calc(var(--tab-min-height) / 2) !important;
    min-height: calc(var(--tab-min-height) / 2) !important;
    max-height: calc(var(--tab-min-height) / 2) !important;
    padding: 0 !important;
  }

  #tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper .tabbrowser-tab > .tab-stack > .tab-background {
    width: 100% !important;
    height: calc(var(--tab-min-height) / 2) !important;
    min-height: calc(var(--tab-min-height) / 2) !important;
    margin: 0 !important;
    border: 0 !important;
    border-radius: 0 !important;
  }

  #tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper .tab-content {
    box-sizing: border-box;
    width: 100% !important;
    height: 100% !important;
    padding: 0 !important;
    justify-content: center !important;
  }

  #tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper .tab-icon-image,
  #tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper .tab-throbber {
    width: 12px !important;
    height: 12px !important;
    margin: 0 !important;
  }

  #tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper .tab-close-button,
  #tabbrowser-tabs[orient="vertical"] tab-split-view-wrapper .tab-label-container {
    display: none !important;
  }
}

/* Horizontal split uses the same one-slot footprint as a normal tab. */
#tabbrowser-tabs[orient="horizontal"] tab-split-view-wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr;
  gap: 0 !important;
  align-items: stretch !important;
  box-sizing: border-box;
  flex: 100 100 !important;
  min-width: var(--tab-min-width-pref, var(--tab-min-width)) !important;
  max-width: var(--tab-max-width) !important;
  margin: 0 !important;
  padding: 0 !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  outline: none !important;
  box-shadow: none !important;
}

#tabbrowser-tabs[orient="horizontal"] tab-split-view-wrapper[hasactivetab],
#tabbrowser-tabs[orient="horizontal"] tab-split-view-wrapper:hover {
  background: transparent !important;
  outline: none !important;
}

#tabbrowser-tabs[orient="horizontal"] tab-split-view-wrapper .tabbrowser-tab {
  box-sizing: border-box;
  height: 100% !important;
  margin: 0 !important;
  padding: 0 var(--fg-tabs-tab-padding) !important;
  border: 0 !important;
}

#tabbrowser-tabs[orient="horizontal"] tab-split-view-wrapper .tabbrowser-tab > .tab-stack > .tab-background {
  box-sizing: border-box;
  width: 100% !important;
  height: var(--tab-min-height) !important;
  min-height: var(--tab-min-height) !important;
  margin-block: var(--tab-block-margin) !important;
  margin-inline: 0 !important;
  border-radius: var(--fg-radius) !important;
}

#tabbrowser-tabs[orient="horizontal"] tab-split-view-wrapper .tabbrowser-tab:first-child > .tab-stack > .tab-background {
  border-start-end-radius: 0 !important;
  border-end-end-radius: 0 !important;
  border-inline-end: 0 !important;
}

#tabbrowser-tabs[orient="horizontal"] tab-split-view-wrapper .tabbrowser-tab:last-child > .tab-stack > .tab-background {
  border-start-start-radius: 0 !important;
  border-end-start-radius: 0 !important;
  border-inline-start: 0 !important;
}

#tabbrowser-tabs[orient="horizontal"] tab-split-view-wrapper .tabbrowser-tab:last-child {
  border-inline-start: 0 !important;
}

/* Vertical drop indicator. Same pin look as the horizontal one, rotated for
 * rows. The element has no height, so it never shifts the strip. */
#tabbrowser-tabs[orient="vertical"] > .tab-drop-indicator {
  position: relative;
  width: calc(100% - 2 * var(--fg-tabs-margin)) !important;
  height: 0 !important;
  margin: 0 var(--fg-tabs-margin) !important;
  background: none !important;
}

#tabbrowser-tabs[orient="vertical"] > .tab-drop-indicator::before {
  content: "";
  position: absolute;
  inset-block-start: -5px;
  inset-inline-start: 0;
  width: 10px;
  height: 10px;
  box-sizing: border-box;
  border: 2px solid var(--fg-tabbar);
  border-radius: 50%;
  background-color: AccentColor;
  box-shadow: 0 1px 2px light-dark(rgba(0, 0, 0, 0.25), rgba(0, 0, 0, 0.55));
  pointer-events: none;
}

#tabbrowser-tabs[orient="vertical"] > .tab-drop-indicator::after {
  content: "";
  position: absolute;
  inset-block-start: -1px;
  inset-inline: 5px 0;
  height: 2px;
  border-radius: 1px;
  background-color: AccentColor;
  pointer-events: none;
}

/* Tab group editor. */
/* Tab group editor. */
.tab-group-editor-panel {
  --panel-background-color: var(--fg-bg);
  --panel-border-color: var(--fg-border);
  --panel-text-color: var(--fg-text);
  --panel-border-radius: var(--fg-radius);
}

.tab-group-editor-panel .tab-group-editor-name input {
  appearance: none;
  background-color: var(--fg-bg-3);
  border: 1px solid var(--fg-border);
  border-radius: var(--border-radius-medium);
  color: var(--fg-text);
  padding: 6px 10px;
}

.tab-group-editor-panel .tab-group-editor-name input:focus {
  border-color: AccentColor;
  outline: none;
}

.tab-group-editor-panel .tab-group-editor-swatch {
  box-sizing: border-box;
  width: 18px;
  height: 18px;
  padding: 0;
  background-clip: border-box;
  border: 1px solid var(--fg-border);
  border-radius: 6px;
}

.tab-group-editor-panel input:checked + .tab-group-editor-swatch {
  border-color: AccentColor;
  outline: 1px solid AccentColor;
  outline-offset: 1px;
}

/* Drag targets use the accent color. */
#tabbrowser-tabs[movingtab-group] .tabbrowser-tab[dragover-groupTarget] > .tab-stack > .tab-background,
#tabbrowser-tabs[movingtab-group] .tabbrowser-tab > .tab-stack > .tab-background[dragover-groupTarget] {
  background-color: var(--fg-hover) !important;
  outline: 1px solid AccentColor !important;
  outline-offset: -1px;
}
"""# Flat content area. Stock draws a hairline outline around the page and rounds
# the corner next to the sidebar. Firegila keeps it square and borderless.
CONTENT_AREA_CSS = """
.browserContainer {
  box-sizing: border-box;
  outline: none;
  border: 1px solid var(--fg-divider);
  border-radius: 0 !important;
  overflow: clip;
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
  background-color: var(--fg-bg-3) !important;
  transition:
    background-color var(--fg-motion-fast) var(--fg-ease),
    border-color var(--fg-motion-fast) var(--fg-ease),
    width 100ms ease-out,
    height 100ms ease-out !important;
}
.top-site-outer:hover .tile,
.top-site-outer:focus-within .tile,
.top-site-outer.add-button:hover .tile,
.top-site-outer.add-button:focus-within .tile,
.nova-enabled .top-site-outer:hover .tile,
.nova-enabled .top-site-outer:focus-within .tile,
.nova-enabled .top-site-outer.add-button:hover .tile,
.nova-enabled .top-site-outer.add-button:focus-within .tile {
  background-color: var(--fg-hover) !important;
}
.top-site-outer .tile:active,
.top-site-outer.add-button .tile:active,
.nova-enabled .top-site-outer .tile:active,
.nova-enabled .top-site-outer.add-button .tile:active {
  box-shadow: none !important;
  border: 1px solid var(--fg-border) !important;
  background-color: var(--fg-active) !important;
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
  transition: background-color var(--fg-motion-fast) var(--fg-ease);
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
  background: var(--fg-hover) !important;
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
/* Uploaded wallpapers. The stock subpanel is already a three column grid
   with its own scroll, so each upload is one slot next to the add tile. */
.wallpaper-input.theme-custom-wallpaper.fg-has-upload::after {
  display: none;
}
.wallpaper-input.theme-custom-wallpaper.fg-has-upload {
  border: none;
}
.fg-wallpaper-slot {
  position: relative;
  min-width: 0;
}
.fg-wallpaper-slot .wallpaper-input {
  display: block;
}
.fg-wallpaper-remove {
  position: absolute;
  inset-block-start: 4px;
  inset-inline-end: 4px;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  inline-size: 22px;
  block-size: 22px;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background-color: var(--fg-bg-3);
  color: var(--fg-text);
  cursor: pointer;
  transition: background-color var(--fg-motion-fast) var(--fg-ease);
}
.fg-wallpaper-remove::before {
  content: "";
  display: block;
  inline-size: 12px;
  block-size: 12px;
  background-image: url("chrome://global/skin/icons/close.svg");
  background-position: center;
  background-repeat: no-repeat;
  background-size: 12px;
  -moz-context-properties: fill;
  fill: var(--fg-text);
}
.fg-wallpaper-remove:hover {
  background-color: var(--fg-hover);
}
.fg-wallpaper-remove:active {
  background-color: var(--fg-active);
}
.fg-wallpaper-remove:focus-visible {
  outline: 1px solid AccentColor;
  outline-offset: 1px;
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

:root {
  --fg-tabs-tab-padding: 2px;
  --fg-tabs-collapsed-width: var(--fg-navbar-height, var(--tab-min-height));
  --fg-pinned-columns: 4;
  /* The tabs column reveal is longer than the base motion, so the wide
   * width and pinned grid slide settle together. */
  --fg-tabs-motion: 160ms;
}

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

/* Panel: plain full height section, no radius, no divider on the strip side.
 * Width is the stored drag size when there is one, else 500px. */

#sidebar-box {
  box-sizing: border-box;
  padding-block-end: 0;
  margin-block-end: 0;
  overflow: clip;
  background-color: var(--fg-bg);
  border-radius: 0;
  outline: none;
  width: var(--fg-panel-width, 500px);
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
  position: relative;
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-height: 0;
  background-color: var(--fg-tabbar);
}

/* Drop targets for a tab drag. They overlay the empty end of the column so
 * the strip never grows or shifts while a drag is active. */
#firegila-tab-dropzones {
  display: none;
  position: absolute;
  inset-inline: var(--fg-tabs-margin);
  inset-block-end: calc(2 * var(--fg-tabs-margin));
  z-index: var(--browser-area-z-index-sidebar-expand-on-hover);
  flex-direction: column;
  gap: var(--fg-tabs-margin);
  pointer-events: none;
}

:root:has(#tabbrowser-tabs[movingtab]) #firegila-tab-dropzones,
:root[fg-tab-drag-hover] #firegila-tab-dropzones {
  display: flex;
}

.firegila-tab-dropzone {
  display: flex;
  align-items: center;
  gap: var(--fg-tabs-inset);
  box-sizing: border-box;
  min-height: var(--tab-min-height);
  padding-inline: var(--fg-tabs-inset);
  border: 1px solid var(--fg-border);
  border-radius: var(--fg-radius);
  background-color: var(--fg-bg);
  color: var(--fg-text);
  font-weight: var(--font-weight-semibold);
  pointer-events: auto;
  transition:
    background-color var(--fg-motion-fast) var(--fg-ease),
    border-color var(--fg-motion-fast) var(--fg-ease);
}

.firegila-tab-dropzone:hover,
.firegila-tab-dropzone[dragover] {
  border-color: AccentColor;
  background-color: var(--fg-hover);
}

.firegila-tab-dropzone > image {
  width: 16px;
  height: 16px;
  -moz-context-properties: fill;
  fill: currentColor;
}

#vertical-tabs {
  flex-grow: 1;
  min-height: 0;
}

@media -moz-pref("sidebar.verticalTabs") {
  #vertical-tabs-container {
    width: var(--fg-tabs-width);
  }

  /* One spacing system for every vertical tabs mode. The tab row keeps the
   * same 4px side margin and 12px content inset whether auto-collapse is on,
   * off, or auto-hide. */
  #tabbrowser-tabs[orient="vertical"] {
    gap: 2px !important;
    width: 100% !important;
    min-width: 0 !important;
  }

  #vertical-tabs {
    width: 100% !important;
    min-width: 0 !important;
  }

  #tabbrowser-tabs[orient="vertical"] .tabbrowser-tab > .tab-stack > .tab-background {
    /* The tab itself carries 2px of inline padding. The margin is reduced by
     * that amount so the visible gap still matches the 4px token. */
    width: calc(100% - 2 * (var(--fg-tabs-margin) - 2px)) !important;
    margin-inline: calc(var(--fg-tabs-margin) - 2px) !important;
  }

  #tabbrowser-tabs[orient="vertical"] .tab-content {
    padding-inline: calc(var(--fg-tabs-margin) + var(--fg-tabs-inset) - 2px) !important;
  }

  #tabbrowser-tabs[orient="vertical"] .tab-label-container {
    flex: 1 1 auto;
    min-width: 0;
    max-width: 100%;
    overflow: hidden;
    mask-image: none !important;
  }

  #tabbrowser-tabs[orient="vertical"] .tab-label {
    flex: 1 1 auto;
    min-width: 0;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  #tabbrowser-tabs[orient="vertical"] > #vertical-tabs-newtab-button > .toolbarbutton-text,
  #tabbrowser-arrowscrollbox[orient="vertical"] > #tabbrowser-arrowscrollbox-periphery > #tabs-newtab-button > .toolbarbutton-text {
    min-width: 0;
    max-width: 20ch;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

/* Hiding the sidebar keeps the tabs column. The hide button closes the
 * strip and panel only. */

/* The slot is a real flex item so the stock position code can order it. A
 * display:contents wrapper ignores its own order and moves the tabs to the
 * far edge. */
#firegila-tabs-slot {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* Without vertical tabs the stock strip lives in the toolbar. The held slot
 * must not keep an empty column in layout. */
@media not -moz-pref("sidebar.verticalTabs") {
  #firegila-tabs-slot {
    display: none !important;
  }
}

/* Pinned tabs in vertical mode. Up to four square tiles per row. The grid
 * fills the bar, so the tile size follows the row width. One tile per row in
 * the collapsed strip. Equal 4px gaps and padding, default tab border. No
 * splitter and no divider. */
#vertical-pinned-tabs-splitter {
  display: none !important;
}

#pinned-tabs-container[orient="vertical"] {
  flex: 0 0 auto !important;
  width: 100% !important;
  max-width: 100% !important;
  min-width: 0 !important;
  overflow: hidden !important;
  height: auto !important;
  max-height: none !important;
  min-height: 0 !important;
  padding-inline: 0 !important;
}

:root:not([sidebar-expand-on-hover]) #pinned-tabs-container[orient="vertical"]::part(scrollbox) {
  overflow: hidden !important;
  padding: 0 !important;
}

:root:not([sidebar-expand-on-hover]) #pinned-tabs-container[orient="vertical"]::part(items-wrapper) {
  display: grid !important;
  grid-template-columns: repeat(var(--fg-pinned-columns), minmax(var(--tab-collapsed-background-width), 1fr)) !important;
  grid-auto-rows: 32px !important;
  justify-content: stretch !important;
  align-items: stretch !important;
  gap: var(--fg-tabs-margin) !important;
  padding: 2px var(--fg-tabs-margin) 0 !important;
}

/* The grid pans between the collapsed column and the full grid. The slide
 * shares the width timing, so the active tile stays in view and the tiles
 * never jump when the state flips. */
:root[fg-autocollapse-tabs] #pinned-tabs-container[orient="vertical"]::part(items-wrapper) {
  transition: transform var(--fg-tabs-motion) var(--fg-ease);
  will-change: transform;
}

:root:not([sidebar-expand-on-hover]) #pinned-tabs-container[orient="vertical"] .tabbrowser-tab {
  width: 100% !important;
  min-width: var(--tab-collapsed-background-width) !important;
  max-width: none !important;
  height: 32px !important;
  min-height: 32px !important;
  max-height: 32px !important;
  margin: 0 !important;
  padding: 0 !important;
}

:root:not([sidebar-expand-on-hover]) #pinned-tabs-container[orient="vertical"] .tabbrowser-tab > .tab-stack > .tab-background {
  box-sizing: border-box;
  width: 100% !important;
  min-width: 0 !important;
  height: 100% !important;
  min-height: 0 !important;
  margin: 0 !important;
  border: 1px solid var(--fg-tab-border) !important;
  border-radius: var(--fg-radius) !important;
  background-color: var(--fg-tab-bg) !important;
}

:root:not([sidebar-expand-on-hover]) #pinned-tabs-container[orient="vertical"] .tabbrowser-tab:not([selected], [multiselected]):hover > .tab-stack > .tab-background {
  background-color: var(--fg-tab-bg-hover) !important;
}

:root:not([sidebar-expand-on-hover]) #pinned-tabs-container[orient="vertical"] .tabbrowser-tab[selected] > .tab-stack > .tab-background,
:root:not([sidebar-expand-on-hover]) #pinned-tabs-container[orient="vertical"] .tabbrowser-tab[multiselected] > .tab-stack > .tab-background {
  border-color: AccentColor !important;
  background-color: var(--tab-background-color-selected) !important;
}

/* In the collapsed strip the grid slides horizontally to the active pinned
 * column. The row and order stay the same, and one tab from every row stays
 * visible. */
:root[fg-autocollapse-tabs]:not([fg-tabs-revealed]) #pinned-tabs-container[orient="vertical"]::part(items-wrapper) {
  transform: translateX(
    calc(-1 * var(--fg-pinned-column, 0) * (var(--tab-collapsed-background-width) + var(--fg-tabs-margin)))
  );
}

:root:not([sidebar-expand-on-hover]) #pinned-tabs-container[orient="vertical"] .tab-content {
  padding: 0 !important;
  justify-content: center !important;
  align-items: center !important;
}

:root:not([sidebar-expand-on-hover]) #pinned-tabs-container[orient="vertical"] .tab-icon-image,
:root:not([sidebar-expand-on-hover]) #pinned-tabs-container[orient="vertical"] .tab-throbber {
  margin: 0 !important;
}

:root:not([sidebar-expand-on-hover]) #pinned-tabs-container[orient="vertical"] .tab-label-container,
:root:not([sidebar-expand-on-hover]) #pinned-tabs-container[orient="vertical"] .tab-close-button {
  display: none !important;
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
    transition: transform var(--fg-tabs-motion) var(--fg-ease);
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
}

/* Auto-collapse tabs. The column keeps the sidebar strip width in layout and
 * expands to the full vertical bar on hover. One width transition drives the
 * bar, the tabs and the workspace row. Margins stay fixed, so the text is
 * clipped with an ellipsis at every point instead of being hidden or moved. */
@media -moz-pref("sidebar.verticalTabs") {
  :root[fg-autocollapse-tabs] #firegila-tabs-slot {
    display: block;
    position: relative;
    flex: 0 0 var(--fg-tabs-collapsed-width);
    width: var(--fg-tabs-collapsed-width);
    min-width: var(--fg-tabs-collapsed-width);
    z-index: var(--browser-area-z-index-sidebar-expand-on-hover);
  }

  :root[fg-autocollapse-tabs] #vertical-tabs-container {
    display: flex;
    flex-direction: column;
    position: absolute;
    inset-block: 0;
    inset-inline-start: 0;
    inset-inline-end: auto;
    width: var(--fg-tabs-collapsed-width);
    background-color: var(--fg-tabbar);
    transition: width var(--fg-tabs-motion) var(--fg-ease);
    z-index: var(--browser-area-z-index-sidebar-expand-on-hover);
    overflow: hidden;
    container-type: inline-size;
    container-name: fg-tabs-width;
  }

  :root[fg-autocollapse-tabs][fg-tabs-revealed] #vertical-tabs-container {
    width: var(--fg-tabs-width);
  }

  /* Anchor on the same side the tabs column occupies. */
  :root[fg-autocollapse-tabs]:has(#sidebar-container[sidebar-positionend]) #vertical-tabs-container,
  :root[fg-autocollapse-tabs][fg-tabs-opposite] #vertical-tabs-container {
    inset-inline-start: auto;
    inset-inline-end: 0;
  }

  :root[fg-autocollapse-tabs][fg-tabs-opposite]:has(#sidebar-container[sidebar-positionend]) #vertical-tabs-container {
    inset-inline-start: 0;
    inset-inline-end: auto;
  }

  /* Clicks wait for the open motion, so the menu anchor never moves. */
  :root[fg-autocollapse-tabs] #vertical-tabs-container > #firegila-workspaces {
    pointer-events: none;
  }

  :root[fg-autocollapse-tabs][fg-tabs-open] #vertical-tabs-container > #firegila-workspaces {
    pointer-events: auto;
  }

  /* A native tab drag keeps the column fully open even if a pointer event is
   * lost. Stock sets movingtab for the whole drag, including group creation. */
  :root[fg-autohide-tabs]:has(#tabbrowser-tabs:is([movingtab], [movingtab-group], [movingtab-addToGroup], [movingtab-ungroup])) #vertical-tabs-container,
  :root[fg-autocollapse-tabs]:has(#tabbrowser-tabs:is([movingtab], [movingtab-group], [movingtab-addToGroup], [movingtab-ungroup])) #vertical-tabs-container {
    transform: none !important;
    width: var(--fg-tabs-width) !important;
  }

  :root[fg-autocollapse-tabs]:has(#tabbrowser-tabs:is([movingtab], [movingtab-group], [movingtab-addToGroup], [movingtab-ungroup])) #pinned-tabs-container[orient="vertical"]::part(items-wrapper) {
    transform: none !important;
  }
}

/* Collapsed state: icons only. Text, the close box and the chevron wait for
 * room, then the width reveal grows them letter by letter. */
@container fg-tabs-width (max-width: 48px) {
  :root[fg-autocollapse-tabs] #tabbrowser-tabs[orient="vertical"] .tab-label-container,
  :root[fg-autocollapse-tabs] #tabbrowser-tabs[orient="vertical"] .tab-close-button,
  :root[fg-autocollapse-tabs] #tabbrowser-tabs[orient="vertical"] > #vertical-tabs-newtab-button > .toolbarbutton-text,
  :root[fg-autocollapse-tabs] #tabbrowser-arrowscrollbox[orient="vertical"] > #tabbrowser-arrowscrollbox-periphery > #tabs-newtab-button > .toolbarbutton-text,
  :root[fg-autocollapse-tabs] #vertical-tabs-container > #firegila-workspaces > .toolbarbutton-text {
    max-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    opacity: 0;
  }

  :root[fg-autocollapse-tabs] #vertical-tabs-container > #firegila-workspaces {
    justify-content: center;
  }

  :root[fg-autocollapse-tabs] #vertical-tabs-container > #firegila-workspaces > .firegila-workspace-arrow-box {
    max-width: 12px !important;
    margin-inline: 0 !important;
    opacity: 1;
  }

  /* The stock audio button does not fit a 32px collapsed tab. Use the stock
   * small audio overlay instead. */
  :root[fg-autocollapse-tabs] #tabbrowser-tabs[orient="vertical"] .tab-audio-button {
    display: none !important;
  }

  :root[fg-autocollapse-tabs] #tabbrowser-tabs[orient="vertical"] .tab-icon-overlay:is([soundplaying], [muted], [activemedia-blocked]):not([crashed]) {
    display: revert !important;
    --audio-overlay-extra-background: transparent;
    background-color: var(--lwt-accent-color);
    -moz-context-properties: fill;
    fill: var(--fg-audio);
    color-scheme: var(--tab-selected-color-scheme);
    border-radius: var(--border-radius-circle);
    background-image: image(var(--audio-overlay-extra-background)), image(var(--toolbox-background-color));
  }

  :root[fg-autocollapse-tabs] #tabbrowser-tabs[orient="vertical"] .tabbrowser-tab[selected] .tab-icon-overlay:is([soundplaying], [muted], [activemedia-blocked]):not([crashed]) {
    background-image:
      image(var(--audio-overlay-extra-background)), image(var(--tab-background-color-selected)),
      image(var(--toolbox-background-color));
  }

  :root[fg-autocollapse-tabs] #tabbrowser-tabs[orient="vertical"] .tab-icon-overlay:is([soundplaying], [muted], [activemedia-blocked]):not([crashed]):-moz-window-inactive {
    background-image:
      image(var(--audio-overlay-extra-background)), image(var(--toolbox-background-color-inactive));
  }

  :root[fg-autocollapse-tabs] #tabbrowser-tabs[orient="vertical"] .tabbrowser-tab[selected] .tab-icon-overlay:is([soundplaying], [muted], [activemedia-blocked]):not([crashed]):-moz-window-inactive {
    background-image:
      image(var(--audio-overlay-extra-background)), image(var(--tab-background-color-selected)),
      image(var(--toolbox-background-color-inactive));
  }

  :root[fg-autocollapse-tabs] #tabbrowser-tabs[orient="vertical"] .tab-icon-overlay:is([soundplaying], [muted], [activemedia-blocked]):not([crashed]):hover {
    --audio-overlay-extra-background: var(--button-background-color-ghost-hover);
  }

  :root[fg-autocollapse-tabs] #tabbrowser-tabs[orient="vertical"] .tab-icon-overlay:is([soundplaying], [muted], [activemedia-blocked]):not([crashed]):hover:active {
    --audio-overlay-extra-background: var(--button-background-color-ghost-active);
  }

  :root[fg-autocollapse-tabs] #tabbrowser-tabs[orient="vertical"] .tab-icon-overlay[soundplaying] {
    list-style-image: url("chrome://browser/skin/tabbrowser/tab-audio-playing-small.svg");
  }

  :root[fg-autocollapse-tabs] #tabbrowser-tabs[orient="vertical"] .tab-icon-overlay[muted] {
    list-style-image: url("chrome://browser/skin/tabbrowser/tab-audio-muted-small.svg");
  }

  :root[fg-autocollapse-tabs] #tabbrowser-tabs[orient="vertical"] .tab-icon-overlay[activemedia-blocked] {
    list-style-image: url("chrome://browser/skin/tabbrowser/tab-audio-blocked-small.svg");
  }
}

@media (prefers-reduced-motion: reduce) {
  :root[fg-autohide-tabs] #vertical-tabs-container,
  :root[fg-autocollapse-tabs] #vertical-tabs-container,
  :root[fg-autocollapse-tabs] #pinned-tabs-container[orient="vertical"]::part(items-wrapper),
  .tab-group-label,
  .tab-group-label::after,
  #tabbrowser-arrowscrollbox[orient="vertical"] tab-group > .tabbrowser-tab,
  #tabbrowser-tabs[orient="horizontal"] tab-group > .tabbrowser-tab {
    transition: none;
  }
}

/* A workspace popup pins the strip. The column keeps the resting width, so
 * the menu and dialog anchors stay still while the popup is open. The button
 * keeps the same padding as the revealed state, so it never shifts. */
:root[fg-tabs-reveal-pinned][fg-autohide-tabs] #vertical-tabs-container,
:root[fg-tabs-context-pinned][fg-autohide-tabs] #vertical-tabs-container {
  transition: none;
  transform: none;
  width: var(--fg-tabs-width);
}

:root[fg-tabs-reveal-pinned][fg-autocollapse-tabs] #vertical-tabs-container,
:root[fg-tabs-context-pinned][fg-autocollapse-tabs] #vertical-tabs-container {
  transition: none !important;
  width: var(--fg-tabs-width) !important;
}

/* A popup opens at the full width in one step. The pinned grid does the same,
 * so it stays under the menu anchor. */
:root[fg-tabs-reveal-pinned][fg-autocollapse-tabs] #pinned-tabs-container[orient="vertical"]::part(items-wrapper),
:root[fg-tabs-context-pinned][fg-autocollapse-tabs] #pinned-tabs-container[orient="vertical"]::part(items-wrapper) {
  transition: none !important;
}

/* Tabs on the opposite side of the sidebar. Stock writes order inline as
 * 1..N on every child, so the values here sit outside that range and important
 * beats the inline style. Auto-hide only needs the inset flipped. */

/* The column carries the strip surface in every mode now, so the tab fill and
 * border keep the same separation as before. */

:root[fg-tabs-opposite] .tabbrowser-tab:not([selected], [multiselected]) > .tab-stack > .tab-background {
  border-color: var(--fg-tab-border);
}

/* Not on hover, so the stock hover rule still wins. */

:root[fg-tabs-opposite] .tabbrowser-tab:not([selected], [multiselected]):not(:hover) > .tab-stack > .tab-background {
  background-color: var(--fg-tab-bg-opposite);
}

@media -moz-pref("sidebar.verticalTabs") {
  :root[fg-tabs-opposite]:not([lwtheme]) {
    --tab-background-color-hover: var(--fg-tab-bg-opposite-hover);
  }
}

:root[fg-tabs-opposite]:not(:has(#sidebar-container[sidebar-positionend])) #firegila-tabs-slot {
  order: 9999 !important;
}

:root[fg-tabs-opposite]:has(#sidebar-container[sidebar-positionend]) #firegila-tabs-slot {
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

/* Pressed feedback. Only the round icon box scales. Menu buttons are left out
 * so their panels keep the same anchor. */

@media (prefers-reduced-motion: no-preference) {
  .tab-close-button,
  .button-icon {
    transition: transform var(--fg-press-up) var(--fg-press-ease);
  }

  .toolbarbutton-1:not(#firegila-workspaces, #unified-extensions-button, #PanelUI-menu-button, #downloads-button, #library-button, [type="menu"], [aria-haspopup]) .toolbarbutton-icon {
    transition:
      transform var(--fg-press-up) var(--fg-press-ease),
      background-color var(--fg-motion-fast) var(--fg-ease),
      border-color var(--fg-motion-fast) var(--fg-ease);
  }

  .urlbar-page-action:not([aria-haspopup]) .urlbar-icon,
  .tabbrowser-tab .tab-icon-image {
    transition: transform var(--fg-press-up) var(--fg-press-ease);
  }

  .tab-close-button:active,
  button:active > .button-icon,
  .toolbarbutton-1:active:not([disabled]):not(#firegila-workspaces, #unified-extensions-button, #PanelUI-menu-button, #downloads-button, #library-button, [type="menu"], [aria-haspopup]) .toolbarbutton-icon,
  .urlbar-page-action:active:not([disabled]):not([aria-haspopup]) .urlbar-icon,
  .tabbrowser-tab:active .tab-icon-image {
    transform: scale(0.9);
    transition-duration: var(--fg-press-down);
    transition-timing-function: var(--fg-press-ease-down);
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
  position: relative;
  align-items: center;
  flex: 0 0 auto;
  box-sizing: border-box;
  width: 150px;
  height: 32px;
  min-height: 32px;
  margin-block: 4px;
  margin-inline: 4px 2px;
  padding: 0 8px;
  border: 1px solid var(--fg-tab-border);
  border-radius: 8px;
  background-color: var(--fg-tab-bg);
  color: var(--fg-text);
}

#firegila-workspaces:hover {
  background-color: var(--fg-tab-bg-hover);
}

/* Same shift as the background tabs when the strip sits on the other side. */

:root[fg-tabs-opposite] .toolbar-items > #firegila-workspaces {
  background-color: var(--fg-tab-bg-opposite);
}

:root[fg-tabs-opposite] .toolbar-items > #firegila-workspaces:hover {
  background-color: var(--fg-tab-bg-hover);
}

/* The workspaces icon. The label and chevron share the same 8px gap as the
 * tab icon and label. */

/* The switcher shows its label and chevron only. The folder icon is gone. */
#firegila-workspaces > .toolbarbutton-icon {
  display: none !important;
}

#firegila-workspaces > .toolbarbutton-text {
  display: block;
  flex: 1 1 auto;
  min-width: 0;
  max-width: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
  contain: inline-size;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: start;
}

/* The row itself carries the hover and open fill. Stock also paints the icon
 * and label boxes, which adds inner squares and shifts the glyph on click. */
#firegila-workspaces > .toolbarbutton-icon,
#firegila-workspaces > .toolbarbutton-text,
#firegila-workspaces > .firegila-workspace-arrow-box {
  background-color: transparent !important;
  outline: none !important;
}

/* Chevron. A real image in currentColor, so it follows the text in both
 * modes. The box is ordered after the label. */

#firegila-workspaces > .firegila-workspace-arrow-box {
  order: -1;
  display: flex;
  flex: 0 0 12px;
  justify-content: center;
  align-items: center;
  width: 12px;
  max-width: 12px;
  overflow: hidden;
  margin-inline: 0 8px;
  /* Clicks on the chevron must hit the menu button itself, so the popup
   * opens from any part of the button. */
  pointer-events: none;
}

/* One audio dot style everywhere: 6px, neutral theme color, round. On the workspace
 * button it is a corner badge, so the label and chevron never move. */

#firegila-workspaces .firegila-workspace-audio {
  display: none;
  position: absolute;
  inset-block-start: 4px;
  inset-inline-end: 4px;
  width: 6px;
  height: 6px;
  margin: 0;
  border-radius: 50%;
  background-color: var(--fg-audio);
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

/* The switcher does not scale on press. The label and chevron stay fixed. */
#firegila-workspaces,
#firegila-workspaces > .toolbarbutton-text,
#firegila-workspaces > .firegila-workspace-arrow-box {
  transform: none !important;
}

#vertical-tabs-container > #firegila-workspaces {
  position: relative;
  display: flex !important;
  align-items: center;
  overflow: hidden;
  contain: layout paint;
  flex: 0 0 auto;
  width: calc(100% - 2 * var(--fg-tabs-margin));
  max-width: none;
  height: 32px;
  min-height: 32px;
  margin-block: var(--fg-tabs-margin) 2px;
  margin-inline: var(--fg-tabs-margin);
  padding-inline: calc(var(--fg-tabs-inset) + 1px);
  border: 1px solid var(--fg-tab-border);
  border-radius: 8px;
  background-color: var(--fg-tab-bg);
}

#vertical-tabs-container > #firegila-workspaces:hover {
  background-color: var(--fg-tab-bg-hover);
}

/* The workspace list uses the app surfaces, not the GTK menu colors, so it
 * matches the popups that belong to Firegila. */

#firegila-workspace-menu {
  --panel-padding: 4px;
  --panel-background-color: var(--fg-bg);
  --panel-border-color: var(--fg-border);
  --panel-text-color: var(--fg-text);
  /* Script replaces this with the live button width, so the list is exactly
   * as wide as the button in both tab modes. The minimum keeps the menu
   * readable when the button is narrower than its labels. */
  --panel-width: 200px;
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
  background-color: var(--fg-audio);
}

/* Sidebar audio dot. Same 6px neutral circle as the workspace button and the
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
  background-color: var(--fg-audio);
  pointer-events: none;
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

/* Website audio dots use the shared neutral token. The stock green token is
 * scoped to direct moz-button children, so override it there. */

.fg-webpanel-list,
.fg-webpanel-list > moz-button {
  --button-attention-dot-color: var(--fg-audio) !important;
  --button-badge-background-color: var(--fg-audio) !important;
  --button-badge-size: 6px;
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
  const AUTO_COLLAPSE_PREF = "firegila.sidebar.autoCollapseTabs";
  const OPPOSITE_PREF = "firegila.sidebar.tabsOpposite";
  const { SessionStore } = ChromeUtils.importESModule(
    "resource:///modules/sessionstore/SessionStore.sys.mjs"
  );
  const { ShortcutUtils } = ChromeUtils.importESModule(
    "resource://gre/modules/ShortcutUtils.sys.mjs"
  );
  const SHORTCUTS_PREF = "firegila.shortcuts";
  const COMMAND_LABELS = {
    cmd_newNavigator: "New window",
    cmd_newNavigatorTabNoEvent: "New tab",
    "Browser:OpenLocation": "Focus address bar",
    "Tools:Search": "Focus search",
    "Browser:OpenFile": "Open file",
    "Browser:SavePage": "Save page",
    cmd_print: "Print",
    cmd_close: "Close tab",
    cmd_closeWindow: "Close window",
    cmd_toggleMute: "Mute tab",
    "Tools:Downloads": "Downloads",
    "Tools:Addons": "Add-ons",
    "Browser:Back": "Back",
    "Browser:Forward": "Forward",
    "Browser:Reload": "Reload",
    "Browser:ReloadSkipCache": "Reload skipping cache",
    "Browser:ShowAllHistory": "History",
    "Browser:AddBookmarkAs": "Bookmark this page",
    "Browser:ShowAllBookmarks": "Bookmarks",
    "Browser:DuplicateTab": "Duplicate tab",
    "firegila-cmd-copy-page-link": "Copy page link",
    "Browser:AddTabSplitView": "Add split view",
    "Browser:SeparateTabSplitView": "Separate split view",
    "Browser:Stop": "Stop loading",
    "Browser:NextTab": "Next tab",
    "Browser:PrevTab": "Previous tab",
    "Browser:ShowAllTabs": "List all tabs",
    cmd_find: "Find",
    cmd_findAgain: "Find again",
    cmd_findPrevious: "Find previous",
    "View:FullScreen": "Full screen",
    "View:PageSource": "Page source",
    "View:PageInfo": "Page info",
    "Tools:PrivateBrowsing": "Private window",
    "Tools:Sanitize": "Clear recent history",
  };
  const REVEAL_DELAY = 100;
  const POINTER_RELEASE_DELAY = 80;
  const COLLAPSE_SETTLE_DELAY = 40;
  const TAB_DROP_TYPE = "application/x-moz-tabbrowser-tab";
  let revealTimer = 0;
  let openTimer = 0;
  let collapseTimer = 0;
  let contextPins = 0;
  let interactionPinned = false;
  let pointerHeld = false;
  let pointerSerial = 0;
  let draggingTabs = false;
  let dragHover = false;
  let shortcutDefaults = null;
  let tabsRestored = false;
  let pinnedColumns = 0;
  const DEFAULT_BOOKMARKS_PREF = "firegila.migration.defaultBookmarks";
  const STRICT_TRACKING_PREF = "firegila.migration.strictTracking";
  const GPC_PREF = "firegila.migration.globalPrivacyControl";
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
  // Existing profiles start on Standard. Move that exact stock value to
  // Strict once, and leave a custom or strict choice alone.
  function migrateStrictTracking() {
    if (Services.prefs.getBoolPref(STRICT_TRACKING_PREF, false)) {
      return;
    }
    try {
      if (
        Services.prefs.getStringPref(
          "browser.contentblocking.category",
          "standard"
        ) === "standard"
      ) {
        Services.prefs.setStringPref(
          "browser.contentblocking.category",
          "strict"
        );
      }
    } catch (e) {}
    Services.prefs.setBoolPref(STRICT_TRACKING_PREF, true);
  }

  // Tell sites not to sell or share data. Existing profiles opt in once on
  // upgrade, and the default pref covers every new profile.
  function migrateGlobalPrivacyControl() {
    if (Services.prefs.getBoolPref(GPC_PREF, false)) {
      return;
    }
    try {
      Services.prefs.setBoolPref(
        "privacy.globalprivacycontrol.functionality.enabled",
        true
      );
      Services.prefs.setBoolPref("privacy.globalprivacycontrol.enabled", true);
    } catch (e) {}
    Services.prefs.setBoolPref(GPC_PREF, true);
  }

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
    const vertical = Services.prefs.getBoolPref("sidebar.verticalTabs", false);
    tabs.toggleAttribute("expanded", vertical);
    syncTabsMode();
    if (!vertical) {
      document.documentElement.removeAttribute("fg-tabs-revealed");
      document.documentElement.removeAttribute("fg-tabs-open");
    }
  }

  function start() {
    publishMotion();
    publishNavbarMetrics();
    persistPanelWidth();
    syncTabStripExpanded();
    captureShortcutDefaults();
    applyShortcuts();
    installShortcutApi();
    Services.prefs.addObserver(SHORTCUTS_PREF, applyShortcuts);
    migrateDefaultBookmarks();
    // user.js lands after the first window in some profiles. Run the privacy
    // defaults again once startup has settled, guarded so they run once.
    window.setTimeout(() => {
      migrateStrictTracking();
      migrateGlobalPrivacyControl();
    }, 500);
    watchSidebarHidden();
    watchRevealEnter();
    watchRevealLeave();
    watchEdgeSensor();
    watchTabsContextMenu();
    watchTabInteraction();
    patchDragStart();
    watchExternalDrag();
    createTabDropZones();
    watchTabGroupPanels();
    watchFiregilaCommands();
    watchPinnedTabs();
    watchPinnedColumn();
    Services.prefs.addObserver("sidebar.verticalTabs", syncTabStripExpanded);
  }

  // Auto-hide tabs. The column floats at the window edge, so a reveal is one
  // attribute flip and the stylesheet animates the width. The state is set
  // before the sidebar renders, so the first frame is already collapsed.
  function syncAutoHide() {
    const on =
      Services.prefs.getBoolPref("sidebar.verticalTabs", false) &&
      Services.prefs.getBoolPref(AUTO_HIDE_PREF, false) &&
      !Services.prefs.getBoolPref(AUTO_COLLAPSE_PREF, false);
    document.documentElement.toggleAttribute("fg-autohide-tabs", on);
    if (!on) {
      document.documentElement.removeAttribute("fg-tabs-revealed");
      document.documentElement.removeAttribute("fg-tabs-open");
    }
  }

  // Auto-collapse keeps the column in layout at the strip width. The same
  // reveal attribute drives the expansion, so both tabs modes share the
  // pointer handling and only one can be active.
  function syncAutoCollapse() {
    const on =
      Services.prefs.getBoolPref("sidebar.verticalTabs", false) &&
      Services.prefs.getBoolPref(AUTO_COLLAPSE_PREF, false);
    document.documentElement.toggleAttribute("fg-autocollapse-tabs", on);
    if (!on) {
      document.documentElement.removeAttribute("fg-tabs-revealed");
      document.documentElement.removeAttribute("fg-tabs-open");
    }
  }

  function syncTabsMode() {
    syncAutoHide();
    syncAutoCollapse();
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

  // The open attribute only lands after the reveal motion. Labels use it to
  // fade in without ever changing layout while the column moves.
  function motionDuration() {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return 0;
    }
    return parseFloat(
      getComputedStyle(document.documentElement).getPropertyValue(
        "--fg-tabs-motion"
      )
    );
  }

  function setRevealed(on) {
    clearTimeout(revealTimer);
    clearTimeout(openTimer);
    clearTimeout(collapseTimer);
    const root = document.documentElement;
    if (
      !on &&
      (root.hasAttribute("fg-tabs-reveal-pinned") ||
        root.hasAttribute("fg-tabs-context-pinned") ||
        root.hasAttribute("fg-tabs-interaction-pinned") ||
        tabStripIsMoving() ||
        dragHover)
    ) {
      return;
    }
    if (!on) {
      root.removeAttribute("fg-tabs-revealed");
      root.removeAttribute("fg-tabs-open");
      return;
    }
    root.setAttribute("fg-tabs-revealed", "");
    const delay = motionDuration();
    if (!delay) {
      root.setAttribute("fg-tabs-open", "");
      return;
    }
    openTimer = window.setTimeout(() => {
      if (root.hasAttribute("fg-tabs-revealed")) {
        root.setAttribute("fg-tabs-open", "");
      }
    }, delay);
  }

  // Let the pointer settle after a popup closes or a tab is dropped. Hover
  // state arrives a frame late, so checking it immediately made the column
  // close even when the pointer was still inside it.
  function requestCollapse() {
    clearTimeout(collapseTimer);
    collapseTimer = window.setTimeout(() => {
      const tabs = document.getElementById("vertical-tabs-container");
      if (tabs && tabs.matches(":hover")) {
        return;
      }
      setRevealed(false);
    }, COLLAPSE_SETTLE_DELAY);
  }

  // A context menu keeps the column open even when the pointer leaves it to
  // use the menu.
  function pinContextReveal() {
    if (!Services.prefs.getBoolPref("sidebar.verticalTabs", false)) {
      return;
    }
    contextPins++;
    const root = document.documentElement;
    root.setAttribute("fg-tabs-context-pinned", "");
    root.setAttribute("fg-tabs-revealed", "");
    root.setAttribute("fg-tabs-open", "");
  }

  function unpinContextReveal() {
    contextPins = Math.max(0, contextPins - 1);
    if (contextPins) {
      return;
    }
    const root = document.documentElement;
    root.removeAttribute("fg-tabs-context-pinned");
    requestCollapse();
  }

  // A press in the tabs column, or a tab drag, pins the reveal for the whole
  // gesture. Tab drags leave the column, so mouseleave alone would collapse
  // it mid gesture.
  function pinInteraction() {
    if (!Services.prefs.getBoolPref("sidebar.verticalTabs", false)) {
      return;
    }
    const root = document.documentElement;
    root.setAttribute("fg-tabs-interaction-pinned", "");
    root.setAttribute("fg-tabs-revealed", "");
    root.setAttribute("fg-tabs-open", "");
  }

  function unpinInteraction() {
    const root = document.documentElement;
    root.removeAttribute("fg-tabs-interaction-pinned");
    requestCollapse();
  }

  function tabStripIsMoving() {
    const strip = document.getElementById("tabbrowser-tabs");
    return !!strip && strip.hasAttribute("movingtab");
  }

  function syncInteractionPin() {
    const vertical = Services.prefs.getBoolPref(
      "sidebar.verticalTabs",
      false
    );
    const active =
      vertical &&
      (pointerHeld || draggingTabs || dragHover || tabStripIsMoving());
    if (active === interactionPinned) {
      return;
    }
    interactionPinned = active;
    if (active) {
      pinInteraction();
    } else {
      unpinInteraction();
    }
  }

  function holdPointer() {
    pointerSerial++;
    pointerHeld = true;
    syncInteractionPin();
  }

  // Hold the pin briefly after a release. A native tab drag sets movingtab
  // after the press, and a slow drag threshold must not drop the pin before
  // the strip reports the drag.
  function releasePointer() {
    const serial = ++pointerSerial;
    window.setTimeout(() => {
      if (serial !== pointerSerial) {
        return;
      }
      if (draggingTabs || dragHover || tabStripIsMoving()) {
        return;
      }
      pointerHeld = false;
      syncInteractionPin();
    }, POINTER_RELEASE_DELAY);
  }

  // Cross-window tab drags carry the tab flavor into this window. Reveal the
  // column on entry so a collapsed strip can accept the drop, and keep it
  // open until the drag leaves or the drop settles.
  function isTabDrag(event) {
    return !!event.dataTransfer?.types?.includes(TAB_DROP_TYPE);
  }

  function splitTargets(element) {
    const gb = window.gBrowser;
    if (!gb || !element || gb.isTabGroupLabel(element)) {
      return [];
    }
    let targets = (
      element.multiselected
        ? gb.selectedElements
        : [element.splitview || element]
    ).filter(target => target && !target.closing);
    if (!targets.length) {
      return [];
    }
    if (targets.length === 1) {
      const index = gb.tabs.indexOf(targets[0]);
      const candidates = gb.visibleTabs.filter(
        tab =>
          tab !== targets[0] &&
          !tab.pinned &&
          !tab.closing &&
          !tab.hidden &&
          !gb.isTabGroupLabel(tab)
      );
      candidates.sort(
        (a, b) =>
          Math.abs(gb.tabs.indexOf(a) - index) -
          Math.abs(gb.tabs.indexOf(b) - index)
      );
      const partner = candidates[0];
      if (!partner) {
        return [];
      }
      targets.push(partner);
    }
    return targets;
  }

  // A custom drop target runs before the stock drop cleanup. Remove every
  // inline drag style first so split view and new window never inherit a
  // transform or a frozen width from the drag.
  function clearDragState() {
    const gb = window.gBrowser;
    const strip = gb?.tabContainer;
    if (!strip) {
      return;
    }
    const dnd = strip.tabDragAndDrop;
    try {
      dnd?.finishAnimateTabMove();
    } catch (e) {}
    try {
      dnd?._resetTabsAfterDrop(document);
    } catch (e) {}
    for (const attr of [
      "movingtab",
      "movingtab-group",
      "movingtab-ungroup",
      "movingtab-addToGroup",
    ]) {
      strip.removeAttribute(attr);
    }
    const indicator = strip.querySelector(".tab-drop-indicator");
    if (indicator) {
      indicator.hidden = true;
    }
    for (const el of strip.querySelectorAll(
      ".tabbrowser-tab, tab-split-view-wrapper, .tab-group-label-container, .tab-group-label"
    )) {
      el.style.transform = "";
      el.style.width = "";
      el.style.height = "";
      el.style.maxWidth = "";
      el.style.left = "";
      el.style.top = "";
      el.style.pointerEvents = "";
      el.removeAttribute("dragtarget");
      el.removeAttribute("small-stack");
      el.removeAttribute("big-stack");
      delete el.currentIndex;
    }
  }

  function createTabDropZones() {
    const container = document.getElementById("vertical-tabs-container");
    if (!container || document.getElementById("firegila-tab-dropzones")) {
      return;
    }
    const zones = document.createXULElement("box");
    zones.id = "firegila-tab-dropzones";
    const items = [
      [
        "split",
        "firegila-tab-drop-split",
        "chrome://browser/skin/split-view-left-16.svg",
      ],
      [
        "window",
        "firegila-tab-drop-window",
        "chrome://global/skin/icons/open-in-new.svg",
      ],
    ];
    for (const [action, l10nId, icon] of items) {
      const zone = document.createXULElement("box");
      zone.className = "firegila-tab-dropzone";
      zone.setAttribute("data-action", action);
      const image = document.createXULElement("image");
      image.setAttribute("src", icon);
      const label = document.createXULElement("label");
      label.setAttribute("data-l10n-id", l10nId);
      zone.append(image, label);
      zone.addEventListener("dragover", event => {
        if (!isTabDrag(event)) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        zone.setAttribute("dragover", "");
      });
      zone.addEventListener("dragleave", () => {
        zone.removeAttribute("dragover");
      });
      zone.addEventListener("drop", event => {
        if (!isTabDrag(event)) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        zone.removeAttribute("dragover");
        let element;
        try {
          element = event.dataTransfer.mozGetDataAt(TAB_DROP_TYPE, 0);
        } catch (e) {
          element = null;
        }
        const gb = window.gBrowser;
        if (!element || !gb) {
          return;
        }
        clearDragState();
        if (action === "split") {
          const targets = splitTargets(element);
          if (targets.length < 2) {
            return;
          }
          const split = gb.addTabSplitView(targets);
          if (split?.tabs?.length) {
            gb.selectedTab = split.tabs[0];
          }
          return;
        }
        gb.replaceTabsWithWindow(element);
      });
      zones.appendChild(zone);
    }
    container.appendChild(zones);
    document.l10n?.translateElements?.([
      ...zones.querySelectorAll("[data-l10n-id]"),
    ]);
  }

  // Keep the grabbed vertical tab centered under the pointer from the first
  // frame. Stock records the pointer offset, which leaves the row above the
  // cursor when the grab starts near the bottom of the tab.
  function patchDragStart() {
    const proto = window.TabDragAndDrop?.prototype;
    if (!proto || proto._firegilaCentered) {
      return;
    }
    proto._firegilaCentered = true;
    const original = proto.handle_dragstart;
    proto.handle_dragstart = function (event) {
      const result = original.call(this, event);
      if (!Services.prefs.getBoolPref("sidebar.verticalTabs", false)) {
        return result;
      }
      const tab = event.target?.closest?.("tab");
      const data = tab?._dragData;
      if (!data) {
        return result;
      }
      const rect = tab.getBoundingClientRect();
      if (rect.height) {
        const top =
          typeof tab.screenY === "number"
            ? tab.screenY
            : window.mozInnerScreenY + rect.top;
        data.screenY = top + rect.height / 2;
      }
      return result;
    };
  }

  function watchExternalDrag() {
    window.addEventListener(
      "dragenter",
      event => {
        if (
          !isTabDrag(event) ||
          !Services.prefs.getBoolPref("sidebar.verticalTabs", false)
        ) {
          return;
        }
        dragHover = true;
        document.documentElement.setAttribute("fg-tab-drag-hover", "");
        syncInteractionPin();
        setRevealed(true);
      },
      true
    );

    window.addEventListener(
      "dragover",
      event => {
        if (
          !isTabDrag(event) ||
          !Services.prefs.getBoolPref("sidebar.verticalTabs", false)
        ) {
          return;
        }
        if (!document.documentElement.hasAttribute("fg-tabs-revealed")) {
          setRevealed(true);
        }
      },
      true
    );

    window.addEventListener(
      "dragleave",
      event => {
        if (!isTabDrag(event) || event.relatedTarget) {
          return;
        }
        dragHover = false;
        document.documentElement.removeAttribute("fg-tab-drag-hover");
        syncInteractionPin();
      },
      true
    );

    window.addEventListener(
      "drop",
      event => {
        if (!isTabDrag(event)) {
          return;
        }
        dragHover = false;
        document.documentElement.removeAttribute("fg-tab-drag-hover");
        releasePointer();
      },
      true
    );

    window.addEventListener(
      "dragend",
      () => {
        dragHover = false;
        document.documentElement.removeAttribute("fg-tab-drag-hover");
        syncInteractionPin();
      },
      true
    );

  }

  function watchTabInteraction() {
    const tabs = document.getElementById("vertical-tabs-container");
    const strip = document.getElementById("tabbrowser-tabs");
    if (!tabs) {
      return;
    }
    const inside = event => {
      const node = event.target;
      return node && (node === tabs || tabs.contains(node));
    };
    window.addEventListener(
      "pointerdown",
      event => {
        if (inside(event)) {
          holdPointer();
        }
      },
      true
    );
    window.addEventListener(
      "pointerup",
      () => {
        releasePointer();
      },
      true
    );
    window.addEventListener(
      "pointercancel",
      () => {
        releasePointer();
      },
      true
    );
    window.addEventListener(
      "mouseup",
      () => {
        releasePointer();
      },
      true
    );
    const startDrag = event => {
      if (!inside(event)) {
        return;
      }
      draggingTabs = true;
      holdPointer();
      syncInteractionPin();
    };
    window.addEventListener("dragstart", startDrag, true);
    window.addEventListener("draggesture", startDrag, true);
    window.addEventListener(
      "dragend",
      () => {
        draggingTabs = false;
        pointerHeld = false;
        pointerSerial++;
        syncInteractionPin();
      },
      true
    );
    window.addEventListener(
      "drop",
      event => {
        if (!inside(event)) {
          return;
        }
        draggingTabs = false;
        releasePointer();
      },
      true
    );
    window.addEventListener(
      "blur",
      () => {
        releasePointer();
      },
      true
    );
    // Stock marks the strip for the whole tab drag, including the steps that
    // create or move a group. Watching the attribute covers drag paths that
    // do not deliver pointer or drag events to this window.
    if (strip) {
      new MutationObserver(() => syncInteractionPin()).observe(strip, {
        attributes: true,
        attributeFilter: [
          "movingtab",
          "movingtab-group",
          "movingtab-addToGroup",
          "movingtab-ungroup",
        ],
      });
    }
  }

  function shortcutBinding(key) {
    return {
      key: key.getAttribute("key") || "",
      keycode: key.getAttribute("keycode") || "",
      modifiers: key.getAttribute("modifiers") || "",
    };
  }

  function setShortcutBinding(key, binding) {
    key.removeAttribute("key");
    key.removeAttribute("keycode");
    if (binding.keycode) {
      key.setAttribute("keycode", binding.keycode);
    } else if (binding.key) {
      key.setAttribute("key", binding.key);
    }
    if (binding.modifiers) {
      key.setAttribute("modifiers", binding.modifiers);
    } else {
      key.removeAttribute("modifiers");
    }
  }

  function captureShortcutDefaults() {
    const keyset = document.getElementById("mainKeyset");
    if (!keyset) {
      return;
    }
    shortcutDefaults = new Map();
    let index = 0;
    for (const key of keyset.querySelectorAll("key")) {
      if (!key.id) {
        key.id = `firegila-key-${index}`;
      }
      index++;
      shortcutDefaults.set(key.id, shortcutBinding(key));
    }
  }

  function readShortcuts() {
    try {
      return (
        JSON.parse(Services.prefs.getStringPref(SHORTCUTS_PREF, "{}")) || {}
      );
    } catch (e) {
      return {};
    }
  }

  function writeShortcuts(map) {
    Services.prefs.setStringPref(SHORTCUTS_PREF, JSON.stringify(map));
  }

  async function shortcutLabel(key) {
    const l10nId = key.getAttribute("data-l10n-id");
    if (l10nId && !key.getAttribute("command")) {
      const value = await document.l10n
        .formatValue(l10nId)
        .catch(() => "");
      if (value) {
        return value;
      }
    }
    const command = key.getAttribute("command") || "";
    if (command) {
      if (COMMAND_LABELS[command]) {
        return COMMAND_LABELS[command];
      }
      const owner = document.querySelector(
        `[command="${CSS.escape(command)}"][data-l10n-id]`
      );
      const ownerId = owner?.getAttribute("data-l10n-id");
      if (ownerId) {
        const value = await document.l10n
          .formatValue(ownerId)
          .catch(() => "");
        if (value) {
          return value;
        }
      }
      return command
        .replace(/^(cmd_|Browser:|View:|Tools:)/, "")
        .replace(/([a-z])([A-Z])/g, "$1 $2");
    }
    return key.id.replace(/^key[_-]?/, "").replace(/([a-z])([A-Z])/g, "$1 $2");
  }

  async function shortcutEntries() {
    const keyset = document.getElementById("mainKeyset");
    if (!keyset) {
      return [];
    }
    const list = [];
    for (const key of keyset.querySelectorAll("key")) {
      let shortcut = "";
      try {
        shortcut = ShortcutUtils.prettifyShortcut(key);
      } catch (e) {}
      list.push({
        id: key.id,
        label: await shortcutLabel(key),
        shortcut,
        ...shortcutBinding(key),
      });
    }
    return list;
  }

  function applyShortcuts() {
    if (!shortcutDefaults) {
      captureShortcutDefaults();
    }
    const map = readShortcuts();
    for (const [id, def] of shortcutDefaults) {
      const key = document.getElementById(id);
      if (!key) {
        continue;
      }
      setShortcutBinding(key, def);
      if (map[id]) {
        setShortcutBinding(key, map[id]);
      }
    }
  }

  function duplicateShortcut(id, binding) {
    const keyset = document.getElementById("mainKeyset");
    const target = document.getElementById(id);
    if (!keyset || !target) {
      return "";
    }
    const combo = `${(binding.modifiers || "").toLowerCase()}|${(
      binding.keycode ||
      binding.key ||
      ""
    ).toLowerCase()}`;
    for (const key of keyset.querySelectorAll("key")) {
      if (key === target) {
        continue;
      }
      const current = shortcutBinding(key);
      if (!current.key && !current.keycode) {
        continue;
      }
      const other = `${(current.modifiers || "").toLowerCase()}|${(
        current.keycode ||
        current.key ||
        ""
      ).toLowerCase()}`;
      if (other === combo) {
        return key.id;
      }
    }
    return "";
  }

  function installShortcutApi() {
    window.FiregilaShortcuts = {
      async entries() {
        return shortcutEntries();
      },
      set(id, binding) {
        const map = readShortcuts();
        map[id] = binding;
        writeShortcuts(map);
        applyShortcuts();
        const key = document.getElementById(id);
        return {
          shortcut: key ? ShortcutUtils.prettifyShortcut(key) : "",
          duplicate: duplicateShortcut(id, binding),
        };
      },
      reset(id) {
        const map = readShortcuts();
        delete map[id];
        writeShortcuts(map);
        applyShortcuts();
        const key = document.getElementById(id);
        return {
          shortcut: key ? ShortcutUtils.prettifyShortcut(key) : "",
        };
      },
      resetAll() {
        writeShortcuts({});
        applyShortcuts();
      },
    };
  }

  function copyPageLink() {
    const uri = window.gBrowser?.currentURI?.spec;
    if (!uri) {
      return;
    }
    try {
      Cc["@mozilla.org/widget/clipboardhelper;1"]
        .getService(Ci.nsIClipboardHelper)
        .copyString(uri);
    } catch (e) {}
  }

  function watchFiregilaCommands() {
    document
      .getElementById("firegila-cmd-copy-page-link")
      ?.addEventListener("command", copyPageLink);
  }

  // The tab group editor and preview panels can stay open after the pointer
  // leaves the column. Keep the column open while either panel is visible.
  function watchTabGroupPanels() {
    const pinIfVertical = () => {
      if (Services.prefs.getBoolPref("sidebar.verticalTabs", false)) {
        pinContextReveal();
      }
    };
    const preview = document.getElementById("tabgroup-preview-panel");
    if (preview) {
      preview.addEventListener("popupshowing", pinIfVertical);
      preview.addEventListener("popuphidden", unpinContextReveal);
    }
    const editor = document.getElementById("tab-group-editor");
    const panel =
      editor?.querySelector("panel") ||
      editor?.shadowRoot?.querySelector("panel");
    if (panel) {
      panel.addEventListener("popupshowing", pinIfVertical);
      panel.addEventListener("popuphidden", unpinContextReveal);
    }
  }

  // Cached so the pointer handler never forces a layout. The width is a fixed
  // token, the same one the stylesheet uses.
  let tabsWidth;

  function readTabsWidth() {
    tabsWidth = parseFloat(
      getComputedStyle(document.documentElement).getPropertyValue(
        "--fg-tabs-width"
      )
    );
  }

  function onPointerMove(event) {
    const root = document.documentElement;
    if (
      !root.hasAttribute("fg-autohide-tabs") ||
      !root.hasAttribute("fg-tabs-revealed") ||
      root.hasAttribute("fg-tabs-interaction-pinned") ||
      tabStripIsMoving()
    ) {
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
      setRevealed(true);
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

  // Entering the collapsed column expands it. The column is in layout at the
  // strip width, so the pointer can reach the icons directly, without an edge
  // sensor.
  function watchRevealEnter() {
    const tabs = document.getElementById("vertical-tabs-container");
    if (!tabs) {
      return;
    }
    tabs.addEventListener("mouseenter", () => {
      const root = document.documentElement;
      if (!root.hasAttribute("fg-autocollapse-tabs")) {
        return;
      }
      clearTimeout(revealTimer);
      revealTimer = window.setTimeout(() => {
        if (tabs.matches(":hover")) {
          setRevealed(true);
        }
      }, REVEAL_DELAY);
    });
  }

  // Leaving the column hides it. A content document does not report mousemove
  // to this window, so the edge sensor alone would leave the column open while
  // the pointer sits in the page or in an open panel.
  function watchRevealLeave() {
    const tabs = document.getElementById("vertical-tabs-container");
    if (tabs) {
      tabs.addEventListener("mouseleave", () => {
        clearTimeout(revealTimer);
        requestCollapse();
      });
    }
  }

  // New tabs have no page to pin. The menu item is disabled and any pin from a
  // drag or another path is undone immediately.
  function emptyTab(tab) {
    const browser = tab?.linkedBrowser;
    const uri = browser?.currentURI;
    if (!uri) {
      return true;
    }
    // A page that is still loading can report about:blank as its current
    // URI. Leave that pin alone until the page settles.
    if (tab.hasAttribute("busy")) {
      return false;
    }
    const spec = uri.spec;
    return (
      spec === "about:newtab" ||
      spec === "about:home" ||
      spec === "about:blank" ||
      spec === "about:privatebrowsing"
    );
  }

  function watchPinnedTabs() {
    const gb = window.gBrowser;
    if (!gb?.tabContainer) {
      return;
    }
    // Restored pinned tabs are pinned before their page is loaded, so their
    // current URI can still be about:blank. Only guard pins after restore.
    SessionStore.promiseAllWindowsRestored.then(
      () => {
        tabsRestored = true;
      },
      () => {
        tabsRestored = true;
      }
    );
    gb.tabContainer.addEventListener("TabPinned", event => {
      if (!tabsRestored) {
        return;
      }
      const tab = event.target;
      if (emptyTab(tab)) {
        try {
          gb.unpinTab(tab);
        } catch (e) {}
      }
    });
  }

  // The collapsed strip shows one pinned column. Slide the grid to the
  // selected tab's column without changing its row or order.
  function syncPinnedColumn() {
    const pinned = document.getElementById("pinned-tabs-container");
    const gb = window.gBrowser;
    if (!pinned || !gb) {
      return;
    }
    const pins = [...pinned.querySelectorAll("tab")];
    const index = pins.indexOf(gb.selectedTab);
    const column =
      index >= 0 && pinnedColumns > 0 ? index % pinnedColumns : 0;
    pinned.style.setProperty("--fg-pinned-column", String(column));
  }

  function watchPinnedColumn() {
    const gb = window.gBrowser;
    if (!gb?.tabContainer) {
      return;
    }
    pinnedColumns = parseInt(
      getComputedStyle(document.documentElement).getPropertyValue(
        "--fg-pinned-columns"
      ),
      10
    );
    syncPinnedColumn();
    for (const type of ["TabSelect", "TabPinned", "TabUnpinned", "TabMove"]) {
      gb.tabContainer.addEventListener(type, syncPinnedColumn);
    }
  }

  // The sidebar menu on the tabs column background and the tab menu. Both
  // pin the column open while the menu is visible, so leaving the bar to use
  // the menu does not collapse it.
  function watchTabsContextMenu() {
    const container = document.getElementById("vertical-tabs-container");
    if (!container) {
      return;
    }

    const tabMenu = document.getElementById("tabContextMenu");
    const menuTab = () => {
      const node = tabMenu?.triggerNode;
      const tab = node?.closest?.("tab") || window.gBrowser?.selectedTab;
      return tab && container.contains(tab) ? tab : null;
    };

    if (tabMenu) {
      tabMenu.addEventListener("popupshowing", () => {
        if (menuTab() || container.matches(":hover")) {
          pinContextReveal();
        }
      });

      tabMenu.addEventListener("popupshown", () => {
        const tab = menuTab();
        const empty = !tab || emptyTab(tab);
        for (const id of ["context_pinTab", "context_pinSelectedTabs"]) {
          const item = document.getElementById(id);
          if (item) {
            item.disabled = empty;
          }
        }
      });

      tabMenu.addEventListener(
        "command",
        event => {
          const id = event.target?.id;
          if (id !== "context_pinTab" && id !== "context_pinSelectedTabs") {
            return;
          }
          const selected = window.gBrowser?.selectedTabs || [];
          const blocked =
            id === "context_pinTab"
              ? emptyTab(menuTab() || window.gBrowser?.selectedTab)
              : selected.some(emptyTab);
          if (blocked) {
            event.preventDefault();
            event.stopPropagation();
          }
        },
        true
      );

      tabMenu.addEventListener("popuphidden", unpinContextReveal);
    }

    const sidebarMenu = document.getElementById("sidebar-context-menu");
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
      if (
        !main ||
        !sidebarMenu ||
        typeof main.updateSidebarContextMenuItems !== "function"
      ) {
        return;
      }
      event.preventDefault();
      main.updateSidebarContextMenuItems();
      pinContextReveal();
      sidebarMenu.addEventListener("popuphidden", unpinContextReveal, {
        once: true,
      });
      sidebarMenu.openPopupAtScreen(event.screenX, event.screenY, true);
    });
  }

  syncTabsMode();
  syncTabsSide();
  readTabsWidth();
  Services.prefs.addObserver(AUTO_HIDE_PREF, syncTabsMode);
  Services.prefs.addObserver(AUTO_COLLAPSE_PREF, syncTabsMode);
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
  const COLLAPSE_SETTLE_DELAY = 40;
  const MENU_MIN_WIDTH = 200;
  const MENU_MAX_WIDTH = 260;

  const { SessionStore } = ChromeUtils.importESModule(
    "resource:///modules/sessionstore/SessionStore.sys.mjs"
  );
  const l10n = new Localization(["browser/sidebar.ftl"], true);

  let workspaces = [];
  let activeId = null;
  let nameMode = "new";
  let lastScroll = 0;
  let started = false;
  let revealPins = 0;
  const lastTab = new Map();

  function tabsBrowser() {
    return window.gBrowser;
  }

  // Keep the tabs column expanded while one of its popups is open. The
  // pointer leaves the column to use the menu, so without this the column
  // collapses and the next popup anchors to a moved button.
  function pinReveal() {
    if (!Services.prefs.getBoolPref("sidebar.verticalTabs", false)) {
      return;
    }
    revealPins++;
    const root = document.documentElement;
    root.setAttribute("fg-tabs-reveal-pinned", "");
    root.setAttribute("fg-tabs-revealed", "");
    root.setAttribute("fg-tabs-open", "");
    // Flush the snapped layout before a popup reads the anchor box.
    const button = document.getElementById("firegila-workspaces");
    if (button) {
      button.getBoundingClientRect();
    }
  }

  function unpinReveal() {
    revealPins = Math.max(0, revealPins - 1);
    if (revealPins) {
      return;
    }
    const root = document.documentElement;
    root.removeAttribute("fg-tabs-reveal-pinned");
    window.setTimeout(() => {
      const tabs = document.getElementById("vertical-tabs-container");
      if (tabs && tabs.matches(":hover")) {
        return;
      }
      if (
        root.hasAttribute("fg-tabs-context-pinned") ||
        root.hasAttribute("fg-tabs-interaction-pinned")
      ) {
        return;
      }
      const strip = document.getElementById("tabbrowser-tabs");
      if (strip && strip.hasAttribute("movingtab")) {
        return;
      }
      root.removeAttribute("fg-tabs-revealed");
      root.removeAttribute("fg-tabs-open");
    }, COLLAPSE_SETTLE_DELAY);
  }

  // Use the resting width, not the animating one. In vertical tabs the
  // button is the column width minus its fixed inline margins.
  function workspaceMenuWidth(button) {
    const vertical = Services.prefs.getBoolPref("sidebar.verticalTabs", false);
    let width = Math.round(button.getBoundingClientRect().width);
    if (vertical) {
      const rootStyle = getComputedStyle(document.documentElement);
      const tabsWidth = parseFloat(
        rootStyle.getPropertyValue("--fg-tabs-width")
      );
      const margin = parseFloat(
        rootStyle.getPropertyValue("--fg-tabs-margin")
      );
      width = Math.round(tabsWidth - 2 * margin);
    }
    return Math.max(MENU_MIN_WIDTH, Math.min(MENU_MAX_WIDTH, width));
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
    pinReveal();
    el.panel.addEventListener("popuphidden", unpinReveal, { once: true });
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
    pinReveal();
    el.panel.addEventListener("popuphidden", unpinReveal, { once: true });
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
      // A tab adopted from another window can belong to a workspace that is
      // not active here. Follow it when it arrives selected, so a cross-window
      // drag never lands in a hidden workspace.
      if (tab.selected && saved !== activeId) {
        activeId = saved;
        hideOthers(saved);
        syncUI();
      }
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
      pinReveal();
      menu.style.setProperty(
        "--panel-width",
        `${workspaceMenuWidth(button)}px`
      );
      buildMenu();
    });
    menu.addEventListener("popuphidden", unpinReveal);
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
    SessionStore.promiseAllWindowsRestored.then(
      () => {
        migrateStrictTracking();
        migrateGlobalPrivacyControl();
        restoreDone();
      },
      () => {
        migrateStrictTracking();
        migrateGlobalPrivacyControl();
        restoreDone();
      }
    );
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
/* Icon stays on the optical center. Some SVG boxes carry uneven padding. */
.button-background img {
  display: block;
  flex: none;
  margin: 0;
  vertical-align: middle;
}

/* Hover, press and selected fills fade in step with the chrome. */
.button-background {
  transition:
    background-color var(--fg-motion-fast) var(--fg-ease),
    border-color var(--fg-motion-fast) var(--fg-ease);
}

@media (prefers-reduced-motion: no-preference) {
  .button-background img {
    transition: transform var(--fg-press-up, 220ms)
      var(--fg-press-ease, cubic-bezier(0.2, 0, 0, 1));
  }

  #main-button:active .button-background img {
    transform: scale(0.9);
    transition-duration: var(--fg-press-down, 90ms);
    transition-timing-function: var(
      --fg-press-ease-down,
      cubic-bezier(0.3, 0, 0.2, 1)
    );
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
NEWTAB_PATTERN_SVG = (ROOT / "branding" / "newtab-pattern.svg").read_text()


def newtab_pattern_url(color):
    return "data:image/svg+xml," + quote(
        NEWTAB_PATTERN_SVG.replace("#e0e0e0", color), safe=""
    )


NEWTAB_PATTERN_CSS = f"""
/* Topography background on the plain new tab. The line color follows the
 * theme divider, and the page background follows the theme surface. */
:root {{
  --fg-newtab-pattern: url("{newtab_pattern_url("#e0e0e0")}");
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --fg-newtab-pattern: url("{newtab_pattern_url("#2f2f2f")}");
  }}
}}
body:not(.lightWallpaper):not(.darkWallpaper) {{
  background-color: var(--fg-bg);
  background-image: var(--fg-newtab-pattern);
  background-size: 600px 600px;
  background-position: center center;
  background-repeat: repeat;
}}
"""


NEWTAB_CSS_FILES = [
    "chrome/browser/builtin-addons/newtab/data/css/activity-stream.css",
    "chrome/browser/builtin-addons/newtab/data/css/nova/activity-stream.css",
]
NEWTAB_CSS = (
    NEWTAB_PALETTE_CSS
    + NEWTAB_BUTTONS_CSS
    + NEWTAB_DIALOG_CSS
    + NEWTAB_TWEAKS_CSS
    + NEWTAB_PATTERN_CSS
)

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

FIREGILA_SHORTCUTS_MJS = r"""/* Firegila shortcut editor. Lists every key in the main keyset and stores
 * overrides in firegila.shortcuts. */
import { SettingGroupManager } from "chrome://browser/content/preferences/config/SettingGroupManager.mjs";

const NAMED_KEYS = {
  ArrowLeft: "VK_LEFT",
  ArrowRight: "VK_RIGHT",
  ArrowUp: "VK_UP",
  ArrowDown: "VK_DOWN",
  Home: "VK_HOME",
  End: "VK_END",
  PageUp: "VK_PAGE_UP",
  PageDown: "VK_PAGE_DOWN",
  Insert: "VK_INSERT",
  Delete: "VK_DELETE",
  Backspace: "VK_BACK",
  Enter: "VK_RETURN",
  Escape: "VK_ESCAPE",
  Tab: "VK_TAB",
};

const IGNORED_KEYS = new Set([
  "Control",
  "Shift",
  "Alt",
  "Meta",
  "OS",
  "AltGraph",
  "CapsLock",
]);

function browserWindow() {
  return Services.wm.getMostRecentWindow("navigator:browser");
}

function captureBinding(event) {
  if (IGNORED_KEYS.has(event.key)) {
    return null;
  }
  const modifiers = [];
  if (event.ctrlKey) {
    modifiers.push("accel");
  }
  if (event.metaKey) {
    modifiers.push("meta");
  }
  if (event.shiftKey) {
    modifiers.push("shift");
  }
  if (event.altKey) {
    modifiers.push("alt");
  }
  const mods = modifiers.join(",");
  if (event.key === " ") {
    return { keycode: "VK_SPACE", modifiers: mods };
  }
  if (event.key.length === 1) {
    return { key: event.key.toUpperCase(), modifiers: mods };
  }
  if (/^F\d{1,2}$/.test(event.key)) {
    return { keycode: "VK_" + event.key.toUpperCase(), modifiers: mods };
  }
  if (NAMED_KEYS[event.key]) {
    return { keycode: NAMED_KEYS[event.key], modifiers: mods };
  }
  return { key: event.key, modifiers: mods };
}

class FiregilaShortcutsList extends HTMLElement {
  connectedCallback() {
    if (this._started) {
      return;
    }
    this._started = true;
    this.classList.add("firegila-shortcuts");
    this.build();
  }

  async message(id) {
    try {
      return await document.l10n.formatValue(id);
    } catch (e) {
      return "";
    }
  }

  async build() {
    const win = browserWindow();
    this.replaceChildren();
    const status = document.createElement("p");
    status.className = "firegila-shortcuts-status";
    this.append(status);

    if (!win?.FiregilaShortcuts) {
      status.textContent = await this.message("firegila-shortcuts-no-window");
      return;
    }

    status.textContent = await this.message("firegila-shortcuts-loading");
    const entries = await win.FiregilaShortcuts.entries();
    status.remove();

    const description = document.createElement("p");
    description.className = "firegila-shortcuts-description";
    description.textContent = await this.message("firegila-shortcuts-description");
    this.append(description);

    const resetAll = document.createElement("button");
    resetAll.className = "firegila-shortcuts-reset-all";
    resetAll.textContent = await this.message("firegila-shortcuts-reset-all");
    resetAll.addEventListener("click", () => {
      win.FiregilaShortcuts.resetAll();
      this.build();
    });
    this.append(resetAll);

    const list = document.createElement("div");
    list.className = "firegila-shortcuts-list";
    const empty = await this.message("firegila-shortcuts-empty");
    const resetLabel = await this.message("firegila-shortcuts-reset");
    const duplicateText = await this.message("firegila-shortcuts-duplicate");

    for (const entry of entries) {
      const row = document.createElement("div");
      row.className = "firegila-shortcut-row";

      const label = document.createElement("span");
      label.className = "firegila-shortcut-label";
      label.textContent = entry.label;

      const input = document.createElement("input");
      input.className = "firegila-shortcut-input";
      input.type = "text";
      input.readOnly = true;
      input.autocomplete = "off";
      input.spellcheck = false;
      input.value = entry.shortcut || empty;
      input.addEventListener("focus", () => input.select());
      input.addEventListener("keydown", event => {
        if (
          event.key === "Tab" &&
          !event.ctrlKey &&
          !event.altKey &&
          !event.metaKey
        ) {
          return;
        }
        const binding = captureBinding(event);
        if (!binding) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        const result = win.FiregilaShortcuts.set(entry.id, binding);
        input.value = result.shortcut || empty;
        input.classList.toggle("duplicate", !!result.duplicate);
        input.title = result.duplicate ? duplicateText : "";
      });

      const reset = document.createElement("button");
      reset.className = "firegila-shortcut-reset";
      reset.textContent = resetLabel;
      reset.addEventListener("click", () => {
        const result = win.FiregilaShortcuts.reset(entry.id);
        input.value = result.shortcut || empty;
        input.classList.remove("duplicate");
        input.title = "";
      });

      row.append(label, input, reset);
      list.append(row);
    }

    this.append(list);
  }
}

customElements.define("firegila-shortcuts-list", FiregilaShortcutsList);

SettingGroupManager.registerGroups({
  firegilaShortcuts: {
    l10nId: "firegila-shortcuts-heading",
    headingLevel: 2,
    items: [],
  },
});

function mountShortcutList() {
  const pane = [...document.querySelectorAll("setting-pane")].find(
    p => p.name === "paneShortcuts"
  );
  if (!pane) {
    return false;
  }
  if (!pane.querySelector("firegila-shortcuts-list")) {
    const list = document.createElement("firegila-shortcuts-list");
    pane.append(list);
  }
  return true;
}

if (!mountShortcutList()) {
  const observer = new MutationObserver(() => {
    if (mountShortcutList()) {
      observer.disconnect();
    }
  });
  observer.observe(document.documentElement, { childList: true, subtree: true });
}
"""

FIREGILA_SHORTCUTS_CSS = """
.firegila-shortcuts {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-block: 4px 8px;
}

.firegila-shortcuts-description,
.firegila-shortcuts-status {
  margin: 0;
  color: var(--text-color-deemphasized);
}

.firegila-shortcuts-reset-all {
  align-self: start;
  font: inherit;
}

.firegila-shortcuts-list {
  display: flex;
  flex-direction: column;
  border-top: 1px solid var(--border-color);
}

.firegila-shortcut-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(12em, 18em) auto;
  align-items: center;
  gap: 8px;
  padding-block: 6px;
  border-bottom: 1px solid var(--border-color);
}

.firegila-shortcut-label {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.firegila-shortcut-input {
  box-sizing: border-box;
  width: 100%;
  padding: 4px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--background-color-box);
  color: var(--text-color);
  font: inherit;
  text-align: center;
}

.firegila-shortcut-input:focus {
  outline: 2px solid var(--focus-outline-color);
  outline-offset: 1px;
}

.firegila-shortcut-input.duplicate {
  border-color: var(--text-color-error);
}

.firegila-shortcut-reset {
  font: inherit;
}
"""

patch_jar(BUILD / "browser/omni.ja", BROWSER_EDITS, REMOVE_DIRS_BROWSER, ART_SVG_BROWSER, sweep=True,
          appends=[(f, NEWTAB_CSS) for f in NEWTAB_CSS_FILES] + [
                   # The stock browser defaults file loads after the app level
                   # defaults/pref files, so stock wins on any pref both set.
                   # Appending our defaults here makes the intended value
                   # final. customize.sh writes the file before this runs.
                   ("defaults/preferences/firefox.js", "\n" + FIREGILA_PREFS),
                   ("chrome/browser/skin/classic/browser/tabbrowser/tab.tokens.css", TAB_CSS),
                   ("chrome/browser/skin/classic/browser/tabbrowser/tabs.css", TAB_GROUP_CSS),
                   ("chrome/browser/content/browser/sidebar/sidebar.css", SIDEBAR_PAGE_CSS),
                   ("chrome/browser/skin/classic/browser/tabbrowser/content-area.css", CONTENT_AREA_CSS),
                   ("chrome/browser/skin/classic/browser/sidebar.css", SB_CHROME_CSS),
                   ("localization/en-US/browser/browserSets.ftl", "\nfiregila-copy-page-link = Copy Page Link\n"),
                   ("localization/en-US/browser/browserContext.ftl", "\nfiregila-context-copy-page-link =\n  .label = Copy Page Link\n  .accesskey = L\n"),
                   ("localization/en-US/browser/preferences/preferences.ftl", "\nfiregila-shortcuts-section = Shortcuts\nfiregila-shortcuts-heading = Keyboard shortcuts\nfiregila-shortcuts-description = Every shortcut in the browser. Select a field and press a new combination.\nfiregila-shortcuts-change = Change\nfiregila-shortcuts-reset = Reset\nfiregila-shortcuts-reset-all = Reset all shortcuts\nfiregila-shortcuts-empty = Not set\nfiregila-shortcuts-duplicate = Already used by another command.\nfiregila-shortcuts-loading = Loading shortcuts...\nfiregila-shortcuts-no-window = Open a browser window to edit shortcuts.\n"),
                   ("chrome/browser/content/browser/sidebar/sidebar-main.css", SB_MAIN_CSS),
                   ("chrome/browser/skin/classic/browser/preferences/preferences.css", FIREGILA_SHORTCUTS_CSS),
                   ("chrome/browser/content/browser/sidebar/browser-sidebar.js", SB_BOOTSTRAP_JS),
                   ("chrome/browser/content/browser/sidebar/browser-sidebar.js", SB_ANIM_JS),
                   ("chrome/browser/content/browser/sidebar/browser-sidebar.js", SB_WEBPANELS_JS),
                   ("chrome/browser/content/browser/sidebar/browser-sidebar.js", SB_WORKSPACES_JS)],
          overwrites=[("chrome/browser/content/browser/default-bookmarks.html", DEFAULT_BOOKMARKS),
                      ("chrome/browser/content/browser/preferences/config/firegila-shortcuts.mjs", FIREGILA_SHORTCUTS_MJS)])
