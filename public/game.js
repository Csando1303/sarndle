// Game logic, shared by the browser (public/index.html), the Cloudflare Pages Function (functions/api/guess.js) and tests.
// On Cloudflare the answer comes from SARNDLE_SECRET on the server. On static hosting (GitHub Pages) the page runs this
// itself with a public seed, so the answer can be worked out by reading the source.
// A sandwich is [name, shop, price £, fillings[], bread, range].

export const MAX = 6;
export const LAUNCH = "2026-11-17"; // Sarndle #1
const DAY = 864e5;

// Bread families: same family = yellow.
export const FAM = { Sliced: 1, White: 1, Malted: 1, Wholemeal: 1, Oatmeal: 1, Seeded: 1, Rye: 1, "Onion bread": 1, "Sub roll": 2, Baguette: 2, Roll: 2, Bagel: 2, Brioche: 2, Wrap: 3, Naan: 3, Toastie: 4 };

export const key = s => s[0] + "|" + s[1];

export function londonDate(d) {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/London", year: "numeric", month: "2-digit", day: "2-digit" }).format(d);
}
export const addDays = (date, n) => new Date(Date.parse(date) + n * DAY).toISOString().slice(0, 10);
export const dayNumber = date => Math.round((Date.parse(date) - Date.parse(LAUNCH)) / DAY) + 1;

// Secret, stable order of the whole list: sort by HMAC(secret, sandwich key).
// Cached per isolate; the list is a static import so it never changes while running.
const enc = new TextEncoder();
let cached = { secret: null, list: null, order: null };
async function secretOrder(list, secret) {
  if (cached.secret === secret && cached.list === list) return cached.order;
  const k = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const tags = await Promise.all(list.map(s => crypto.subtle.sign("HMAC", k, enc.encode(key(s)))));
  const hex = tags.map(t => [...new Uint8Array(t)].map(b => b.toString(16).padStart(2, "0")).join(""));
  const order = list.map((_, i) => i).sort((a, b) => (hex[a] < hex[b] ? -1 : hex[a] > hex[b] ? 1 : 0));
  cached = { secret, list, order };
  return order;
}

// Today's sandwich. Walks the secret order one step per day, so nothing repeats until the pool is used up.
// Festive lines are only in the pool in November and December.
export async function pick(list, secret, date) {
  const order = await secretOrder(list, secret);
  const m = +date.slice(5, 7), festive = m === 11 || m === 12;
  const pool = festive ? order : order.filter(i => list[i][5] !== "Festive");
  const n = dayNumber(date) - 1;
  return list[pool[((n % pool.length) + pool.length) % pool.length]];
}

function cmpNum(a, b, tol, fmt) {
  const c = a === b ? "g" : Math.abs(a - b) <= tol + 1e-9 ? "y" : "r";
  return [c, fmt(a) + (a < b ? " ↑" : a > b ? " ↓" : "")];
}

// Clues for one guess: [[colour, text] x5] for Supermarket, Price, Filling, Bread, Range. Colour is g / y / r.
export function cols(s, ans) {
  const shop = [s[1] === ans[1] ? "g" : "r", s[1]];
  const price = cmpNum(s[2], ans[2], 0.5, v => "£" + v.toFixed(2));
  const hit = s[3].filter(f => ans[3].includes(f)).length;
  const fill = [hit === s[3].length && hit === ans[3].length ? "g" : hit ? "y" : "r", s[3].join(", ")];
  const bread = [s[4] === ans[4] ? "g" : FAM[s[4]] && FAM[s[4]] === FAM[ans[4]] ? "y" : "r", s[4] === "Sliced" ? "Sliced bread" : s[4]];
  const rng = [s[5] === ans[5] ? "g" : "r", s[5]];
  return [shop, price, fill, bread, rng];
}

// body: { day: "YYYY-MM-DD", guesses: ["name|shop", ...], hint: bool }
// Stateless: the browser sends all of today's guesses each time, and the server works out the clues again.
// The answer is only included once the game is over (won, or 6 guesses).
export async function handle(body, { secret, list, now }) {
  if (!body || typeof body !== "object") return { status: 400, body: { error: "bad request" } };
  const today = londonDate(now), yesterday = addDays(today, -1);
  let day = body.day, raw = Array.isArray(body.guesses) ? body.guesses.slice(0, 20) : [];
  // Allow yesterday so a game started just before midnight can finish. Anything else (stale, future, wrong clock) restarts on today.
  if (day !== today && !(day === yesterday && yesterday >= LAUNCH)) { day = today; raw = []; }

  const idx = new Map(list.map((s, i) => [key(s), i]));
  const ans = await pick(list, secret, day), ak = key(ans);
  const results = [], seen = new Set();
  let won = false;
  for (const k of raw) {
    if (won || results.length >= MAX) break;
    if (typeof k !== "string" || !idx.has(k) || seen.has(k)) continue; // unknown/duplicate guesses are dropped
    seen.add(k);
    results.push({ k, c: cols(list[idx.get(k)], ans) });
    if (k === ak) won = true;
  }
  const done = won || results.length >= MAX;
  const out = { day, dayNo: dayNumber(day), results, won, done };
  if (done) out.answer = ans;
  else if (body.hint && results.length >= 3) out.hint = { filling: ans[3][0] || null, price: Math.floor(ans[2]) };
  return { status: 200, body: out };
}
