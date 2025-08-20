const { runAccessibilityTests } = require('./accessibility-test');
const { runPerformanceTests } = require('./performance-test');
const fs = require('fs');
const path = require('path');

async function runAllTests() {
  console.log('🚀 Starting comprehensive testing for Agent Exo-Suit V5.0...');
  console.log('===========================================================\n');
  
  const startTime = Date.now();
  const results = {
    timestamp: new Date().toISOString(),
    website: 'http://127.0.0.1:8000',
    tests: {}
  };
  
  try {
    // 1. Run Playwright functional tests
    console.log('🔧 Step 1: Running Playwright functional tests...');
    console.log('Run: npm run test');
    console.log('This will test all website functionality across multiple browsers\n');
    
    // 2. Run accessibility tests
    console.log('♿ Step 2: Running accessibility tests...');
    const accessibilityResults = await runAccessibilityTests();
    results.tests.accessibility = accessibilityResults;
    
    if (accessibilityResults.success) {
      console.log(`✅ Accessibility: ${accessibilityResults.passes} passes, ${accessibilityResults.violations} violations`);
    } else {
      console.log(`❌ Accessibility: Failed - ${accessibilityResults.error}`);
    }
    
    console.log('');
    
    // 3. Run performance tests
    console.log('⚡ Step 3: Running performance tests...');
    const performanceResults = await runPerformanceTests();
    results.tests.performance = performanceResults;
    
    if (performanceResults.success) {
      console.log(`✅ Performance: Overall score ${performanceResults.scores.overall}/100`);
      console.log(`   Performance: ${performanceResults.scores.performance}/100`);
      console.log(`   Accessibility: ${performanceResults.scores.accessibility}/100`);
      console.log(`   Best Practices: ${performanceResults.scores.bestPractices}/100`);
      console.log(`   SEO: ${performanceResults.scores.seo}/100`);
    } else {
      console.log(`❌ Performance: Failed - ${performanceResults.error}`);
    }
    
    console.log('');
    
    // 4. Generate unified report
    console.log('📊 Step 4: Generating unified test report...');
    const reportDir = path.join(__dirname, '../test-results');
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }
    
    const unifiedReportPath = path.join(reportDir, 'unified-test-report.json');
    fs.writeFileSync(unifiedReportPath, JSON.stringify(results, null, 2));
    console.log(`📄 Unified report saved to: ${unifiedReportPath}`);
    
    // 5. Generate summary report
    const summaryReport = {
      timestamp: results.timestamp,
      website: results.website,
      summary: {
        accessibility: {
          status: results.tests.accessibility?.success ? 'PASS' : 'FAIL',
          passes: results.tests.accessibility?.passes || 0,
          violations: results.tests.accessibility?.violations || 0,
          critical: results.tests.accessibility?.critical || 0,
          serious: results.tests.accessibility?.serious || 0
        },
        performance: {
          status: results.tests.performance?.success ? 'PASS' : 'FAIL',
          overallScore: results.tests.performance?.scores?.overall || 0,
          performanceScore: results.tests.performance?.scores?.performance || 0,
          accessibilityScore: results.tests.performance?.scores?.accessibility || 0,
          bestPracticesScore: results.tests.performance?.scores?.bestPractices || 0,
          seoScore: results.tests.performance?.scores?.seo || 0
        }
      },
      recommendations: generateRecommendations(results),
      nextSteps: generateNextSteps(results)
    };
    
    const summaryPath = path.join(reportDir, 'test-summary.json');
    fs.writeFileSync(summaryPath, JSON.stringify(summaryReport, null, 2));
    console.log(`📋 Summary report saved to: ${summaryPath}`);
    
    // 6. Display final results
    const totalTime = Date.now() - startTime;
    console.log('🏁 All tests completed!');
    console.log('=======================');
    console.log(`⏱️  Total time: ${Math.round(totalTime / 1000)}s`);
    console.log(`📊 Reports saved to: ${reportDir}`);
    
    // Overall assessment
    const overallAssessment = assessOverallQuality(results);
    console.log(`\n🏆 Overall Assessment: ${overallAssessment.grade}`);
    console.log(overallAssessment.message);
    
    // Next steps
    console.log('\n📋 Next Steps:');
    console.log('===============');
    summaryReport.nextSteps.forEach((step, index) => {
      console.log(`${index + 1}. ${step}`);
    });
    
    return {
      success: true,
      results: results,
      assessment: overallAssessment
    };
    
  } catch (error) {
    console.error('💥 Error during comprehensive testing:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

function generateRecommendations(results) {
  const recommendations = [];
  
  // Accessibility recommendations
  if (results.tests.accessibility?.success) {
    const acc = results.tests.accessibility;
    if (acc.violations > 0) {
      if (acc.critical > 0) {
        recommendations.push('Fix critical accessibility issues before launch');
      }
      if (acc.serious > 0) {
        recommendations.push('Address serious accessibility violations');
      }
      if (acc.violations <= 3) {
        recommendations.push('Minor accessibility improvements recommended');
      }
    } else {
      recommendations.push('Excellent accessibility - no issues found');
    }
  }
  
  // Performance recommendations
  if (results.tests.performance?.success) {
    const perf = results.tests.performance;
    if (perf.scores.overall >= 90) {
      recommendations.push('Outstanding performance - ready for production');
    } else if (perf.scores.overall >= 80) {
      recommendations.push('Good performance with minor optimizations possible');
    } else if (perf.scores.overall >= 60) {
      recommendations.push('Performance needs improvement before launch');
    } else {
      recommendations.push('Significant performance issues must be addressed');
    }
    
    if (perf.scores.performance < 80) {
      recommendations.push('Focus on performance optimization');
    }
    if (perf.scores.accessibility < 80) {
      recommendations.push('Improve accessibility scores');
    }
    if (perf.scores.seo < 80) {
      recommendations.push('Enhance SEO optimization');
    }
  }
  
  return recommendations;
}

function generateNextSteps(results) {
  const nextSteps = [];
  
  // Check if website is ready for launch
  const accReady = results.tests.accessibility?.success && results.tests.accessibility?.violations === 0;
  const perfReady = results.tests.performance?.success && results.tests.performance?.scores?.overall >= 80;
  
  if (accReady && perfReady) {
    nextSteps.push('Website is ready for production launch! 🎉');
    nextSteps.push('Run Playwright tests to verify all functionality');
    nextSteps.push('Deploy to production environment');
  } else {
    if (!accReady) {
      nextSteps.push('Fix accessibility issues identified in testing');
    }
    if (!perfReady) {
      nextSteps.push('Address performance issues before launch');
    }
    nextSteps.push('Re-run tests after fixes are implemented');
    nextSteps.push('Ensure all tests pass before production deployment');
  }
  
  nextSteps.push('Monitor website performance in production');
  nextSteps.push('Set up automated testing for future updates');
  
  return nextSteps;
}

function assessOverallQuality(results) {
  let score = 0;
  let maxScore = 0;
  
  // Accessibility scoring
  if (results.tests.accessibility?.success) {
    const acc = results.tests.accessibility;
    if (acc.violations === 0) {
      score += 100;
    } else if (acc.critical === 0 && acc.serious <= 2) {
      score += 80;
    } else if (acc.critical === 0 && acc.serious <= 5) {
      score += 60;
    } else {
      score += 20;
    }
    maxScore += 100;
  }
  
  // Performance scoring
  if (results.tests.performance?.success) {
    const perf = results.tests.performance;
    score += perf.scores.overall;
    maxScore += 100;
  }
  
  const overallScore = maxScore > 0 ? Math.round(score / maxScore * 100) : 0;
  
  if (overallScore >= 90) {
    return {
      grade: 'A+ (EXCELLENT)',
      message: 'Website meets all quality standards and is ready for production launch!'
    };
  } else if (overallScore >= 80) {
    return {
      grade: 'A (VERY GOOD)',
      message: 'Website is in excellent condition with minor improvements possible.'
    };
  } else if (overallScore >= 70) {
    return {
      grade: 'B (GOOD)',
      message: 'Website is good but has some issues that should be addressed before launch.'
    };
  } else if (overallScore >= 60) {
    return {
      grade: 'C (FAIR)',
      message: 'Website needs improvement before production launch.'
    };
  } else {
    return {
      grade: 'D (NEEDS WORK)',
      message: 'Website has significant issues that must be resolved before launch.'
    };
  }
}

// Run tests if called directly
if (require.main === module) {
  runAllTests()
    .then(results => {
      if (results.success) {
        console.log('\n🎯 Testing completed successfully!');
        process.exit(0);
      } else {
        console.log('\n💥 Testing failed!');
        process.exit(1);
      }
    })
    .catch(error => {
      console.error('💥 Unexpected error:', error);
      process.exit(1);
    });
}

module.exports = { runAllTests };
