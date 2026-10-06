import type { AnalyzeResult, Aspect, Example, Overview, Provider } from "./types";

// Server-side calls go straight to the backend. (Browser-side calls use same-origin "/api/..." — see next.config.mjs.)
const BASE = (process.env.API_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(url, { cache: "no-store", ...init });
  } catch {
    throw new ApiError(0, `Cannot reach the API at ${url.startsWith("http") ? BASE : "/api"}. Is the backend running?`);
  }
  if (!res.ok) throw new ApiError(res.status, `API ${res.status} for ${url.replace(BASE, "")}`);
  return (await res.json()) as T;
}

/** Server-component data loaders. */
export const api = {
  overview: () => request<Overview>(`${BASE}/api/overview`),
  providers: async () => (await request<{ items: Provider[] }>(`${BASE}/api/providers?limit=500`)).items,
  aspects: () => request<Aspect[]>(`${BASE}/api/aspects`),
  examples: () => request<Example[]>(`${BASE}/api/examples`),
  analyze: (text: string) =>
    request<AnalyzeResult>(`${BASE}/api/analyze`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text }) }),
};

/** Browser-side: same-origin, proxied to the backend by next.config.mjs. */
export const analyzeInBrowser = (text: string) =>
  request<AnalyzeResult>("/api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text }) });
