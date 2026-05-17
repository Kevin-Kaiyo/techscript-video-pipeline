// Puppeteer 分批渲染 — 每 N 帧重启 browser，避免内存累积
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
const BATCH_SIZE = parseInt(process.argv[8] || '20');
const TOTAL_FRAMES = Math.round(FPS * DURATION);

console.log(`\n🎬 Render: ${DURATION}s @ ${FPS}fps = ${TOTAL_FRAMES} frames, batch=${BATCH_SIZE}\n`);

if (existsSync(FRAMES_DIR)) await rm(FRAMES_DIR, { recursive: true });
await mkdir(FRAMES_DIR, { recursive: true });

const startTime = Date.now();

async function renderBatch(startFrame, endFrame) {
  const browser = await launch({
    headless: 'new',
    args: [
      '--no-sandbox', '--disable-setuid-sandbox',
      '--disable-gpu', '--disable-dev-shm-usage',
      '--window-size=1920,1080',
      '--memory-pressure-off',
      '--max_old_space_size=512'
    ]
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  await page.goto(URL, { waitUntil: 'networkidle0', timeout: 30000 });
  await new Promise(r => setTimeout(r, 1500));

  for (let i = startFrame; i < endFrame; i++) {
    const t = i / FPS;
    await page.evaluate(([compId, time]) => {
      const tl = window.__timelines[compId];
      tl.pause();
      tl.seek(time, false);
    }, [COMPOSITION_ID, t]);
    await new Promise(r => setTimeout(r, 20));

    const padded = String(i).padStart(5, '0');
    await page.screenshot({
      path: `${FRAMES_DIR}/frame_${padded}.png`,
      clip: { x: 0, y: 0, width: 1920, height: 1080 },
      omitBackground: false
    });
  }

  await page.close();
  await browser.close();
}

// 分批执行
for (let batchStart = 0; batchStart < TOTAL_FRAMES; batchStart += BATCH_SIZE) {
  const batchEnd = Math.min(batchStart + BATCH_SIZE, TOTAL_FRAMES);
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log(`   [${elapsed}s] Batch ${Math.floor(batchStart/BATCH_SIZE)+1}/${Math.ceil(TOTAL_FRAMES/BATCH_SIZE)}: frames ${batchStart}-${batchEnd-1}`);
  
  try {
    await renderBatch(batchStart, batchEnd);
  } catch (err) {
    console.error(`   ⚠️  Batch failed: ${err.message}`);
    console.error(`   Will retry once...`);
    await new Promise(r => setTimeout(r, 2000));
    await renderBatch(batchStart, batchEnd);
  }
  
  // 强制 GC + 等内存回收
  if (global.gc) global.gc();
  await new Promise(r => setTimeout(r, 500));
}

const renderTime = ((Date.now() - startTime) / 1000).toFixed(1);
console.log(`\n✅ All ${TOTAL_FRAMES} frames captured in ${renderTime}s`);

// FFmpeg 合成
console.log(`\n🎞️  Encoding to MP4...`);
const outDir = OUTPUT_MP4.substring(0, OUTPUT_MP4.lastIndexOf('/'));
if (outDir && !existsSync(outDir)) await mkdir(outDir, { recursive: true });

const ffmpegCmd = `ffmpeg -y -framerate ${FPS} -i ${FRAMES_DIR}/frame_%05d.png -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium -movflags +faststart ${OUTPUT_MP4}`;
execSync(ffmpegCmd, { stdio: ['ignore', 'pipe', 'pipe'] });

const stats = execSync(`ls -lh "${OUTPUT_MP4}" | awk '{print $5}'`).toString().trim();
const duration = execSync(`ffprobe -v error -show_entries format=duration -of csv=p=0 "${OUTPUT_MP4}"`).toString().trim();
console.log(`✅ ${OUTPUT_MP4} — ${stats}, ${parseFloat(duration).toFixed(2)}s`);
