# Working rules in this folder

This is the brand kit concept **Poster** of the brand **Pro Extinction**. For any design, web or
graphics work:

1. **`BRAND.md` is binding** and beats general design conventions.
   `../REFERENCE.md` is for reference. If they disagree, `BRAND.md` wins.
2. **Only the defined tokens.** No new colours, no new fonts, no raw
   hex values in the layout, always `var(--…)` from `tokens.css` / `brand-helmet.html`.
3. **Light and dark are equal.** Every area must work in both modes.
4. **Accent under 5 % of the area,** never as a background, never as a gradient. Small text never in `--accent`.
5. **Do not reinvent the wordmark.** Use `wordmark.svg` and `mark.svg`. Banned: stock photos,
   skull and blood clichés, metal look in body text.
6. **Look before reinventing:** `beispiel/bausteine.html` shows all building blocks at the correct sizes.
7. **Text:** in German, address the reader as "du"; factual. Never rewrite the movement's original text. Banned phrases are in `BRAND.md`.
8. **Before handing in,** go through the checklist in `BRAND.md`.
9. **This concept is not chosen.** Do not mix concepts. If a token changes,
   run `python3 tools/kit.py && python3 tools/build.py` afterwards.

Changes to the kit itself: ask first. These files are the only source of truth for this concept.
