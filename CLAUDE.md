# Sarndle

Wordle-style daily game: guess today's UK supermarket sandwich in 6 tries.
Owner: Connor. Originally built as a claude.ai artifact (https://claude.ai/artifact/A22oHadBzEkCn5L2a7QeAa); next goal is a full standalone website.

## Files
- `index.html` – the whole game (HTML/CSS/JS in one file, no build step). Sandwich list is embedded as `const S=[...]`.
- `data/sarndle.db` – SQLite: `shop`, `sandwich`, `filling`, `daily` tables.
- `data/sandwiches.csv`, `data/sandwiches.json` – same 250 sandwiches.
- `data/build.py` – regenerates CSV/JSON from the hand-collected lists (prices checked 17 Nov 2026).

## Game rules
Clues per guess: Supermarket (exact), Price (green exact, yellow within 50p, ↑↓), Filling (green all match, yellow overlap),
Bread (green exact, yellow same family: sliced / rolls / wraps / toastie), Range (Value, Standard, Premium, Festive, Plant-based, Free From; exact only).

## How the daily sandwich is chosen
- `autoPick(date)`: seeded shuffle of the base list, indexed by days since LAUNCH (2026-11-17 = #1). No repeats until all used. Festive range only in Nov/Dec.
- Optional manual override per day via hidden admin view (`#admin`, editors only).

## Hosting
- Publish `index.html`, `privacy.html`, `ads.txt` (no build). `data/` is source material and doesn't need to be published.
- AdSense: set `ADSENSE_CLIENT` + uncomment the `google-adsense-account` meta in `index.html`, replace `pub-XXXXXXXXXXXXXXXX` in `ads.txt`,
  and `CONTACT_EMAIL` in `privacy.html`. Ads load only when the ID is set and the page is on http(s) outside claude.ai. Consent (UK/EEA) is Google's CMP, set up in the AdSense dashboard.
- Share text uses `SITE_URL`: the page's own URL when it's served over http(s), or the claude.ai artifact URL otherwise (file:// or inside claude.ai).

## claude.ai-specific code (inert on a standalone site)
- `window.claude.use("db")` / `use("user")` – artifact database + permissions. Docs: `days/<YYYY-MM-DD>` (override sandwich), `sandwiches/*` (extra sandwiches).
  Without `window.claude`, the boot code skips it: no overrides, and `#admin` never opens (isEditor stays false). So the standalone site is auto-pick only.
  To bring back overrides: move them + the sandwich list to a backend (e.g. SQLite/Postgres API) and protect admin with real auth.

## Local state (localStorage)
`sarndle-v2` (today's guesses, keyed to answer), `sarndle-stats`, `sarndle-seen`, `sarndle-cb` (colour-blind mode).

## Known data gaps / todo
- No Lidl data (no online shop); Boots only 5 premium lines; M&S prices from Zoom by Ocado (may be above in-store).
- 145 sandwiches have bread "Sliced" (listing didn't say). Fillings parsed from product names.
- Festive lines will go out of stock in January – refresh data.
- Sandwich pictures are SVG drawings generated from bread + fillings (`sandwichSVG`).
