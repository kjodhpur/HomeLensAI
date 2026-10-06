// API_BASE_URL = where the FastAPI backend lives.
//   local:   http://127.0.0.1:8000  (default)
//   Vercel:  https://<your-backend-project>.vercel.app   (set it in the frontend project's Environment Variables)
const API_BASE_URL = (process.env.API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Browser code can call same-origin "/api/..." — Next proxies it to the backend (no CORS needed).
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API_BASE_URL}/api/:path*` }];
  },
};

export default nextConfig;
