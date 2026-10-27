"""Generate the brand kit (brand/<concept>/) from tokens.css + concept facts.

Run after editing a tokens.css:  python3 tools/kit.py && python3 tools/build.py
"""
import json, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
BRAND = ROOT / 'brand'

ROLES = {
 'bg': 'Base surface', 'surface': 'Cards, panels, navigation bar', 'text': 'Main text',
 'muted': 'Descriptions, labels, metadata', 'line': 'Borders, dividers, 1px',
 'accent': 'Accent: areas, lines, buttons, large numbers (not for small text)',
 'link': 'Accent for text: links, active navigation, small numbers',
 'on-accent': 'Text on the accent colour',
 'accent-deep': 'darker accent variant (reserve)', 'grain': 'Grain opacity',
}
ORDER = ['bg', 'surface', 'text', 'muted', 'line', 'accent', 'link', 'on-accent']

CONCEPTS = {
 'b-poster': dict(
  name='Poster', fonts='family=Anton&family=Barlow:wght@400;500;600&family=JetBrains+Mono:wght@400;500',
  display='Anton', body='Barlow', body_kind='sans-serif (not Inter, not Roboto)', default_mode='dark',
  one_liner='Square, centred, poster-like: large capitals, outlined numbers, calm text.',
  shape='square (radius 0 everywhere)', shape_short='square',
  accent_share='under 5 % of the area',
  nav='Navbar at the top below the header, centred, wraps onto two lines from 900 px, sticks to the top (sticky). A horizontal stripe below. Active page: red and underlined.',
  toc='Chapter overview as in A: accent line on the left, numbered; from 1280 px to the right of the text, 14 rem, following the reader (sticky). Below that, above the text.',
  layout='Centred: title, divider, chapter headings in the middle, body text left-aligned in a 68 ch column.',
  efforts='Container width: under 38 rem 1 column, from 38 rem 2×2. Number as an outlined digit 4–7 rem (Anton, 2 px accent outline).',
  h1='clamp(2,6 rem, 9 vw, 6 rem)', wordmark_hero='clamp(2.2 rem, 11.5 vw, 9.5 rem)',
  gutter='clamp(1.1 rem, 5 vw, 3 rem)', wide='60 rem', body_size='1.125 rem / line height 1.65',
  bp='640 (compact header) · 760 (three-column header) · 900 (navbar wraps)',
  banned_extra=['Round shapes', 'Left-aligned headings', 'Serifs in body text'],
  rail_note='No sidebar, so no scrolling problem in the navigation.'),
}

# ---------- helpers
def parse_tokens(c):
    s = (BRAND / c / 'tokens.css').read_text(encoding='utf-8')
    root = re.search(r':root\{([^}]*)\}', s).group(1)
    th = {m: dict(re.findall(r'--([\w-]+):([^;}]+)', re.search(r':root\[data-theme=%s\]\{([^}]*)\}' % m, s).group(1))) for m in ('dark', 'light')}
    base = dict(re.findall(r'--([\w-]+):([^;}]+)', root))
    return base, th

def _norm(h):
    h = h.strip().lstrip('#'); return ''.join(ch * 2 for ch in h) if len(h) == 3 else h
def _lum(h):
    h = _norm(h); rgb = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(rgb[0]) + 0.7152 * f(rgb[1]) + 0.0722 * f(rgb[2])
def contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True); return round((la + 0.05) / (lb + 0.05), 1)

def pretty_tokens(c):
    base, th = parse_tokens(c); d = CONCEPTS[c]
    out = [f'/* Pro Extinction · Konzept {d["name"]} · ausführbare Tokens (einzige Quelle der Wahrheit).',
           '   Werte sind VORLÄUFIG, bis ein Konzept gewählt ist (siehe /DECISIONS.md).',
           '   Rollen und Kontraste stehen in BRAND.md. Im Layout nur var(--…) benutzen, keine rohen Hex-Werte. */', ':root{']
    for k, v in base.items(): out.append(f'  --{k}:{v};')
    out.append('}')
    for m in ('dark', 'light'):
        out.append(f':root[data-theme={m}]{{')
        for k in ORDER + [k for k in th[m] if k not in ORDER]:
            if k in th[m]: out.append(f'  --{k}:{th[m][k]};' + (f'  /* {ROLES[k]} */' if k in ROLES else ''))
        out.append('}')
    (BRAND / c / 'tokens.css').write_text('\n'.join(out) + '\n', encoding='utf-8')

def helmet(c):
    d = CONCEPTS[c]; tok = (BRAND / c / 'tokens.css').read_text(encoding='utf-8')
    return f'''<!-- Brand Kit Pro Extinction · {d["name"]}. Generiert von tools/kit.py. Nicht von Hand ändern.
     Im Layout ausschließlich var(--…) benutzen. Der <style>-Block gehört in den <head>.
     Vor dem Livegang die Schriften selbst hosten (DSGVO), siehe BRAND.md, Abschnitt „Offen". -->
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{d["fonts"]}&display=swap">
<style>
{tok}
*,*::before,*::after{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:var(--body);line-height:1.65}}
h1,h2,h3{{margin:0;font-family:var(--display);font-weight:var(--display-weight,600);text-transform:uppercase;line-height:1.05}}
a{{color:var(--link)}}
:focus-visible{{outline:2px solid var(--accent);outline-offset:3px}}
.lbl{{font-family:var(--mono);font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}}
.val{{font-family:var(--mono);font-variant-numeric:tabular-nums}}
</style>
'''

def brand_md(c):
    d = CONCEPTS[c]; base, th = parse_tokens(c)
    rows = []
    for k in ORDER:
        rows.append(f'| `--{k}` | `{th["dark"].get(k,"–")}` | `{th["light"].get(k,"–")}` | {ROLES[k]} |')
    cr = []
    for m, label in (('dark', 'Dark'), ('light', 'Light')):
        t = th[m]
        cr.append(f'| {label} | {contrast(t["text"], t["bg"])} | {contrast(t["muted"], t["bg"])} | {contrast(t["link"], t["bg"])} | {contrast(t["accent"], t["bg"])} | {contrast(t["on-accent"], t["accent"])} |')
    banned = ['Inter or Roboto as the main font', 'Stock photos, sunset silhouettes, skull and blood clichés',
              'Metal look in body text', 'Gradients or shine except in the logo and wordmark', 'Shadows and glass effects',
              'Accent colour as a section background or gradient', 'Accent colour for small text (use `--link`)',
              'New colours, new fonts, raw hex values in the layout'] + d['banned_extra']
    bl = '\n'.join(f'- {b}' for b in banned)
    return f'''# BRAND · Pro Extinction · Concept {d["name"]}

Binding summary. The reasons are in `../REFERENCE.md`. **Status: concept,
not final.** Which of the two concepts applies is still open (`/DECISIONS.md`). All values
below are provisional, but binding within this concept.

## 1. Brand
**Pro Extinction.** A movement that wants to end suffering by standing against forced existence.
Audience: convince newcomers. Tagline: **"Together, we end suffering."**
Personality: serious · rational · empathetic · determined · calm and dark.
Not: sensational, shocking, esoteric, playful, hopeless.
Concept {d["name"]}: {d["one_liner"]}

## 2. Tokens
Source: `tokens.css` (embedded identically in `brand-helmet.html`). Light and dark are
equal, switch at the top right. Default: {d["default_mode"]}.

| Token | Dark | Light | Role |
|---|---|---|---|
{chr(10).join(rows)}

The names differ from the skill's template (`--surface` instead of `--surf`, `--text` instead of `--fg`,
`--muted` instead of `--mut`, `--accent` instead of `--acc`). They apply only in this kit.

**Area split:** base surface 75–85 % · cards/panels 10–20 % · accent {d["accent_share"]}.
Accent never as a section background, never as a gradient.

**Contrast (ratio to the base surface, target for text ≥ 4.5):**

| Mode | Text | Muted | Link | Accent | Text on accent |
|---|---|---|---|---|---|
{chr(10).join(cr)}

The accent itself is below 4.5 in some modes. So: **small text never in `--accent`,
always in `--link`.** `--accent` only for areas, lines, bars and large numbers (from 2 rem).

## 3. Typography
| Role | Font | Use |
|---|---|---|
| Display | {d["display"]} (fallback Arial Narrow, Impact) | Headings, wordmark, buttons, navigation. Always capitals |
| Body | {d["body"]} · {d["body_kind"]} | Body text |
| Mono | JetBrains Mono | Labels, chapter numbers, sources. Sparingly, capitals, 0.72–0.8 rem |

Sizes: body text {d["body_size"]} · line length 65–70 characters (`68ch`) · H1 `{d["h1"]}` ·
H2 `clamp(1.4 rem, 3.2 vw, 2 rem)` · hero wordmark `{d["wordmark_hero"]}`.
Never Inter or Roboto as the main font. Self-host the fonts before going live.

## 4. Grid and spacing
| Measure | Value |
|---|---|
| Page margin | `{d["gutter"]}` |
| Maximum content width | {d["wide"]} |
| Shape | {d["shape"]} |
| Border | 1 px `--line`; accent border only for active elements |
| Shadows, gradients, glass | none (exception: wordmark metal, logo glow in the effect) |
| Grain | SVG noise over the page, `--grain` opacity, never animated |
| Breakpoints | {d["bp"]} |

Tested at 320 · 390 · 600 · 768 · 1024 · 1280 · 1920 · 2560 px. No horizontal scrolling.

## 5. Logo and wordmark
| File | When |
|---|---|
| `wordmark.svg` | Lettering "PRO EXTINCTION" in {d["display"]}, the default case |
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
| Navigation | {d["nav"]} {d["rail_note"]} |
| Chapter overview | {d["toc"]} Active chapter in `--link`, numbered 01, 02 … |
| Long text | {d["layout"]} Paragraph spacing 1.15 em |
| Four efforts | {d["efforts"]} |
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
{bl}

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
'''

def claude_md(c):
    d = CONCEPTS[c]
    return f'''# Working rules in this folder

This is the brand kit concept **{d["name"]}** of the brand **Pro Extinction**. For any design, web or
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
'''

def readme(c):
    d = CONCEPTS[c]
    return f'''# Brand Kit · Pro Extinction · {d["name"]}

{d["one_liner"]} **Status: concept, not chosen yet** (see `/DECISIONS.md`).

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
First read brand/{c}/BRAND.md and follow it exactly.
Reference: brand/{c}/beispiel/bausteine.html
```

`wordmark.svg` contains `<text>` and needs the font {d["display"]} on the displaying device.
As soon as the wordmark leaves the browser (print, Illustrator, PDF), it must be converted to paths.

Generate again: `python3 tools/kit.py` (kit files) and `python3 tools/build.py` (pages).
'''

def wordmark_svg(c):
    d = CONCEPTS[c]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 80" role="img" aria-label="Pro Extinction">
  <!-- Schriftzug als <text>: braucht {d["display"]}. Vor Druck/Export in Pfade umwandeln. Farbe: currentColor (im Browser inline einbetten). -->
  <text x="0" y="62" fill="currentColor" font-family="'{d["display"]}','Arial Narrow',Impact,sans-serif" font-size="68" letter-spacing="3" font-weight="600">PRO EXTINCTION</text>
</svg>
'''

def props_json(c):
    base, th = parse_tokens(c)
    opts = sorted({th['dark']['accent'], th['light']['accent']})
    return json.dumps({
        'accent': {'label': 'Akzent', 'options': opts, 'default': th['dark']['accent']},
        '_note': 'Prüfwerkzeug, kein zweiter Markenakzent. Nur Markenfarben, keine Funktionsfarben.'
    }, indent=2, ensure_ascii=False) + '\n'

def examples(c):
    d = CONCEPTS[c]; base, th = parse_tokens(c)
    css = (ROOT / 'site' / 'style.css').read_text(encoding='utf-8')
    js = (ROOT / 'tools' / 'assets' / 'site.js').read_text(encoding='utf-8')
    def sw(m):
        return ''.join(f'<li><span class="sw" style="background:{th[m][k]}"></span><b class="mono">--{k}</b><code>{th[m][k]}</code></li>' for k in ORDER)
    cur = ' aria-current="page"'
    nav = ''.join('<li><a href="#"%s>%s</a></li>' % (cur if i == 1 else '', t) for i, t in enumerate(['Home', 'Manifest', 'Basis-FAQ', 'Vollständiges FAQ', 'Geschichte', 'Aktiv werden', 'Kontakt']))
    eff = ''.join(f'<li><span class="num mono">{i+1:02d}</span><p class="eff-label mono">Einsatz {i+1}</p><p>Beispieltext für einen Einsatz. Länge und Umbruch wie im Original.</p></li>' for i in range(4))
    toc = ''.join(f'<li><a href="#b{i}">Beispielkapitel {i}</a></li>' for i in range(1, 6))
    faq = ''.join(f'<details><summary>Beispielfrage {i}?</summary><div class="a"><p>Beispielantwort. Echter Text kommt wörtlich aus dem Original.</p></div></details>' for i in range(1, 4))
    page = f'''<!doctype html>
<html lang="de" data-concept="{c}" data-default="{'light' if 'hell' in d['default_mode'] else 'dark'}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bausteine · Pro Extinction · {d["name"]}</title><meta name="robots" content="noindex">
<script>(function(){{var d=document.documentElement,m=null;try{{m=new URLSearchParams(location.search).get('theme')||localStorage.getItem('pe-theme')}}catch(e){{}}if(m!=='light'&&m!=='dark')m=d.dataset.default;d.dataset.theme=m}})()</script>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{d["fonts"]}&display=swap">
<style>{css}
.ex-block{{padding:2rem var(--gutter);max-width:var(--wide);margin-inline:auto}}
.ex-block>h2{{font-size:1.4rem;margin-bottom:1rem}}
.ex-flag{{margin:0 0 1.2rem}}
.sw-list{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(11rem,1fr));gap:.6rem}}
.sw-list li{{display:grid;gap:.15rem;font-size:.8rem}}.sw{{display:block;height:2.2rem;border:1px solid var(--line)}}
.scroll-demo{{height:9rem;overflow:auto;border:1px solid var(--line);padding:1rem;max-width:30rem}}
.ex-row{{display:flex;flex-wrap:wrap;gap:.8rem;align-items:center}}
</style></head>
<body>
<div class="progress" aria-hidden="true"><i></i></div>
<header class="top"><div class="lead"><a class="brand" href="#"><span class="logo" role="img" aria-label="Pro Extinction"></span><span class="wordmark">PRO EXTINCTION</span></a></div>
<div class="tools"><a class="lang" href="#">EN</a><button class="theme" type="button" aria-label="Hell/Dunkel umschalten"><span></span></button></div></header>
<div class="shell"><nav class="sitenav" aria-label="Beispiel"><ul>{nav}</ul></nav>
<main id="main">
<section class="ex-block"><p class="mono ex-flag">BEISPIELDATEN · Referenz für Konzept {d["name"]} · alle Texte hier sind Platzhalter</p>
<h1>Bausteine</h1><hr class="slash"></section>
<section class="ex-block"><h2>Farben (Tokens)</h2><p class="mono ex-flag">Dunkel</p><ul class="sw-list">{sw("dark")}</ul><p class="mono ex-flag" style="margin-top:1.2rem">Hell</p><ul class="sw-list">{sw("light")}</ul></section>
<section class="ex-block"><h2>Typografie</h2><h1 style="font-size:{d['h1'].replace(',', '.').replace(' ', '')}">Überschrift H1</h1><h2 style="margin:1rem 0">Überschrift H2</h2><p class="lede">Lede-Zeile in Kursiv.</p><p style="max-width:68ch">Fließtext: {d["body"]}. Die Zeilenlänge bleibt bei etwa 68 Zeichen, damit lange Texte lesbar sind. <a href="#">Ein Link</a> steht in <code>--link</code>.</p><p class="mono">Mono-Label · 01 · Quelle</p></section>
<section class="ex-block"><h2>Buttons und Trenner</h2><div class="ex-row"><a class="btn primary" href="#">Aktiv werden</a><a class="btn" href="#">Manifest lesen</a></div><hr class="slash"></section>
<section class="hero" aria-label="Hero und Logo-Animation"><span class="hero-logo" role="img" aria-label="Logo"><span class="lg lg-snake"></span><span class="lg lg-cut"></span><span class="lg lg-slash"></span></span><h1 class="wordmark">PRO EXTINCTION</h1><p class="hero-tag">Together, we end suffering.</p><p class="hero-sub">Das große Logo dreht sich in Schleife.</p></section>
<section class="mission"><hr class="slash"><p class="mono kicker">Unsere Mission</p><blockquote>Beispielzitat in der Zitat-Schrift des Konzepts.</blockquote></section>
<section class="efforts"><ol>{eff}</ol></section>
<section class="ex-block"><h2>Kapitelübersicht und Langtext</h2><nav class="toc" aria-label="Auf dieser Seite"><p class="mono">Auf dieser Seite</p><ol>{toc}</ol></nav><div class="prose"><h2 id="b1">Beispielkapitel 1</h2><p>Absatz mit Beispieltext. Das mitlaufende aktive Kapitel wird per Script markiert.</p><ul><li>Listenpunkt mit Akzent-Marker</li><li>Zweiter Punkt</li></ul><h2 id="b2">Beispielkapitel 2</h2><p>Zweiter Absatz.</p></div></section>
<section class="ex-block"><h2>FAQ</h2><div class="faq">{faq}</div></section>
<section class="ex-block"><h2>Scrollbar (innen)</h2><div class="scroll-demo"><p>Scrolle in diesem Feld. Innere Scrollbars sind dünner und dunkler als die der Seite.</p>{"<p>Zeile Beispieltext.</p>"*12}</div></section>
<section class="cta"><hr class="slash"><h2>Mach mit</h2><p class="cta-sub">Together, we end suffering.</p><p class="cta-links"><a class="btn primary" href="#">Discord</a><a class="btn" href="#">WhatsApp</a><a class="btn" href="#">info@proextinction.com</a></p></section>
</main></div>
<footer class="foot"><p class="mono">Beispieldaten · Pro Extinction · {d["name"]}</p></footer>
<script>{js}</script></body></html>
'''
    (BRAND / c / 'beispiel' / 'bausteine.html').write_text(page, encoding='utf-8')
    (BRAND / c / 'beispiel' / 'bausteine-mobil.html').write_text(f'''<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bausteine mobil · {d["name"]}</title>
<body style="margin:0;background:#444;display:grid;place-items:center;min-height:100vh"><iframe src="bausteine.html" title="Mobil 390 px" style="width:390px;height:844px;border:0;background:#fff"></iframe></body></html>
''', encoding='utf-8')

def main():
    logo = (ROOT / 'tools' / 'assets' / 'logo.svg').read_text(encoding='utf-8')
    for c in CONCEPTS:
        d = BRAND / c; (d / 'beispiel').mkdir(parents=True, exist_ok=True)
        pretty_tokens(c)
        (d / 'brand-helmet.html').write_text(helmet(c), encoding='utf-8')
        (d / 'BRAND.md').write_text(brand_md(c), encoding='utf-8')
        (d / 'CLAUDE.md').write_text(claude_md(c), encoding='utf-8')
        (d / 'README.md').write_text(readme(c), encoding='utf-8')
        (d / 'wordmark.svg').write_text(wordmark_svg(c), encoding='utf-8')
        (d / 'mark.svg').write_text(logo, encoding='utf-8')
        (d / 'brand-props.json').write_text(props_json(c), encoding='utf-8')
        examples(c)
    print('kits written:', ', '.join(CONCEPTS))

if __name__ == '__main__':
    main()
