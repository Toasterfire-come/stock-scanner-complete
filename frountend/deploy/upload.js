#!/usr/bin/env node
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');
let Client;
try {
  Client = require('ssh2-sftp-client');
} catch (_) {
  Client = null;
}

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

  if (!Client) {
    // Fallback path: SSH cleanup using absolute path, then SFTP batch upload to login directory ('.')
    if (PASS === 'REPLACE_ME') {
      throw new Error('SFTP_PASS is not set. Please set environment variable SFTP_PASS with your password.');
    }
    const escapedPass = PASS.replace(/'/g, "'\\''");
    const base = `sshpass -p '${escapedPass}'`;
    console.log(`Cleaning remote directory (preserving logs): ${REMOTE_ROOT}`);
    try {
      execSync(`${base} ssh -o StrictHostKeyChecking=no -p ${PORT} ${USER}@${HOST} "mkdir -p '${REMOTE_ROOT}' && cd '${REMOTE_ROOT}' && find . -mindepth 1 -maxdepth 1 -not -name logs -exec rm -rf {} +"`, { stdio: 'inherit' });
    } catch (err) {
      console.warn('Warning: remote cleanup reported an issue:', err && err.message ? err.message : err);
    }

    // Use SFTP batch to upload to the login directory ('.') to avoid absolute path canonicalization issues
    const batchFile = path.resolve('/tmp/sftp_batch_upload.txt');
    const batch = [
      'cd .',
      `lcd ${LOCAL_BUILD}`.replace(/\\/g, '/'),
      'put -r *'
    ].join('\n');
    fs.writeFileSync(batchFile, batch);

    console.log(`Uploading directory via SFTP batch: ${LOCAL_BUILD} -> (login dir)`);
    execSync(`${base} sftp -oBatchMode=no -o PreferredAuthentications=password -o PubkeyAuthentication=no -o StrictHostKeyChecking=no -P ${PORT} -b '${batchFile}' ${USER}@${HOST}`, { stdio: 'inherit' });

    // Upload extra files (if present) to login directory
    for (const localFile of EXTRA_FILES) {
      if (!fs.existsSync(localFile)) continue;
      const fileBatch = path.resolve('/tmp/sftp_batch_file.txt');
      fs.writeFileSync(fileBatch, [
        'cd .',
        `lcd ${path.dirname(localFile)}`.replace(/\\/g, '/'),
        `put ${path.basename(localFile)}`
      ].join('\n'));
      console.log(`Uploading extra file via SFTP: ${localFile}`);
      execSync(`${base} sftp -oBatchMode=no -o PreferredAuthentications=password -o PubkeyAuthentication=no -o StrictHostKeyChecking=no -P ${PORT} -b '${fileBatch}' ${USER}@${HOST}`, { stdio: 'inherit' });
    }

    console.log('✅ Upload completed successfully');
    return;
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

    // Verify remote path; if it fails, fall back to login directory '.'
    let destination = REMOTE_ROOT;
    try {
      await sftp.list(REMOTE_ROOT);
    } catch (_) {
      console.warn(`Warning: Remote path not accessible via SFTP: ${REMOTE_ROOT}. Falling back to login directory '.'`);
      destination = '.';
    }

    // Upload build directory contents
    console.log(`Uploading directory: ${LOCAL_BUILD} -> ${destination}`);
    await sftp.uploadDir(LOCAL_BUILD, destination);

    // Upload extra files to remote root
    for (const localFile of EXTRA_FILES) {
      if (!fs.existsSync(localFile)) continue;
      const remoteFile = path.posix.join(destination, path.basename(localFile));
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

