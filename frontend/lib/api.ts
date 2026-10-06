import type { AnalyzeResult, Provider, ProviderList, Summary } from "./types";

// Server-side calls go straight to the backend. (Browser-side calls use same-origin "/api/..." — see next.config.mjs.)
const BASE = (process.env.API_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function get<T>(path: string): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  } catch {
    throw new ApiError(0, `Cannot reach the API at ${BASE}. Is the backend running?`);
  }
  if (!res.ok) throw new ApiError(res.status, `API ${res.status} for ${path}`);
  return (await res.json()) as T;
}

export const api = {
  summary: () => get<Summary>("/api/summary"),
  providers: (params: Record<string, string | undefined> = {}) => {
    const qs = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) if (v) qs.set(k, v);
    return get<ProviderList>(`/api/providers?${qs.toString()}`);
  },
  provider: (id: string) => get<Provider>(`/api/providers/${encodeURIComponent(id)}`),
};

/** Browser-side helper (used by the client component on /analyze). */
export async function analyzeText(text: string): Promise<AnalyzeResult> {
  const res = await fetch("/api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text }) });
  if (!res.ok) throw new ApiError(res.status, `Analyze failed (${res.status})`);
  return (await res.json()) as AnalyzeResult;
}
