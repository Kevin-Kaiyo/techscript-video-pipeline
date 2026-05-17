// 断点续传渲染 — 检查已存在的帧，跳过已完成的；每次最多渲染 N 帧后退出
import { spawn, execSync } from 'child_process';
import { mkdir, rm } from 'fs/promises';
import { existsSync, writeFileSync, readdirSync } from 'fs';
import { WebSocket } from 'ws';

const FPS = parseInt(process.argv[2] || '24');
const DURATION = parseFloat(process.argv[3] || '8');
const FRAMES_DIR = process.argv[4] || '/tmp/scene1_frames';
const COMPOSITION_ID = process.argv[5] || 'microled-scene1';
const URL = process.argv[6] || 'http://localhost:18234/scene1.html';
const MAX_FRAMES_THIS_RUN = parseInt(process.argv[7] || '80');
const TOTAL_FRAMES = Math.round(FPS * DURATION);
const CDP_PORT = 19222;

if (!existsSync(FRAMES_DIR)) await mkdir(FRAMES_DIR, { recursive: true });

// 找已完成的帧
const existing = new Set(readdirSync(FRAMES_DIR).filter(f => f.endsWith('.jpg')).map(f => parseInt(f.match(/\d+/)[0])));
const remaining = [];
for (let i = 0; i < TOTAL_FRAMES; i++) {
  if (!existing.has(i)) remaining.push(i);
}

console.log(`\n📊 Progress: ${existing.size}/${TOTAL_FRAMES} done, ${remaining.length} remaining`);

if (remaining.length === 0) {
  console.log('✅ All frames already rendered!');
  process.exit(0);
}

const toRender = remaining.slice(0, MAX_FRAMES_THIS_RUN);
console.log(`🎬 This run: ${toRender.length} frames (${toRender[0]}..${toRender[toRender.length-1]})\n`);

const chromeBin = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const chrome = spawn(chromeBin, [
  '--headless=new', '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage',
  '--window-size=1920,1080',
  `--remote-debugging-port=${CDP_PORT}`,
  '--user-data-dir=/tmp/chrome-render-profile',
  URL
], { stdio: 'ignore' });

async function waitForCDP(port, timeoutMs = 15000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const r = await fetch(`http://127.0.0.1:${port}/json`);
      if (r.ok) return await r.json();
    } catch {}
    await new Promise(r => setTimeout(r, 300));
  }
  throw new Error('CDP did not start within ' + timeoutMs + 'ms');
}
const targets = await waitForCDP(CDP_PORT);
const pageTarget = targets.find(t => t.type === 'page');
const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);
let msgId = 0;
const pending = new Map();
ws.on('message', (data) => {
  const msg = JSON.parse(data.toString());
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
});
await new Promise(r => ws.on('open', r));

async function send(method, params = {}) {
  const id = ++msgId;
  return new Promise((resolve, reject) => {
    pending.set(id, (msg) => msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result));
    ws.send(JSON.stringify({ id, method, params }));
  });
}

await new Promise(r => setTimeout(r, 1500));

const startTime = Date.now();
let count = 0;
for (const i of toRender) {
  const t = i / FPS;
  // 1. seek with timeout safeguard
  await Promise.race([
    send('Runtime.evaluate', {
      expression: `(()=>{const tl=window.__timelines['${COMPOSITION_ID}'];tl.pause();tl.time(${t});tl.pause();return 1;})()`,
      returnByValue: true
    }),
    new Promise((_, rej) => setTimeout(() => rej(new Error('seek timeout')), 3000))
  ]).catch(e => console.error(`   frame ${i} seek error: ${e.message}`));
  // 2. wait 2x requestAnimationFrame to guarantee DOM/GSAP fully reflowed (fixes flicker)
  await Promise.race([
    send('Runtime.evaluate', {
      expression: `new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r(1))))`,
      awaitPromise: true,
      returnByValue: true
    }),
    new Promise((_, rej) => setTimeout(() => rej(new Error('raf timeout')), 2000))
  ]).catch(e => console.error(`   frame ${i} raf error: ${e.message}`));
  // 3. capture with timeout
  let shot;
  try {
    shot = await Promise.race([
      send('Page.captureScreenshot', {
        format: 'jpeg', quality: 95, captureBeyondViewport: false,
        clip: { x: 0, y: 0, width: 1920, height: 1080, scale: 1 }
      }),
      new Promise((_, rej) => setTimeout(() => rej(new Error('capture timeout')), 5000))
    ]);
  } catch (e) {
    console.error(`   frame ${i} CAPTURE FAIL: ${e.message} — aborting batch, will resume next run`);
    break;
  }
  writeFileSync(`${FRAMES_DIR}/frame_${String(i).padStart(5, '0')}.jpg`, Buffer.from(shot.data, 'base64'));
  shot.data = null;
  count++;
  if (count % 10 === 0) {
    const el = ((Date.now() - startTime) / 1000).toFixed(1);
    console.log(`   ${count}/${toRender.length} (${el}s)`);
    if (global.gc) global.gc();
  }
}

ws.close();
chrome.kill();
console.log(`✅ Rendered ${count} frames in ${((Date.now()-startTime)/1000).toFixed(1)}s`);
const remainingAfter = TOTAL_FRAMES - (existing.size + count);
if (remainingAfter > 0) {
  console.log(`⏭️  ${remainingAfter} frames remain — run again`);
  process.exit(2);  // exit code 2 = more work
} else {
  console.log(`🎉 All frames complete!`);
  process.exit(0);
}
