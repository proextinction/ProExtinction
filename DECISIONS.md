# Decisions · Pro Extinction website redesign

Status: kept up to date. **Decided: design B (Poster).** A Ember is removed (still on `backup/vercel-2026-10-06`), C Ring was dropped earlier.

## Open (decide later)
| Question | Status | When |
|---|---|---|
| Final hex values | provisional in `brand/b-poster/tokens.css` | open |
| Original logo as a vector | missing, `mark.svg` is a redrawing | as soon as it turns up |
| Self-hosted fonts | **done** for `site/` (local, OFL). Only `brand-helmet.html` still loads from Google | – |
| Legal notice | **decided: none for now** (loose group, operators not in DE/AT). Draft is ready, `IMPRINT` in `tools/build.py` | check again as soon as someone from DE/AT acts as operator |
| Open to search engines | **done** (October 2026), `INDEXABLE = True` in `tools/build.py`: all 29 languages, all crawlers (AI too) | – |
| Pictures on "Suffering in detail" (16) | blurred behind a click | – |
| German translation of the 4 missing pages | drafts in `content/_translation-pending/`, not built in | separate step |
| Phone number on the German site | stays (as requested), confirm before going live | before going live |
| Hosting and domain | **Cloudflare Workers** (static files from `site/`, `wrangler.jsonc`) in James's Cloudflare account, where the domain already is (free, `HOSTING.md`); `proextinction.com` without www. Open: setup by James, branch `main` as the live version, repository in a GitHub organisation | with the move |

## Decided
1. **Brand:** Pro Extinction. "AbolishSuffering" stays only as the Discord name.
2. **Tagline:** "Together, we end suffering."
3. **Goal:** convince newcomers, not mobilise the community.
4. **Personality:** serious, rational, empathetic, determined, calm and dark. Not sensational, esoteric, playful or hopeless.
5. **Modes:** light and dark, switchable by a button at the top right.
6. **Languages of the concepts:** EN (default and template), DE, PL, ES, IT. If an English page is missing in another language, it is AI-translated from English and marked with a note on the page (no "(AI)" in the menu). Pages that exist in only one language (DE Ressourcen, PL Zasoby, ES Recursos/Mapa del sitio) are kept. Added: FR, PT, RU, ZH (Chinese, simplified), HI (Hindi), AR (Arabic), BN (Bengali), UR (Urdu), ID (Indonesian), JA (Japanese), TR (Turkish), VI (Vietnamese), KO (Korean), FA (Persian), MR (Marathi), TE (Telugu), TA (Tamil), SW (Swahili), TH (Thai), NL (Dutch), UK (Ukrainian), TL (Filipino), PA (Punjabi) and GU (Gujarati) without an original site: fully translated from English, marked in the language picker as e.g. "RU (AI)" and with a note on every page, but without "(AI)" on every menu item. Cyrillic (Russian, Ukrainian) comes from local font files (Oswald, Source Serif 4, JetBrains Mono); Chinese, Japanese, Korean, Thai, Hindi, Marathi, Bengali, Telugu, Tamil, Punjabi (Gurmukhi), Gujarati, Arabic, Urdu and Persian from the system fonts. Arabic, Urdu and Persian run right to left (`dir="rtl"`): the CSS uses logical properties (inline-start/end), so navigation, chapter overview and border lines are mirrored; the wordmark and the English slogan stay left to right. The translations follow the rules of the unslop skill (cursor/plugins). Typos are corrected.
7. **Content:** original text stays word for word. Only buttons, subheadings and notes are newly written (addressing the reader as "you", factual, list of banned words in `BRAND.md`).
8. **Colour:** accent on less than about 5 % of the area, silver only in the logo and wordmark.
9. **Typography:** heavy uppercase grotesque for display, mono sparingly, never Inter or Roboto as the main font. Wordmark as type with CSS metal, no flyer picture.
10. **Look:** white space, narrow text column (68 ch), grain, hairlines, no shadows or glass effects.
11. **Signature:** the red slash (divider, progress, hover).
12. **Building blocks:** navigation always visible (no hamburger menu), chapter overview, expandable FAQ, quote block, four efforts, call to action, language and theme switchers.
13. **Pictures:** the main visual language is in code (lines, rings, slash, grain). No stock photos. Graphic pictures only behind a click. **Status now:** the 30 content pictures of the original English site are built in for review, numbered (#1 to #30, list in `content/images.json`, files in `presentation/img/`). Then it is decided which stay and which go behind a click.
14. **Logo effect:** no hover effect any more (removed 2026-10). The large logo on the home page turns in a loop and respects "reduce motion".
15. **Scrollbars:** thin, accent colour; darker inside than outside.
16. **Target platform:** website only, responsive. No PDFs, slides, thumbnails.

## Design B (Poster)
| | |
|---|---|
| Shape | square corners |
| Layout | centred, poster-like |
| Navigation | navbar at the top |
| Chapter overview | follows on the right from 1280 px |
| Colours | red/black/silver |
| Body text | sans (Barlow) |
| Default mode | dark |

## Structure of the website (decided 2026-10)
One file per page in `site/`, addresses `/<language>/<page>`; `/` picks the language from the browser. The former single-file presentation (`presentation/index.html`, 8.8 MB with all languages) is replaced: it was slow and only a single page for search engines. `/` forwards its old links (`#/de/manifest`).
The default mode stays dark; light only when the visitor chooses it.

## Protests on the History page (decided 2026-10)
Past protests are no longer on the page, and so neither is the heading "Upcoming protests". History, social media link, "Where we are today" and the three protest photos stay.
The schedule view is still in the code (`history_outline` and `sched_html` in `tools/build.py`). A new protest appears as a schedule again when it is entered in `content/en/history.json` (and the same in the AI translations) after the line with the social media link, one line per entry:
- heading, e.g. `Upcoming protests:`
- city with a colon, e.g. `WROCŁAW:` (becomes a sub-chapter)
- date as `DD.MM.YYYY`
- one line per place: `Place 14:55-16:00` (a comma or semicolon at the end is allowed), then the next date
Then raise the `where` numbers of the History photos in `content/images.json` by the number of new lines.

## How we work
1. Shared parts are in `tools/css/base.css`, `tools/build.py`, `tools/blocks.py`, `content/`; the design in `brand/b-poster/tokens.css` and `tools/css/b.css`.
2. After every change: `python3 tools/build_all.py`.
