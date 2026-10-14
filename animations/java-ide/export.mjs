// Capture the deterministic timeline as PNG frames, then encode a real GIF.
import { chromium } from 'playwright-core';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const project = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(project, '../..');
const frames = path.join(project, '.hyperframes/gif-frames');
const assets = path.join(root, 'assets');
const fps = 10;
const ffmpeg = process.env.FFMPEG_PATH;
if (!ffmpeg) throw new Error('Set FFMPEG_PATH to the FFmpeg executable.');
await mkdir(frames, { recursive: true });
const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  headless: true,
  args: ['--disable-gpu', '--allow-file-access-from-files'],
});
try {
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(pathToFileURL(path.join(project, 'index.html')).href);
  await page.evaluate(() => document.fonts.ready);
  const displayed = await page.evaluate(() => window.__JAVA_SOURCE);
  const java = await readFile(path.join(project, 'src/dev/pedroyuri/Developer.java'), 'utf8');
  if (displayed.trim() !== java.trim()) throw new Error('Java in the animation differs from the compiled source.');
  for (let frame = 0; frame < fps * 15; frame++) {
    await page.evaluate(time => window.__seek(time), frame / fps);
    await page.screenshot({ path: path.join(frames, `${String(frame).padStart(4, '0')}.png`) });
    if (frame % 30 === 0) process.stdout.write(`Captured ${frame}/${fps*15} frames\n`);
  }
  await page.evaluate(() => window.__seek(8.99));
  await page.screenshot({ path: path.join(assets, 'animated-java-ide-preview.png') });
  await page.evaluate(() => window.__seek(12));
  await page.screenshot({ path: path.join(assets, 'animated-java-ide-running.png') });
  const layout = await page.evaluate(() => {
    const viewport = document.getElementById('viewport').getBoundingClientRect();
    return [...document.querySelectorAll('.line-content')].map(line => {
      const r = line.getBoundingClientRect();
      return { text: line.textContent, right: r.right, viewportRight: viewport.right };
    });
  });
  if (layout.some(line => line.right > line.viewportRight + 1)) throw new Error('Java code overflows the editor horizontally.');
  if (errors.length) throw new Error(errors.join('\n'));
  await writeFile(path.join(project, '.hyperframes/capture-validation.json'), JSON.stringify({
    width: 1600, height: 900, fps, seconds: 15, frames: fps*15,
    sourceMatchesJava: true, runtimeErrors: errors, horizontalOverflow: false,
  }, null, 2));
} finally {
  await browser.close();
}

function encode(args) {
  const result = spawnSync(ffmpeg, ['-hide_banner', '-loglevel', 'error', '-y', ...args], { stdio: 'inherit' });
  if (result.status !== 0) throw new Error(`FFmpeg failed with exit code ${result.status}`);
}
const sequence = path.join(frames, '%04d.png');
const palette = path.join(frames, 'palette.png');
encode(['-framerate', String(fps), '-i', sequence, '-vf', 'palettegen=max_colors=128:stats_mode=diff', '-frames:v', '1', palette]);
encode(['-framerate', String(fps), '-i', sequence, '-i', palette, '-lavfi', 'paletteuse=dither=none:diff_mode=rectangle', '-loop', '0', path.join(assets, 'animated-java-ide.gif')]);
// A closer editor view provides a larger code size on narrower README layouts.
const mobilePalette = path.join(frames, 'palette-mobile.png');
const crop = 'crop=1188:806:321:37';
encode(['-framerate', String(fps), '-i', sequence, '-vf', `${crop},palettegen=max_colors=128:stats_mode=diff`, '-frames:v', '1', mobilePalette]);
encode(['-framerate', String(fps), '-i', sequence, '-i', mobilePalette, '-lavfi', `[0:v]${crop}[v];[v][1:v]paletteuse=dither=none:diff_mode=rectangle`, '-loop', '0', path.join(assets, 'animated-java-ide-mobile.gif')]);
process.stdout.write('Exported desktop/mobile GIFs and static previews.\n');
