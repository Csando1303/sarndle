# Sarndle

Wordle-style daily game: guess today's UK supermarket sandwich in 6 tries.
Owner: Connor. Originally built as a claude.ai artifact (https://claude.ai/artifact/A22oHadBzEkCn5L2a7QeAa); next goal is a full standalone website.

## Files
- `public/` – the published site (no build step): `index.html` (UI), `game.js` (game logic), `sandwiches.json` (list), `privacy.html`, `ads.txt`.
- `functions/api/guess.js` – optional Cloudflare Pages Function that runs `public/game.js` on the server with `SARNDLE_SECRET`.
- `tests/game.test.mjs` – `npm test`.
- `data/sarndle.db` – SQLite: `shop`, `sandwich`, `filling`, `daily` tables.
- `data/sandwiches.csv`, `data/sandwiches.json` – same 250 sandwiches.
- `data/build.py` – regenerates CSV/JSON from the hand-collected lists (prices checked 17 Nov 2026).

## Game rules
Clues per guess: Supermarket (exact), Price (green exact, yellow within 50p, ↑↓), Filling (green all match, yellow overlap),
Bread (green exact, yellow same family: sliced / rolls / wraps / toastie), Range (Value, Standard, Premium, Festive, Plant-based, Free From; exact only).

## How the daily sandwich is chosen
- `pick(list, secret, date)` in `public/game.js`: list sorted by HMAC(secret, sandwich), walked one step per day since LAUNCH (2026-11-17 = #1). No repeats until all used. Festive range only in Nov/Dec.

## Hosting
- **GitHub Pages (live)**: `.github/workflows/static.yml` publishes `public/` on every push to `main`. There's no backend, so `POST api/guess`
  returns 404/405 and the page switches to running `game.js` in the browser with `PUBLIC_SEED` (in `index.html`). Anyone can work out the answer from the source.
  Changing `PUBLIC_SEED` reshuffles every day, including past ones.
- **Cloudflare Pages (optional)**: `npm run deploy`. The page uses `api/guess`, and the answer stays secret until the game ends. Needs `SARNDLE_SECRET`.
  The two hosts give different daily sandwiches.
- `data/` is source material and isn't published.
- ads.txt only counts at the domain root, so on a `*.github.io/sarndle-repo/` project page it needs a custom domain (or a `<user>.github.io` repo).
- AdSense: set `ADSENSE_CLIENT` + uncomment the `google-adsense-account` meta in `index.html`, replace `pub-XXXXXXXXXXXXXXXX` in `ads.txt`,
  and `CONTACT_EMAIL` in `privacy.html`. Ads load only when the ID is set and the page is on http(s) outside claude.ai. Consent (UK/EEA) is Google's CMP, set up in the AdSense dashboard.
- Share text uses `SITE_URL`: the page's own URL when it's served over http(s), or the claude.ai artifact URL otherwise (file:// or inside claude.ai).

## Local state (localStorage)
`sarndle-v2` (today's guesses: `{day, g, hint}`), `sarndle-stats`, `sarndle-seen`, `sarndle-cb` (colour-blind mode).

## Known data gaps / todo
- No Lidl data (no online shop); Boots only 5 premium lines; M&S prices from Zoom by Ocado (may be above in-store).
- 145 sandwiches have bread "Sliced" (listing didn't say). Fillings parsed from product names.
- Festive lines will go out of stock in January – refresh data.
- Sandwich pictures are SVG drawings generated from bread + fillings (`sandwichSVG`).
