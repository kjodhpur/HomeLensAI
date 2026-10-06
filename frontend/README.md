# Frontend (Next.js 16, App Router, TypeScript) — "liquid glass" dashboard

```bash
cp .env.example .env.local        # API_BASE_URL=http://127.0.0.1:8000
npm install
npm run dev                       # http://localhost:3000   (start the backend first)
npm run typecheck && npm run build
```

One page, five components, no UI/animation library (CSS + a little SVG/canvas physics):

| Component | What it is |
|---|---|
| `LiquidBackground` | obsidian canvas with a faint aura of liquid globs that drift and lean toward the pointer |
| `Glass` + `app/liquid.css` | the glass substrate: blur(24px) saturate(180%), prism edge, pointer-tracked specular light, click ripples, spring (`linear()`) easing |
| `KpiPods` + `MercurySparkline` | three pods with liquid-metal sparklines; hover swells the pod and drops a detail panel |
| `Leaderboard` + `TrajectoryChart` | ≥20-review providers as glass tabs; risk-spike gradients; a selected row melts open into its yearly trajectory |
| `AspectBlob` | the 8 aspects as a spring-physics liquid blob; hover sends a pressure wave and opens the keyword-cluster bubble; click filters the leaderboard |
| `EvidenceFeed` | review with jelly-boxed risky sentences ⟷ terminal view with the evidence sentence in a viscous column; "View Model Weights" drops the token-weight pills |
| `TriageDock` | bubble that surfaces when a risk flag is selected: draft email / audit checklist (drafts only, nothing is sent) |
| `DisclaimerEtch` | the allegation disclaimer, etched into the bottom edge with parallax |

* Server components load data via `lib/api.ts` (`API_BASE_URL`); the browser calls same-origin `/api/analyze`, which `next.config.mjs` proxies to the backend.
* Types mirror [`../docs/DATA_CONTRACT.md`](../docs/DATA_CONTRACT.md) in `lib/types.ts`. Design tokens (tier colours, easings) live at the top of `app/liquid.css`.
* Motion respects `prefers-reduced-motion`. Tier colours are reserved for risk and always paired with a text label; purple is the single accent.
* Open tasks: [`../docs/TEAM_GUIDE.md`](../docs/TEAM_GUIDE.md). Deployment: [`../docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md).
