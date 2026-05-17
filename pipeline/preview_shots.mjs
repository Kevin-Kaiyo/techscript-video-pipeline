// 快速预览：在指定时间点截图
import { spawn } from 'child_process';
import { WebSocket } from 'ws';
import { writeFileSync } from 'fs';

const URL = process.argv[2];
const COMP_ID = process.argv[3];
const TIMES = process.argv[4].split(',').map(parseFloat);
const OUT_PREFIX = process.argv[5];

const chromeBin = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const chrome = spawn(chromeBin, [
  '--headless=new', '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage',
  '--window-size=1920,1080',
  '--remote-debugging-port=19222',
  '--user-data-dir=/tmp/chrome-render-profile',
  URL
], { stdio: 'ignore' });
// 等 CDP 端口 ready
async function waitForCDP(timeoutMs = 15000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const r = await fetch('http://127.0.0.1:19222/json');
      if (r.ok) return await r.json();
    } catch {}
    await new Promise(r => setTimeout(r, 300));
  }
  throw new Error('CDP did not start within ' + timeoutMs + 'ms');
}
const targets = await waitForCDP();
const pt = targets.find(t => t.type === 'page');
const ws = new WebSocket(pt.webSocketDebuggerUrl);
let msgId = 0; const pending = new Map();
ws.on('message', d => { const m = JSON.parse(d); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
await new Promise(r => ws.on('open', r));
const send = (method, params={}) => new Promise((res, rej) => {
  const id = ++msgId;
  pending.set(id, m => m.error ? rej(new Error(m.error.message)) : res(m.result));
  ws.send(JSON.stringify({ id, method, params }));
});
await new Promise(r => setTimeout(r, 1500));

for (const t of TIMES) {
  await send('Runtime.evaluate', {
    expression: `(()=>{const tl=window.__timelines['${COMP_ID}'];tl.pause();tl.seek(${t},false);return 1;})()`,
    returnByValue: true
  });
  await send('Runtime.evaluate', {
    expression: `new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r(1))))`,
    awaitPromise: true, returnByValue: true
  });
  const shot = await send('Page.captureScreenshot', {
    format: 'jpeg', quality: 95,
    clip: { x: 0, y: 0, width: 1920, height: 1080, scale: 1 }
  });
  const f = `${OUT_PREFIX}_t${t.toFixed(1)}.jpg`;
  writeFileSync(f, Buffer.from(shot.data, 'base64'));
  console.log(`✓ ${f}`);
}

ws.close(); chrome.kill();
process.exit(0);
