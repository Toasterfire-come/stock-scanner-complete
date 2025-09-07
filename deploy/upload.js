#!/usr/bin/env node
const path = require('path');
const fs = require('fs');
const Client = require('ssh2-sftp-client');

async function ensureFileExists(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Missing file: ${filePath}`);
  }
}

async function main() {
  const HOST = process.env.SFTP_HOST || 'access-5018544625.webspace-host.com';
  const PORT = parseInt(process.env.SFTP_PORT || '22', 10);
  const USER = process.env.SFTP_USER || 'a2565254';
  const PASS = process.env.SFTP_PASS || 'REPLACE_ME';

  const LOCAL_BUILD = path.resolve('/workspace/frontend/build');
  const EXTRA_FILES = [
    path.resolve('/workspace/frontend/public/.htaccess'),
    path.resolve('/workspace/frontend/public/offline.html'),
  ];

  if (!fs.existsSync(LOCAL_BUILD)) {
    throw new Error(`Build directory not found: ${LOCAL_BUILD}`);
  }

  for (const f of EXTRA_FILES) {
    if (!fs.existsSync(f)) {
      // Skip missing optional extras
      continue;
    }
  }

  const sftp = new Client();
  try {
    await sftp.connect({ host: HOST, port: PORT, username: USER, password: PASS, readyTimeout: 15000 });

    // Upload build directory contents to remote root
    // ssh2-sftp-client's uploadDir will create directories as needed
    console.log(`Uploading directory: ${LOCAL_BUILD} -> /`);
    await sftp.uploadDir(LOCAL_BUILD, '/');

    // Upload extra files to remote root
    for (const localFile of EXTRA_FILES) {
      if (!fs.existsSync(localFile)) continue;
      const remoteFile = '/' + path.basename(localFile);
      console.log(`Uploading file: ${localFile} -> ${remoteFile}`);
      await sftp.fastPut(localFile, remoteFile);
    }

    console.log('✅ Upload completed successfully');
  } finally {
    try { await sftp.end(); } catch {}
  }
}

main().catch((err) => {
  console.error('❌ Upload failed:', err && err.message ? err.message : err);
  process.exit(1);
});

