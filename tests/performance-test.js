const lighthouse = require('lighthouse');
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function runPerformanceTests() {
  console.log('🚀 Starting performance testing for Agent Exo-Suit V5.0...');
  
  const browser = await puppeteer.launch({ 
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    
    // Set viewport
    await page.setViewport({ width: 1280, height: 720 });
    
    // Navigate to the website
    console.log('📱 Loading website for performance testing...');
    await page.goto('http://127.0.0.1:8000', { 
      waitUntil: 'networkidle0',
      timeout: 30000 
    });
    
    // Wait for content to load
    await page.waitForSelector('.hero-title', { timeout: 10000 });
    
    console.log('🔍 Running Lighthouse performance audit...');
    
    // Run Lighthouse audit
    const results = await lighthouse(page.url(), {
      port: (new URL(browser.wsEndpoint())).port,
      output: 'json',
      onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
      formFactor: 'desktop',
      throttling: {
        rttMs: 40,
        throughputKbps: 10240,
        cpuSlowdownMultiplier: 1,
        requestLatencyMs: 0,
        downloadThroughputKbps: 0,
        uploadThroughputKbps: 0
      }
    });
    
    const lhr = results.lhr;
    
    console.log('\n📊 Lighthouse Performance Test Results:');
    console.log('=======================================');
    
    // Performance Score
    const performanceScore = Math.round(lhr.categories.performance.score * 100);
    console.log(`⚡ Performance Score: ${performanceScore}/100`);
    
    // Accessibility Score
    const accessibilityScore = Math.round(lhr.categories.accessibility.score * 100);
    console.log(`♿ Accessibility Score: ${accessibilityScore}/100`);
    
    // Best Practices Score
    const bestPracticesScore = Math.round(lhr.categories['best-practices'].score * 100);
    console.log(`✅ Best Practices Score: ${bestPracticesScore}/100`);
    
    // SEO Score
    const seoScore = Math.round(lhr.categories.seo.score * 100);
    console.log(`🔍 SEO Score: ${seoScore}/100`);
    
    // Overall Score
    const overallScore = Math.round((performanceScore + accessibilityScore + bestPracticesScore + seoScore) / 4);
    console.log(`🎯 Overall Score: ${overallScore}/100`);
    
    // Performance Metrics
    console.log('\n📈 Performance Metrics:');
    console.log('========================');
    
    const metrics = lhr.audits;
    
    // First Contentful Paint
    const fcp = metrics['first-contentful-paint'];
    if (fcp) {
      console.log(`🎨 First Contentful Paint: ${Math.round(fcp.numericValue)}ms (${fcp.score === 1 ? '✅ Good' : '⚠️ Needs Improvement'})`);
    }
    
    // Largest Contentful Paint
    const lcp = metrics['largest-contentful-paint'];
    if (lcp) {
      console.log(`🖼️ Largest Contentful Paint: ${Math.round(lcp.numericValue)}ms (${lcp.score === 1 ? '✅ Good' : '⚠️ Needs Improvement'})`);
    }
    
    // First Input Delay
    const fid = metrics['max-potential-fid'];
    if (fid) {
      console.log(`⌨️ First Input Delay: ${Math.round(fid.numericValue)}ms (${fid.score === 1 ? '✅ Good' : '⚠️ Needs Improvement'})`);
    }
    
    // Cumulative Layout Shift
    const cls = metrics['cumulative-layout-shift'];
    if (cls) {
      console.log(`📐 Cumulative Layout Shift: ${cls.numericValue.toFixed(3)} (${cls.score === 1 ? '✅ Good' : '⚠️ Needs Improvement'})`);
    }
    
    // Speed Index
    const speedIndex = metrics['speed-index'];
    if (speedIndex) {
      console.log(`🚀 Speed Index: ${Math.round(speedIndex.numericValue)}ms (${speedIndex.score === 1 ? '✅ Good' : '⚠️ Needs Improvement'})`);
    }
    
    // Total Blocking Time
    const tbt = metrics['total-blocking-time'];
    if (tbt) {
      console.log(`⏱️ Total Blocking Time: ${Math.round(tbt.numericValue)}ms (${tbt.score === 1 ? '✅ Good' : '⚠️ Needs Improvement'})`);
    }
    
    // Opportunities for improvement
    console.log('\n🔧 Opportunities for Improvement:');
    console.log('==================================');
    
    const opportunities = Object.values(metrics).filter(audit => 
      audit.details && audit.details.type === 'opportunity' && audit.numericValue
    );
    
    if (opportunities.length > 0) {
      opportunities.slice(0, 5).forEach((opportunity, index) => {
        const savings = Math.round(opportunity.numericValue);
        console.log(`${index + 1}. ${opportunity.title}: Save ${savings}ms`);
      });
    } else {
      console.log('🎉 No major performance opportunities found!');
    }
    
    // Diagnostics
    console.log('\n🔍 Performance Diagnostics:');
    console.log('============================');
    
    const diagnostics = Object.values(metrics).filter(audit => 
      audit.details && audit.details.type === 'diagnostic'
    );
    
    if (diagnostics.length > 0) {
      diagnostics.slice(0, 3).forEach((diagnostic, index) => {
        console.log(`${index + 1}. ${diagnostic.title}: ${diagnostic.description}`);
      });
    }
    
    // Generate reports
    const reportDir = path.join(__dirname, '../test-results');
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }
    
    // Save detailed Lighthouse report
    const reportPath = path.join(reportDir, 'lighthouse-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(lhr, null, 2));
    console.log(`\n📄 Detailed Lighthouse report saved to: ${reportPath}`);
    
    // Generate HTML report
    const htmlReportPath = path.join(reportDir, 'lighthouse-report.html');
    const htmlResults = await lighthouse(page.url(), {
      port: (new URL(browser.wsEndpoint())).port,
      output: 'html',
      onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo']
    });
    
    fs.writeFileSync(htmlReportPath, htmlResults.report);
    console.log(`🌐 HTML report saved to: ${htmlReportPath}`);
    
    // Generate summary report
    const summaryReport = {
      timestamp: new Date().toISOString(),
      url: 'http://127.0.0.1:8000',
      scores: {
        performance: performanceScore,
        accessibility: accessibilityScore,
        bestPractices: bestPracticesScore,
        seo: seoScore,
        overall: overallScore
      },
      metrics: {
        firstContentfulPaint: fcp ? Math.round(fcp.numericValue) : null,
        largestContentfulPaint: lcp ? Math.round(lcp.numericValue) : null,
        firstInputDelay: fid ? Math.round(fid.numericValue) : null,
        cumulativeLayoutShift: cls ? cls.numericValue : null,
        speedIndex: speedIndex ? Math.round(speedIndex.numericValue) : null,
        totalBlockingTime: tbt ? Math.round(tbt.numericValue) : null
      },
      opportunities: opportunities.slice(0, 5).map(opp => ({
        title: opp.title,
        description: opp.description,
        savings: Math.round(opp.numericValue)
      }))
    };
    
    const summaryPath = path.join(reportDir, 'performance-summary.json');
    fs.writeFileSync(summaryPath, JSON.stringify(summaryReport, null, 2));
    console.log(`📋 Summary report saved to: ${summaryPath}`);
    
    // Overall assessment
    console.log('\n🏆 Performance Assessment:');
    console.log('===========================');
    
    if (overallScore >= 90) {
      console.log('🎉 EXCELLENT! Website performs exceptionally well.');
    } else if (overallScore >= 80) {
      console.log('✅ GOOD! Website performs well with minor improvements possible.');
    } else if (overallScore >= 60) {
      console.log('⚠️  FAIR! Website has performance issues that should be addressed.');
    } else {
      console.log('❌ NEEDS IMPROVEMENT! Website has significant performance issues.');
    }
    
    // Specific recommendations
    if (performanceScore < 80) {
      console.log('\n💡 Performance Recommendations:');
      console.log('• Optimize images and assets');
      console.log('• Minimize JavaScript execution time');
      console.log('• Reduce server response time');
      console.log('• Implement lazy loading');
    }
    
    if (accessibilityScore < 80) {
      console.log('\n💡 Accessibility Recommendations:');
      console.log('• Ensure proper color contrast');
      console.log('• Add alt text to images');
      console.log('• Use semantic HTML elements');
      console.log('• Test with screen readers');
    }
    
    if (seoScore < 80) {
      console.log('\n💡 SEO Recommendations:');
      console.log('• Optimize meta descriptions');
      console.log('• Improve page titles');
      console.log('• Add structured data');
      console.log('• Ensure mobile-friendliness');
    }
    
    return {
      success: true,
      scores: summaryReport.scores,
      metrics: summaryReport.metrics
    };
    
  } catch (error) {
    console.error('❌ Error during performance testing:', error.message);
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
  runPerformanceTests()
    .then(results => {
      if (results.success) {
        console.log('\n🏁 Performance testing completed successfully!');
        process.exit(0);
      } else {
        console.log('\n💥 Performance testing failed!');
        process.exit(1);
      }
    })
    .catch(error => {
      console.error('💥 Unexpected error:', error);
      process.exit(1);
    });
}

module.exports = { runPerformanceTests };
