import { test, expect, Page } from '@playwright/test';

/** Dismiss any full-page modal dialog Google may show (GDPR consent, Chrome promo, etc.) */
async function dismissDialog(page: Page) {
  // The GDPR consent dialog renders as aria-modal and blocks all background elements.
  // Clicking the first button ("Reject all" in most EU locales) clears the modal.
  const dialogFirstBtn = page.locator('[role="dialog"] button, dialog button').first();
  if (await dialogFirstBtn.isVisible({ timeout: 4000 }).catch(() => false)) {
    await dialogFirstBtn.click();
    // Wait for the dialog to disappear before continuing
    await dialogFirstBtn.waitFor({ state: 'hidden', timeout: 4000 }).catch(() => {});
  }
}

test.describe('Google Homepage', () => {
  test.beforeEach(async ({ page }) => {
    // ?hl=en forces an English interface even when Google detects a non-English region
    await page.goto('https://www.google.com/?hl=en');
    await dismissDialog(page);
  });

  test('TC-01: should display the correct page title', async ({ page }) => {
    await expect(page).toHaveTitle('Google');
  });

  test('TC-02: should display the Google logo', async ({ page }) => {
    const logo = page.getByRole('img', { name: 'Google' });
    await expect(logo).toBeVisible();
  });

  test('TC-03: should display search input and allow typing a query', async ({ page }) => {
    // name="q" is stable and locale-independent across all Google UI versions
    const searchBox = page.locator('textarea[name="q"], input[name="q"]').first();
    await expect(searchBox).toBeVisible();
    await searchBox.fill('Playwright testing');
    await expect(searchBox).toHaveValue('Playwright testing');
  });

  test('TC-04: should navigate to search results when submitting a query', async ({ page }) => {
    const searchBox = page.locator('textarea[name="q"], input[name="q"]').first();
    await searchBox.fill('Playwright testing');
    await searchBox.press('Enter');
    // Google search results always redirect to /search?q=...
    await expect(page).toHaveURL(/\/search\?q=Playwright/, { timeout: 10000 });
    // The results container is always present on a results page
    await expect(page.locator('#search')).toBeVisible();
  });

  test('TC-05: should display header navigation links', async ({ page }) => {
    // Gmail link text is the same in all locales; use href as a stable fallback
    await expect(page.locator('a[href*="mail.google.com"]').first()).toBeVisible();
    // Images link: look by the href pattern rather than the translated text
    await expect(page.locator('a[href*="/imghp"]').first()).toBeVisible();
    // Sign-in link: href always points to accounts.google.com/ServiceLogin
    await expect(page.locator('a[href*="ServiceLogin"]').first()).toBeVisible();
  });
});
