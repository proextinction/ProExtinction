# Brand Kit · Pro Extinction · Poster

Square, centred, poster-like: large capitals, outlined numbers, calm text. **Status: concept, not chosen yet** (see `/DECISIONS.md`).

| File | Purpose |
|---|---|
| `BRAND.md` | the binding summary |
| `CLAUDE.md` | working rules, apply automatically in this folder |
| `tokens.css` | executable tokens, the only source of truth |
| `brand-helmet.html` | font link, tokens and base styles as a ready block (generated) |
| `brand-props.json` | accent switchable in the design editor (brand colours only) |
| `wordmark.svg` | lettering |
| `mark.svg` | logo mark, redrawn from the original |
| `beispiel/` | working reference with all building blocks, desktop and mobile |
| `../REFERENCE.md` | raw notes from the interview, with reasons |

**The kit does not load by itself.** If you work outside this folder, copy this sentence to
the start of the session:

```
First read brand/b-poster/BRAND.md and follow it exactly.
Reference: brand/b-poster/beispiel/bausteine.html
```

`wordmark.svg` contains `<text>` and needs the font Anton on the displaying device.
As soon as the wordmark leaves the browser (print, Illustrator, PDF), it must be converted to paths.

Generate again: `python3 tools/kit.py` (kit files) and `python3 tools/build.py` (pages).
