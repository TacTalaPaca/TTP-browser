# AGENTS.md - Firegila

## 1. Comments and text

- Plain words only. Short lines. Neutral tone.
- Never use em dashes in any file, including code, comments, docs and strings. Use a period, comma or colon instead.
- No hype words and no filler. No extra adjectives.
- Shell scripts: one short `#` line per block. Lowercase start is fine.
- `firegila.js`: section labels like `// Telemetry`. No sentences in labels.
- Docs: short facts only. No marketing copy.

## 2. Scope

- Linux x86_64 only. No Windows, no macOS, no Android, no iOS.
- Base is the ESR in `VERSION`. Binary repackage only. No source build.
- Keep the browser usable. Cookies, history and passwords persist. Nothing is cleared on exit.
- Changes go in `configs/`, `branding/` and `scripts/`. `patches/` stays empty until a source build exists.
- Check with `grep -rP '\x{2014}|\x{2013}' .` before finishing. It must print nothing.
