const { test, expect } = require('@playwright/test');

test.describe('Agent Exo-Suit V5.0 Website - Functional Testing', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the homepage before each test
    await page.goto('/');
    // Wait for the page to be fully loaded
    await page.waitForLoadState('networkidle');
  });

  test('Homepage loads successfully with correct title and meta tags', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Agent Exo-Suit V5.0/);
    
    // Check meta description
    const metaDescription = page.locator('meta[name="description"]');
    await expect(metaDescription).toHaveAttribute('content', /26\/43 tools operational/);
    
    // Check favicon
    const favicon = page.locator('link[rel="icon"]');
    await expect(favicon).toBeVisible();
  });

  test('Hero section displays correctly with "What is this?" explanation', async ({ page }) => {
    // Check hero title
    const heroTitle = page.locator('.hero-title');
    await expect(heroTitle).toContainText('Agent Exo-Suit V5');
    
    // Check "What is this?" section
    const whatIsThis = page.locator('.what-is-this');
    await expect(whatIsThis).toBeVisible();
    await expect(whatIsThis).toContainText('What is this?');
    await expect(whatIsThis).toContainText('Swiss Army knife');
    
    // Check key benefits
    const benefits = page.locator('.benefit');
    await expect(benefits).toHaveCount(4);
    await expect(benefits.nth(0)).toContainText('Local & Secure');
    await expect(benefits.nth(1)).toContainText('Production Ready');
    await expect(benefits.nth(2)).toContainText('High Performance');
    await expect(benefits.nth(3)).toContainText('Developer Friendly');
  });

  test('Hero stats display correct tool count and status', async ({ page }) => {
    // Check tool count
    const toolCount = page.locator('.hero-stat-value').first();
    await expect(toolCount).toContainText('26/43');
    
    // Check system health
    const systemHealth = page.locator('.hero-stat-value').nth(2);
    await expect(systemHealth).toContainText('PROTECTED');
    
    // Check completion percentage
    const completion = page.locator('.hero-stat-value').nth(3);
    await expect(completion).toContainText('60%');
    
    // Check MMH-RS status
    const mmhRs = page.locator('.hero-stat-value').nth(4);
    await expect(mmhRs).toContainText('MMH-RS');
  });

  test('Call-to-action buttons are functional and link correctly', async ({ page }) => {
    // Check primary CTA button
    const primaryButton = page.locator('.btn-primary');
    await expect(primaryButton).toContainText('Get Started Now');
    await expect(primaryButton).toHaveAttribute('href', /github\.com/);
    
    // Check secondary CTA button
    const secondaryButton = page.locator('.btn-secondary');
    await expect(secondaryButton).toContainText('Quick Start Guide');
    await expect(secondaryButton).toHaveAttribute('href', 'docs/00-QUICKSTART.md');
    
    // Check tertiary CTA button
    const tertiaryButton = page.locator('.btn-tertiary');
    await expect(tertiaryButton).toContainText('See All Tools');
    await expect(tertiaryButton).toHaveAttribute('href', 'docs/05-TOOLS/tools-overview.md');
  });

  test('Navigation menu functions correctly', async ({ page }) => {
    // Check navigation links
    const navLinks = page.locator('.nav-links a');
    await expect(navLinks).toHaveCount(10);
    
    // Check logo and status
    const logoStatus = page.locator('.logo-status');
    await expect(logoStatus).toContainText('26/43 Tools Operational');
    
    // Check search functionality
    const searchInput = page.locator('#global-search');
    await expect(searchInput).toBeVisible();
    await expect(searchInput).toHaveAttribute('placeholder', 'Search documentation...');
  });

  test('Performance cards display correct information', async ({ page }) => {
    // Check first performance card
    const firstCard = page.locator('.perf-card-primary');
    await expect(firstCard).toContainText('26/43');
    await expect(firstCard).toContainText('60% Complete');
    
    // Check second performance card
    const secondCard = page.locator('.perf-card-secondary');
    await expect(secondCard).toContainText('207-3.7K');
    await expect(secondCard).toContainText('Files/Second');
    
    // Check third performance card
    const thirdCard = page.locator('.perf-card-success');
    await expect(thirdCard).toContainText('MAXIMUM');
    await expect(thirdCard).toContainText('Security Level');
  });

  test('Copy buttons function correctly', async ({ page }) => {
    // Test copy functionality (mock clipboard API)
    await page.addInitScript(() => {
      Object.defineProperty(navigator, 'clipboard', {
        value: {
          writeText: () => Promise.resolve(),
        },
      });
    });
    
    // Click copy button
    const copyButton = page.locator('.copy-btn').first();
    await copyButton.click();
    
    // Check if button shows success state
    await expect(copyButton).toContainText('Copied!');
  });

  test('Breadcrumb navigation works correctly', async ({ page }) => {
    // Check breadcrumb structure
    const breadcrumbList = page.locator('.breadcrumb-list');
    await expect(breadcrumbList).toBeVisible();
    
    // Check breadcrumb links
    const homeLink = page.locator('.breadcrumb-link').first();
    await expect(homeLink).toContainText('Home');
    await expect(homeLink).toHaveAttribute('href', '#overview');
  });

  test('User journey steps are displayed correctly', async ({ page }) => {
    // Check user journey steps
    const journeySteps = page.locator('.journey-step');
    await expect(journeySteps).toHaveCount(9);
    
    // Check first step is active
    const firstStep = journeySteps.first();
    await expect(firstStep).toHaveClass(/active/);
    
    // Check step labels
    await expect(journeySteps.nth(0)).toContainText('Quick Stats');
    await expect(journeySteps.nth(1)).toContainText('Performance');
    await expect(journeySteps.nth(2)).toContainText('Safety');
  });

  test('Page sections are properly structured', async ({ page }) => {
    // Check main sections exist
    const overviewSection = page.locator('#overview');
    await expect(overviewSection).toBeVisible();
    
    const performanceSection = page.locator('#performance');
    await expect(performanceSection).toBeVisible();
    
    // Check section headers
    const sectionTitle = page.locator('.section-title').first();
    await expect(sectionTitle).toContainText('System Overview');
  });

  test('Responsive design elements work on different viewports', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check if navigation is still accessible
    const navToggle = page.locator('.nav-toggle');
    if (await navToggle.isVisible()) {
      await navToggle.click();
    }
    
    // Check if hero section is still readable
    const heroTitle = page.locator('.hero-title');
    await expect(heroTitle).toBeVisible();
    
    // Reset viewport
    await page.setViewportSize({ width: 1280, height: 720 });
  });

  test('CSS and JavaScript assets load correctly', async ({ page }) => {
    // Check CSS loading
    const cssLink = page.locator('link[href*="core.css"]');
    await expect(cssLink).toBeVisible();
    
    // Check JavaScript loading
    const jsScript = page.locator('script[src*="component-loader.js"]');
    await expect(jsScript).toBeVisible();
    
    // Check if animations are working
    const animatedElement = page.locator('.scroll-animate');
    await expect(animatedElement).toBeVisible();
  });

  test('Footer information is correct and complete', async ({ page }) => {
    // Scroll to footer
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    
    // Check footer content
    const footer = page.locator('footer, .footer, [class*="footer"]');
    if (await footer.isVisible()) {
      await expect(footer).toContainText('Agent Exo-Suit V5.0');
      await expect(footer).toContainText('26/43 Tools Operational');
    }
  });

  test('Page loads within acceptable time limits', async ({ page }) => {
    // Measure page load time
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    // Page should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);
  });

  test('All internal links are accessible', async ({ page }) => {
    // Get all internal links
    const internalLinks = page.locator('a[href^="/"], a[href^="#"], a[href^="docs/"]');
    
    // Check if links are present and have valid href attributes
    const linkCount = await internalLinks.count();
    expect(linkCount).toBeGreaterThan(0);
    
    // Test a few key links
    const quickStartLink = page.locator('a[href="docs/00-QUICKSTART.md"]');
    await expect(quickStartLink).toBeVisible();
    
    const toolsLink = page.locator('a[href="docs/05-TOOLS/tools-overview.md"]');
    await expect(toolsLink).toBeVisible();
  });
});
