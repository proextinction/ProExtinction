# Livegang auf Cloudflare Workers

**Was live geht:** der Ordner `site/`: eine Datei pro Seite, dazu Sprachwahl, 404-Seite, Sitemap, `robots.txt`, Schriften und Bilder.
Es gibt keinen Build-Schritt bei Cloudflare: Die Seiten werden hier mit `python tools/build_all.py` gebaut und fertig committet.
Cloudflare liest zwei Steuerdateien in `site/` (beide werden nicht als Seite ausgeliefert, beide schreibt `tools/build.py`):
- `_headers`: Sicherheits-Header, Cache für Schriften, solange gesperrt auch `X-Robots-Tag: noindex`
- `_redirects`: alte englische Adressen der Google Site (`/manifesto`, `/home` …) auf die neuen (`/en/manifesto`, `/en/`)

Die Domain `proextinction.com` liegt schon im Cloudflare-Konto von James. Die Website kommt in **dasselbe Konto**, damit nichts an einer Einzelperson hängt.
Schritt-für-Schritt-Anleitung für James (Englisch): `HOSTING.md`.

## Adressen
- Startseite einer Sprache: `/en/`, `/de/` (mit Schrägstrich; Cloudflare leitet `/en` dorthin um)
- Seiten: `/en/manifesto`, `/de/manifest` (Cloudflare leitet `…/manifest.html` dorthin um)
- `/` wählt die Sprache nach dem Browser und leitet alte Links der Ein-Datei-Version (`#/de/manifest`) weiter
- Jeder andere Branch wird bei Cloudflare als Vorschau-Version hochgeladen, mit eigener Adresse, wenn *Preview URLs* an sind

## Vor dem Teilen prüfen
| Punkt | Stand |
|---|---|
| Suchmaschinen | gesperrt. Freischalten: in `tools/build.py` `INDEXABLE = True` setzen, `python tools/build_all.py`, committen. Das ändert Meta-Tag, `X-Robots-Tag` (`site/_headers`) und `robots.txt` zusammen. Danach `https://proextinction.com/sitemap.xml` in der Google Search Console einreichen |
| Domain | `SITE_URL` in `tools/build.py` (`https://proextinction.com`, ohne www). www leitet per Cloudflare-Regel auf die Domain ohne www (siehe `HOSTING.md`) |
| Datenschutz | fertig (`content/legal/<de|en>.json`, `privacy`), im Footer jeder Seite verlinkt; Verantwortliche: Pro Extinction als Gruppe von Privatpersonen, info@proextinction.com. Keine Rechtsberatung |
| Impressum | bewusst **nicht veröffentlicht** (Betreiber nicht in Deutschland/Österreich). Liegt als Entwurf bereit (`imprint` in denselben Dateien); `IMPRINT = True` in `tools/build.py` baut und verlinkt es, vorher die Platzhalter in eckigen Klammern ausfüllen |
| Schriften | lokal gehostet, kein Google-Abruf (Lizenz OFL, `site/fonts/licenses/`) |
| Inhalte | Texte, Name, Logo und Spenden-IBAN stammen unverändert von der Original-Seite. Vorher sicherstellen, dass der Auftraggeber der Veröffentlichung zustimmt |
| Telefonnummer | steht auf der deutschen Startseite (Wunsch), vor Livegang bestätigen lassen |

## Aktualisieren
Nach Änderungen: `python tools/build_all.py`, Ergebnis committen und pushen. Cloudflare veröffentlicht automatisch neu.
Lokal ansehen: `python tools/serve.py`. Genau wie Cloudflare (mit `_headers` und `_redirects`, liest `wrangler.jsonc`): `npx wrangler dev`.

## Vercel (Übergang)
`vercel.json` zeigt nur noch Vorschauen von `site/` (immer `noindex`), bis die Seite auf Cloudflare läuft. Danach kann das Vercel-Projekt gelöscht werden.

## Schriften neu beziehen
Quelle: npm-Pakete `@fontsource/*` (Oswald, Anton, Barlow, JetBrains Mono).
Verwendet werden nur `latin` und `latin-ext`, `woff2`. Die `@font-face`-Regeln stehen in `tools/fonts.css`.
