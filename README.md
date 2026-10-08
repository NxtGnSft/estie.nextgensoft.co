# estie.nextgensoft.co

Catalog website for PT Estie Kusuma Indonesia (teak furniture, Semarang). Live at https://estie.nextgensoft.co.

- `npm run dev` — local dev server
- `npm run build` — static build to `dist/`
- `npm run test:e2e` — Playwright smoke tests
- `/usr/bin/python3 scripts/extract.py` — regenerate `src/data/products.json` and crops from `public/ESTIE-KUSUMA-catalog.pdf` (one-time; hand fixes in the JSON would be overwritten, so diff before committing)

Deploys to GitHub Pages on push to `main`. DNS: CNAME `estie.nextgensoft.co` → `nxtgnsft.github.io` (Hetzner, set via `infra/scripts/dns.sh`).
