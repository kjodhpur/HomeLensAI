import type { MetadataRoute } from "next";
import { SITE } from "@/lib/site";

const PATHS = ["", "/product", "/how-it-works", "/pricing", "/security", "/docs", "/about", "/faq", "/contact", "/changelog", "/privacy", "/terms", "/demo"];

export default function sitemap(): MetadataRoute.Sitemap {
  return PATHS.map((p) => ({ url: `${SITE.url}${p}`, changeFrequency: "monthly", priority: p === "" ? 1 : p === "/demo" ? 0.9 : 0.6 }));
}
