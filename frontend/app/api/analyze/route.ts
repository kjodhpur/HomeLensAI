import { NextResponse } from "next/server";
import { analyzeReview } from "@/lib/engine/analyze";

export const runtime = "nodejs";
const MAX_CHARS = 5000;

/** POST { text } → review risk analysis. Part of the web app itself (no separate backend). */
export async function POST(req: Request) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Body must be JSON: { \"text\": \"…\" }" }, { status: 400 });
  }
  const text = typeof body === "object" && body !== null ? (body as { text?: unknown }).text : undefined;
  if (typeof text !== "string" || text.trim().length < 3 || text.length > MAX_CHARS) {
    return NextResponse.json({ error: `text must be a string of 3–${MAX_CHARS} characters` }, { status: 400 });
  }
  return NextResponse.json(analyzeReview(text));
}
