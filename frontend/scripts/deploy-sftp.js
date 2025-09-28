/* eslint-disable no-console */
const path = require('path');
const fs = require('fs');
const SftpClient = require('ssh2-sftp-client');

async function clearRemoteDir(sftp, remoteDir) {
  const preserveHtaccess = process.env.PRESERVE_HTACCESS !== 'false';
  const entries = await sftp.list(remoteDir);
  for (const entry of entries) {
    const name = entry.name;
    if (!name || name === '.' || name === '..') continue;
    const remotePath = path.posix.join(remoteDir, name);
    try {
      // Preserve .htaccess optionally (default: preserve)
      if (preserveHtaccess && name === '.htaccess') {
        console.log(`Preserving file: ${remotePath}`);
        continue;
      }
      if (entry.type === 'd') {
        await sftp.rmdir(remotePath, true);
        console.log(`Removed directory: ${remotePath}`);
      } else {
        await sftp.delete(remotePath);
        console.log(`Removed file: ${remotePath}`);
      }
    } catch (err) {
      console.warn(`Warn: failed to remove ${remotePath}: ${err.message}`);
    }
  }
}

async function main() {
  const host = process.env.SFTP_HOST;
  const port = Number(process.env.SFTP_PORT || 22);
  const username = process.env.SFTP_USER;
  const password = process.env.SFTP_PASS;
  const remoteDir = process.env.SFTP_REMOTE_DIR || '/';
  const localBuildDir = process.env.LOCAL_BUILD_DIR || path.resolve(__dirname, '..', 'build');

  if (!host || !username || !password) {
    console.error('Missing required env vars: SFTP_HOST, SFTP_USER, SFTP_PASS');
    process.exit(1);
  }
  if (!fs.existsSync(localBuildDir)) {
    console.error(`Local build directory not found: ${localBuildDir}`);
    process.exit(1);
  }

  const sftp = new SftpClient();
  try {
    console.log(`Connecting to ${host}:${port} as ${username} ...`);
    await sftp.connect({
      host,
      port,
      username,
      password,
      readyTimeout: 20000,
      tryKeyboard: true,
      onKeyboardInteractive: (_name, _instructions, _lang, prompts, finish) => {
        try {
          if (Array.isArray(prompts) && prompts.length > 0) {
            finish([password]);
          } else {
            finish([]);
          }
        } catch (_) {
          try { finish([]); } catch {}
        }
      }
    });

    // Ensure target directory exists and is accessible
    try {
      await sftp.mkdir(remoteDir, true);
    } catch {}

    const cwd = await sftp.cwd();
    console.log(`Connected. Remote CWD: ${cwd}`);

    console.log(`Clearing remote directory: ${remoteDir}`);
    await clearRemoteDir(sftp, remoteDir);

    console.log(`Uploading ${localBuildDir} -> ${remoteDir}`);
    await sftp.uploadDir(localBuildDir, remoteDir);
    console.log('Upload complete.');
  } catch (err) {
    console.error('Deployment failed:', err);
    process.exitCode = 1;
  } finally {
    try { await sftp.end(); } catch {}
  }
}

main();

