// Puppeteer 逐帧渲染脚本 — 绕过 HyperFrames 多进程 OOM
// 用法: node render_scene1.mjs <fps> <duration> <output_dir>
import { mkdir, rm } from 'fs/promises';
import { existsSync } from 'fs';
import { execSync } from 'child_process';

const PUPPETEER_BASE = '/Users/kimmy/.npm/_npx/5dbd0d84e5fd82ec/node_modules/puppeteer';
const { launch } = await import(`${PUPPETEER_BASE}/lib/esm/puppeteer/puppeteer.js`);

const FPS = parseInt(process.argv[2] || '24');
const DURATION = parseFloat(process.argv[3] || '8');
const FRAMES_DIR = process.argv[4] || '/tmp/scene1_frames';
const COMPOSITION_ID = process.argv[5] || 'microled-scene1';
const URL = process.argv[6] || 'http://localhost:18234/scene1.html';
const OUTPUT_MP4 = process.argv[7] || './renders/scene1.mp4';
const TOTAL_FRAMES = Math.round(FPS * DURATION);

console.log(`\n🎬 Render config:`);
console.log(`   URL: ${URL}`);
console.log(`   Composition: ${COMPOSITION_ID}`);
console.log(`   Duration: ${DURATION}s @ ${FPS}fps = ${TOTAL_FRAMES} frames`);
console.log(`   Frames dir: ${FRAMES_DIR}`);
console.log(`   Output: ${OUTPUT_MP4}\n`);

// 清理旧 frames
if (existsSync(FRAMES_DIR)) {
  await rm(FRAMES_DIR, { recursive: true });
}
await mkdir(FRAMES_DIR, { recursive: true });

const browser = await launch({
  headless: 'new',
  args: [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-gpu',
    '--disable-dev-shm-usage',
    '--disable-web-security',
    '--window-size=1920,1080'
  ]
});

const page = await browser.newPage();
await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });

console.log(`📡 Loading ${URL}...`);
await page.goto(URL, { waitUntil: 'networkidle0', timeout: 30000 });

// 等动画/字体准备好
await new Promise(r => setTimeout(r, 2000));

// 检查 timeline 是否存在
const tlExists = await page.evaluate((compId) => {
  return !!(window.__timelines && window.__timelines[compId]);
}, COMPOSITION_ID);

if (!tlExists) {
  console.error(`❌ Timeline "${COMPOSITION_ID}" not found in window.__timelines`);
  await browser.close();
  process.exit(1);
}
console.log(`✅ Timeline "${COMPOSITION_ID}" found\n`);

const startTime = Date.now();
let lastProgress = 0;

for (let i = 0; i < TOTAL_FRAMES; i++) {
  const t = i / FPS;
  
  await page.evaluate(([compId, time]) => {
    const tl = window.__timelines[compId];
    tl.pause();
    tl.seek(time, false);
  }, [COMPOSITION_ID, t]);

  // 微小等待保证 DOM 重绘
  await new Promise(r => setTimeout(r, 30));

  const padded = String(i).padStart(5, '0');
  await page.screenshot({
    path: `${FRAMES_DIR}/frame_${padded}.png`,
    clip: { x: 0, y: 0, width: 1920, height: 1080 }
  });

  const progress = Math.floor(((i + 1) / TOTAL_FRAMES) * 100);
  if (progress >= lastProgress + 10) {
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    const eta = (((Date.now() - startTime) / (i + 1)) * (TOTAL_FRAMES - i - 1) / 1000).toFixed(0);
    console.log(`   ${progress}% — frame ${i+1}/${TOTAL_FRAMES} (${elapsed}s elapsed, ~${eta}s remaining)`);
    lastProgress = progress;
  }
}

await browser.close();

const renderTime = ((Date.now() - startTime) / 1000).toFixed(1);
console.log(`\n✅ All ${TOTAL_FRAMES} frames captured in ${renderTime}s`);

// FFmpeg 合成 MP4
console.log(`\n🎞️  Encoding to MP4 with FFmpeg...`);
const ffmpegCmd = [
  'ffmpeg', '-y',
  '-framerate', String(FPS),
  '-i', `${FRAMES_DIR}/frame_%05d.png`,
  '-c:v', 'libx264',
  '-pix_fmt', 'yuv420p',
  '-crf', '18',
  '-preset', 'medium',
  '-movflags', '+faststart',
  OUTPUT_MP4
].join(' ');

try {
  await mkdir(OUTPUT_MP4.substring(0, OUTPUT_MP4.lastIndexOf('/')), { recursive: true });
  execSync(ffmpegCmd, { stdio: ['ignore', 'pipe', 'pipe'] });
  const stats = execSync(`ls -lh "${OUTPUT_MP4}" | awk '{print $5}'`).toString().trim();
  const duration = execSync(`ffprobe -v error -show_entries format=duration -of csv=p=0 "${OUTPUT_MP4}"`).toString().trim();
  console.log(`✅ Output: ${OUTPUT_MP4} (${stats}, ${parseFloat(duration).toFixed(2)}s)`);
} catch (err) {
  console.error(`❌ FFmpeg failed:`, err.message);
  process.exit(1);
}
