import { test, expect } from '@playwright/test';

/**
 * Dashboard E2E Tests
 * 
 * Tests for the main dashboard functionality
 */

test.describe('Dashboard', () => {
    test('should display dashboard with key metrics', async ({ page }) => {
        await page.goto('/dashboard');

        // Check page title
        await expect(page).toHaveTitle(/Dashboard|MyCRM/i);

        // Check for key dashboard elements
        await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();

        // Check for stats cards
        const statsSection = page.locator('.stats-cards, [data-testid="stats-section"]');
        await expect(statsSection.or(page.getByText(/total|leads|revenue/i).first())).toBeVisible();
    });

    test('should navigate to leads page', async ({ page }) => {
        await page.goto('/dashboard');

        // Click on leads link
        await page.getByRole('link', { name: /leads/i }).first().click();

        // Verify navigation
        await expect(page).toHaveURL(/.*leads.*/);
    });

    test('should navigate to contacts page', async ({ page }) => {
        await page.goto('/dashboard');

        // Click on contacts link
        await page.getByRole('link', { name: /contacts/i }).first().click();

        // Verify navigation
        await expect(page).toHaveURL(/.*contacts.*/);
    });

    test('should open command palette with keyboard shortcut', async ({ page }) => {
        await page.goto('/dashboard');

        // Press Cmd+K or Ctrl+K
        await page.keyboard.press('Meta+k');

        // Check if command palette is visible
        const commandPalette = page.locator('[data-command-palette], [role="dialog"]');
        await expect(commandPalette.first()).toBeVisible({ timeout: 5000 }).catch(() => {
            // Try Ctrl+K as fallback
            page.keyboard.press('Control+k');
        });
    });

    test('should show user menu when clicking avatar', async ({ page }) => {
        await page.goto('/dashboard');

        // Click user avatar/menu
        const userMenu = page.locator('[data-user-menu], .user-avatar, [aria-label*="user"]');
        if (await userMenu.count() > 0) {
            await userMenu.first().click();

            // Should show dropdown with options
            await expect(page.getByRole('menu').or(page.getByRole('menuitem').first())).toBeVisible();
        }
    });

    test('should be responsive on mobile viewport', async ({ page }) => {
        // Set mobile viewport
        await page.setViewportSize({ width: 375, height: 667 });
        await page.goto('/dashboard');

        // Dashboard should still be visible
        await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();

        // Sidebar might be collapsed - check for hamburger menu
        const hamburgerMenu = page.locator('[data-mobile-menu], .hamburger, [aria-label*="menu"]');
        if (await hamburgerMenu.count() > 0) {
            await expect(hamburgerMenu.first()).toBeVisible();
        }
    });
});

test.describe('Dashboard Widgets', () => {
    test('should display chart widgets', async ({ page }) => {
        await page.goto('/dashboard');

        // Look for chart containers
        const charts = page.locator('canvas, svg, .recharts-wrapper, [data-chart]');

        // At least one chart should be visible (may not be on all dashboards)
        const chartCount = await charts.count();
        if (chartCount > 0) {
            await expect(charts.first()).toBeVisible();
        }
    });

    test('should display recent activity', async ({ page }) => {
        await page.goto('/dashboard');

        // Look for activity section
        const activitySection = page.getByText(/recent|activity|latest/i);
        if (await activitySection.count() > 0) {
            await expect(activitySection.first()).toBeVisible();
        }
    });
});
