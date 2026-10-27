# Rules for AI agents (and humans) working on this repository

This is the website of Pro Extinction: a static site in 29 languages, built by a Python script and hosted on Cloudflare Pages.
These rules apply to every contributor and every AI tool (Claude Code, Codex, Cursor, Copilot …). `CLAUDE.md` points here.

## How the repository works
- **Sources:** `content/` (text as JSON, one file per page and language), `tools/` (generator, CSS, JS), `site/img/`, `site/fonts/`, `site/favicon.svg`.
- **Generated:** everything else in `site/` (and `brand/`). It is committed, because Cloudflare serves `site/` as it is, without a build step.
  Never edit generated files by hand. Change the source, then run `python tools/build_all.py` and commit sources and output together.
- **Gate:** `python tools/check.py` rebuilds and checks the whole site: valid content, one title and one h1 per page, no broken internal links,
  hreflang both ways, nothing loaded from other servers, security headers, no secrets, no huge files. **Run it before every commit.** CI runs the same check (with `--ci`) on every pull request.
- **Preview:** `python tools/serve.py`, then http://localhost:8000.
- Where things are: `README.md`. Decisions and their reasons: `DECISIONS.md`. Going live: `DEPLOY.md`, `HOSTING.md`.

## Who can publish
- Only the owners (see `.github/CODEOWNERS`) decide what is merged. Everyone else, and every AI agent, works on a branch and opens a pull request.
- An agent may merge a pull request into `main` only when an owner (Jonas, GitHub `AppsOfUse`, or James, GitHub `idoinejd`) asks for it in the conversation, for that pull request, and only when the `check` job is green and there is no merge conflict. A general "you may merge" does not cover later pull requests.
- Agents never push to `main` directly, never force-push, never delete branches, never approve pull requests and never change repository settings.

## Content rules
1. **English is the source.** `content/en/` is the reference. Other languages are original texts (from the old language sites) or AI translations. `SITE` in `tools/build.py` says which is which (`None` in the last field = AI translation).
2. **AI translations match English line by line:** same number of lines, same order. When an English line changes, the AI translations of that line change with it. Original pages in other languages are not touched unless asked.
3. **Translation style:** plain words, active voice, short sentences. No em dashes, straight quotes only (`tools/put_translation.py` enforces this). Keep names, numbers and links as they are.
4. **Do not remove pages that exist only in some languages.** Not every language has every page, on purpose.
5. **Do not rewrite "I" statements** in the texts (the authors speak in the first person). Exception: the cosmic extinction page.
6. **The page structure is set by hand** (headings, pictures, kinds in `KINDS_BY_HAND`, `JOIN`, `DROP` in `tools/build.py`). Do not "fix" it without being asked.
7. **AI notes** on translated pages never mention an "original site".
8. **Open questions about the English texts** are listed in `KORREKTUREN-OFFEN.md`. They wait for a decision by the owners, don't apply them on your own.

## Images
- **Never open, view, convert or describe the photos on "Suffering in detail"** (`site/img/bild-08.webp` to `bild-21.webp`). Their descriptions are in `content/alt/*.json`, keys 8 to 21. The hook in `.claude/hooks/guard.py` blocks it for Claude Code. Other tools must respect it too.
- Screenshots for testing hide images: inject `img{visibility:hidden}` before taking them.
- New pictures: WebP, under 300 KB, an entry in `content/images.json` and an alt text in every `content/alt/<lang>.json` (English first).

## Security and privacy
- **Nothing from other servers:** no CDNs, Google Fonts, analytics, trackers, embeds (YouTube, maps), iframes or forms. Everything is self-hosted. The one exception, decided by the owners: Cloudflare Web Analytics (cookieless visitor counts, `ANALYTICS` in `tools/build.py`). The Content Security Policy in `site/_headers` (written by `hosting()` in `tools/build.py`) enforces this, and `DECISIONS.md` and the privacy policy promise it. Changing it needs an owner's decision and an update of the privacy policy (`content/legal/`).
- **No cookies, no personal data.** The browser storage keeps only settings (theme, motion, logo counter). Anything new that stores or sends data needs an owner's decision and an update of the privacy policy.
- **No secrets in the repository.** No tokens, passwords, API keys or `.env` files, not even in examples. The site needs none.
- **No new dependencies.** The build uses the Python standard library only. Node (Playwright) is used only for occasional tools (`tools/og.js`, screenshots) and is not committed. Adding a package needs an owner's decision.
- **Links that open a new tab** get `rel="noopener"`. No `javascript:` links. Text from `content/` is escaped (`esc()`), never inserted as raw HTML unless it is markup we wrote.

## Switches only the owners flip
In `tools/build.py`: `INDEXABLE` (search engines, now `False`), `IMPRINT` (legal notice, now `False`), `SITE_URL`. Do not change them unless an owner asks you to in the conversation.

## Working style
- Keep changes small and focused: one topic per pull request. Do not refactor or reformat code you were not asked to touch.
- Match the existing code: same naming, same comment density, standard library only.
- When something is unclear (content, tone, a decision), ask instead of guessing.
- Commit messages in English, describing what changed and why.
- Use the pull request template (`.github/pull_request_template.md`) and say which parts an AI wrote.
