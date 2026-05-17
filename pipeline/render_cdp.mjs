// CDP 单 Chrome 渲染 — 启动一次 Chrome with --remote-debugging-port，逐帧用 CDP 控制
import { spawn, execSync } from 'child_process';
import { mkdir, rm } from 'fs/promises';
import { existsSync, writeFileSync } from 'fs';
import { WebSocket } from 'ws';

const FPS = parseInt(process.argv[2] || '24');
const DURATION = parseFloat(process.argv[3] || '8');
const FRAMES_DIR = process.argv[4] || '/tmp/scene1_frames';
const COMPOSITION_ID = process.argv[5] || 'microled-scene1';
const URL = process.argv[6] || 'http://localhost:18234/scene1.html';
const OUTPUT_MP4 = process.argv[7] || './renders/scene1.mp4';
const TOTAL_FRAMES = Math.round(FPS * DURATION);
const CDP_PORT = 19222;

console.log(`\n🎬 ${DURATION}s @ ${FPS}fps = ${TOTAL_FRAMES} frames`);

if (existsSync(FRAMES_DIR)) await rm(FRAMES_DIR, { recursive: true });
await mkdir(FRAMES_DIR, { recursive: true });

// 启动 Chrome
const chromeBin = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
console.log(`🚀 Starting Chrome on port ${CDP_PORT}...`);
const chrome = spawn(chromeBin, [
  '--headless=new',
  '--disable-gpu',
  '--no-sandbox',
  '--disable-dev-shm-usage',
  '--window-size=1920,1080',
  `--remote-debugging-port=${CDP_PORT}`,
  '--user-data-dir=/tmp/chrome-render-profile',
  URL
], { detached: false, stdio: 'ignore' });

// 等 CDP ready
await new Promise(r => setTimeout(r, 2500));

// 拉取 page target
const targets = await fetch(`http://localhost:${CDP_PORT}/json`).then(r => r.json());
const pageTarget = targets.find(t => t.type === 'page');
if (!pageTarget) {
  console.error('❌ No page target');
  chrome.kill();
  process.exit(1);
}
console.log(`✅ CDP attached: ${pageTarget.webSocketDebuggerUrl.slice(0, 60)}...`);

const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);
let msgId = 0;
const pending = new Map();

ws.on('message', (data) => {
  const msg = JSON.parse(data.toString());
  if (msg.id && pending.has(msg.id)) {
    pending.get(msg.id)(msg);
    pending.delete(msg.id);
  }
});

await new Promise((resolve) => ws.on('open', resolve));

async function send(method, params = {}) {
  const id = ++msgId;
  return new Promise((resolve, reject) => {
    pending.set(id, (msg) => {
      if (msg.error) reject(new Error(msg.error.message));
      else resolve(msg.result);
    });
    ws.send(JSON.stringify({ id, method, params }));
  });
}

// 等 GSAP/字体加载
await new Promise(r => setTimeout(r, 1500));

// 验证 timeline 存在
const check = await send('Runtime.evaluate', {
  expression: `!!(window.__timelines && window.__timelines['${COMPOSITION_ID}'])`,
  returnByValue: true
});
if (!check.result.value) {
  console.error(`❌ Timeline "${COMPOSITION_ID}" not found`);
  ws.close(); chrome.kill();
  process.exit(1);
}
console.log(`✅ Timeline found, starting render...\n`);

const startTime = Date.now();
let lastProgress = 0;

for (let i = 0; i < TOTAL_FRAMES; i++) {
  const t = i / FPS;
  
  await send('Runtime.evaluate', {
    expression: `(() => { const tl = window.__timelines['${COMPOSITION_ID}']; tl.pause(); tl.seek(${t}, false); return true; })()`,
    returnByValue: true
  });

  // 等下一帧渲染
  await new Promise(r => setTimeout(r, 25));

  const shot = await send('Page.captureScreenshot', {
    format: 'jpeg',
    quality: 92,
    captureBeyondViewport: false,
    clip: { x: 0, y: 0, width: 1920, height: 1080, scale: 1 }
  });

  const padded = String(i).padStart(5, '0');
  // Decode + write + explicitly null out
  const buf = Buffer.from(shot.data, 'base64');
  writeFileSync(`${FRAMES_DIR}/frame_${padded}.jpg`, buf);
  shot.data = null;

  // Periodic GC hint
  if (i % 8 === 7 && global.gc) global.gc();

  const progress = Math.floor(((i + 1) / TOTAL_FRAMES) * 100);
  if (progress >= lastProgress + 10) {
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    const eta = (((Date.now() - startTime) / (i + 1)) * (TOTAL_FRAMES - i - 1) / 1000).toFixed(0);
    console.log(`   ${progress}% — ${i+1}/${TOTAL_FRAMES} (${elapsed}s, ~${eta}s left)`);
    lastProgress = progress;
  }
}

const renderTime = ((Date.now() - startTime) / 1000).toFixed(1);
console.log(`\n✅ ${TOTAL_FRAMES} frames in ${renderTime}s (${(TOTAL_FRAMES/renderTime).toFixed(1)} fps)`);

ws.close();
chrome.kill();
await new Promise(r => setTimeout(r, 500));

// FFmpeg 合成
console.log(`\n🎞️  Encoding MP4...`);
const outDir = OUTPUT_MP4.substring(0, OUTPUT_MP4.lastIndexOf('/'));
if (outDir && !existsSync(outDir)) await mkdir(outDir, { recursive: true });

execSync(`ffmpeg -y -framerate ${FPS} -i ${FRAMES_DIR}/frame_%05d.jpg -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium -movflags +faststart ${OUTPUT_MP4}`, { stdio: ['ignore', 'pipe', 'pipe'] });

const stats = execSync(`ls -lh "${OUTPUT_MP4}" | awk '{print $5}'`).toString().trim();
const dur = execSync(`ffprobe -v error -show_entries format=duration -of csv=p=0 "${OUTPUT_MP4}"`).toString().trim();
console.log(`✅ ${OUTPUT_MP4} — ${stats}, ${parseFloat(dur).toFixed(2)}s`);

process.exit(0);
