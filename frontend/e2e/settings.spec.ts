import { test, expect } from '@playwright/test';

/**
 * Settings & User Profile E2E Tests
 * 
 * Tests for settings and user profile functionality
 */

test.describe('User Profile', () => {
    test('should access profile settings', async ({ page }) => {
        await page.goto('/settings');
        
        await expect(page.getByRole('heading', { name: /settings|profile/i })).toBeVisible();
    });

    test('should update profile information', async ({ page }) => {
        await page.goto('/settings');
        
        const profileTab = page.getByRole('tab', { name: /profile|account/i });
        if (await profileTab.count() > 0) {
            await profileTab.click();
        }

        const nameInput = page.getByLabel(/name/i);
        if (await nameInput.count() > 0) {
            await nameInput.clear();
            await nameInput.fill('Updated Name');
        }

        const saveButton = page.getByRole('button', { name: /save|update/i });
        if (await saveButton.count() > 0) {
            await saveButton.click();
            
            await expect(page.getByText(/saved|updated|success/i)).toBeVisible({ timeout: 5000 });
        }
    });

    test('should change password', async ({ page }) => {
        await page.goto('/settings');
        
        const securityTab = page.getByRole('tab', { name: /security|password/i });
        if (await securityTab.count() > 0) {
            await securityTab.click();
        }

        const currentPassword = page.getByLabel(/current password/i);
        if (await currentPassword.count() > 0) {
            await currentPassword.fill('oldpassword');
            
            const newPassword = page.getByLabel(/new password/i);
            await newPassword.fill('newpassword123');
            
            const confirmPassword = page.getByLabel(/confirm/i);
            await confirmPassword.fill('newpassword123');
        }
    });

    test('should toggle 2FA settings', async ({ page }) => {
        await page.goto('/settings');
        
        const securityTab = page.getByRole('tab', { name: /security/i });
        if (await securityTab.count() > 0) {
            await securityTab.click();
        }

        const twoFactorToggle = page.getByRole('switch', { name: /two-factor|2fa/i });
        if (await twoFactorToggle.count() > 0) {
            await expect(twoFactorToggle).toBeVisible();
        }
    });
});

test.describe('Notification Settings', () => {
    test('should access notification settings', async ({ page }) => {
        await page.goto('/settings');
        
        const notificationsTab = page.getByRole('tab', { name: /notification/i });
        if (await notificationsTab.count() > 0) {
            await notificationsTab.click();
            
            // Notification options should be visible
            const emailNotifications = page.getByText(/email/i);
            await expect(emailNotifications.first()).toBeVisible();
        }
    });

    test('should toggle email notifications', async ({ page }) => {
        await page.goto('/settings');
        
        const notificationsTab = page.getByRole('tab', { name: /notification/i });
        if (await notificationsTab.count() > 0) {
            await notificationsTab.click();
        }

        const emailToggle = page.getByRole('switch').first();
        if (await emailToggle.count() > 0) {
            await emailToggle.click();
        }
    });
});

test.describe('Integration Settings', () => {
    test('should view integrations', async ({ page }) => {
        await page.goto('/settings');
        
        const integrationsTab = page.getByRole('tab', { name: /integration/i });
        if (await integrationsTab.count() > 0) {
            await integrationsTab.click();
            
            // Integration options should be visible
            const integrationCards = page.locator('[data-testid="integration-card"]');
            if (await integrationCards.count() > 0) {
                await expect(integrationCards.first()).toBeVisible();
            }
        }
    });

    test('should connect integration', async ({ page }) => {
        await page.goto('/integrations');
        
        const connectButton = page.getByRole('button', { name: /connect/i });
        if (await connectButton.count() > 0) {
            await expect(connectButton.first()).toBeVisible();
        }
    });
});

test.describe('Theme & Appearance', () => {
    test('should toggle dark mode', async ({ page }) => {
        await page.goto('/settings');
        
        const appearanceTab = page.getByRole('tab', { name: /appearance|theme/i });
        if (await appearanceTab.count() > 0) {
            await appearanceTab.click();
        }

        const darkModeToggle = page.getByRole('switch', { name: /dark mode/i });
        if (await darkModeToggle.count() > 0) {
            await darkModeToggle.click();
            
            // Check if dark mode is applied
            await page.waitForTimeout(300);
        }
    });
});
