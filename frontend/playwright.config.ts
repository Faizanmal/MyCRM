import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E Test Configuration
 * 
 * Run E2E tests with:
 *   npx playwright test
 *   npx playwright test --ui  (interactive mode)
 */

export default defineConfig({
    testDir: './e2e',
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: process.env.CI ? 1 : undefined,
    reporter: [
        ['html', { outputFolder: 'playwright-report' }],
        ['json', { outputFile: 'test-results/results.json' }],
    ],

    use: {
        baseURL: process.env.BASE_URL || 'http://localhost:3000',
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
    },

    projects: [
        // Authentication setup
        {
            name: 'setup',
            testMatch: /.*\.setup\.ts/,
        },

        // Desktop browsers
        {
            name: 'chromium',
            use: {
                ...devices['Desktop Chrome'],
                storageState: 'playwright/.auth/user.json',
            },
            dependencies: ['setup'],
        },
        {
            name: 'firefox',
            use: {
                ...devices['Desktop Firefox'],
                storageState: 'playwright/.auth/user.json',
            },
            dependencies: ['setup'],
        },
        {
            name: 'webkit',
            use: {
                ...devices['Desktop Safari'],
                storageState: 'playwright/.auth/user.json',
            },
            dependencies: ['setup'],
        },

        // Mobile browsers
        {
            name: 'mobile-chrome',
            use: {
                ...devices['Pixel 5'],
                storageState: 'playwright/.auth/user.json',
            },
            dependencies: ['setup'],
        },
        {
            name: 'mobile-safari',
            use: {
                ...devices['iPhone 12'],
                storageState: 'playwright/.auth/user.json',
            },
            dependencies: ['setup'],
        },
    ],

    // Run local dev server before tests
    webServer: {
        command: 'npm run dev',
        url: 'http://localhost:3000',
        reuseExistingServer: !process.env.CI,
        timeout: 120 * 1000,
    },
});
