## What & why
<!-- one or two sentences; link the issue -->

## Track
- [ ] backend  - [ ] frontend  - [ ] notebook / data  - [ ] docs / infra

## Checks
- [ ] `make test` passes locally (backend `pytest`, frontend `typecheck`)
- [ ] Works on the sample data; UI changes include a screenshot and the **Vercel preview URL**
- [ ] If a JSON field changed: notebook export + backend + `frontend/lib/types.ts` + `docs/DATA_CONTRACT.md` all updated
- [ ] No Yelp data, `data/processed/*`, secrets or `.env*` files committed
- [ ] The "complaint signals, not findings" disclaimer is still visible
