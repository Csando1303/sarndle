// POST /api/guess — checks guesses against today's secret sandwich. See public/game.js.
import LIST from "../../public/sandwiches.json";
import { handle } from "../../public/game.js";

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });

export async function onRequestPost({ request, env }) {
  const secret = env.SARNDLE_SECRET;
  if (!secret) return json({ error: "SARNDLE_SECRET is not set" }, 500);
  let body;
  try { body = await request.json(); } catch { return json({ error: "bad json" }, 400); }
  const out = await handle(body, { secret, list: LIST, now: new Date() });
  return json(out.body, out.status);
}
