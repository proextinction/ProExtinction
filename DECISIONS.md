# Entscheidungen · Pro Extinction Website-Redesign

Stand: laufend gepflegt. **Entschieden: Design B (Poster).** A Ember ist entfernt (noch im alten Repository `AppsOfUse/ProExtinction` auf `backup/vercel-2026-10-06`), C Ring war schon verworfen.

## Offen (später festlegen)
| Frage | Stand | Wann |
|---|---|---|
| Endgültige Hex-Werte | vorläufig in `brand/b-poster/tokens.css` | offen |
| Original-Logo als Vektor | fehlt, `mark.svg` ist eine Nachzeichnung | sobald auffindbar |
| Schriften selbst hosten | **erledigt** für `site/` (lokal, OFL). Nur `brand-helmet.html` lädt noch von Google | – |
| Impressum | **entschieden: vorerst keins** (lose Gruppe, Betreiber nicht in DE/AT). Entwurf liegt bereit, `IMPRINT` in `tools/build.py` | wieder prüfen, sobald jemand aus DE/AT als Betreiber auftritt |
| Suchmaschinen freischalten | gesperrt, `INDEXABLE` in `tools/build.py`; entschieden: dann alle 29 Sprachen und alle Crawler (auch KI) zulassen | beim Livegang |
| Bilder von „Suffering in detail" (16) | hinter einem Klick verschwommen | – |
| Deutsche Übersetzung der 4 fehlenden Seiten | Entwürfe in `content/_translation-pending/`, nicht eingebaut | eigener Schritt |
| Telefonnummer auf der deutschen Seite | bleibt (Wunsch), vor Livegang bestätigen | vor Livegang |
| Hosting und Domain | **Cloudflare Pages** im Cloudflare-Konto von James, wo die Domain schon liegt (gratis, `HOSTING.md`); `proextinction.com` ohne www. Repository liegt in der Organisation `proextinction` (`proextinction/ProExtinction`). Offen: Einrichtung durch James mit Branch `main` als Live-Stand; `main` schützen (Repository öffentlich oder GitHub Team, `HOSTING.md` Abschnitt 5) | beim Livegang |

## Entschieden
1. **Marke:** Pro Extinction. „AbolishSuffering" bleibt nur der Discord-Name.
2. **Tagline:** „Together, we end suffering."
3. **Ziel:** Neulinge überzeugen, nicht die Community mobilisieren.
4. **Persönlichkeit:** ernst, rational, empathisch, entschlossen, ruhig-düster. Nicht reißerisch, esoterisch, verspielt, hoffnungslos.
5. **Modi:** Hell und Dunkel, umschaltbar per Button oben rechts.
6. **Sprachen der Konzepte:** EN (Standard und Vorlage), DE, PL, ES, IT. Fehlt eine englische Seite in einer anderen Sprache, wird sie per KI aus dem Englischen übersetzt und mit einem Hinweis auf der Seite gekennzeichnet (kein "(AI)" im Menü). Seiten, die es nur in einer Sprache gibt (DE Ressourcen, PL Zasoby, ES Recursos/Mapa del sitio), bleiben erhalten. Dazu kommen FR, PT, RU, ZH (Chinesisch, vereinfacht) HI (Hindi), AR (Arabisch), BN (Bengalisch), UR (Urdu), ID (Indonesisch), JA (Japanisch), TR (Türkisch), VI (Vietnamesisch), KO (Koreanisch), FA (Persisch), MR (Marathi), TE (Telugu), TA (Tamil), SW (Swahili), TH (Thai), NL (Niederländisch), UK (Ukrainisch), TL (Filipino), PA (Punjabi) und GU (Gujarati) ohne Originalseite: komplett aus dem Englischen übersetzt, in der Sprachauswahl als z. B. "RU (AI)" markiert und mit Hinweis auf jeder Seite, aber ohne "(AI)" an jedem Menüpunkt. Kyrillisch (Russisch, Ukrainisch) kommt aus lokalen Schriftdateien (Oswald, Source Serif 4, JetBrains Mono), Chinesisch, Japanisch, Koreanisch, Thai, Hindi, Marathi, Bengalisch, Telugu, Tamil, Punjabi (Gurmukhi), Gujarati, Arabisch, Urdu und Persisch aus den Systemschriften. Arabisch, Urdu und Persisch laufen von rechts nach links (`dir="rtl"`): das CSS nutzt logische Eigenschaften (inline-start/end), damit Navigation, Kapitelübersicht und Randlinien gespiegelt werden; Wordmark und englischer Slogan bleiben links nach rechts. Die Übersetzungen folgen den Regeln des unslop-Skills (cursor/plugins). Tippfehler werden korrigiert.
7. **Inhalt:** Originaltext bleibt wörtlich. Neu geschrieben werden nur Buttons, Zwischenüberschriften, Hinweise (du-Ansprache, sachlich, Verbotsliste in `BRAND.md`).
8. **Farbe:** Akzent unter etwa 5 % der Fläche, Silber nur in Logo und Wordmark.
9. **Typografie:** schwere Versalien-Grotesk für Display, Mono sparsam, nie Inter oder Roboto als Hauptschrift. Wordmark als Schrift mit CSS-Metall, kein Flyer-Bild.
10. **Anmutung:** Leerraum, schmale Textspalte (68 ch), Körnung, Haarlinien, keine Schatten oder Glaseffekte.
11. **Signatur:** der rote Schrägstrich (Trenner, Fortschritt, Hover).
12. **Bausteine:** Navigation immer sichtbar (kein Hamburger-Menü), Kapitelübersicht, FAQ aufklappbar, Zitatblock, vier Efforts, Call-to-Action, Sprach- und Theme-Umschalter.
13. **Bilder:** Hauptbildsprache im Code (Linien, Ringe, Schrägstrich, Körnung). Keine Stockfotos. Drastische Bilder nur hinter einem Klick. **Stand jetzt:** die 30 Inhaltsbilder der englischen Originalseite sind zur Sichtung eingebaut, durchnummeriert (#1 bis #30, Liste in `content/images.json`, Dateien in `presentation/img/`). Danach wird entschieden, welche bleiben und welche hinter einen Klick kommen.
14. **Logo-Effekt:** nur das große Logo, beim 1. Hover und jedem 10., maximal 1,5×, 4 s, respektiert „Bewegung reduzieren".
15. **Scrollbars:** dünn, Akzentfarbe; innen dunkler als außen.
16. **Zielplattform:** nur Website, responsiv. Keine PDFs, Slides, Thumbnails.

## Design B (Poster)
| | |
|---|---|
| Form | eckig |
| Aufbau | zentriert, plakativ |
| Navigation | Navbar oben |
| Kapitelübersicht | rechts mitlaufend ab 1280 px |
| Farbwelt | Rot/Schwarz/Silber |
| Fließtext | Sans (Barlow) |
| Standardmodus | dunkel |

## Aufbau der Website (entschieden 2026-10)
Eine Datei pro Seite in `site/`, Adressen `/<sprache>/<seite>`; `/` wählt die Sprache nach dem Browser. Die frühere Ein-Datei-Präsentation (`presentation/index.html`, 8,8 MB mit allen Sprachen) ist ersetzt: Sie war langsam und für Suchmaschinen nur eine einzige Seite. Ihre alten Links (`#/de/manifest`) leitet `/` weiter.
Standardmodus bleibt dunkel; Hell nur, wenn der Besucher es wählt.

## Vorgehen
1. Gemeinsames liegt in `tools/css/base.css`, `tools/build.py`, `tools/blocks.py`, `content/`; Design in `brand/b-poster/tokens.css` und `tools/css/b.css`.
2. Nach jeder Änderung: `python3 tools/build_all.py`.
