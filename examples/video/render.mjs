import {readFile, mkdtemp, rename, rm} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {bundle} from '@remotion/bundler';
import {renderMedia, selectComposition} from '@remotion/renderer';

const [input, output] = process.argv.slice(2);
if (!input || !output) throw new Error('Usage: node render.mjs input.json output.mp4');
const props = JSON.parse(await readFile(input, 'utf8'));
const valid = (value, max) => typeof value === 'string' &&
  /^[\x20-\x7E]+$/.test(value) && value.trim().length > 0 && value.length <= max;
if (!props || Object.keys(props).length !== 2 ||
    !valid(props.title, 48) || !valid(props.subtitle, 96)) {
  throw new Error('Expected an ASCII title (1–48 chars) and subtitle (1–96 chars)');
}
const stage = await mkdtemp(resolve(dirname(output), '.render-'));
try {
  const serveUrl = await bundle(fileURLToPath(new URL('./index.jsx', import.meta.url)));
  const shared = {serveUrl, inputProps: props, browserExecutable: process.env.CHROME_BIN};
  const composition = await selectComposition({...shared, id: 'TitleCard'});
  const rendered = resolve(stage, 'rendered.mp4');
  await renderMedia({...shared, composition, codec: 'h264', outputLocation: rendered, concurrency: 2});
  const final = resolve(stage, 'final.mp4');
  execFileSync('ffmpeg', ['-v', 'error', '-i', rendered, '-c', 'copy', '-movflags', '+faststart', final]);
  const report = JSON.parse(execFileSync('ffprobe', [
    '-v', 'error', '-select_streams', 'v:0', '-show_entries',
    'stream=width,height,nb_frames,codec_name', '-of', 'json', final,
  ], {encoding: 'utf8'}));
  const [stream] = report.streams;
  if (stream.width !== 640 || stream.height !== 360 ||
      Number(stream.nb_frames) !== 24 || stream.codec_name !== 'h264') {
    throw new Error('Rendered video failed the format gate');
  }
  execFileSync('ffmpeg', ['-v', 'error', '-xerror', '-i', final, '-f', 'null', '-']);
  await rename(final, output);
} finally {
  await rm(stage, {recursive: true, force: true});
}
