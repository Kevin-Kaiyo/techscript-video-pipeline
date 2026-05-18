#!/usr/bin/env node
import { execFileSync } from 'child_process';
import { existsSync, readFileSync, readdirSync, accessSync, constants } from 'fs';
import { dirname, join, resolve } from 'path';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ep = process.argv[2];

function fail(message) {
  console.error('ERROR: ' + message);
  process.exitCode = 1;
}

function warn(message) {
  console.warn('WARN: ' + message);
}

function hasCommand(name) {
  try {
    execFileSync('which', [name], { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

if (!ep) {
  console.error('usage: node pipeline/preflight.mjs <episode>');
  process.exit(2);
}

for (const bin of ['ffmpeg', 'ffprobe', 'node', 'python3', 'bc']) {
  if (!hasCommand(bin)) fail('Missing required command: ' + bin);
}

const chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
if (!existsSync(chrome)) fail('Google Chrome not found at ' + chrome);

try {
  require.resolve('ws');
} catch {
  fail('Node dependency ws is missing. Run: npm install');
}

const epDir = join(projectRoot, 'episodes', ep);
const hfDir = join(epDir, 'animations', 'hyperframes');
const indexPath = join(hfDir, 'index.html');
const manimScenePath = join(projectRoot, 'pipeline', 'manim', 'microled_mass_transfer.py');
const manimPython = join(projectRoot, '.venv-manim', 'bin', 'python');
const schedulePath = join(epDir, 'audio_schedule.json');
const audioDir = join(epDir, 'audio', 'voiceover');
const videoConfigPath = join(projectRoot, 'shared', 'brand', 'video.json');

if (!existsSync(epDir)) fail('Episode directory not found: ' + epDir);
const hasHyperFrames = existsSync(indexPath);
const isManimEpisode = ep === 'demo-manim' || existsSync(join(epDir, 'animations', 'manim'));

if (!hasHyperFrames && !isManimEpisode) fail('HyperFrames entry not found: ' + indexPath);
if (isManimEpisode) {
  if (!existsSync(manimScenePath)) fail('Manim scene not found: ' + manimScenePath);
  if (!existsSync(manimPython)) fail('Manim Python not found. Run: python3.11 -m venv .venv-manim && .venv-manim/bin/pip install -r requirements-manim.txt');
}

if (existsSync(videoConfigPath)) {
  const config = JSON.parse(readFileSync(videoConfigPath, 'utf8'));
  if (!config.fps) warn('shared/brand/video.json has no fps; build will fall back to FPS env or 24.');
}

if (hasHyperFrames) {
  const html = readFileSync(indexPath, 'utf8');
  if (!html.match(/data-composition-id="[^"]+"/)) fail('index.html is missing data-composition-id.');
  if (!html.match(/data-duration="[^"]+"/)) fail('index.html is missing data-duration.');
}

if (existsSync(schedulePath)) {
  if (!existsSync(audioDir)) fail('audio_schedule.json exists, but voiceover directory is missing: ' + audioDir);
  const schedule = JSON.parse(readFileSync(schedulePath, 'utf8'));
  const tracks = Array.isArray(schedule.tracks) ? schedule.tracks : [];
  if (tracks.length === 0) warn('audio_schedule.json has no tracks. Output will be silent or invalid.');
  for (const track of tracks) {
    if (!track.file) {
      fail('audio_schedule.json contains a track without file.');
      continue;
    }
    const audioPath = join(audioDir, track.file);
    if (!existsSync(audioPath)) fail('Missing voiceover file referenced by schedule: ' + audioPath);
  }
} else {
  warn('No audio_schedule.json found. build_episode.sh will create silent output only.');
}

try {
  accessSync('/tmp', constants.W_OK);
} catch {
  fail('/tmp is not writable; frame rendering needs a writable temp directory.');
}

if (existsSync(audioDir)) {
  const mp3Count = readdirSync(audioDir).filter((file) => file.endsWith('.mp3')).length;
  if (mp3Count === 0) warn('Voiceover directory exists but contains no mp3 files: ' + audioDir);
}

if (process.exitCode) process.exit(process.exitCode);
console.log('preflight ok: ' + ep);
