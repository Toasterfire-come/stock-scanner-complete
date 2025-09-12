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
  const USER = process.env.SFTP_USER || 'a1531117';
  const PASS = process.env.SFTP_PASS || 'REPLACE_ME';

  // Determine local build directory (prefer root build, fallback to nested ./frontend/build)
  const ROOT_BUILD = path.resolve('/workspace/frountend/build');
  const NESTED_BUILD = path.resolve('/workspace/frountend/frontend/build');
  const LOCAL_BUILD = fs.existsSync(ROOT_BUILD) ? ROOT_BUILD : (fs.existsSync(NESTED_BUILD) ? NESTED_BUILD : ROOT_BUILD);
  const REMOTE_ROOT = process.env.SFTP_REMOTE_ROOT || '/homepages/46/d4299295342/htdocs';
  const EXTRA_FILES = [
    path.resolve('/workspace/frountend/public/.htaccess'),
    path.resolve('/workspace/frountend/public/offline.html'),
  ];

  if (!fs.existsSync(LOCAL_BUILD)) {
    throw new Error(`Build directory not found: ${LOCAL_BUILD}. Ensure you've built the frontend.`);
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

    // Clean remote directory except for logs folder which is host-managed
    const entries = await sftp.list(REMOTE_ROOT);
    for (const entry of entries) {
      const remotePath = path.posix.join(REMOTE_ROOT, entry.name);
      if (entry.name === 'logs') continue; // Preserve logs
      try {
        if (entry.type === 'd') {
          console.log(`Removing remote directory: ${remotePath}`);
          await sftp.rmdir(remotePath, true);
        } else {
          console.log(`Removing remote file: ${remotePath}`);
          await sftp.delete(remotePath);
        }
      } catch (e) {
        console.warn(`Warning: failed to remove ${remotePath}: ${e && e.message ? e.message : e}`);
      }
    }

    // Upload build directory contents to remote root
    console.log(`Uploading directory: ${LOCAL_BUILD} -> ${REMOTE_ROOT}`);
    await sftp.uploadDir(LOCAL_BUILD, REMOTE_ROOT);

    // Upload extra files to remote root
    for (const localFile of EXTRA_FILES) {
      if (!fs.existsSync(localFile)) continue;
      const remoteFile = path.posix.join(REMOTE_ROOT, path.basename(localFile));
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

