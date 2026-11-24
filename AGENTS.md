# AGENTS.md - Firegila

## 1. Text

- Plain words only. Short lines. Neutral tone.
- Never use em dashes in any file, including code, comments, docs and strings. Use a period, comma or colon instead.
- No hype words and no filler. No extra adjectives.
- No AI filler, no first person and no personal notes.
- Commit messages and release notes: short, mechanical, no personal tone.
- Shell scripts: one short `#` line per block. Lowercase start is fine.
- `firegila.js`: section labels like `// Telemetry`. No sentences in labels.
- Docs: short facts only. No marketing copy.
- Run `grep -rIP '\x{2014}|\x{2013}' .` before finishing. It must print nothing. `-I` skips binary assets.

## 2. Scope

- Linux x86_64 only. No Windows, no macOS, no Android, no iOS.
- The product name is Firegila in text. The public repository is `TTP-browser`. Paths, packages and commands stay lowercase.
- Binary repackage of Firefox ESR. No source build.
- `VERSION` is the Firegila release. `ESR_VERSION` is the Firefox base. Keep them separate.
- Keep the browser usable. Cookies, history, passwords and bookmarks persist. Nothing is cleared on exit.
- Do not delete user data. A migration may remove exact stock values and nothing else.
- Changes go in `configs/`, `assets/`, `scripts/` and `packaging/`. `patches/` stays empty until a source build exists.

## 3. Layout

```
VERSION              Firegila release
ESR_VERSION          Firefox base
CHANGELOG.md         release history
configs/             prefs, policies, autoconfig, distribution
assets/              desktop entry, launcher, newtab pattern, uBlock
scripts/             fetch, customize, patch, package, install, check
scripts/packages/    executable build driver per package format
packaging/           declarative package templates and metadata
packaging/common/    shared metadata for every format
packaging/deb/       Debian template
packaging/rpm/       RPM spec template
packaging/arch/      Arch PKGBUILD template
packaging/appimage/  AppImage template and pinned tool
assets/icons/        icon masters
dev                  fresh profile launcher, never shipped
build/               generated tree, ignored
dist/                generated packages, ignored
sources/             upstream tarball, ignored
```

- Keep generated files out of git.
- One staging tree in `scripts/package.sh` feeds every package format.

## 4. Build

```sh
./scripts/fetch-esr.sh      download and verify the ESR tarball
./scripts/customize.sh      unpack, brand, patch, icons, configs
./dev                       run on a fresh profile
./dev --build               rebuild, then run fresh
./scripts/package.sh        build every format
./scripts/package.sh deb    build only the named formats
./scripts/install.sh dist/firegila-<version>-linux-x86_64.tar.xz
```

- Run `./scripts/check-commit.sh` before every commit.
- Check Python syntax with `python3 -m py_compile` on changed scripts.
- Validate metadata with `desktop-file-validate` and `appstreamcli`.
- Keep the AppImage tool pinned in `packaging/appimage/appimagetool.sha256`.

### Package metadata

- Use the shared `MAINTAINER`, `VENDOR`, `HOMEPAGE`, `SUMMARY` and `LICENSE` values in `scripts/packages/common.sh`.
- Do not hardcode maintainer, vendor, homepage or license in a format script.
- Every format carries the same maintainer, homepage, license and description where the format supports it.
- Debian packages include `copyright` and `changelog.Debian.gz`.
- Arch packages include `firegila.install` and a real `PACKAGER`.

## 5. Repository, versions and commits

### Repository

- The public GitHub repository is `TTP-browser`. The product name remains Firegila.
- Do not add a remote, commit, tag, push or publish anything until the owner explicitly states.
- Publishing is manual. The owner controls every public action.
- Do not create or push 0.x tags, releases or packages.
- Keep private data, tokens, local profiles, build output and package files out of the repository.

### Versioning

- Versions use the 1.x line. Do not create new 0.x versions.
- The first number is the major line. Change it only when the owner decides, for example to 2.1.
- The second number increases by one for every commit.
- `VERSION` is the single source for the current version.
- `ESR_VERSION` is the Firefox base. The two files move separately.
- `CHANGELOG.md` gets an entry for every version.
- `customize.sh` writes `firegila.version` and `firegila.build`.
- Build packages into `dist/`. Only the latest set stays in the repository.
- Before building a new version, the previous `dist/` must already be archived in `TTP-pkgs/pkgs/firegila/<version>/`.
- Build packages only from a committed tree.
- Tag releases as `v<version>`. Do not create, move or push 0.x tags.
- GitHub releases follow the version tags.

### Commits

- Every commit bumps `VERSION` by one in the second number.
- Commit subjects use `Firegila <version>: <summary>`.
- The summary is short, mechanical and states what changed.
- No personal tone, no filler, no em dashes.
- Keep each commit focused. Do not mix unrelated work.
- Do not rewrite history without owner approval.
- Run `scripts/check-commit.sh` before every commit.

### Release approval

- The no-commit rule in Repository applies to every step.
- Ask before changing the major line.
- Ask before rebuilding the existing `dist/`.
- Ask before leaving a change unreleased.
- The user decides: rebuild the same version, bump the version, or do not repackage yet.
- Do not replace release files, move release tags or rewrite release history without approval.
- After approval, rebuild from the final commit.

## 6. Defaults and migrations

- Product prefs go in `configs/firegila.js`.
- UI and theme changes go in `scripts/patch-omni-theme.py`.
- Branding changes go in `scripts/patch-omni-branding.py`.
- New profiles must start clean. Old profiles may need a one-time migration.
- Put migrations in `SB_BOOTSTRAP_JS`, guard them with a `firegila.migration.*` pref, and match exact stock values.
- Never clear cookies, history, passwords, bookmarks or tabs on exit.

## 7. Git hygiene

- Ignored: `/build/`, `/dist/`, `/sources/`, `__pycache__/`, `*.py[cod]`.
- Never commit build output, package files, tarballs or `__pycache__`.
- Anchor root ignore patterns, so `scripts/packages/` stays tracked.
- Run `scripts/check-commit.sh` before commit.
- Leave the working tree clean after an approved release.

## 8. Code

- Use CSS variables for repeated colors, timings, sizes and spacing.
- Use JS constants for repeated pref names, selectors and values.
- Keep one definition for a value used in more than one place.
- Context menus use stock Firefox menu styling. Do not add custom menu background, border, padding or radius. The rest of the chrome stays on the Firegila theme.
- Use the system UI font for chrome. Do not bundle or force a chrome font.
- Use `AccentColor` for every accent. Do not add a fixed accent fallback.
- Tab groups use a folder label tinted with the group color. A chevron shows open or closed. Grouped tabs use a matching border and tint, stay aligned with the strip, and use `AccentColor` for drag targets.
- Audio indicators use the shared neutral `--fg-audio` token. Use the native tab audio overlay in the collapsed strip.
- Keep the tabs column open while a tab is dragged, a tab group panel is open, or the pointer is held in the tabs column.
