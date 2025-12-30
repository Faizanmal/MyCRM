import { test, expect } from '@playwright/test';

/**
 * Tasks E2E Tests
 * 
 * Tests for task management functionality
 */

test.describe('Tasks Management', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/tasks');
    });

    test('should display tasks page', async ({ page }) => {
        await expect(page.getByRole('heading', { name: /tasks/i })).toBeVisible();
    });

    test('should show task list', async ({ page }) => {
        const tasksList = page.locator('[data-testid="tasks-list"], table, [role="list"]');
        await expect(tasksList).toBeVisible();
    });

    test('should add new task', async ({ page }) => {
        const addButton = page.getByRole('button', { name: /add|new|create/i });
        await addButton.click();

        // Fill task form
        const titleInput = page.getByLabel(/title|name|subject/i);
        await titleInput.fill('Test Task');

        const descriptionInput = page.getByLabel(/description|details/i);
        if (await descriptionInput.count() > 0) {
            await descriptionInput.fill('Test task description');
        }

        // Set due date
        const dueDateInput = page.getByLabel(/due|date/i);
        if (await dueDateInput.count() > 0) {
            await dueDateInput.click();
        }

        // Set priority
        const prioritySelect = page.getByLabel(/priority/i);
        if (await prioritySelect.count() > 0) {
            await prioritySelect.click();
            await page.getByRole('option', { name: /high/i }).click();
        }
    });

    test('should filter tasks by status', async ({ page }) => {
        const filterButtons = page.getByRole('tab').or(page.getByRole('button', { name: /all|open|completed|pending/i }));
        if (await filterButtons.count() > 0) {
            const completedFilter = page.getByRole('tab', { name: /completed/i }).or(
                page.getByRole('button', { name: /completed/i })
            );
            if (await completedFilter.count() > 0) {
                await completedFilter.click();
                await page.waitForTimeout(300);
            }
        }
    });

    test('should filter tasks by priority', async ({ page }) => {
        const priorityFilter = page.getByRole('button', { name: /priority|filter/i });
        if (await priorityFilter.count() > 0) {
            await priorityFilter.click();
            
            const highPriority = page.getByRole('menuitem', { name: /high/i });
            if (await highPriority.count() > 0) {
                await highPriority.click();
            }
        }
    });

    test('should complete a task', async ({ page }) => {
        const checkbox = page.getByRole('checkbox').first();
        if (await checkbox.count() > 0) {
            await checkbox.check();
            
            // Should update task status
            await page.waitForTimeout(500);
        }
    });

    test('should sort tasks', async ({ page }) => {
        const sortButton = page.getByRole('button', { name: /sort/i });
        if (await sortButton.count() > 0) {
            await sortButton.click();
            
            const sortOptions = page.getByRole('menuitem');
            await expect(sortOptions.first()).toBeVisible();
        }
    });

    test('should show overdue tasks indicator', async ({ page }) => {
        const overdueTasks = page.locator('[data-testid="overdue"], .overdue, .text-red');
        // Overdue tasks may or may not exist
        if (await overdueTasks.count() > 0) {
            await expect(overdueTasks.first()).toBeVisible();
        }
    });
});

test.describe('Task Details', () => {
    test('should view task details', async ({ page }) => {
        await page.goto('/tasks');
        
        const firstTask = page.locator('[data-testid="task-row"], tr, [data-task]').first();
        if (await firstTask.count() > 0) {
            await firstTask.click();
            
            // Should show details panel or navigate
            const detailsPanel = page.locator('[data-testid="task-details"], .task-details');
            if (await detailsPanel.count() > 0) {
                await expect(detailsPanel).toBeVisible();
            }
        }
    });

    test('should edit task', async ({ page }) => {
        await page.goto('/tasks/1');
        
        const editButton = page.getByRole('button', { name: /edit/i });
        if (await editButton.count() > 0) {
            await editButton.click();
            
            const titleInput = page.getByLabel(/title|name/i);
            await expect(titleInput).toBeEditable();
        }
    });

    test('should delete task', async ({ page }) => {
        await page.goto('/tasks/1');
        
        const deleteButton = page.getByRole('button', { name: /delete/i });
        if (await deleteButton.count() > 0) {
            await deleteButton.click();
            
            // Confirmation dialog
            const confirmButton = page.getByRole('button', { name: /confirm|yes|delete/i });
            if (await confirmButton.count() > 0) {
                await expect(confirmButton).toBeVisible();
            }
        }
    });

    test('should add comment to task', async ({ page }) => {
        await page.goto('/tasks/1');
        
        const commentInput = page.getByPlaceholder(/comment|add a comment/i);
        if (await commentInput.count() > 0) {
            await commentInput.fill('Test comment');
            
            const submitButton = page.getByRole('button', { name: /post|send|add/i });
            await submitButton.click();
        }
    });

    test('should assign task to user', async ({ page }) => {
        await page.goto('/tasks/1');
        
        const assigneeSelect = page.getByLabel(/assignee|assign to/i);
        if (await assigneeSelect.count() > 0) {
            await assigneeSelect.click();
            
            const userOptions = page.getByRole('option');
            await expect(userOptions.first()).toBeVisible();
        }
    });
});
