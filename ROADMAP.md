# Roadmap · Ideas for later

Ideas that are worked out but not yet decided or built. Build them only after the owners decide.
Platform details as of October 2026. Platform prices and rules change often, check again before starting.

## 1. Activist feed: all videos in one place

**Idea:** One page shows the latest videos and posts of the activists (TikTok, Instagram, X). Supporters find them quickly
and like and comment on them without searching the app for long.

**What works and what doesn't**
| Part | Feasible? | Why |
|---|---|---|
| List of the latest videos | yes | Activists report their links (form in Discord, file in the repo) or the list is kept from the profiles in `content/social.json` |
| Thumbnail and title | yes, at build time | TikTok and X offer oEmbed without login. The build script fetches picture and title once and stores them in `site/`. The visitor loads nothing from other servers |
| One click opens the video directly in the app | yes | A normal link to the video; on a phone it opens the app right there |
| Liking and commenting directly on our site | **no** | TikTok has no interface for it. Instagram allows comments only under a business account's own posts, likes not at all. X allows it only through a login of each user to our app (paid API, around $0.015 per reply) |
| Playing videos on our site | only by breaking our rules | Embedding loads scripts and cookies from TikTok/Meta/X. That contradicts the privacy policy and the Content Security Policy |

**Risk:** Organised liking from a list can break the platforms' rules against artificial engagement. In the worst case
the activists' accounts get throttled. So: invite people to watch and comment for real, not to "work through likes".

**Proposal in stages**
1. *Now, free:* A channel in Discord or in the WhatsApp group where new videos are posted. No code needed.
2. *Website:* A "Support" page with the videos of the last 14 days, as tiles with thumbnails. Kept in a file
   (`content/feed.json`), updated by pull request or weekly by a script. Fits the existing rules (static, nothing from other servers).
3. *Later, optional:* Collect new videos automatically. TikTok allows this only if every activist gives our app access themselves (Display API).
   Needs an app review at TikTok and a place for credentials outside the repo.

**Effort:** stage 2 about 1 to 2 days. Stage 3 much more, plus ongoing maintenance.

## 2. Monthly inspiration: the most successful posts on veganism, antinatalism and efilism

**Idea:** Once a month, a collection of the most popular TikToks, Instagram posts and X posts on these topics.
The activists see which formats, hooks and lengths work right now and take inspiration from them.

**Data access**
| Source | Feasible? | Conditions |
|---|---|---|
| TikTok Research API | rather no | Only for universities and registered non-profits (EU), application, no commercial use. Pro Extinction is not a registered association |
| TikTok Creative Center (trend page for advertisers) | yes, by hand | Shows popular hashtags and videos, no interface |
| Instagram hashtag search (Graph API) | yes | Needs a business or creator account and a Meta app with review; at most 30 hashtags per 7 days, returns "top media" per hashtag |
| X search (API) | yes, costs money | Billed per post read (around $0.005). 1,000 posts a month cost about $5 |
| Scraping (reading the pages automatically) | not recommended | Breaks the platforms' rules, gets blocked fast (during the link check in October 2026, Instagram answered with blocks right away) |

**Privacy:** The posts belong to other people. Only share links and our own short descriptions, no copies of the videos.
Best kept internal (Discord) rather than public on the website.

**Proposal in stages**
1. *Now, free:* Once a month one person collects 10 examples per topic by hand (TikTok Creative Center, Instagram and X search)
   and has an AI summarise why they work (hook, length, format, tone). The result is posted in Discord.
2. *Semi-automatic:* Instagram hashtag search and X search by script, once a month (GitHub Actions or a Cloudflare Worker on a schedule).
   TikTok stays manual. X costs a few dollars a month.
3. *Later:* Apply for the TikTok Research API if Pro Extinction becomes a registered association.

**Effort:** stage 1 about 1 to 2 hours a month. Stage 2 about 2 to 3 days once.

## What the owners must decide first
1. Whether anything automatic runs at all: credentials (API keys) must not go into the repo (`AGENTS.md`), they would need a protected place
   (GitHub Secrets or Cloudflare), and someone has to manage them.
2. Public on the website or only internal (Discord)?
3. Whether the privacy policy must change (only needed if the website loads data from other servers or processes visitor data).

## 3. Development branch `develop` and a preview on dev.proextinction.com

**Idea:** New changes go to `develop` first and can be seen on dev.proextinction.com. Only what was checked through `develop` reaches `main` (the real site).

- **Branch:** create `develop` from today's `main` (the AI can do this).
- **Only Jonas and James merge:** GitHub → *Settings* → *Rules* → *Rulesets* for `main` and `develop`: only by pull request, `check` must be green, no deleting, no force push, merge only for the org owners (bypass list).
  Private repo: needs GitHub Team (around $4 per person per month); public repo: free.
- **Into `main` only from `develop`:** no GitHub setting for this. Solution: a small check in the workflow that turns red when a pull request to `main` does not come from `develop`; add it to the ruleset as a required check.
- **dev.proextinction.com:** a second Cloudflare Worker (e.g. `proextinction-dev`), same repo, production branch `develop`, custom domain `dev.proextinction.com`.
  Recommended: visible only to your e-mail addresses through Cloudflare Access (free for up to 50 people).
- **Search engines:** the dev site must stay closed (otherwise duplicate and unchecked content on Google). The build needs a switch that always sets `develop` to "noindex".
- **Rules for the AI:** change `AGENTS.md` (pull requests to `develop`, only `develop` into `main`). An owner changes this.
- **Open pull requests** then move to `develop`.

**Status:** discussed, not decided yet.

## 4. Search engines and domain

- **Done:** website open to search engines (`INDEXABLE = True`, October 2026).
- **Google still shows the old version** (old Google Sites page, "no information available"). It is read again on Google's next visit.
- **Google Search Console:** verify the domain `proextinction.com` (TXT record in Cloudflare DNS), submit the sitemap `https://proextinction.com/sitemap.xml`,
  `https://proextinction.com/en/` via *URL Inspection* → *Request indexing*. Optionally the same in Bing Webmaster Tools.
- **Redirect www to the domain without www:** today www serves its own copy. Cloudflare → *Rules* → *Redirect Rules*: hostname `www.proextinction.com`
  → `https://proextinction.com${http.request.uri.path}`, 301, keep the query string.
- Responsible: James (Cloudflare account) or Jonas with access (see 5).

## 5. Cloudflare access for Jonas

- No shared password: James invites Jonas (*Manage Account* → *Members* → *Invite*).
- Roles: "Administrator Read Only" (view only) or "Administrator" (set up everything, billing stays with James).
- Only for the domain: a domain-scoped role (e.g. "Domain Administrator", scope only `proextinction.com`), if the plan offers it.
- Only for the Worker is not possible: Workers permissions apply to all Workers in the account.
- If James has other things in the account too: a separate Cloudflare account only for Pro Extinction, move the domain and the Worker there, both Administrator.
- Jonas: turn on two-factor sign-in.

## 6. Other open points (waiting for an owner decision)

- **Quiz before the WhatsApp group:** add "Sorry, you didn't make it" to the rejection text? (Today: friendly text plus "You can still help: share our website!")
- **PR #7 (Cloudflare Workers):** close it, keep only the docs, or only remove the security section from `HOSTING.md` (it should go before the repo is public).
- **Preview builds on pull requests** always fail at Cloudflare (the real site from `main` works). Look for the cause in the Worker settings at Cloudflare.
- **`CODEOWNERS`:** add James (`idoinejd`) as soon as he has accepted the invitation as org owner.
- **Shorten the privacy policy** (sections "Contact by e-mail", "Your rights"): only after confirmation.
- **Cartoon picture in the FAQ** (picture 31, moral subjectivity): blurred behind a click like the pictures on "Suffering in detail"?
- **Dependabot PR #1** (actions/checkout 4.2.2 → 7.0.1): review and merge or close.
- **Public repo or GitHub Team:** needed for rulesets (see 3).
