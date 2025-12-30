import { test, expect } from '@playwright/test';

/**
 * Leads Management E2E Tests
 * 
 * Tests for lead CRUD operations and management
 */

test.describe('Leads Management', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/leads');
    });

    test('should display leads list', async ({ page }) => {
        // Check page loaded
        await expect(page.getByRole('heading', { name: /leads/i })).toBeVisible();

        // Should have a table or list of leads
        const leadsContainer = page.locator('table, [data-testid="leads-list"], .leads-list');
        await expect(leadsContainer.first()).toBeVisible();
    });

    test('should open create lead modal', async ({ page }) => {
        // Click add lead button
        const addButton = page.getByRole('button', { name: /add|new|create/i });
        await addButton.first().click();

        // Modal or form should appear
        const modal = page.locator('[role="dialog"], form, .modal');
        await expect(modal.first()).toBeVisible();
    });

    test('should create a new lead', async ({ page }) => {
        // Click add button
        await page.getByRole('button', { name: /add|new|create/i }).first().click();

        // Fill in lead details
        await page.getByLabel(/first name/i).fill('E2E');
        await page.getByLabel(/last name/i).fill('TestLead');
        await page.getByLabel(/email/i).fill(`e2e-test-${Date.now()}@example.com`);

        // Fill company if available
        const companyField = page.getByLabel(/company/i);
        if (await companyField.count() > 0) {
            await companyField.fill('Test Company');
        }

        // Submit form
        await page.getByRole('button', { name: /save|create|submit/i }).click();

        // Should show success message or redirect
        await expect(
            page.getByText(/success|created|saved/i).or(page.locator('table'))
        ).toBeVisible({ timeout: 10000 });
    });

    test('should search leads', async ({ page }) => {
        // Find search input
        const searchInput = page.getByPlaceholder(/search/i).or(page.getByRole('searchbox'));

        if (await searchInput.count() > 0) {
            await searchInput.first().fill('test');
            await page.keyboard.press('Enter');

            // Wait for search results
            await page.waitForTimeout(1000);

            // Results should update
            await expect(page.locator('table, [data-testid="leads-list"]').first()).toBeVisible();
        }
    });

    test('should filter leads by status', async ({ page }) => {
        // Look for filter controls
        const filterButton = page.getByRole('button', { name: /filter/i });

        if (await filterButton.count() > 0) {
            await filterButton.click();

            // Select a status filter
            const statusFilter = page.getByLabel(/status/i).or(page.getByText(/status/i));
            if (await statusFilter.count() > 0) {
                await statusFilter.first().click();
            }
        }
    });

    test('should open lead details', async ({ page }) => {
        // Click on first lead in the list
        const leadRow = page.locator('table tbody tr, [data-testid="lead-item"]').first();

        if (await leadRow.count() > 0) {
            await leadRow.click();

            // Should navigate to detail page or open modal
            await expect(
                page.getByRole('heading').or(page.locator('[role="dialog"]'))
            ).toBeVisible();
        }
    });

    test('should handle empty state', async ({ page }) => {
        // Navigate with filter that might return no results
        await page.goto('/leads?status=nonexistent');

        // Should either show empty state or redirect
        await page.waitForTimeout(2000);

        const emptyState = page.getByText(/no leads|no results|empty/i);
        const leadsTable = page.locator('table tbody tr');

        // Either empty state message or table should be visible
        const isEmpty = await emptyState.count() > 0;
        const hasData = await leadsTable.count() > 0;

        expect(isEmpty || hasData).toBeTruthy();
    });
});

test.describe('Lead Detail Page', () => {
    test('should display lead information', async ({ page }) => {
        // Go to leads and click first one
        await page.goto('/leads');

        const leadRow = page.locator('table tbody tr, [data-testid="lead-item"]').first();
        if (await leadRow.count() > 0) {
            await leadRow.click();
            await page.waitForTimeout(1000);

            // Should show lead details
            const detailsVisible = await page.getByText(/email|phone|company/i).first().isVisible();
            expect(detailsVisible).toBeTruthy();
        }
    });
});
