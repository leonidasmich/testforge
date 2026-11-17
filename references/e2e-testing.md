# End-to-End & Playwright Best Practices

## 1. User-Facing Locators
Avoid brittle CSS selectors or deep XPath expressions that break on layout styling changes. Use user-facing role locators:
```javascript
// GOOD
await page.getByRole('button', { name: 'Submit Order' }).click();
await expect(page.getByText('Order Confirmation')).toBeVisible();

// BAD
await page.locator('div.main > form > button.btn-primary-v2').click();


2. Web-First Assertions & Auto-Waiting

Use Playwright's web-first assertions that automatically wait for conditions to be met before failing:

// GOOD: Automatically waits for element to appear
await expect(page.getByTestId('status-banner')).toHaveText('Success');

// BAD: Flaky manual boolean check
expect(await page.getByTestId('status-banner').isVisible()).toBe(true);


3. Soft Assertions

Use soft assertions when inspecting multiple independent page properties in a single scenario without aborting the test early:

await expect.soft(page.getByTestId('user-name')).toHaveText('Alice');
await expect.soft(page.getByTestId('user-role')).toHaveText('Admin');

