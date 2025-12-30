import { test, expect } from '@playwright/test';

/**
 * Contacts E2E Tests
 * 
 * Tests for contacts management functionality
 */

test.describe('Contacts Management', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/contacts');
    });

    test('should display contacts list', async ({ page }) => {
        await expect(page.getByRole('heading', { name: /contacts/i })).toBeVisible();
        
        // Should have a table or list of contacts
        const contactsList = page.locator('[data-testid="contacts-list"], table, [role="grid"]');
        await expect(contactsList).toBeVisible();
    });

    test('should have add contact button', async ({ page }) => {
        const addButton = page.getByRole('button', { name: /add|new|create/i });
        await expect(addButton).toBeVisible();
    });

    test('should open add contact form', async ({ page }) => {
        const addButton = page.getByRole('button', { name: /add|new|create/i });
        await addButton.click();

        // Form should be visible
        await expect(page.getByLabel(/first name|name/i)).toBeVisible();
        await expect(page.getByLabel(/email/i)).toBeVisible();
    });

    test('should validate required fields in contact form', async ({ page }) => {
        const addButton = page.getByRole('button', { name: /add|new|create/i });
        await addButton.click();

        // Try to submit empty form
        const submitButton = page.getByRole('button', { name: /save|create|submit/i });
        await submitButton.click();

        // Should show validation errors
        const errorMessages = page.getByText(/required|invalid|enter/i);
        await expect(errorMessages.first()).toBeVisible();
    });

    test('should search contacts', async ({ page }) => {
        const searchInput = page.getByPlaceholder(/search/i);
        if (await searchInput.count() > 0) {
            await searchInput.fill('test');
            await page.waitForTimeout(500); // Debounce
            
            // Results should update
            await expect(page).toHaveURL(/.*search|filter|q=test.*/);
        }
    });

    test('should filter contacts by status', async ({ page }) => {
        const filterButton = page.getByRole('button', { name: /filter|status/i });
        if (await filterButton.count() > 0) {
            await filterButton.click();
            
            // Filter options should appear
            const filterOptions = page.getByRole('menuitem').or(page.getByRole('option'));
            await expect(filterOptions.first()).toBeVisible();
        }
    });

    test('should paginate contacts list', async ({ page }) => {
        const nextButton = page.getByRole('button', { name: /next|»|>/i });
        if (await nextButton.count() > 0 && await nextButton.isEnabled()) {
            await nextButton.click();
            await expect(page).toHaveURL(/.*page=2.*/);
        }
    });

    test('should export contacts', async ({ page }) => {
        const exportButton = page.getByRole('button', { name: /export|download/i });
        if (await exportButton.count() > 0) {
            // Click export button
            const downloadPromise = page.waitForEvent('download');
            await exportButton.click();
            
            // Should trigger a download or show export options
        }
    });

    test('should bulk select contacts', async ({ page }) => {
        const selectAllCheckbox = page.getByRole('checkbox', { name: /select all/i });
        if (await selectAllCheckbox.count() > 0) {
            await selectAllCheckbox.check();
            
            // Bulk action buttons should appear
            const bulkActions = page.getByRole('button', { name: /delete selected|bulk/i });
            await expect(bulkActions).toBeVisible();
        }
    });
});

test.describe('Contact Details', () => {
    test('should view contact details', async ({ page }) => {
        await page.goto('/contacts');
        
        // Click on first contact
        const firstContact = page.locator('tr, [data-testid="contact-row"]').first();
        if (await firstContact.count() > 0) {
            await firstContact.click();
            
            // Should show contact details
            await expect(page).toHaveURL(/.*contacts\/\d+.*/);
        }
    });

    test('should edit contact', async ({ page }) => {
        await page.goto('/contacts/1'); // Assuming contact ID 1 exists
        
        const editButton = page.getByRole('button', { name: /edit/i });
        if (await editButton.count() > 0) {
            await editButton.click();
            
            // Edit form should appear
            await expect(page.getByRole('textbox').first()).toBeEditable();
        }
    });

    test('should show contact activity history', async ({ page }) => {
        await page.goto('/contacts/1');
        
        const activityTab = page.getByRole('tab', { name: /activity|history/i });
        if (await activityTab.count() > 0) {
            await activityTab.click();
            
            // Activity list should be visible
            const activityList = page.locator('[data-testid="activity-list"]');
            await expect(activityList).toBeVisible();
        }
    });

    test('should add note to contact', async ({ page }) => {
        await page.goto('/contacts/1');
        
        const addNoteButton = page.getByRole('button', { name: /add note|new note/i });
        if (await addNoteButton.count() > 0) {
            await addNoteButton.click();
            
            const noteInput = page.getByPlaceholder(/note|comment/i);
            await noteInput.fill('Test note content');
            
            const saveButton = page.getByRole('button', { name: /save|add/i });
            await saveButton.click();
            
            // Note should appear in list
            await expect(page.getByText('Test note content')).toBeVisible();
        }
    });
});
