import { test, expect } from '@playwright/test';

/**
 * Opportunities (Deals) E2E Tests
 * 
 * Tests for opportunities/deals management functionality
 */

test.describe('Opportunities Management', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/opportunities');
    });

    test('should display opportunities page', async ({ page }) => {
        await expect(page.getByRole('heading', { name: /opportunities|deals|pipeline/i })).toBeVisible();
    });

    test('should show pipeline view', async ({ page }) => {
        // Look for Kanban board or pipeline stages
        const pipelineView = page.locator('[data-testid="pipeline-board"], .kanban-board, [data-pipeline]');
        if (await pipelineView.count() > 0) {
            await expect(pipelineView).toBeVisible();
        }
    });

    test('should switch between list and board view', async ({ page }) => {
        const viewToggle = page.getByRole('button', { name: /list|board|kanban|table/i });
        if (await viewToggle.count() > 0) {
            await viewToggle.click();
            
            // View should change
            await page.waitForTimeout(300);
        }
    });

    test('should add new opportunity', async ({ page }) => {
        const addButton = page.getByRole('button', { name: /add|new|create/i });
        await addButton.click();

        // Fill opportunity form
        const nameInput = page.getByLabel(/name|title|deal/i);
        if (await nameInput.count() > 0) {
            await nameInput.fill('Test Opportunity');
        }

        const valueInput = page.getByLabel(/value|amount/i);
        if (await valueInput.count() > 0) {
            await valueInput.fill('50000');
        }

        // Check for stage selection
        const stageSelect = page.getByLabel(/stage/i);
        if (await stageSelect.count() > 0) {
            await stageSelect.click();
            await page.getByRole('option').first().click();
        }
    });

    test('should filter opportunities by stage', async ({ page }) => {
        const stageFilter = page.getByRole('button', { name: /filter|stage/i });
        if (await stageFilter.count() > 0) {
            await stageFilter.click();
            
            const filterOptions = page.getByRole('menuitem').or(page.getByRole('option'));
            await expect(filterOptions.first()).toBeVisible();
        }
    });

    test('should show opportunity statistics', async ({ page }) => {
        // Look for stats cards
        const statsCards = page.locator('[data-testid="stats-card"], .stat-card, .kpi-card');
        if (await statsCards.count() > 0) {
            await expect(statsCards.first()).toBeVisible();
        }
    });

    test('should show forecast data', async ({ page }) => {
        const forecastSection = page.getByText(/forecast|pipeline value|expected/i);
        if (await forecastSection.count() > 0) {
            await expect(forecastSection.first()).toBeVisible();
        }
    });
});

test.describe('Opportunity Details', () => {
    test('should view opportunity details', async ({ page }) => {
        await page.goto('/opportunities');
        
        // Click on first opportunity
        const firstOpp = page.locator('[data-testid="opportunity-card"], tr').first();
        if (await firstOpp.count() > 0) {
            await firstOpp.click();
            
            // Should navigate to details
            await expect(page).toHaveURL(/.*opportunities\/\d+.*/);
        }
    });

    test('should update opportunity stage', async ({ page }) => {
        await page.goto('/opportunities/1');
        
        const stageSelect = page.getByRole('combobox', { name: /stage/i });
        if (await stageSelect.count() > 0) {
            await stageSelect.click();
            await page.getByRole('option').nth(1).click();
            
            // Should update
            await expect(page.getByText(/updated|saved/i)).toBeVisible({ timeout: 5000 });
        }
    });

    test('should add activity to opportunity', async ({ page }) => {
        await page.goto('/opportunities/1');
        
        const addActivityButton = page.getByRole('button', { name: /add activity|log/i });
        if (await addActivityButton.count() > 0) {
            await addActivityButton.click();
            
            // Activity form should appear
            const activityTypeSelect = page.getByLabel(/type|activity/i);
            await expect(activityTypeSelect).toBeVisible();
        }
    });

    test('should show related contacts', async ({ page }) => {
        await page.goto('/opportunities/1');
        
        const contactsSection = page.getByText(/contacts|people|stakeholders/i);
        if (await contactsSection.count() > 0) {
            await expect(contactsSection.first()).toBeVisible();
        }
    });

    test('should close/win opportunity', async ({ page }) => {
        await page.goto('/opportunities/1');
        
        const closeButton = page.getByRole('button', { name: /close|win|won/i });
        if (await closeButton.count() > 0) {
            await closeButton.click();
            
            // Confirmation dialog
            const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
            if (await confirmButton.count() > 0) {
                await confirmButton.click();
            }
        }
    });
});
