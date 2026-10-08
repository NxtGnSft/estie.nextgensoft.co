import { test, expect } from '@playwright/test';

const COUNTS: Record<string, number> = {
  'dining-chairs': 90, 'dining-tables': 30, 'bar-stools': 45, 'lounge-chairs': 36, 'sofas': 18,
  'benches': 12, 'coffee-tables': 18, 'nightstands': 18, 'sideboards-tv-cabinets': 24,
};

test('home renders hero, tiles and contact', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('h1')).toContainText('Teak furniture');
  await expect(page.locator('#categories li')).toHaveCount(9);
  await expect(page.locator('#contact a[href^="https://wa.me/6281391199692"]')).toBeVisible();
});

for (const [slug, n] of Object.entries(COUNTS)) {
  test(`category ${slug} renders ${n} cards`, async ({ page }) => {
    await page.goto(`/catalog/${slug}/`);
    await expect(page.locator('.card')).toHaveCount(n);
    await expect(page.locator('#result-count')).toHaveText(`${n} of ${n}`);
  });
}

test('card opens dialog with WhatsApp link carrying the code', async ({ page }) => {
  await page.goto('/catalog/dining-chairs/');
  await page.locator('#dc-01 .card-open').click();
  const dialog = page.locator('#product-dialog');
  await expect(dialog).toBeVisible();
  await expect(dialog.locator('[data-field="code"]')).toHaveText('DC-01');
  await expect(dialog.locator('[data-field="wa"]')).toHaveAttribute('href', /wa\.me\/6281391199692\?text=.*DC-01/);
  await page.keyboard.press('Escape');
  await expect(dialog).toBeHidden();
});

test('hash opens the matching product on load', async ({ page }) => {
  await page.goto('/catalog/bar-stools/#bt-05');
  await expect(page.locator('#product-dialog [data-field="code"]')).toHaveText('BT-05');
});

test('material filter narrows the grid', async ({ page }) => {
  await page.goto('/catalog/dining-chairs/');
  const first = await page.locator('#material-filter option').nth(1).getAttribute('value');
  await page.selectOption('#material-filter', first!);
  const shown = await page.locator('.card:visible').count();
  expect(shown).toBeGreaterThan(0);
  expect(shown).toBeLessThan(90);
  await expect(page.locator('#result-count')).toHaveText(`${shown} of 90`);
});

test('catalog root redirects to dining chairs', async ({ page }) => {
  await page.goto('/catalog/');
  await expect(page).toHaveURL(/\/catalog\/dining-chairs\/?$/);
});
