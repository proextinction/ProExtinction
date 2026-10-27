"""The one quality gate for humans, AI agents and CI: `python tools/check.py`.

Rebuilds the site, then checks that it is correct and safe to publish. Exits 1 on any error.
`--ci` additionally fails when the committed site/ differs from a fresh build (someone edited
site/ by hand or forgot to rebuild). Standard library only, so it runs anywhere Python 3.9+ runs.
"""
import json, re, subprocess, sys, pathlib, html.parser, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
CI = '--ci' in sys.argv
errors, warnings = [], []


def err(msg):
    errors.append(msg)


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True).stdout


# 1. Build. A crash here is the first error, nothing else makes sense without a build.
r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'build_all.py')], cwd=ROOT, capture_output=True, text=True)
if r.returncode:
    print(r.stdout[-2000:], r.stderr[-4000:], sep='\n')
    sys.exit('FAIL: the build crashed (see above)')

if CI:
    stale = git('status', '--porcelain', '--', 'site', 'brand').strip()
    if stale:
        err('site/ or brand/ is out of date. Run `python tools/build_all.py` and commit the result. Changed:\n  '
            + '\n  '.join(stale.splitlines()[:20]))

# 2. Content files are valid and complete.
for f in sorted((ROOT / 'content').rglob('*.json')):
    try:
        json.loads(f.read_text(encoding='utf-8'))
    except ValueError as e:
        err(f'{f.relative_to(ROOT)}: invalid JSON ({e})')
sys.path.insert(0, str(ROOT / 'tools'))
import runpy
cfg = runpy.run_path(str(ROOT / 'tools' / 'build.py'), run_name='check')   # config only, build() does not run
for lang in cfg['LANGS']:
    for slug, en, _, orig in cfg['SITE'][lang]:
        f = ROOT / 'content' / lang / f'{slug}.json'
        if orig is None and en and f.is_file():   # AI translation: must stay line by line with English
            try:
                n, m = len(json.loads(f.read_text(encoding='utf-8'))), len(json.loads((ROOT / 'content' / 'en' / f'{en}.json').read_text(encoding='utf-8')))
            except ValueError:
                continue
            if n != m:
                err(f'content/{lang}/{slug}.json has {n} lines, content/en/{en}.json has {m}. AI translations must match English line by line')
for folder in ('alt', 'seo'):
    base = json.loads((ROOT / 'content' / folder / 'en.json').read_text(encoding='utf-8'))
    for f in sorted((ROOT / 'content' / folder).glob('*.json')):
        if f.stem == 'en':
            continue
        try:
            keys = json.loads(f.read_text(encoding='utf-8')).keys()
        except ValueError:
            continue
        if folder == 'alt' and set(keys) != set(base):
            err(f'{f.relative_to(ROOT)}: picture keys differ from en.json (missing {sorted(set(base) - set(keys))}, extra {sorted(set(keys) - set(base))})')

# 3. Every page: one title, one h1, no outside resources, internal links that resolve, hreflang both ways.
class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1 = self.titles = 0
        self.links, self.res, self.alts, self.blank, self.robots = [], [], [], [], None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'h1':
            self.h1 += 1
        elif tag == 'title':
            self.titles += 1
        elif tag == 'a' and a.get('href'):
            self.links.append(a['href'])
            if a.get('target') == '_blank' and 'noopener' not in (a.get('rel') or ''):
                self.blank.append(a['href'])
        elif tag == 'link' and a.get('rel') == 'alternate' and a.get('hreflang'):
            self.alts.append(a['href'])
        elif tag == 'meta' and a.get('name') == 'robots':
            self.robots = a.get('content')
        if tag in ('script', 'img', 'iframe', 'source', 'video', 'audio', 'embed', 'object') and a.get('src'):
            self.res.append(a['src'])
        if tag == 'link' and a.get('rel') in ('stylesheet', 'preload', 'icon', 'manifest', 'modulepreload'):
            self.res.append(a.get('href', ''))
        if tag in ('iframe', 'form', 'object', 'embed'):
            self.res.append(f'<{tag}> is not allowed (the CSP blocks it)')


build_src = (ROOT / 'tools' / 'build.py').read_text(encoding='utf-8')
SITE_URL = re.search(r"SITE_URL\s*=\s*'([^']+)'", build_src).group(1)
INDEXABLE = re.search(r'^INDEXABLE\s*=\s*(True|False)', build_src, re.M).group(1) == 'True'


def resolve(path):
    """Same lookup as Cloudflare Pages and tools/serve.py: /x → x.html, /x/ → x/index.html."""
    p = urllib.parse.unquote(path.split('#')[0].split('?')[0]).lstrip('/')
    t = SITE / p
    return any(c.is_file() for c in (t, t / 'index.html', t.with_name(t.name + '.html'))) if p else True


redirects = {l.split()[0] for l in (SITE / '_redirects').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')}
alts_of = {}
pages = sorted(SITE.rglob('*.html'))
for f in pages:
    rel = f.relative_to(SITE).as_posix()
    p = Page()
    p.feed(f.read_text(encoding='utf-8'))
    if p.titles != 1:
        err(f'site/{rel}: {p.titles} <title> tags, expected 1')
    if p.h1 != 1 and rel != 'index.html':
        err(f'site/{rel}: {p.h1} <h1> headings, expected 1')
    for s in p.res:
        if s.startswith('<'):
            err(f'site/{rel}: {s}')
        elif re.match(r'(https?:)?//', s):
            err(f'site/{rel}: loads {s} from another server. Everything must be self-hosted (CSP, privacy policy)')
    for h in p.blank:
        err(f'site/{rel}: link to {h} opens a new tab without rel="noopener"')
    for h in p.links:
        if h.startswith(SITE_URL):
            h = h[len(SITE_URL):] or '/'
        if h.startswith('/') and not h.startswith('//') and h not in redirects and not resolve(h):
            err(f'site/{rel}: broken link {h}')
        if h.lower().startswith('javascript:'):
            err(f'site/{rel}: javascript: link')
    if not INDEXABLE and p.robots and 'noindex' not in p.robots:
        err(f'site/{rel}: indexable although INDEXABLE is False')
    url = SITE_URL + '/' + (rel[:-len('index.html')] if rel.endswith('index.html') else rel[:-5])
    alts_of[url] = set(p.alts)
for url, alts in alts_of.items():
    for a in alts:
        if a not in alts_of:
            err(f'{url}: hreflang points to {a}, which is not a page')
        elif url not in alts_of[a]:
            err(f'{url}: hreflang to {a} is not returned by that page')

# 4. Security headers stay in place.
headers = (SITE / '_headers').read_text(encoding='utf-8')
for must in ("Content-Security-Policy: default-src 'self'", 'frame-ancestors', 'X-Content-Type-Options: nosniff', 'Strict-Transport-Security'):
    if must not in headers:
        err(f'site/_headers lost "{must}"')
csp = re.search(r'Content-Security-Policy: (.*)', headers).group(1)
# the one exception: Cloudflare Web Analytics (ANALYTICS in tools/build.py, named in the privacy policy)
if re.search(r'https?:|\*', re.sub(r'https://(static\.)?cloudflareinsights\.com(?=[ ;])', '', csp)):
    err(f'site/_headers: the CSP allows another server ({csp}). Self-host the resource instead')

# 5. Tracked files: no secrets, nothing huge.
SECRET = re.compile(r'AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_\w{20,}|sk-[A-Za-z0-9_-]{20,}|xox[abpr]-[\w-]{10,}'
                    r'|AIza[\w-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----|CLOUDFLARE_API_TOKEN\s*[=:]\s*\S{10,}')
TEXT = {'.py', '.js', '.json', '.md', '.html', '.css', '.txt', '.svg', '.xml', '.yml', '.yaml', '.toml', '.sh', ''}
for name in git('ls-files', '--cached', '--others', '--exclude-standard').splitlines():
    f = ROOT / name
    if not f.is_file():
        continue
    size = f.stat().st_size
    if size > 2_000_000:
        err(f'{name}: {size // 1024} KB. Files over 2 MB do not belong in the repository (compress images to WebP)')
    elif size > 500_000 and not name.startswith('site/sitemap'):
        warnings.append(f'{name}: {size // 1024} KB, consider compressing')
    if f.suffix in TEXT or f.name.startswith('.env'):
        if f.name.startswith('.env'):
            err(f'{name}: environment files must never be committed')
        elif SECRET.search(f.read_text(encoding='utf-8', errors='ignore')):
            err(f'{name}: looks like it contains a password, key or token. Remove it and rotate the secret')

for w in warnings:
    print('warn:', w)
for e in errors:
    print('FAIL:', e)
print(f'{len(pages)} pages checked, INDEXABLE={INDEXABLE}: '
      + (f'{len(errors)} error(s)' if errors else 'all good'))
sys.exit(1 if errors else 0)
