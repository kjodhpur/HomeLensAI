# Frontend (Next.js 16, App Router, TypeScript)

```bash
cp .env.example .env.local        # API_BASE_URL=http://127.0.0.1:8000
npm install
npm run dev                       # http://localhost:3000   (start the backend first)
npm run typecheck && npm run build
```

* Pages are **server components** that call the API through `lib/api.ts` (`API_BASE_URL`); `/analyze` is a client component that calls same-origin `/api/analyze`, which `next.config.mjs` proxies to the backend.
* Types mirror [`../docs/DATA_CONTRACT.md`](../docs/DATA_CONTRACT.md) in `lib/types.ts`.
* Open tasks (charts, polish) are listed in [`../docs/TEAM_GUIDE.md`](../docs/TEAM_GUIDE.md). Deployment: [`../docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md).
