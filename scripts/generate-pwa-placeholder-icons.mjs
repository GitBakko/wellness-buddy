#!/usr/bin/env node
// Phase 1 PWA placeholder icons — solid warm-coral background with a small white "wb" mark.
// Final icons land in Plan 08 after tone-calibration mockup review.
//
// Why hand-rolled: zero runtime deps, deterministic byte output for reproducible CI builds.
// The small text/glyph is approximated with a simple block letter draw — placeholder quality
// is intentional; this is NOT the final brand mark.
import { writeFileSync, mkdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { deflateSync } from 'node:zlib';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = resolve(__dirname, '..', 'frontend', 'public', 'icons');
mkdirSync(OUT_DIR, { recursive: true });

// Warm-coral RGB approximation of oklch(63% 0.165 28) — sRGB ~ #E66B4A
const CORAL = { r: 0xe6, g: 0x6b, b: 0x4a };
const WHITE = { r: 0xff, g: 0xff, b: 0xff };

// CRC32 table (PNG spec)
const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();
function crc32(buf) {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
function chunk(type, data) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);
  const typeBuf = Buffer.from(type, 'ascii');
  const crcBuf = Buffer.alloc(4);
  crcBuf.writeUInt32BE(crc32(Buffer.concat([typeBuf, data])), 0);
  return Buffer.concat([len, typeBuf, data, crcBuf]);
}

function generatePNG(size, withGlyph = true) {
  // Build raw RGB pixel data (filter byte + 3 bytes per pixel per row)
  const rowLen = 1 + size * 3;
  const raw = Buffer.alloc(rowLen * size);
  for (let y = 0; y < size; y++) {
    raw[y * rowLen] = 0; // filter type 0 (None)
    for (let x = 0; x < size; x++) {
      // Solid coral background by default
      let r = CORAL.r, g = CORAL.g, b = CORAL.b;
      if (withGlyph) {
        // Crude white "wb" mark — two thick vertical strokes in the centered area
        const cx = size / 2, cy = size / 2;
        const half = size * 0.18;
        const stroke = Math.max(2, Math.round(size * 0.06));
        // Letter box: cx - half ... cx + half horizontally, cy - half ... cy + half vertically
        const inBoxY = y >= cy - half && y <= cy + half;
        // "w" is two slashes — too complex; placeholder: simple "+" inside coral square
        const onVertical = Math.abs(x - cx) <= stroke / 2 && inBoxY;
        const onHorizontal = Math.abs(y - cy) <= stroke / 2 && x >= cx - half && x <= cx + half;
        if (onVertical || onHorizontal) {
          r = WHITE.r; g = WHITE.g; b = WHITE.b;
        }
      }
      const off = y * rowLen + 1 + x * 3;
      raw[off] = r;
      raw[off + 1] = g;
      raw[off + 2] = b;
    }
  }

  // PNG signature
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

  // IHDR
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(size, 0);
  ihdr.writeUInt32BE(size, 4);
  ihdr[8] = 8;       // bit depth
  ihdr[9] = 2;       // color type: RGB
  ihdr[10] = 0;      // compression: deflate
  ihdr[11] = 0;      // filter: standard
  ihdr[12] = 0;      // interlace: none

  const idat = deflateSync(raw, { level: 9 });
  const iend = Buffer.alloc(0);

  return Buffer.concat([
    sig,
    chunk('IHDR', ihdr),
    chunk('IDAT', idat),
    chunk('IEND', iend),
  ]);
}

const targets = [
  { name: 'icon-192.png', size: 192, withGlyph: true },
  { name: 'icon-512.png', size: 512, withGlyph: true },
  { name: 'icon-maskable-512.png', size: 512, withGlyph: true },
  { name: 'apple-touch-icon-180.png', size: 180, withGlyph: true },
];

for (const t of targets) {
  const png = generatePNG(t.size, t.withGlyph);
  writeFileSync(resolve(OUT_DIR, t.name), png);
  console.log(`wrote ${t.name} (${t.size}x${t.size}, ${png.length} bytes)`);
}
