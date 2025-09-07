#!/usr/bin/env node

const { Client } = require('ssh2');
const fs = require('fs');
const path = require('path');

// Configuration
const config = {
  host: 'access-5018544625.webspace-host.com',
  port: 22,
  username: 'a2565254',
  password: 'C2rt3rK#2010'
};

const buildDir = path.join(__dirname, 'frontend', 'build');
const remoteDir = '.';

console.log('🚀 Starting deployment to webspace...');

// Check if build directory exists
if (!fs.existsSync(buildDir)) {
  console.error('❌ Build directory not found. Please run the build first.');
  process.exit(1);
}

const conn = new Client();

// Function to upload directory recursively
async function uploadDirectory(sftp, localDir, remoteDir) {
  const files = fs.readdirSync(localDir);
  
  for (const file of files) {
    const localPath = path.join(localDir, file);
    const remotePath = remoteDir + '/' + file;
    const stat = fs.statSync(localPath);
    
    if (stat.isDirectory()) {
      // Create remote directory
      try {
        await new Promise((resolve, reject) => {
          sftp.mkdir(remotePath, (err) => {
            if (err && err.code !== 4) reject(err); // Ignore if exists
            else resolve();
          });
        });
      } catch (err) {
        // Directory might already exist
      }
      
      // Recursively upload subdirectory
      await uploadDirectory(sftp, localPath, remotePath);
    } else {
      // Upload file
      await new Promise((resolve, reject) => {
        console.log(`📤 Uploading: ${file}`);
        sftp.fastPut(localPath, remotePath, (err) => {
          if (err) reject(err);
          else resolve();
        });
      });
    }
  }
}

conn.on('ready', () => {
  console.log('✅ Connected to server');
  
  conn.sftp(async (err, sftp) => {
    if (err) {
      console.error('❌ SFTP error:', err);
      conn.end();
      return;
    }
    
    try {
      console.log('📦 Starting file upload...');
      await uploadDirectory(sftp, buildDir, remoteDir);
      console.log('✅ All files uploaded successfully!');
      console.log('🌐 Your site should be live at your webspace URL');
    } catch (uploadErr) {
      console.error('❌ Upload error:', uploadErr);
    } finally {
      conn.end();
    }
  });
});

conn.on('error', (err) => {
  console.error('❌ Connection error:', err.message);
  
  // Provide fallback instructions
  console.log('\n📝 MANUAL DEPLOYMENT INSTRUCTIONS:');
  console.log('=====================================');
  console.log('Since automated deployment failed, please use an SFTP client:');
  console.log('');
  console.log('Connection details:');
  console.log('  Host: access-5018544625.webspace-host.com');
  console.log('  Port: 22');
  console.log('  Username: a2565254');
  console.log('  Password: C2rt3rK#2010');
  console.log('');
  console.log('Upload the contents of: /workspace/frontend/build/');
  console.log('To the remote directory: /html/');
  console.log('');
  console.log('Your build files are ready at: ' + buildDir);
});

// Connect
console.log('🔌 Connecting to webspace...');
conn.connect(config);