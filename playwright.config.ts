import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: 'tests/e2e',
  use: { baseURL: 'http://localhost:4321' },
  webServer: { command: 'npm run build && npx astro preview --port 4321', url: 'http://localhost:4321', reuseExistingServer: true, timeout: 180_000 },
  projects: [{ name: 'mobile', use: { viewport: { width: 375, height: 800 } } }],
});
