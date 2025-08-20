const puppeteer = require('puppeteer');
const { AxePuppeteer } = require('@axe-core/puppeteer');
const fs = require('fs');
const path = require('path');

async function runAccessibilityTests() {
  console.log('🚀 Starting accessibility testing for Agent Exo-Suit V5.0...');
  
  const browser = await puppeteer.launch({ 
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    
    // Set viewport
    await page.setViewport({ width: 1280, height: 720 });
    
    // Navigate to the website
    console.log('📱 Loading website...');
    await page.goto('http://127.0.0.1:8000', { 
      waitUntil: 'networkidle0',
      timeout: 30000 
    });
    
    // Wait for content to load
    await page.waitForSelector('.hero-title', { timeout: 10000 });
    
    console.log('🔍 Running accessibility audit...');
    
    // Run axe-core accessibility tests
    const results = await new AxePuppeteer(page).analyze();
    
    // Process results
    const violations = results.violations;
    const passes = results.passes;
    const incomplete = results.incomplete;
    
    console.log('\n📊 Accessibility Test Results:');
    console.log('================================');
    console.log(`✅ Passes: ${passes.length}`);
    console.log(`❌ Violations: ${violations.length}`);
    console.log(`⚠️  Incomplete: ${incomplete.length}`);
    
    // Report violations
    if (violations.length > 0) {
      console.log('\n❌ Accessibility Violations Found:');
      console.log('==================================');
      
      violations.forEach((violation, index) => {
        console.log(`\n${index + 1}. ${violation.help} (${violation.impact})`);
        console.log(`   Description: ${violation.description}`);
        console.log(`   Help: ${violation.helpUrl}`);
        console.log(`   Affected Elements: ${violation.nodes.length}`);
        
        violation.nodes.forEach((node, nodeIndex) => {
          console.log(`   ${nodeIndex + 1}. ${node.html}`);
        });
      });
    } else {
      console.log('\n🎉 No accessibility violations found!');
    }
    
    // Report passes
    if (passes.length > 0) {
      console.log('\n✅ Accessibility Passes:');
      console.log('========================');
      passes.slice(0, 10).forEach((pass, index) => {
        console.log(`${index + 1}. ${pass.help}`);
      });
      
      if (passes.length > 10) {
        console.log(`... and ${passes.length - 10} more passes`);
      }
    }
    
    // Generate detailed report
    const reportPath = path.join(__dirname, '../test-results/accessibility-report.json');
    const reportDir = path.dirname(reportPath);
    
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }
    
    fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
    console.log(`\n📄 Detailed report saved to: ${reportPath}`);
    
    // Generate summary report
    const summaryReport = {
      timestamp: new Date().toISOString(),
      url: 'http://127.0.0.1:8000',
      summary: {
        passes: passes.length,
        violations: violations.length,
        incomplete: incomplete.length,
        total: passes.length + violations.length + incomplete.length
      },
      violations: violations.map(v => ({
        id: v.id,
        impact: v.impact,
        description: v.description,
        help: v.help,
        helpUrl: v.helpUrl,
        tags: v.tags,
        nodes: v.nodes.length
      })),
      passes: passes.map(p => ({
        id: p.id,
        description: p.description,
        help: p.help
      }))
    };
    
    const summaryPath = path.join(__dirname, '../test-results/accessibility-summary.json');
    fs.writeFileSync(summaryPath, JSON.stringify(summaryReport, null, 2));
    console.log(`📋 Summary report saved to: ${summaryPath}`);
    
    // Check for critical accessibility issues
    const criticalIssues = violations.filter(v => v.impact === 'critical');
    const seriousIssues = violations.filter(v => v.impact === 'serious');
    
    if (criticalIssues.length > 0) {
      console.log(`\n🚨 CRITICAL ISSUES: ${criticalIssues.length}`);
      console.log('These must be fixed before launch!');
    }
    
    if (seriousIssues.length > 0) {
      console.log(`\n⚠️  SERIOUS ISSUES: ${seriousIssues.length}`);
      console.log('These should be fixed for better accessibility.');
    }
    
    // Overall assessment
    const totalIssues = violations.length;
    if (totalIssues === 0) {
      console.log('\n🎉 EXCELLENT! Website meets accessibility standards.');
    } else if (totalIssues <= 3) {
      console.log('\n✅ GOOD! Website has minor accessibility issues.');
    } else if (totalIssues <= 8) {
      console.log('\n⚠️  FAIR! Website has some accessibility issues to address.');
    } else {
      console.log('\n❌ NEEDS IMPROVEMENT! Website has significant accessibility issues.');
    }
    
    return {
      success: true,
      violations: violations.length,
      passes: passes.length,
      critical: criticalIssues.length,
      serious: seriousIssues.length
    };
    
  } catch (error) {
    console.error('❌ Error during accessibility testing:', error.message);
    return {
      success: false,
      error: error.message
    };
  } finally {
    await browser.close();
  }
}

// Run tests if called directly
if (require.main === module) {
  runAccessibilityTests()
    .then(results => {
      if (results.success) {
        console.log('\n🏁 Accessibility testing completed successfully!');
        process.exit(results.violations === 0 ? 0 : 1);
      } else {
        console.log('\n💥 Accessibility testing failed!');
        process.exit(1);
      }
    })
    .catch(error => {
      console.error('💥 Unexpected error:', error);
      process.exit(1);
    });
}

module.exports = { runAccessibilityTests };
