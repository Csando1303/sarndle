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
- Archive: `handle()` accepts any day from LAUNCH to today (future/bad days restart on today). The page plays Sarndle #N at `?d=N`, and the 📅 button lists every day.
  Archive games don't count towards stats or streaks, and their share text links to `?d=N`.

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
- Analytics: GoatCounter (no cookies, so no consent banner). Set `GOATCOUNTER` in `index.html` to the site code (`<code>.goatcounter.com`); empty = off, and nothing is sent from localhost/file/claude.ai.
  Events via `track()`: `today|archive/started`, `today|archive/won-N`, `today|archive/lost`, `hint`, `shared`, `archive-opened`, `stats-opened`, `colour-blind-on`. Described in `privacy.html`.
  GoatCounter's hosted service is free for non-commercial use, so once AdSense is on, check its terms (paid plan or self-host).
- Share text uses `SITE_URL`: the page's own URL when it's served over http(s), or the claude.ai artifact URL otherwise (file:// or inside claude.ai).

## Local state (localStorage)
`sarndle-v2` (today's guesses: `{day, g, hint}`), `sarndle-archive` (`{day: {day, g, hint}}` for past days), `sarndle-history` (`{day: guesses to win, 0 = lost}`, today's and archive games, for the 📅 list), `sarndle-stats` (today's games only), `sarndle-seen`, `sarndle-cb` (colour-blind mode).

## Sides & drinks (planned: full meal deal)
- `data/build_extras.py` → `data/sides.csv/json`, `data/drinks.csv/json` (one row per shop) and `*_products.json` (merged by product, `shops: {shop: price}`).
- Collected 18 Nov 2026 from Tesco's meal-deal lists and Morrisons' "Food To Go Meal Deal" offer page only (167 sides, 158 drinks). Sainsbury's, Asda, Co-op, Waitrose, Boots and M&S didn't give readable lists (bot-blocked or loaded by JavaScript).
- `*_products.json` is the game list: one product per drink/side, merged across shops and pack sizes (165 sides, 145 drinks).
  `shops` lists every shop that sells it, `shop_prices` gives each shop's price and pack size, and `price_gbp` is the average at the main size (500ml if sold, otherwise the largest).
  `sizes`, `listings` and `needs_check` are kept for reference.
- `in_game`: only these go in the game (157 sides, 126 drinks). Energy drinks are capped at 3 per brand (`CAP`, best-known first from `KEEP`), and copies of the same product (Duo bars and similar) are left out (`DUPLICATE`). `left_out` gives the reason.
- Types and flavours come from keyword rules. `ALIAS` (same product, different name), `FIX` (wrong fields; flavours not in the name were looked up on brand pages) and `validate()` live in the script, and the build stops if the data has gaps.
- Proposed clues. Sides: Shop(s), Price, Type (yellow = same family: Salty / Sweet / Chilled savoury / Fresh), Flavour (overlap), Brand (yellow = same maker).
  Drinks: Shop(s), Price, Type (yellow = family: Fizzy / Energy & sport / Water / Juice & smoothie / Milky / Tea & kombucha), Flavour, Size ml (↑↓), Sugar.
- Branded items are sold at several shops, so the Shop clue needs a list: green = same shops, yellow = overlap.

## Known data gaps / todo
- No Lidl data (no online shop); Boots only 5 premium lines; M&S prices from Zoom by Ocado (may be above in-store).
- 145 sandwiches have bread "Sliced" (listing didn't say). Fillings parsed from product names.
- Festive lines will go out of stock in January – refresh data.
- Sandwich pictures are SVG drawings generated from bread + fillings (`sandwichSVG`).
