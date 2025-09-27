/* eslint-disable no-console */
const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const pngToIco = require('png-to-ico');

const OUTPUT_DIR = path.resolve(__dirname, '..', 'public');

function ensureOutputDir() {
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }
}

function createHeaderLogoSVG(baseSize = 1024) {
  // Brand blue matched to theme-color in index.html
  const brandBlue = '#2563eb';

  // Three white bars (inspired by the header's BarChart3 icon) on rounded blue square
  // Coordinates are tuned for a balanced visual at favicon sizes
  const barWidth = 140;
  const cornerRadius = 200;
  const barCornerRadius = 50;
  const marginX = 170;
  const marginBottom = 180;

  const x1 = marginX;
  const x2 = baseSize / 2 - barWidth / 2;
  const x3 = baseSize - marginX - barWidth;

  const h1 = 420;
  const h2 = 620;
  const h3 = 780;

  const y1 = baseSize - marginBottom - h1;
  const y2 = baseSize - marginBottom - h2;
  const y3 = baseSize - marginBottom - h3;

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${baseSize}" height="${baseSize}" viewBox="0 0 ${baseSize} ${baseSize}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Logo">
  <rect x="0" y="0" width="${baseSize}" height="${baseSize}" rx="${cornerRadius}" fill="${brandBlue}" />
  <rect x="${x1}" y="${y1}" width="${barWidth}" height="${h1}" rx="${barCornerRadius}" fill="#ffffff" />
  <rect x="${x2}" y="${y2}" width="${barWidth}" height="${h2}" rx="${barCornerRadius}" fill="#ffffff" />
  <rect x="${x3}" y="${y3}" width="${barWidth}" height="${h3}" rx="${barCornerRadius}" fill="#ffffff" />
</svg>`;
}

async function writeIconPngs(svgMarkup) {
  const sizes = [
    { name: 'logo.png', size: 1024 },
    { name: 'icon-512x512.png', size: 512 },
    { name: 'icon-192x192.png', size: 192 },
    { name: 'apple-touch-icon.png', size: 180 },
    { name: 'favicon-32x32.png', size: 32 },
    { name: 'favicon-16x16.png', size: 16 },
  ];

  await Promise.all(
    sizes.map(async ({ name, size }) => {
      const outPath = path.join(OUTPUT_DIR, name);
      const buffer = Buffer.from(svgMarkup);
      await sharp(buffer, { density: 384 }) // higher density for crisper downscales
        .resize(size, size, { fit: 'cover' })
        .png({ compressionLevel: 9, quality: 100 })
        .toFile(outPath);
      console.log(`Wrote ${name}`);
    })
  );
}

async function writeFaviconIco() {
  const p16 = path.join(OUTPUT_DIR, 'favicon-16x16.png');
  const p32 = path.join(OUTPUT_DIR, 'favicon-32x32.png');
  const icoPath = path.join(OUTPUT_DIR, 'favicon.ico');
  const buf = await pngToIco([p16, p32]);
  fs.writeFileSync(icoPath, buf);
  console.log('Wrote favicon.ico');
}

async function main() {
  ensureOutputDir();
  const svg = createHeaderLogoSVG(1024);
  await writeIconPngs(svg);
  await writeFaviconIco();
  console.log('All icons generated successfully.');
}

main().catch((err) => {
  console.error('Icon generation failed:', err);
  process.exit(1);
});

