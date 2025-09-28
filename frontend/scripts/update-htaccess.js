/* eslint-disable no-console */
const SftpClient = require('ssh2-sftp-client');

const HTACCESS_CONTENT = `# Canonical host and SPA routing
Options -Indexes -MultiViews

<IfModule mod_rewrite.c>
RewriteEngine On
RewriteBase /

# Canonical domain: redirect www -> apex
RewriteCond %{HTTP_HOST} ^www\.tradescanpro\.com$ [NC]
RewriteRule ^(.*)$ https://tradescanpro.com/$1 [L,R=301]

# Serve existing files/directories as-is
RewriteCond %{REQUEST_FILENAME} -f [OR]
RewriteCond %{REQUEST_FILENAME} -d
RewriteRule ^ - [L]

# SPA fallback to index.html (internal rewrite, no redirect)
RewriteRule . /index.html [L]
</IfModule>
`;

async function main() {
  const host = process.env.SFTP_HOST;
  const port = Number(process.env.SFTP_PORT || 22);
  const username = process.env.SFTP_USER;
  const password = process.env.SFTP_PASS || process.env.SFTP_PASSWORD;
  const remotePath = '/.htaccess';

  if (!host || !username || !password) {
    console.error('Missing SFTP_HOST, SFTP_USER, or SFTP_PASS');
    process.exit(1);
  }

  const sftp = new SftpClient();
  try {
    console.log(`Connecting to ${host}:${port} as ${username} ...`);
    await sftp.connect({ host, port, username, password, readyTimeout: 20000 });
    console.log('Connected. Uploading .htaccess ...');
    await sftp.put(Buffer.from(HTACCESS_CONTENT, 'utf8'), remotePath, {
      flags: 'w'
    });
    console.log('Uploaded .htaccess successfully.');
  } catch (err) {
    console.error('Failed to upload .htaccess:', err.message);
    process.exitCode = 1;
  } finally {
    try { await sftp.end(); } catch {}
  }
}

main();

