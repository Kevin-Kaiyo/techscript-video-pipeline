#!/usr/bin/env node
/**
 * recompose.mjs — 用新 auto_schedule.json 格式重新合成视频
 * Usage: node recompose.mjs <ep>
 */
import { readFileSync, writeFileSync } from 'fs';
import { execSync } from 'child_process';
import { join, resolve } from 'path';
import { fileURLToPath } from 'url';

const EP = process.argv[2];
if (!EP) { console.error('usage: node recompose.mjs <ep>'); process.exit(1); }

const ROOT = resolve(fileURLToPath(import.meta.url), '../../');
const epDir = join(ROOT, 'episodes', EP);
const schedPath = join(epDir, 'audio_schedule.json');
const sched = JSON.parse(readFileSync(schedPath, 'utf8'));

// find silent video
const silentMp4 = join(epDir, 'output', `${EP}_silent.mp4`);
const outMp4 = join(epDir, 'output', `${EP}_full.mp4`);
const duration = sched.total_duration;

// build compose-format schedule
const composeSched = {
  tracks: sched.segments.map(s => ({
    file: s.file.split('/').pop(),
    start_ms: Math.round(s.start * 1000)
  })),
  voice_volume: 1.6
};

const tmpSched = join(epDir, 'audio_schedule_compose.json');
writeFileSync(tmpSched, JSON.stringify(composeSched, null, 2));

const voiceDir = join(epDir, 'audio/voiceover');
const cmd = `node ${join(ROOT, 'pipeline/compose_audio.mjs')} ${silentMp4} ${voiceDir} ${tmpSched} ${outMp4} ${duration}`;
console.log(`🎬 ${EP}: composing ${duration.toFixed(1)}s ...`);
console.log(`   ${cmd}`);
execSync(cmd, { stdio: 'inherit' });
console.log(`✓ ${outMp4}`);
