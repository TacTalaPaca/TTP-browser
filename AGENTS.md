# AGENTS.md - Firegila

## 1. Text

- Plain words only. Short lines. Neutral tone.
- Never use em dashes in any file, including code, comments, docs and strings. Use a period, comma or colon instead.
- No hype words and no filler. No extra adjectives.
- Shell scripts: one short `#` line per block. Lowercase start is fine.
- `firegila.js`: section labels like `// Telemetry`. No sentences in labels.
- Docs: short facts only. No marketing copy.
- Run `grep -rIP '\x{2014}|\x{2013}' .` before finishing. It must print nothing. `-I` skips binary assets.

## 2. Scope

- Linux x86_64 only. No Windows, no macOS, no Android, no iOS.
- Binary repackage of Firefox ESR. No source build.
- `VERSION` is the Firegila release. `ESR_VERSION` is the Firefox base. Keep them separate.
- Keep the browser usable. Cookies, history, passwords and bookmarks persist. Nothing is cleared on exit.
- Do not delete user data. A migration may remove exact stock values and nothing else.
- Changes go in `configs/`, `branding/`, `scripts/` and `packaging/`. `patches/` stays empty until a source build exists.

## 3. Layout

```
VERSION              Firegila release
ESR_VERSION          Firefox base
configs/             prefs, policies, autoconfig, distribution
branding/            desktop entry and launcher
scripts/             fetch, customize, patch, package, install, check
scripts/packages/    one script per package format
packaging/           deb, rpm, arch, appimage and metainfo templates
extensions/          bundled uBlock Origin
app-icons/           icon masters
dev                  fresh profile launcher, never shipped
build/               generated tree, ignored
packages/<version>/  generated packages, ignored
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
./scripts/install.sh packages/<version>/firegila-<version>-linux-x86_64.tar.xz
```

- Run `./scripts/check-commit.sh` before every commit.
- Check Python syntax with `python3 -m py_compile` on changed scripts.
- Validate metadata with `desktop-file-validate` and `appstreamcli`.
- Keep the AppImage tool pinned in `packaging/appimage/appimagetool.sha256`.

## 5. Versions and releases

- Bump `VERSION` for a Firegila release.
- Bump `ESR_VERSION` only for a new Firefox base.
- `customize.sh` writes `firegila.version` and `firegila.build`.
- Build packages into `packages/<VERSION>/` and keep old folders.
- Rebuild packages after the final commit so `BUILDINFO` records the current commit.
- Tag releases as `v<VERSION>`.
- Commit names describe the change. The version lives in `VERSION` and the tag, not in the commit subject.
- Keep the repository local unless the user asks to push.

### Release approval

- Ask the user before rebuilding an existing `packages/<VERSION>/`.
- Ask the user before bumping `VERSION`.
- Ask the user before leaving a change unreleased.
- The user decides: rebuild the same version, bump the version, or do not repackage yet.
- Do not replace release files, move release tags, or rewrite release history without approval.
- After approval, rebuild from the final commit so `BUILDINFO` matches HEAD.

## 6. Defaults and migrations

- Product prefs go in `configs/firegila.js`.
- UI and theme changes go in `scripts/patch-omni-theme.py`.
- Branding changes go in `scripts/patch-omni-branding.py`.
- New profiles must start clean. Old profiles may need a one-time migration.
- Put migrations in `SB_BOOTSTRAP_JS`, guard them with a `firegila.migration.*` pref, and match exact stock values.
- Never clear cookies, history, passwords, bookmarks or tabs on exit.

## 7. Git hygiene

- Ignored: `/build/`, `/packages/`, `/sources/`, `__pycache__/`, `*.py[cod]`.
- Never commit build output, package files, tarballs or `__pycache__`.
- Anchor root ignore patterns, so `scripts/packages/` stays tracked.
- Run `scripts/check-commit.sh` before commit.
- Leave the working tree clean after a release.
