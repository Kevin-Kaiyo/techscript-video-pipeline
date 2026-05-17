#!/usr/bin/env node
/**
 * auto_schedule.mjs — ffprobe 测段长 → 写 audio_schedule.json
 * Usage: node auto_schedule.mjs <ep_dir>
 */
import { execFileSync } from 'child_process';
import { readFileSync, writeFileSync, readdirSync } from 'fs';
import { join } from 'path';

const epDir = process.argv[2];
if (!epDir) { console.error('usage: node auto_schedule.mjs <ep_dir>'); process.exit(1); }

const epName = epDir.split('/').pop();
const audioDir = join(epDir, 'audio/voiceover');
const outPath = join(epDir, 'audio_schedule.json');

// find all segments sorted
const files = readdirSync(audioDir)
  .filter(f => f.match(/^[^_]+_s\d+\.mp3$/))
  .sort((a, b) => {
    const na = parseInt(a.match(/s(\d+)/)[1]);
    const nb = parseInt(b.match(/s(\d+)/)[1]);
    return na - nb;
  });

console.log(`📐 ${epName}: ${files.length} segments`);

const GAP = 0.3; // gap between segments (s)
let cursor = 0;
const schedule = { tracks: [] };

for (const f of files) {
  const fullPath = join(audioDir, f);
  const dur = parseFloat(
    execFileSync('ffprobe', ['-v','error','-show_entries','format=duration','-of','csv=p=0', fullPath]).toString().trim()
  );
  const sid = f.match(/s(\d+)/)[1];
  const entry = { id: `s${sid}`, file: f, start_ms: Math.round(cursor * 1000), duration_s: parseFloat(dur.toFixed(3)) };
  schedule.tracks.push(entry);
  console.log(`  s${sid}: start=${cursor.toFixed(3)}s dur=${dur.toFixed(2)}s`);
  cursor += dur + GAP;
}

schedule.total_duration = parseFloat((cursor - GAP).toFixed(3));
console.log(`  → total: ${schedule.total_duration}s`);
writeFileSync(outPath, JSON.stringify(schedule, null, 2));
console.log(`✓ wrote ${outPath}`);
