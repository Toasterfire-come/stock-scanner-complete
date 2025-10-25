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
  const brandBlue = '#2563eb';
  // ChartColumn icon centered inside a rounded blue square
  const padding = 128;
  const vb = 24; // original lucide viewport
  const scale = (baseSize - padding * 2) / vb;
  const translate = padding;
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${baseSize}" height="${baseSize}" viewBox="0 0 ${baseSize} ${baseSize}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Logo">
  <rect x="0" y="0" width="${baseSize}" height="${baseSize}" rx="200" fill="${brandBlue}" />
  <g transform="translate(${translate},${translate}) scale(${scale})" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none">
    <path d="M3 3v16a2 2 0 0 0 2 2h16"></path>
    <path d="M18 17V9"></path>
    <path d="M13 17V5"></path>
    <path d="M8 17v-3"></path>
  </g>
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

