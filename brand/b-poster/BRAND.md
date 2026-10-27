# BRAND · Pro Extinction · Concept Poster

Binding summary. The reasons are in `../REFERENCE.md`. **Status: concept,
not final.** Which of the two concepts applies is still open (`/DECISIONS.md`). All values
below are provisional, but binding within this concept.

## 1. Brand
**Pro Extinction.** A movement that wants to end suffering by standing against forced existence.
Audience: convince newcomers. Tagline: **"Together, we end suffering."**
Personality: serious · rational · empathetic · determined · calm and dark.
Not: sensational, shocking, esoteric, playful, hopeless.
Concept Poster: Square, centred, poster-like: large capitals, outlined numbers, calm text.

## 2. Tokens
Source: `tokens.css` (embedded identically in `brand-helmet.html`). Light and dark are
equal, switch at the top right. Default: dark.

| Token | Dark | Light | Role |
|---|---|---|---|
| `--bg` | `#0b0708` | `#f3efe9` | Base surface |
| `--surface` | `#150f10` | `#e9e3da` | Cards, panels, navigation bar |
| `--text` | `#e2dfdf` | `#130d0e` | Main text |
| `--muted` | `#9d9595` | `#5a5253` | Descriptions, labels, metadata |
| `--line` | `#2f2426` | `#cdc4b8` | Borders, dividers, 1px |
| `--accent` | `#c4161c` | `#a30f14` | Accent: areas, lines, buttons, large numbers (not for small text) |
| `--link` | `#e8484d` | `#a30f14` | Accent for text: links, active navigation, small numbers |
| `--on-accent` | `#fff` | `#fff` | Text on the accent colour |

The names differ from the skill's template (`--surface` instead of `--surf`, `--text` instead of `--fg`,
`--muted` instead of `--mut`, `--accent` instead of `--acc`). They apply only in this kit.

**Area split:** base surface 75–85 % · cards/panels 10–20 % · accent under 5 % of the area.
Accent never as a section background, never as a gradient.

**Contrast (ratio to the base surface, target for text ≥ 4.5):**

| Mode | Text | Muted | Link | Accent | Text on accent |
|---|---|---|---|---|---|
| Dark | 15.1 | 6.8 | 5.2 | 3.3 | 6.0 |
| Light | 16.8 | 6.6 | 7.0 | 7.0 | 8.0 |

The accent itself is below 4.5 in some modes. So: **small text never in `--accent`,
always in `--link`.** `--accent` only for areas, lines, bars and large numbers (from 2 rem).

## 3. Typography
| Role | Font | Use |
|---|---|---|
| Display | Anton (fallback Arial Narrow, Impact) | Headings, wordmark, buttons, navigation. Always capitals |
| Body | Barlow · sans-serif (not Inter, not Roboto) | Body text |
| Mono | JetBrains Mono | Labels, chapter numbers, sources. Sparingly, capitals, 0.72–0.8 rem |

Sizes: body text 1.125 rem / line height 1.65 · line length 65–70 characters (`68ch`) · H1 `clamp(2,6 rem, 9 vw, 6 rem)` ·
H2 `clamp(1.4 rem, 3.2 vw, 2 rem)` · hero wordmark `clamp(2.2 rem, 11.5 vw, 9.5 rem)`.
Never Inter or Roboto as the main font. Self-host the fonts before going live.

## 4. Grid and spacing
| Measure | Value |
|---|---|
| Page margin | `clamp(1.1 rem, 5 vw, 3 rem)` |
| Maximum content width | 60 rem |
| Shape | square (radius 0 everywhere) |
| Border | 1 px `--line`; accent border only for active elements |
| Shadows, gradients, glass | none (exception: wordmark metal, logo glow in the effect) |
| Grain | SVG noise over the page, `--grain` opacity, never animated |
| Breakpoints | 640 (compact header) · 760 (three-column header) · 900 (navbar wraps) |

Tested at 320 · 390 · 600 · 768 · 1024 · 1280 · 1920 · 2560 px. No horizontal scrolling.

## 5. Logo and wordmark
| File | When |
|---|---|
| `wordmark.svg` | Lettering "PRO EXTINCTION" in Anton, the default case |
| `mark.svg` | Logo mark (ouroboros with a slash) for small areas and the hero |
| Metal look | wordmark only, by CSS (`--metal`), never as a picture |

Minimum size: wordmark 16 px letter height · mark 24 px. Clear space: the height of the "P" all around.
The mark takes the text colour, on hover `--accent`. Do not distort, do not rotate
(except in the logo animation), no shadows. The mark is a **redrawing** of a
500 px picture; the original vector is missing (see Open).

**Logo animation (home page only, large logo):** the snake turns once, then the
slash cuts through, holds and fades, in a loop. No hover effect. With "reduce motion" the logo stands still.

## 6. Building blocks
| Block | Sizes and rules |
|---|---|
| Navigation | Navbar at the top below the header, centred, wraps onto two lines from 900 px, sticks to the top (sticky). A horizontal stripe below. Active page: red and underlined. No sidebar, so no scrolling problem in the navigation. |
| Chapter overview | Chapter overview as in A: accent line on the left, numbered; from 1280 px to the right of the text, 14 rem, following the reader (sticky). Below that, above the text. Active chapter in `--link`, numbered 01, 02 … |
| Long text | Centred: title, divider, chapter headings in the middle, body text left-aligned in a 68 ch column. Paragraph spacing 1.15 em |
| Four efforts | Container width: under 38 rem 1 column, from 38 rem 2×2. Number as an outlined digit 4–7 rem (Anton, 2 px accent outline). |
| Mission quote | Display, capitals (C: serif italic), up to 3.2 rem, at most 22–28 characters wide |
| FAQ | expandable (`<details>`), numbered by CSS, arrow as a slash |
| Call to action | Discord (primary), WhatsApp, e-mail; at the end of every page |
| Slash | Signature: divider, progress bar (top, 4 px), hover; always `--accent` |
| Scrollbars | 8 px, `--accent` (page); in bars 6 px, `--accent-dim` (58 % accent), hover `--accent` |
| Switchers | Language picker (EN, DE, PL, ES, IT plus FR, PT, RU, ZH, HI, AR, BN, UR, ID as "(AI)"; AR and UR right to left) and light/dark at the top right; back button to the concept overview only in the prototype |

## 7. Formats
Website only, responsive. No thumbnails, slides or PDFs in this round.

## 8. Text
In German, address the reader as "du"; factual and direct. The movement's original text stays word for word
(only typos corrected). Only buttons, subheadings and notes are newly written.
Missing pages in DE, PL, ES and IT: AI translation from English, **visibly marked** (note on the page, no "(AI)" in the menu). FR, PT, RU, ZH and HI are fully AI-translated and marked "(AI)" in the language picker, plus a note on every page.
Good: "We want to end as much suffering as possible, without compromise."
Bad: "Together for a better world full of hope!"
Banned in newly written texts: "revolutionary", "groundbreaking", "journey", "community"
in the marketing sense, "hope" as a phrase, exclamation marks, emojis.

## 9. Do not use
- Inter or Roboto as the main font
- Stock photos, sunset silhouettes, skull and blood clichés
- Metal look in body text
- Gradients or shine except in the logo and wordmark
- Shadows and glass effects
- Accent colour as a section background or gradient
- Accent colour for small text (use `--link`)
- New colours, new fonts, raw hex values in the layout
- Round shapes
- Left-aligned headings
- Serifs in body text

## 10. Checklist before handing in
1. Does the layout use only `var(--…)` tokens, no raw hex values?
2. Does the page work in light **and** dark, with a visible switch?
3. Is the accent under 5 % of the area and never a background?
4. Is small text in `--link`/`--text`/`--muted`, never in `--accent`?
5. Are text contrasts ≥ 4.5 : 1 (table above)?
6. Is the text column at most 70 characters wide?
7. Is there no horizontal scrolling at 320, 390, 768, 1280, 2560 px?
8. Is the original text there word for word, and are AI translations marked?
9. Can navigation, chapter overview and FAQ be used by keyboard, with visible focus?
10. Is "reduce motion" respected (no logo effect, no animation)?

## Open (not made up)
- **Choice of concept** A, B or C: later, see `/DECISIONS.md`.
- **Hex values** are suggestions, not approved.
- **Original logo as a vector** is missing; `mark.svg` is a redrawing.
- **Fonts:** self-hosted in `presentation/`. `brand-helmet.html` and the prototype pages still load from Google; switch them too before going live (GDPR).
- **Pictures** ("Suffering in detail", 16 of them): first round without photos; graphic pictures only behind a click.
- **Phone number** only on the German site, confirm before going live.
- **IBAN on the donation page:** unchanged from the original; the page goes live only after approval.
