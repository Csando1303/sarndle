import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { handle, pick, key, londonDate, MAX } from "../public/game.js";

const list = JSON.parse(readFileSync(new URL("../public/sandwiches.json", import.meta.url)));
const secret = "test-secret";
const at = d => new Date(d + "T12:00:00Z");
const call = (body, now = at("2026-11-17")) => handle(body, { secret, list, now });

test("answer is hidden until the game is over", async () => {
  const ans = await pick(list, secret, "2026-11-17");
  const wrong = list.filter(s => key(s) !== key(ans)).map(key);
  let r = await call({ day: "2026-11-17", guesses: wrong.slice(0, 5) });
  assert.equal(r.body.done, false);
  assert.equal(r.body.answer, undefined);
  assert.equal(JSON.stringify(r.body).includes(ans[0]) && !wrong.slice(0, 5).some(k => k.startsWith(ans[0] + "|")), false);
  r = await call({ day: "2026-11-17", guesses: wrong.slice(0, 6) });
  assert.equal(r.body.done, true);
  assert.equal(r.body.won, false);
  assert.deepEqual(r.body.answer, ans);
});

test("correct guess wins and stops further guesses", async () => {
  const ans = await pick(list, secret, "2026-11-17");
  const other = list.find(s => key(s) !== key(ans));
  const r = await call({ day: "2026-11-17", guesses: [key(other), key(ans), key(other)] });
  assert.equal(r.body.won, true);
  assert.equal(r.body.results.length, 2);
  assert.ok(r.body.results[1].c.every(c => c[0] === "g"));
});

test("unknown, duplicate and extra guesses are dropped", async () => {
  const ans = await pick(list, secret, "2026-11-17");
  const wrong = list.filter(s => key(s) !== key(ans)).map(key);
  const r = await call({ day: "2026-11-17", guesses: ["nope|x", wrong[0], wrong[0], ...wrong.slice(1, 10)] });
  assert.equal(r.body.results.length, MAX);
  assert.equal(r.body.results[0].k, wrong[0]);
});

test("future, pre-launch and bad days restart on today", async () => {
  const g = [key(list[0])];
  for (const day of ["2026-11-25", "2026-11-16", "2026-02-30", "nope", 5, undefined]) {
    const r = await call({ day, guesses: g }, at("2026-11-20"));
    assert.equal(r.body.day, "2026-11-20", String(day));
    assert.equal(r.body.results.length, 0);
  }
});

test("archive: any past day back to #1 can be played, with its own answer", async () => {
  const now = at("2026-12-01");
  for (const [day, no] of [["2026-11-17", 1], ["2026-11-19", 3], ["2026-11-30", 14]]) {
    const ans = await pick(list, secret, day);
    const r = await call({ day, guesses: [key(ans)] }, now);
    assert.equal(r.body.day, day);
    assert.equal(r.body.dayNo, no);
    assert.equal(r.body.won, true);
    assert.deepEqual(r.body.answer, ans);
  }
});

test("archive answers stay hidden until the game is over", async () => {
  const ans = await pick(list, secret, "2026-11-18");
  const wrong = list.filter(s => key(s) !== key(ans)).map(key);
  const r = await call({ day: "2026-11-18", guesses: wrong.slice(0, 3) }, at("2026-11-25"));
  assert.equal(r.body.answer, undefined);
});

test("day numbers round-trip", async () => {
  const { dayNumber, dayFromNumber } = await import("../public/game.js");
  for (const n of [1, 2, 45, 400]) assert.equal(dayNumber(dayFromNumber(n)), n);
});

test("hint only after 3 guesses", async () => {
  const ans = await pick(list, secret, "2026-11-17");
  const wrong = list.filter(s => key(s) !== key(ans)).map(key);
  assert.equal((await call({ day: "2026-11-17", guesses: wrong.slice(0, 2), hint: true })).body.hint, undefined);
  const h = (await call({ day: "2026-11-17", guesses: wrong.slice(0, 3), hint: true })).body.hint;
  assert.deepEqual(h, { filling: ans[3][0] || null, price: Math.floor(ans[2]) });
});

test("no repeats within a cycle; festive only in Nov/Dec; secret changes the order", async () => {
  const days = n => Array.from({ length: n }, (_, i) => new Date(Date.parse("2027-01-01") + i * 864e5).toISOString().slice(0, 10));
  const nonFestive = list.filter(s => s[5] !== "Festive").length;
  const picks = await Promise.all(days(nonFestive).map(d => pick(list, secret, d)));
  assert.equal(new Set(picks.map(key)).size, nonFestive);
  assert.ok(picks.every(s => s[5] !== "Festive"));
  const a = await Promise.all(days(10).map(d => pick(list, secret, d)));
  const b = await Promise.all(days(10).map(d => pick(list, "other-secret", d)));
  assert.notDeepEqual(a.map(key), b.map(key));
});

test("london date rolls over at UK midnight", () => {
  assert.equal(londonDate(new Date("2026-07-01T23:30:00Z")), "2026-07-02"); // BST
  assert.equal(londonDate(new Date("2026-12-01T23:30:00Z")), "2026-12-01"); // GMT
});
