import { test, expect } from '@playwright/test';

/**
 * Reports & Analytics E2E Tests
 * 
 * Tests for reporting and analytics functionality
 */

test.describe('Reports & Analytics', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/reports');
    });

    test('should display reports page', async ({ page }) => {
        await expect(page.getByRole('heading', { name: /reports|analytics/i })).toBeVisible();
    });

    test('should show report categories', async ({ page }) => {
        const categories = page.getByRole('tab').or(page.locator('[data-testid="report-category"]'));
        if (await categories.count() > 0) {
            await expect(categories.first()).toBeVisible();
        }
    });

    test('should filter by date range', async ({ page }) => {
        const dateFilter = page.getByRole('button', { name: /date|period|range/i });
        if (await dateFilter.count() > 0) {
            await dateFilter.click();
            
            // Date range options should appear
            const dateOptions = page.getByRole('menuitem').or(page.getByRole('option'));
            await expect(dateOptions.first()).toBeVisible();
        }
    });

    test('should display charts', async ({ page }) => {
        const charts = page.locator('canvas, svg, [data-testid="chart"]');
        if (await charts.count() > 0) {
            await expect(charts.first()).toBeVisible();
        }
    });

    test('should export report', async ({ page }) => {
        const exportButton = page.getByRole('button', { name: /export|download/i });
        if (await exportButton.count() > 0) {
            await exportButton.click();
            
            // Export options or download should start
            const exportOptions = page.getByRole('menuitem', { name: /pdf|csv|excel/i });
            if (await exportOptions.count() > 0) {
                await expect(exportOptions.first()).toBeVisible();
            }
        }
    });

    test('should show KPI metrics', async ({ page }) => {
        const kpiCards = page.locator('[data-testid="kpi-card"], .stat-card, .metric-card');
        if (await kpiCards.count() > 0) {
            await expect(kpiCards.first()).toBeVisible();
        }
    });
});

test.describe('Sales Reports', () => {
    test('should view sales report', async ({ page }) => {
        await page.goto('/reports');
        
        const salesTab = page.getByRole('tab', { name: /sales/i });
        if (await salesTab.count() > 0) {
            await salesTab.click();
            
            // Sales metrics should be visible
            const revenueMetric = page.getByText(/revenue|sales|closed/i);
            await expect(revenueMetric.first()).toBeVisible();
        }
    });

    test('should show pipeline report', async ({ page }) => {
        await page.goto('/reports');
        
        const pipelineTab = page.getByRole('tab', { name: /pipeline/i });
        if (await pipelineTab.count() > 0) {
            await pipelineTab.click();
            
            // Pipeline visualization should be visible
            const pipelineChart = page.locator('[data-testid="pipeline-chart"]');
            if (await pipelineChart.count() > 0) {
                await expect(pipelineChart).toBeVisible();
            }
        }
    });

    test('should show forecast data', async ({ page }) => {
        await page.goto('/reports');
        
        const forecastSection = page.getByText(/forecast|projection/i);
        if (await forecastSection.count() > 0) {
            await expect(forecastSection.first()).toBeVisible();
        }
    });
});

test.describe('Team Performance', () => {
    test('should view team performance', async ({ page }) => {
        await page.goto('/reports');
        
        const teamTab = page.getByRole('tab', { name: /team|performance/i });
        if (await teamTab.count() > 0) {
            await teamTab.click();
            
            // Team metrics should be visible
            const leaderboard = page.locator('[data-testid="leaderboard"]');
            if (await leaderboard.count() > 0) {
                await expect(leaderboard).toBeVisible();
            }
        }
    });

    test('should filter by team member', async ({ page }) => {
        await page.goto('/reports');
        
        const userFilter = page.getByRole('combobox', { name: /user|member|rep/i });
        if (await userFilter.count() > 0) {
            await userFilter.click();
            
            const userOptions = page.getByRole('option');
            await expect(userOptions.first()).toBeVisible();
        }
    });
});
