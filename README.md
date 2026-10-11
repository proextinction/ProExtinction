# Pro Extinction · Website

Die neue Website von Pro Extinction (Repository `proextinction/ProExtinction`) in Design B (Poster), in 29 Sprachen (EN, DE, PL, ES, IT sowie die komplett KI-übersetzten FR, PT, RU, ZH, HI, AR, BN, UR, ID, JA, TR, VI, KO, FA, MR, TE, TA, SW, TH, NL, UK, TL, PA, GU; Arabisch, Urdu und Persisch von rechts nach links), Hell und Dunkel.
Design A (Ember) ist entfernt; er liegt noch im alten Repository `AppsOfUse/ProExtinction` (Archiv) auf dem Branch `backup/vercel-2026-10-06`.

| Pfad | Inhalt |
|---|---|
| **`site/`** | **Die fertige Website (geht live):** eine Datei pro Seite, `site/<sprache>/<seite>.html`, erreichbar als `/<sprache>/<seite>` (Startseite: `/<sprache>/`). Dazu `index.html` (Sprachwahl), `404.html`, `sitemap.xml`, `robots.txt`, `style.css`, `site.js`, `og.png`, Schriften und Bilder. Wird von `tools/build.py` erzeugt, nur `fonts/`, `img/` und `favicon.svg` sind Quellen |
| `DEPLOY.md`, `HOSTING.md` | Livegang auf Cloudflare Pages: Checkliste (DE) und Einrichtung für James (EN). Steuerdateien `site/_headers` und `site/_redirects` schreibt `tools/build.py` |
| `brand/` | Brand Kit von Design B (Tokens, `BRAND.md`, Referenzseiten) |
| `content/` | Text als JSON pro Sprache: Originaltext der jeweiligen Sprachseite plus KI-Übersetzungen der fehlenden Seiten (welche das sind, steht in `SITE` in `tools/build.py`) |
| `content/seo/` | Suchmaschinen-Beschreibung jeder Seite pro Sprache; `en.json` ist die Vorlage |
| `content/alt/` | Bildbeschreibungen (alt-Text) für Screenreader und Bildersuche pro Sprache, Schlüssel = Bildnummer aus `content/images.json`; `en.json` ist die Vorlage. Kanal-Profilbilder neben ihrem Namen haben bewusst keine |
| `content/legal/` | Datenschutz (DE, EN, live) und Impressum (Entwurf, nicht veröffentlicht; Schalter `IMPRINT` in `tools/build.py`) |
| `content/diagrams/` | Texte der zwei Manifest-Grafiken (Kreislauf des Leidens, Grausames Design mit allen Beispielen) pro Sprache, eine Zeile pro Text, Felder mit `|` getrennt; `en.txt` ist die Vorlage (`tools/diagrams.py`, `tools/dg.js`) |
| `raw/` | Rohtext der Google-Sites-Seiten PL/ES/IT (`tools/scrape.py`, dann `tools/parse_raw.py`) |
| `tools/` | Generator: `build.py` (Seiten, SEO, Sitemap, Cloudflare-Steuerdateien), `kit.py` (Brand Kit), `serve.py` (Vorschau), `og.js` (Teilen-Bild), `blocks.py`, `parse.py`, CSS-Quellen, `assets/` (Logo, `site.js`) |
| `DECISIONS.md` | was entschieden und was offen ist |
| `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md` | Regeln für KI-Agents und Mitwirkende (EN), Ablauf eines Beitrags |
| `.claude/` | Claude Code: Wächter-Hook (`hooks/guard.py`), Rechte (`settings.json`), Skills `edit-content`, `translate`, `review` |
| `.github/` | Prüfung bei jedem Pull Request (`workflows/check.yml`), Code-Owner, PR-Vorlage, Dependabot |

Prüfen (vor jedem Commit): `python tools/check.py`, baut alles neu und prüft Links, hreflang, fremde Server, Sicherheits-Header und Geheimnisse.
Bauen: `python tools/build_all.py` (Windows, Mac, Linux; unter Mac/Linux ggf. `python3`).
Ansehen: `python tools/serve.py`, dann http://localhost:8000 öffnen. Die Seiten brauchen einen Server, weil die Links Adressen wie `/de/manifest` sind.

## Suchmaschinen (SEO)
Jede Seite hat Titel, Beschreibung (`content/seo/`), Canonical-Link, `hreflang`-Verweise auf alle Sprachfassungen, Open-Graph-Angaben fürs Teilen (Bild `site/og.png`) und auf den Startseiten Schema.org-Daten zur Organisation. `site/sitemap.xml` listet alle Seiten mit ihren Sprachfassungen.
**Noch gesperrt:** `INDEXABLE = False` in `tools/build.py`. Auf `True` stellen und neu bauen schaltet Meta-Tag, `X-Robots-Tag` (in `site/_headers`) und `robots.txt` gemeinsam frei. Eine Rechtsseite mit Platzhaltern in eckigen Klammern bleibt für Suchmaschinen gesperrt.
Domain: `SITE_URL` in `tools/build.py` (`https://proextinction.com`). Alte englische Adressen (`/manifesto`, `/home` …) leiten auf die neuen um, alte Links der Ein-Datei-Version (`#/de/manifest`) leitet `/` weiter.

Adresszusätze zum Testen: `?theme=light` oder `?theme=dark`, Logo-Effekt `?scare=reset` (Zähler zurück), `?motion=on` (trotz „Bewegung reduzieren").

Versteckte Effekte (`tools/smoke.js`, `tools/eggs.js`): Rauch am Ende langer Seiten; Sterne, die auf „Cosmic Extinction“ beim Lesen verlöschen; Logo fünfmal schnell anklicken (die Seite verblasst, der letzte Satz des Manifests erscheint); Geburtenzähler in der Fusszeile (Menschen, ~Nutztiere, ~Wildtiere, ~Insekten; grobe Schätzungen aus Jahreszahlen, `BORN` in `tools/build.py`); Gruss in der Browser-Konsole. Mit „Bewegung reduzieren“ nur sanfte Überblendungen.
