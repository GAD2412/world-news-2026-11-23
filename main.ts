// Writes the front page of Monday 23 November 2026 to /output/entry.png (Node 22, standard library only).
// entry.png is drawn by render.py (python3 render.py) from the stories listed in FACTS.md; this program checks it
// against the contest's limits and copies it byte for byte. Outside the grader: mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const png = readFileSync(new URL('./entry.png', import.meta.url));
const signature = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const isPng = png.subarray(0, 8).equals(signature);
const width = png.readUInt32BE(16);
const height = png.readUInt32BE(20);
if (!isPng || png.length > 1048576 || width > 1024 || height > 1024) {
  throw new Error(`entry.png out of limits: png=${isPng} bytes=${png.length} size=${width}x${height}`);
}
writeFileSync(join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png'), png);
