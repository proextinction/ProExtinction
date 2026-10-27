# Hosting the site on Cloudflare Workers

A one-time setup of about 10 minutes, done in the Cloudflare account that already holds `proextinction.com`.
It's free, and there is no server or software to maintain. Cloudflare serves the finished files from the `site/` folder of the GitHub repository; `wrangler.jsonc` tells it so.
Every change merged into `main` goes live automatically, and you can roll back any change yourself.

## 1. Give Cloudflare access to the repository
The repository lives in the Pro Extinction organisation on GitHub, `proextinction/ProExtinction`, with both of us as owners. An owner of the organisation approves the Cloudflare GitHub app for this repository when Cloudflare asks in step 2.

## 2. Create the Worker
1. Cloudflare dashboard → **Workers & Pages** → **Create** → **Workers** → **Import a repository** (Connect to Git).
2. Choose **GitHub**, sign in and allow access to the `proextinction/ProExtinction` repository only.
3. Settings (Worker → **Settings** → **Build** for an existing Worker):
   | Field | Value |
   |---|---|
   | Project name | `proextinction` (must match `name` in `wrangler.jsonc`) |
   | Production branch | `main` |
   | Build command | *leave empty* |
   | Deploy command | `npx wrangler deploy` |
   | Non-production branch deploy command | `npx wrangler versions upload` |
   | Root directory | *leave empty* (`/`) |
4. **Deploy.** After about a minute the site is online at `https://proextinction.<account>.workers.dev`.

## 3. Connect the domain
1. Worker → **Settings** → **Domains & Routes** → **Add** → **Custom domain** → `proextinction.com`. Then add a second one: `www.proextinction.com`.
2. Cloudflare offers to replace the DNS records of the old site. Accept, and leave all other records (`MX`, `TXT` for email) as they are.
3. Send `www` to the address without www: **Rules** → **Redirect Rules** → **Create rule** → template **"Redirect from WWW to root"** → Deploy.
4. **SSL/TLS** → **Edge Certificates** → turn on **Always Use HTTPS**.

## 4. Afterwards
- **Changes:** anyone with write access to the repository can propose changes, with or without the help of AI. Each merge into `main` goes live within a minute or two.
- **Previews:** a push to any other branch is uploaded as a preview version, with its own address when *Preview URLs* are on (Worker → **Settings** → **Domains & Routes**). The live site doesn't change until that branch is merged into `main`.
- **Undo:** Worker → **Deployments** → choose an older version → **Rollback**.
- **The old Google Site** stays where it is at its `sites.google.com` address. Old English links like `proextinction.com/manifesto` forward to the new pages.
- **Search engines:** Cloudflare → **Caching** → **Configuration** → turn on **Crawler Hints** (tells Bing and others about changes right away, IndexNow, free).
  Add the site to **Google Search Console** (search.google.com/search-console, *Domain* property; Cloudflare can add the verification record for you) and submit `https://proextinction.com/sitemap.xml`. The same for **Bing Webmaster Tools**, which can import it from Search Console.

## 5. Who can publish: owners and contributors
Goal: the two of us are owners. Other people (and their AI tools) can change the site and propose changes, but nothing goes live until one of us merges it.
Set up once in GitHub, in the organisation from step 1. Teams, CODEOWNERS and the Actions settings are free. The ruleset that protects `main` is free for a public repository.

**People**
- Organisation → *People*: both of us **Owner**. Everyone else **Member** (they get no rights to settings).
- Organisation → *Teams* → *New team*: `owners` (both of us) and `contributors`. Repository → *Settings* → *Collaborators and teams*: `owners` **Admin**, `contributors` **Write**.
  Write lets people push branches and open pull requests, not change settings. Occasional helpers need no access at all: they fork the repository and open a pull request from their fork.
- Replace the names in `.github/CODEOWNERS` with `@proextinction/owners`.

**Protect `main`** (Repository → *Settings* → *Rules* → *Rulesets* → *New branch ruleset*)
| Setting | Value |
|---|---|
| Name / Enforcement | `main is live` / **Active** |
| Target branches | *Include default branch* |
| Restrict deletions, Block force pushes | on |
| Require a pull request before merging | on, **1** approval, **Require review from Code Owners**, *Dismiss stale approvals when new commits are pushed* on, *Require conversation resolution* on |
| Require status checks to pass | on, add **`check`**, *Require branches to be up to date* on |
| Bypass list | *Repository admin*, mode **For pull requests only**. Then an owner still needs a pull request and a green `check`, but can merge their own without waiting for the other owner. Remove it if you want every change seen by both of us. |

**GitHub Actions** (Repository → *Settings* → *Actions* → *General*)
- *Fork pull request workflows from outside collaborators*: **Require approval for all external contributors**.
- *Workflow permissions*: **Read repository contents**, and leave *Allow GitHub Actions to create and approve pull requests* **off**.

**Cloudflare previews**
With *Preview URLs* on, every pushed branch gets a public preview address (hidden from search engines). That is handy for review, but anyone with the link can see unreviewed changes. To keep previews private, protect them with Cloudflare Access (free, only the e-mail addresses you allow), or turn *Preview URLs* off: Worker → **Settings** → **Domains & Routes**.

**AI agents**
They work like any contributor, on branches and through pull requests, with the rules in `AGENTS.md`. Never give an agent an owner's token, and don't install apps that can merge or push to `main`.
