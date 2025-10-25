/* eslint-disable no-console */
const SftpClient = require('ssh2-sftp-client');
const path = require('path');

async function main() {
  const host = process.env.SFTP_HOST;
  const port = Number(process.env.SFTP_PORT || 22);
  const username = process.env.SFTP_USER;
  const password = process.env.SFTP_PASS;
  const targetDir = process.env.SFTP_TARGET_DIR || '/build';

  if (!host || !username || !password) {
    console.error('Missing required env vars: SFTP_HOST, SFTP_USER, SFTP_PASS');
    process.exit(1);
  }

  const sftp = new SftpClient();
  try {
    console.log(`Connecting to ${host}:${port} as ${username} ...`);
    await sftp.connect({ host, port, username, password, readyTimeout: 20000 });

    try {
      const stat = await sftp.stat(targetDir);
      if (stat && stat.type === 'd') {
        console.log(`Removing remote directory recursively: ${targetDir}`);
        await sftp.rmdir(targetDir, true);
        console.log('Remote directory removed.');
      } else if (stat && stat.type === '-') {
        console.log(`Target is a file. Deleting file: ${targetDir}`);
        await sftp.delete(targetDir);
      }
    } catch (err) {
      if (String(err?.message || '').includes('No such file') || String(err?.code) === 2) {
        console.log(`Target not found (ok): ${targetDir}`);
      } else {
        throw err;
      }
    }
  } catch (err) {
    console.error('Removal failed:', err);
    process.exitCode = 1;
  } finally {
    try { await sftp.end(); } catch {}
  }
}

main();

