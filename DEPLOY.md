# Going live on Cloudflare Pages

**What goes live:** the folder `site/`: one file per page, plus the language choice, 404 page, sitemap, `robots.txt`, fonts and pictures.
There is no build step at Cloudflare: the pages are built here with `python tools/build_all.py` and committed finished.
Cloudflare reads two control files in `site/` (neither is served as a page, both are written by `tools/build.py`):
- `_headers`: security headers, cache for fonts, and `X-Robots-Tag: noindex` while search engines are closed out
- `_redirects`: old English addresses of the Google Site (`/manifesto`, `/home` …) to the new ones (`/en/manifesto`, `/en/`)

The domain `proextinction.com` is already in James's Cloudflare account. The website goes into **the same account**, so nothing depends on a single person.
Step-by-step guide for James: `HOSTING.md`.

## Addresses
- Home of a language: `/en/`, `/de/` (with slash; Cloudflare redirects `/en` there)
- Pages: `/en/manifesto`, `/de/manifest` (Cloudflare redirects `…/manifest.html` there)
- `/` picks the language from the browser and forwards old links of the single-file version (`#/de/manifest`)
- Every change on another branch automatically gets its own preview address at Cloudflare (`<branch>.<project>.pages.dev`)

## Check before sharing
| Item | Status |
|---|---|
| Search engines | open (`INDEXABLE = True` in `tools/build.py`). The switch changes the meta tag, `X-Robots-Tag` (`site/_headers`) and `robots.txt` together. Then submit `https://proextinction.com/sitemap.xml` in Google Search Console |
| Domain | `SITE_URL` in `tools/build.py` (`https://proextinction.com`, without www). www redirects to the domain without www by a Cloudflare rule (see `HOSTING.md`) |
| Privacy | done (`content/legal/<de|en>.json`, `privacy`), linked in the footer of every page; controller: Pro Extinction as a group of private persons, info@proextinction.com. Not legal advice |
| Legal notice | **not published** on purpose (operators not in Germany/Austria). Ready as a draft (`imprint` in the same files); `IMPRINT = True` in `tools/build.py` builds and links it, fill in the placeholders in square brackets first |
| Fonts | self-hosted, nothing fetched from Google (licence OFL, `site/fonts/licenses/`) |
| Content | Texts, name, logo and donation IBAN come unchanged from the original site. Make sure beforehand that the owners agree to publishing |
| Phone number | is on the German home page (as requested), confirm before going live |

## Updating
After changes: `python tools/build_all.py`, commit and push the result. Cloudflare publishes again automatically.
Preview locally: `python tools/serve.py`. Exactly like Cloudflare (with `_headers` and `_redirects`): `npx wrangler pages dev site`.

## Vercel (transition)
`vercel.json` only shows previews of `site/` (always `noindex`) until the site runs on Cloudflare. After that the Vercel project can be deleted.

## Getting the fonts again
Source: npm packages `@fontsource/*` (Oswald, Anton, Barlow, JetBrains Mono).
Only `latin` and `latin-ext`, `woff2` are used. The `@font-face` rules are in `tools/fonts.css`.
