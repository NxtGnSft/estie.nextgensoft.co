// astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://estie.nextgensoft.co',
  integrations: [sitemap()],
  redirects: {
    '/catalog': '/catalog/dining-chairs',
  },
});
