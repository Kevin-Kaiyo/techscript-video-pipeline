// compose_audio.mjs — 根据 schedule JSON 把多段配音叠加到静音视频
// 用法: node compose_audio.mjs <silent.mp4> <voice_dir> <schedule.json> <out.mp4> <duration_sec>
//
// schedule.json 示例：
// {
//   "tracks": [
//     {"file": "ep01_s01.mp3", "start_ms": 300},
//     {"file": "ep01_s02.mp3", "start_ms": 5500},
//     ...
//   ],
//   "bgm": {"file": "ep01_bgm.mp3", "volume_db": -18, "start_ms": 0, "fade_out_ms": 2000},
//   "voice_volume": 1.6
// }

import { readFileSync } from 'fs';
import { execSync } from 'child_process';

const [SILENT, VOICE_DIR, SCHEDULE_JSON, OUT, DURATION] = process.argv.slice(2);
const sched = JSON.parse(readFileSync(SCHEDULE_JSON, 'utf8'));

const inputs = ['-i', SILENT];
const filters = [];
const mixLabels = [];

sched.tracks.forEach((t, i) => {
  const idx = i + 1;
  inputs.push('-i', `${VOICE_DIR}/${t.file}`);
  const delay = t.start_ms ?? 0;
  filters.push(`[${idx}:a]adelay=${delay}|${delay}[v${idx}]`);
  mixLabels.push(`[v${idx}]`);
});

const voiceVol = sched.voice_volume ?? 1.5;
const mixCount = mixLabels.length;
filters.push(`${mixLabels.join('')}amix=inputs=${mixCount}:duration=longest:normalize=0,volume=${voiceVol}[voicemix]`);

// BGM 可选
let finalLabel = 'voicemix';
if (sched.bgm) {
  const bgmIdx = sched.tracks.length + 1;
  inputs.push('-i', `${VOICE_DIR}/../bgm/${sched.bgm.file}`);
  const bgmDelay = sched.bgm.start_ms ?? 0;
  const bgmVol = sched.bgm.volume_db ?? -18;
  const fadeOutMs = sched.bgm.fade_out_ms ?? 1500;
  const fadeStart = parseFloat(DURATION) - fadeOutMs/1000;
  filters.push(`[${bgmIdx}:a]adelay=${bgmDelay}|${bgmDelay},volume=${bgmVol}dB,afade=t=out:st=${fadeStart}:d=${fadeOutMs/1000}[bgm]`);
  filters.push(`[voicemix][bgm]amix=inputs=2:duration=longest:normalize=0[mixed]`);
  finalLabel = 'mixed';
}

filters.push(`[${finalLabel}]aformat=channel_layouts=stereo[aout]`);

const cmd = [
  'ffmpeg', '-y',
  ...inputs,
  '-filter_complex', `"${filters.join(';')}"`,
  '-map', '0:v', '-map', '"[aout]"',
  '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
  '-ar', '44100', '-ac', '2',
  '-t', DURATION,
  `"${OUT}"`
].join(' ');

console.log('FFmpeg cmd:');
console.log(cmd);
console.log('---');
execSync(cmd, { stdio: 'inherit' });
console.log(`\n✅ ${OUT}`);
