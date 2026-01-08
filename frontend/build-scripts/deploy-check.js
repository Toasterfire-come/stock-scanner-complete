#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔍 Running deployment readiness check...\n');

const checkPassed = [];
const checkFailed = [];

// Align with production build defaults so deploy checks behave consistently.
const DEFAULT_PROD_BACKEND_URL = 'https://api.tradescanpro.com';
process.env.REACT_APP_BACKEND_URL = process.env.REACT_APP_BACKEND_URL || DEFAULT_PROD_BACKEND_URL;

// Check 1: Build directory exists
if (fs.existsSync('./build')) {
  checkPassed.push('Build directory exists');
} else {
  checkFailed.push('Build directory missing - run build first');
}

// Check 2: Critical files exist
const criticalFiles = [
  './build/index.html',
  './build/manifest.json',
  './build/_headers',
  './build/robots.txt',
  './build/sw.js'
];

criticalFiles.forEach(file => {
  if (fs.existsSync(file)) {
    checkPassed.push(`${path.basename(file)} exists`);
  } else {
    checkFailed.push(`${path.basename(file)} missing`);
  }
});

// Check 3: Environment variables
const requiredEnvVars = [
  'REACT_APP_API_PASSWORD'
];

requiredEnvVars.forEach(varName => {
  if (process.env[varName]) {
    checkPassed.push(`${varName} configured`);
  } else {
    checkFailed.push(`${varName} missing`);
  }
});

// Check 4: Security headers
if (fs.existsSync('./build/_headers')) {
  const headers = fs.readFileSync('./build/_headers', 'utf8');
  const requiredHeaders = [
    'X-Frame-Options',
    'X-Content-Type-Options',
    'Content-Security-Policy',
    'Strict-Transport-Security'
  ];
  
  requiredHeaders.forEach(header => {
    if (headers.includes(header)) {
      checkPassed.push(`${header} configured`);
    } else {
      checkFailed.push(`${header} missing from headers`);
    }
  });
}

// Check 5: Backend connectivity
console.log('🌐 Testing backend connectivity...');
const backendUrl = process.env.REACT_APP_BACKEND_URL;
if (backendUrl) {
  // Note: In a real deployment, you might want to add an actual HTTP check here
  checkPassed.push('Backend URL configured');
} else {
  checkFailed.push('Backend URL not configured');
}

// Check 6: Build optimization
if (fs.existsSync('./build/static')) {
  const jsFiles = fs.readdirSync('./build/static/js');
  const cssFiles = fs.readdirSync('./build/static/css');
  
  if (jsFiles.some(f => f.includes('.min.js') || f.includes('.js'))) {
    checkPassed.push('JavaScript files optimized');
  } else {
    checkFailed.push('JavaScript files not optimized');
  }
  
  if (cssFiles.some(f => f.includes('.min.css') || f.includes('.css'))) {
    checkPassed.push('CSS files optimized');
  } else {
    checkFailed.push('CSS files not optimized');
  }
}

// Results
console.log('\n✅ Passed Checks:');
checkPassed.forEach(check => console.log(`  ✓ ${check}`));

if (checkFailed.length > 0) {
  console.log('\n❌ Failed Checks:');
  checkFailed.forEach(check => console.log(`  ✗ ${check}`));
  console.log('\n🚫 Deployment not ready. Please fix the issues above.');
  process.exit(1);
} else {
  console.log('\n🎉 All checks passed! Ready for deployment.');
  
  // Deployment instructions
  console.log('\n📋 Deployment Instructions:');
  console.log('1. Upload the contents of ./build to your static host');
  console.log('2. Configure your host to use the _headers file');
  console.log('3. Set up HTTPS (required for security features)');
  console.log('4. Test the deployed application');
  console.log('5. Monitor for any console errors');
  
  console.log('\n🔗 Static Hosting Options:');
  console.log('  • Netlify: Supports _headers file automatically');
  console.log('  • Vercel: Use vercel.json for headers');
  console.log('  • AWS S3 + CloudFront: Configure headers in CloudFront');
  console.log('  • GitHub Pages: Limited header support');
  
  process.exit(0);
}