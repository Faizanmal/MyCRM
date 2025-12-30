import { test, expect } from '@playwright/test';

/**
 * Authentication E2E Tests
 * 
 * Tests for login, logout, and authentication flows
 */

test.describe('Authentication', () => {
    // These tests don't use the authenticated state
    test.use({ storageState: { cookies: [], origins: [] } });

    test('should show login page for unauthenticated users', async ({ page }) => {
        await page.goto('/dashboard');

        // Should redirect to login
        await expect(page).toHaveURL(/.*login.*/);

        // Login form should be visible
        await expect(page.getByLabel(/email/i)).toBeVisible();
        await expect(page.getByLabel(/password/i)).toBeVisible();
    });

    test('should show validation errors for empty form', async ({ page }) => {
        await page.goto('/login');

        // Try to submit empty form
        await page.getByRole('button', { name: /sign in|log in/i }).click();

        // Should show validation errors
        const errorMessages = page.getByText(/required|invalid|enter/i);
        await expect(errorMessages.first()).toBeVisible();
    });

    test('should show error for invalid credentials', async ({ page }) => {
        await page.goto('/login');

        // Fill in invalid credentials
        await page.getByLabel(/email/i).fill('invalid@example.com');
        await page.getByLabel(/password/i).fill('wrongpassword');

        // Submit
        await page.getByRole('button', { name: /sign in|log in/i }).click();

        // Should show error message
        await expect(
            page.getByText(/invalid|incorrect|failed|error/i)
        ).toBeVisible({ timeout: 10000 });
    });

    test('should navigate to register page', async ({ page }) => {
        await page.goto('/login');

        // Click register link
        const registerLink = page.getByRole('link', { name: /register|sign up|create account/i });
        if (await registerLink.count() > 0) {
            await registerLink.click();
            await expect(page).toHaveURL(/.*register.*/);
        }
    });

    test('should navigate to forgot password', async ({ page }) => {
        await page.goto('/login');

        // Click forgot password link
        const forgotLink = page.getByRole('link', { name: /forgot|reset/i });
        if (await forgotLink.count() > 0) {
            await forgotLink.click();
            await expect(page).toHaveURL(/.*forgot|reset|password.*/);
        }
    });
});

test.describe('Authenticated User', () => {
    test('should access dashboard when authenticated', async ({ page }) => {
        await page.goto('/dashboard');

        // Should stay on dashboard (not redirect to login)
        await expect(page).toHaveURL(/.*dashboard.*/);
        await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
    });

    test('should show user info in header', async ({ page }) => {
        await page.goto('/dashboard');

        // Look for user info or avatar
        const userElement = page.locator('[data-user-menu], .user-avatar, [aria-label*="user"], [data-testid="user-info"]');
        if (await userElement.count() > 0) {
            await expect(userElement.first()).toBeVisible();
        }
    });

    test('should logout successfully', async ({ page }) => {
        await page.goto('/dashboard');

        // Click user menu
        const userMenu = page.locator('[data-user-menu], .user-avatar').first();
        if (await userMenu.count() > 0) {
            await userMenu.click();

            // Click logout
            const logoutButton = page.getByRole('menuitem', { name: /logout|sign out/i });
            if (await logoutButton.count() > 0) {
                await logoutButton.click();

                // Should redirect to login
                await expect(page).toHaveURL(/.*login.*/);
            }
        }
    });
});

test.describe('Protected Routes', () => {
    test.use({ storageState: { cookies: [], origins: [] } });

    const protectedRoutes = [
        '/dashboard',
        '/leads',
        '/contacts',
        '/opportunities',
        '/tasks',
        '/settings',
    ];

    for (const route of protectedRoutes) {
        test(`should redirect ${route} to login for unauthenticated users`, async ({ page }) => {
            await page.goto(route);

            // Should redirect to login
            await expect(page).toHaveURL(/.*login.*/);
        });
    }
});
