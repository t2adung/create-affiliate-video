// node render.mjs <publicDir> <props.json> <out.mp4> [stillFrames]
import {bundle} from '@remotion/bundler';
import {renderMedia, renderStill, selectComposition} from '@remotion/renderer';
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {availableParallelism} from 'node:os';
const concurrency = Math.max(1, Math.min(4, availableParallelism()));
const [publicDir, propsFile, out, stills] = process.argv.slice(2);
const inputProps = JSON.parse(await readFile(propsFile, 'utf8'));
const b = process.env.CHROME_BIN ? {browserExecutable: process.env.CHROME_BIN} : {};
const serveUrl = await bundle({entryPoint: resolve(import.meta.dirname, 'src/index.jsx'), publicDir: resolve(publicDir)});
const composition = await selectComposition({serveUrl, id: 'DIY', inputProps, ...b});
if (stills) {
  for (const fr of stills.split(',').map(Number)) await renderStill({serveUrl, composition, inputProps, frame: fr, output: `${out}-${fr}.png`, ...b});
} else {
  await renderMedia({serveUrl, composition, inputProps, codec: 'h264', crf: 18, audioCodec: 'aac', outputLocation: out, concurrency, ...b});
}
console.log(JSON.stringify({frames: composition.durationInFrames}));
