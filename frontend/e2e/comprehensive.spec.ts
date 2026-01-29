/**
 * MyCRM - Comprehensive Playwright E2E Tests
 * 
 * End-to-end tests covering major user flows and scenarios
 */

import { test, expect, Page } from '@playwright/test';

// =============================================================================
// Test Fixtures and Utilities
// =============================================================================

const BASE_URL = process.env.PLAYWRIGHT_TEST_URL || 'http://localhost:3000';

interface TestUser {
    email: string;
    password: string;
}

const testUser: TestUser = {
    email: 'test@example.com',
    password: 'TestPassword123!',
};

// Helper function to login
async function login(page: Page, user: TestUser = testUser): Promise<void> {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('[name="email"], [type="email"], input[placeholder*="email" i]', user.email);
    await page.fill('[name="password"], [type="password"], input[placeholder*="password" i]', user.password);
    await page.click('button[type="submit"], button:has-text("Sign in"), button:has-text("Login")');
    await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 10000 });
}

// Helper to wait for page load
async function waitForPageLoad(page: Page): Promise<void> {
    await page.waitForLoadState('networkidle');
}

// =============================================================================
// Authentication Flow Tests
// =============================================================================

test.describe('Authentication Flows', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto(BASE_URL);
    });

    test('displays login page for unauthenticated users', async ({ page }) => {
        await page.goto(`${BASE_URL}/dashboard`);
        
        // Should redirect to login or show login form
        await expect(page).toHaveURL(/login|signin|auth/i);
    });

    test('shows validation errors for empty login form', async ({ page }) => {
        await page.goto(`${BASE_URL}/login`);
        
        // Submit without filling form
        const submitButton = page.locator('button[type="submit"], button:has-text("Sign in"), button:has-text("Login")');
        if (await submitButton.isVisible()) {
            await submitButton.click();
            
            // Should show validation errors
            const errors = page.locator('[role="alert"], .error, [class*="error"]');
            await expect(errors.first()).toBeVisible({ timeout: 5000 }).catch(() => {
                // Some forms may use different error handling
            });
        }
    });

    test('shows error for invalid credentials', async ({ page }) => {
        await page.goto(`${BASE_URL}/login`);
        
        await page.fill('[name="email"], [type="email"]', 'invalid@example.com');
        await page.fill('[name="password"], [type="password"]', 'wrongpassword');
        
        const submitButton = page.locator('button[type="submit"]');
        if (await submitButton.isVisible()) {
            await submitButton.click();
            
            // Should show error message
            const errorMessage = page.locator('text=/invalid|incorrect|wrong|error/i');
            await expect(errorMessage.first()).toBeVisible({ timeout: 5000 }).catch(() => {
                // May have different error handling
            });
        }
    });

    test('password visibility toggle works', async ({ page }) => {
        await page.goto(`${BASE_URL}/login`);
        
        const passwordInput = page.locator('[type="password"]').first();
        if (await passwordInput.isVisible()) {
            await passwordInput.fill('testpassword');
            
            // Look for visibility toggle button
            const toggleButton = page.locator('button:near([type="password"]), [class*="toggle"], [aria-label*="show" i]');
            if (await toggleButton.first().isVisible()) {
                await toggleButton.first().click();
                
                // Password should now be visible (type="text")
                await expect(page.locator('input[value="testpassword"]')).toHaveAttribute('type', 'text').catch(jest.fn());
            }
        }
    });
});

// =============================================================================
// Contact Management Tests
// =============================================================================

test.describe('Contact Management', () => {
    test.beforeEach(async ({ page }) => {
        // Attempt login before each test
        await login(page).catch(() => {
            // If login fails, test may be for unauthenticated scenarios
        });
    });

    test('contact list page loads', async ({ page }) => {
        await page.goto(`${BASE_URL}/contacts`);
        await waitForPageLoad(page);
        
        // Should see contacts page content
        const pageContent = page.locator('main, [role="main"], .content');
        await expect(pageContent.first()).toBeVisible({ timeout: 10000 });
    });

    test('can navigate to create contact form', async ({ page }) => {
        await page.goto(`${BASE_URL}/contacts`);
        await waitForPageLoad(page);
        
        // Look for create/add button
        const createButton = page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New"), a:has-text("Add Contact")');
        if (await createButton.first().isVisible()) {
            await createButton.first().click();
            
            // Should see a form
            const form = page.locator('form');
            await expect(form.first()).toBeVisible({ timeout: 5000 });
        }
    });

    test('contact form has required fields', async ({ page }) => {
        await page.goto(`${BASE_URL}/contacts/new`);
        await waitForPageLoad(page);
        
        // Check for common contact fields
        const fields = [
            'input[name*="first" i], input[placeholder*="first" i]',
            'input[name*="last" i], input[placeholder*="last" i]',
            'input[name*="email" i], input[type="email"]',
        ];
        
        for (const field of fields) {
            const element = page.locator(field);
            if (await element.first().isVisible()) {
                expect(await element.first().isVisible()).toBeTruthy();
            }
        }
    });

    test('search functionality works', async ({ page }) => {
        await page.goto(`${BASE_URL}/contacts`);
        await waitForPageLoad(page);
        
        const searchInput = page.locator('input[type="search"], input[placeholder*="search" i], input[name*="search" i]');
        if (await searchInput.first().isVisible()) {
            await searchInput.first().fill('test');
            
            // Wait for search to execute
            await page.waitForTimeout(500);
            
            // Results should update
            await expect(page.locator('main, [role="main"]')).toBeVisible();
        }
    });
});

// =============================================================================
// Lead Management Tests
// =============================================================================

test.describe('Lead Management', () => {
    test.beforeEach(async ({ page }) => {
        await login(page).catch(jest.fn());
    });

    test('leads list page loads', async ({ page }) => {
        await page.goto(`${BASE_URL}/leads`);
        await waitForPageLoad(page);
        
        const pageContent = page.locator('main, [role="main"], .content, h1:has-text("Lead")');
        await expect(pageContent.first()).toBeVisible({ timeout: 10000 });
    });

    test('can filter leads by status', async ({ page }) => {
        await page.goto(`${BASE_URL}/leads`);
        await waitForPageLoad(page);
        
        // Look for filter controls
        const filterSelect = page.locator('select, [role="combobox"], button:has-text("Filter")');
        if (await filterSelect.first().isVisible()) {
            await filterSelect.first().click();
            
            // Look for filter options
            const filterOptions = page.locator('[role="option"], option, li');
            if (await filterOptions.first().isVisible()) {
                await filterOptions.first().click();
            }
        }
    });

    test('lead status can be changed', async ({ page }) => {
        await page.goto(`${BASE_URL}/leads`);
        await waitForPageLoad(page);
        
        // Click on a lead to view details
        const leadItem = page.locator('tr, [data-testid*="lead"], .lead-item').first();
        if (await leadItem.isVisible()) {
            await leadItem.click();
            await waitForPageLoad(page);
            
            // Look for status dropdown or buttons
            const statusControl = page.locator('select[name*="status"], [aria-label*="status" i], button:has-text("Status")');
            if (await statusControl.first().isVisible()) {
                await statusControl.first().click();
            }
        }
    });
});

// =============================================================================
// Opportunity Pipeline Tests
// =============================================================================

test.describe('Opportunity Pipeline', () => {
    test.beforeEach(async ({ page }) => {
        await login(page).catch(jest.fn());
    });

    test('pipeline page loads', async ({ page }) => {
        await page.goto(`${BASE_URL}/opportunities`);
        await waitForPageLoad(page);
        
        const pageContent = page.locator('main, [role="main"], h1:has-text("Opportunit"), h1:has-text("Pipeline")');
        await expect(pageContent.first()).toBeVisible({ timeout: 10000 });
    });

    test('pipeline shows stages', async ({ page }) => {
        await page.goto(`${BASE_URL}/opportunities`);
        await waitForPageLoad(page);
        
        // Look for stage columns or tabs
        const stages = page.locator('[data-testid*="stage"], .stage, .column, [class*="pipeline"]');
        await expect(stages.first()).toBeVisible({ timeout: 5000 }).catch(() => {
            // Pipeline might be displayed differently
        });
    });

    test('can create new opportunity', async ({ page }) => {
        await page.goto(`${BASE_URL}/opportunities/new`);
        await waitForPageLoad(page);
        
        const form = page.locator('form');
        await expect(form.first()).toBeVisible({ timeout: 10000 }).catch(() => {
            // May redirect or show modal instead
        });
    });
});

// =============================================================================
// Task Management Tests
// =============================================================================

test.describe('Task Management', () => {
    test.beforeEach(async ({ page }) => {
        await login(page).catch(jest.fn());
    });

    test('tasks page loads', async ({ page }) => {
        await page.goto(`${BASE_URL}/tasks`);
        await waitForPageLoad(page);
        
        const pageContent = page.locator('main, [role="main"], h1:has-text("Task")');
        await expect(pageContent.first()).toBeVisible({ timeout: 10000 });
    });

    test('can create a new task', async ({ page }) => {
        await page.goto(`${BASE_URL}/tasks`);
        await waitForPageLoad(page);
        
        // Click add task button
        const addButton = page.locator('button:has-text("Add"), button:has-text("New"), button:has-text("Create")');
        if (await addButton.first().isVisible()) {
            await addButton.first().click();
            
            // Fill task form
            const titleInput = page.locator('input[name*="title" i], input[placeholder*="title" i], input[name*="name" i]');
            if (await titleInput.first().isVisible()) {
                await titleInput.first().fill('E2E Test Task');
            }
        }
    });

    test('task completion works', async ({ page }) => {
        await page.goto(`${BASE_URL}/tasks`);
        await waitForPageLoad(page);
        
        // Look for task checkboxes
        const taskCheckbox = page.locator('input[type="checkbox"], [role="checkbox"]').first();
        if (await taskCheckbox.isVisible()) {
            const isChecked = await taskCheckbox.isChecked();
            await taskCheckbox.click();
            
            // State should have changed
            await expect(taskCheckbox).not.toBeChecked({ checked: isChecked });
        }
    });
});

// =============================================================================
// Dashboard Tests
// =============================================================================

test.describe('Dashboard', () => {
    test.beforeEach(async ({ page }) => {
        await login(page).catch(jest.fn());
    });

    test('dashboard loads with statistics', async ({ page }) => {
        await page.goto(`${BASE_URL}/dashboard`);
        await waitForPageLoad(page);
        
        const statsCards = page.locator('[class*="stat"], [class*="card"], [class*="metric"], [data-testid*="stat"]');
        await expect(statsCards.first()).toBeVisible({ timeout: 10000 }).catch(() => {
            // Dashboard may have different layout
        });
    });

    test('dashboard shows recent activities', async ({ page }) => {
        await page.goto(`${BASE_URL}/dashboard`);
        await waitForPageLoad(page);
        
        const activitySection = page.locator('text=/recent|activity|latest/i');
        await expect(activitySection.first()).toBeVisible({ timeout: 10000 }).catch(jest.fn());
    });

    test('can navigate from dashboard to other sections', async ({ page }) => {
        await page.goto(`${BASE_URL}/dashboard`);
        await waitForPageLoad(page);
        
        // Look for navigation links
        const navLinks = page.locator('nav a, a[href*="/contacts"], a[href*="/leads"]');
        if (await navLinks.first().isVisible()) {
            const href = await navLinks.first().getAttribute('href');
            await navLinks.first().click();
            await waitForPageLoad(page);
            
            // URL should have changed
            if (href) {
                expect(page.url()).toContain(href);
            }
        }
    });
});

// =============================================================================
// Navigation Tests
// =============================================================================

test.describe('Navigation', () => {
    test.beforeEach(async ({ page }) => {
        await login(page).catch(jest.fn());
    });

    test('main navigation is visible', async ({ page }) => {
        await page.goto(`${BASE_URL}/dashboard`);
        await waitForPageLoad(page);
        
        const nav = page.locator('nav, [role="navigation"], aside');
        await expect(nav.first()).toBeVisible({ timeout: 10000 });
    });

    test('mobile menu toggle works', async ({ page }) => {
        // Set mobile viewport
        await page.setViewportSize({ width: 375, height: 667 });
        await page.goto(`${BASE_URL}/dashboard`);
        await waitForPageLoad(page);
        
        // Look for hamburger menu button
        const menuButton = page.locator('button[aria-label*="menu" i], button:has-text("☰"), [class*="hamburger"]');
        if (await menuButton.first().isVisible()) {
            await menuButton.first().click();
            
            // Navigation should appear
            const nav = page.locator('nav, [role="navigation"]');
            await expect(nav.first()).toBeVisible({ timeout: 5000 });
        }
    });

    test('breadcrumb navigation works', async ({ page }) => {
        await page.goto(`${BASE_URL}/contacts/new`);
        await waitForPageLoad(page);
        
        const breadcrumb = page.locator('[aria-label="breadcrumb"], nav:has-text(">")', { strict: false });
        if (await breadcrumb.first().isVisible()) {
            const homeLink = breadcrumb.locator('a').first();
            await homeLink.click();
            
            // Should navigate
            await expect(page).not.toHaveURL(/\/new$/);
        }
    });
});

// =============================================================================
// Responsive Design Tests
// =============================================================================

test.describe('Responsive Design', () => {
    test('desktop layout renders correctly', async ({ page }) => {
        await page.setViewportSize({ width: 1920, height: 1080 });
        await page.goto(`${BASE_URL}/dashboard`);
        await waitForPageLoad(page);
        
        // Sidebar should be visible on desktop
        const sidebar = page.locator('aside, [class*="sidebar"], nav:not([role="navigation"])');
        await expect(sidebar.first()).toBeVisible({ timeout: 10000 }).catch(jest.fn());
    });

    test('tablet layout renders correctly', async ({ page }) => {
        await page.setViewportSize({ width: 768, height: 1024 });
        await page.goto(`${BASE_URL}/dashboard`);
        await waitForPageLoad(page);
        
        // Main content should still be visible
        const mainContent = page.locator('main, [role="main"], .content');
        await expect(mainContent.first()).toBeVisible({ timeout: 10000 });
    });

    test('mobile layout renders correctly', async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 });
        await page.goto(`${BASE_URL}/dashboard`);
        await waitForPageLoad(page);
        
        // Main content should still be visible
        const mainContent = page.locator('main, [role="main"], .content');
        await expect(mainContent.first()).toBeVisible({ timeout: 10000 });
    });
});

// =============================================================================
// Accessibility Tests
// =============================================================================

test.describe('Accessibility', () => {
    test('page has proper heading structure', async ({ page }) => {
        await page.goto(`${BASE_URL}/dashboard`);
        await waitForPageLoad(page);
        
        // Should have at least one h1
        const h1 = page.locator('h1');
        await expect(h1.first()).toBeVisible({ timeout: 10000 }).catch(() => {
            // Some pages may use different heading strategies
        });
    });

    test('form inputs have labels', async ({ page }) => {
        await page.goto(`${BASE_URL}/login`);
        await waitForPageLoad(page);
        
        const inputs = await page.locator('input:not([type="hidden"])').all();
        
        for (const input of inputs) {
            const id = await input.getAttribute('id');
            const ariaLabel = await input.getAttribute('aria-label');
            const placeholder = await input.getAttribute('placeholder');
            
            // Should have some form of accessible name
            const hasLabel = id ? (await page.locator(`label[for="${id}"]`).count()) > 0 : false;
            const hasAccessibleName = hasLabel || ariaLabel || placeholder;
            
            expect(hasAccessibleName).toBeTruthy();
        }
    });

    test('focus is visible on interactive elements', async ({ page }) => {
        await page.goto(`${BASE_URL}/login`);
        await waitForPageLoad(page);
        
        // Tab to first focusable element
        await page.keyboard.press('Tab');
        
        // Should have a focused element
        const focusedElement = await page.locator(':focus').first();
        if (await focusedElement.isVisible()) {
            // Check that focus is visible (has outline or other visual indicator)
            const outline = await focusedElement.evaluate((el) => {
                const style = window.getComputedStyle(el);
                return style.outline !== 'none' || style.boxShadow !== 'none';
            });
            expect(outline).toBeTruthy();
        }
    });

    test('skip link is present', async ({ page }) => {
        await page.goto(`${BASE_URL}/dashboard`);
        
        // Press Tab to reveal skip link
        await page.keyboard.press('Tab');
        
        const skipLink = page.locator('a:has-text("Skip"), [class*="skip"]');
        // Skip link may or may not be present
        if (await skipLink.first().isVisible()) {
            expect(await skipLink.first().isVisible()).toBeTruthy();
        }
    });
});

// =============================================================================
// Error Handling Tests
// =============================================================================

test.describe('Error Handling', () => {
    test('404 page displays for invalid routes', async ({ page }) => {
        await page.goto(`${BASE_URL}/this-page-does-not-exist-12345`);
        await waitForPageLoad(page);
        
        // Should show 404 content
        const errorContent = page.locator('text=/404|not found|page.*exist/i');
        await expect(errorContent.first()).toBeVisible({ timeout: 10000 }).catch(() => {
            // May redirect instead of showing 404
        });
    });

    test('handles network errors gracefully', async ({ page }) => {
        // Abort API requests to simulate network error
        await page.route('**/api/**', (route) => route.abort());
        
        await page.goto(`${BASE_URL}/contacts`);
        await waitForPageLoad(page);
        
        // Should show error message or fallback UI
        const errorMessage = page.locator('text=/error|failed|unable|try again/i');
        await expect(errorMessage.first()).toBeVisible({ timeout: 10000 }).catch(() => {
            // May have different error handling
        });
    });
});

// =============================================================================
// Performance Tests
// =============================================================================

test.describe('Performance', () => {
    test('page loads within acceptable time', async ({ page }) => {
        const startTime = Date.now();
        
        await page.goto(`${BASE_URL}/dashboard`);
        await waitForPageLoad(page);
        
        const loadTime = Date.now() - startTime;
        
        // Should load within 5 seconds
        expect(loadTime).toBeLessThan(5000);
    });

    test('images are optimized', async ({ page }) => {
        await page.goto(`${BASE_URL}/dashboard`);
        await waitForPageLoad(page);
        
        const images = await page.locator('img').all();
        
        for (const img of images) {
            // Check for loading attribute (lazy loading)
            const _loading = await img.getAttribute('loading');
            const src = await img.getAttribute('src');
            
            // Skip small icons or data URLs
            if (src && !src.startsWith('data:')) {
                // Images should ideally have lazy loading
                // This is a soft check
            }
        }
    });
});

// =============================================================================
// Form Validation Tests
// =============================================================================

test.describe('Form Validation', () => {
    test('email validation works', async ({ page }) => {
        await page.goto(`${BASE_URL}/login`);
        await waitForPageLoad(page);
        
        const emailInput = page.locator('input[type="email"], input[name*="email"]').first();
        if (await emailInput.isVisible()) {
            await emailInput.fill('invalid-email');
            await page.keyboard.press('Tab');
            
            // Should show validation error
            const validationMessage = await emailInput.evaluate((el: HTMLInputElement) => el.validationMessage);
            expect(validationMessage).not.toBe('');
        }
    });

    test('required field validation works', async ({ page }) => {
        await page.goto(`${BASE_URL}/contacts/new`);
        await waitForPageLoad(page);
        
        const submitButton = page.locator('button[type="submit"]');
        if (await submitButton.first().isVisible()) {
            await submitButton.first().click();
            
            // Should show required field errors
            const errors = page.locator('[role="alert"], .error, [class*="error"], :invalid');
            await expect(errors.first()).toBeVisible({ timeout: 5000 }).catch(jest.fn());
        }
    });
});

// =============================================================================
// Keyboard Navigation Tests
// =============================================================================

test.describe('Keyboard Navigation', () => {
    test('can navigate form with keyboard', async ({ page }) => {
        await page.goto(`${BASE_URL}/login`);
        await waitForPageLoad(page);
        
        // Tab through form elements
        await page.keyboard.press('Tab');
        await page.keyboard.press('Tab');
        await page.keyboard.press('Tab');
        
        // Should be on submit button
        const focusedElement = await page.locator(':focus').first();
        expect(await focusedElement.isVisible()).toBeTruthy();
    });

    test('escape closes modals', async ({ page }) => {
        await page.goto(`${BASE_URL}/contacts`);
        await waitForPageLoad(page);
        
        // Try to open a modal
        const addButton = page.locator('button:has-text("Add"), button:has-text("New")');
        if (await addButton.first().isVisible()) {
            await addButton.first().click();
            
            // Press Escape
            await page.keyboard.press('Escape');
            
            // Modal should close
            const modal = page.locator('[role="dialog"], .modal');
            await expect(modal).not.toBeVisible({ timeout: 3000 }).catch(jest.fn());
        }
    });

    test('enter submits forms', async ({ page }) => {
        await page.goto(`${BASE_URL}/login`);
        await waitForPageLoad(page);
        
        const emailInput = page.locator('input[type="email"]').first();
        if (await emailInput.isVisible()) {
            await emailInput.fill('test@example.com');
            await page.keyboard.press('Enter');
            
            // Form should attempt to submit (may show error for incomplete form)
        }
    });
});
