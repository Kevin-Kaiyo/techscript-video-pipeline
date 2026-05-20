#!/usr/bin/env node
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const projectRoot = join(dirname(fileURLToPath(import.meta.url)), '..');

const renderers = new Map([
  ['hyperframes', 'HyperFrames'],
  ['manim', 'Manim'],
  ['mixed', 'Mixed'],
]);

const topicFamilies = new Map([
  ['principle', { renderer: 'manim', label: 'Technology principle' }],
  ['process', { renderer: 'manim', label: 'Process sequence' }],
  ['equipment', { renderer: 'hyperframes', label: 'Equipment/material map' }],
  ['industry', { renderer: 'hyperframes', label: 'Industry/value chain' }],
  ['data', { renderer: 'hyperframes', label: 'Market/data story' }],
  ['system', { renderer: 'mixed', label: 'System architecture' }],
]);

function usage() {
  console.error('Usage: node pipeline/scaffold_episode.mjs <episode-id> [family] [renderer]');
  console.error('Families: principle, process, equipment, industry, data, system');
  console.error('Renderers: hyperframes, manim, mixed');
  process.exit(1);
}

const [ep, rawFamily = 'principle', rawRenderer] = process.argv.slice(2);
if (!ep || ep.includes('/') || ep.includes('..')) usage();

const family = topicFamilies.get(rawFamily);
if (!family) usage();

const rendererKey = rawRenderer || family.renderer;
const renderer = renderers.get(rendererKey);
if (!renderer) usage();

const epDir = join(projectRoot, 'episodes', ep);
if (existsSync(epDir)) {
  console.error('Episode already exists: episodes/' + ep);
  process.exit(1);
}

mkdirSync(join(epDir, 'audio', 'voiceover'), { recursive: true });
mkdirSync(join(epDir, 'output'), { recursive: true });

if (rendererKey === 'hyperframes' || rendererKey === 'mixed') {
  mkdirSync(join(epDir, 'animations', 'hyperframes'), { recursive: true });
  writeFileSync(join(epDir, 'animations', 'hyperframes', 'index.html'), hyperframesTemplate(ep), 'utf8');
}

writeFileSync(join(epDir, 'script.md'), scriptTemplate(ep, family.label, renderer), 'utf8');
writeFileSync(join(epDir, 'README.md'), readmeTemplate(ep, family.label, renderer), 'utf8');

console.log('Created episodes/' + ep);
console.log('Family: ' + family.label);
console.log('Renderer: ' + renderer);

function scriptTemplate(epId, familyLabel, rendererName) {
  return [
    '# ' + epId,
    '',
    '| Field | Value |',
    '| --- | --- |',
    '| Topic family | ' + familyLabel + ' |',
    '| Renderer | ' + rendererName + ' |',
    '| Target duration | 30-60s |',
    '| Core question | TODO |',
    '| Key points | TODO |',
    '',
    '## s01',
    'TODO opening hook.',
    '',
    '## s02',
    'TODO context.',
    '',
    '## s03',
    'TODO core explanation.',
    '',
    '## s04',
    'TODO evidence, process step, or comparison.',
    '',
    '## s05',
    'TODO application, implication, or conclusion.',
    '',
  ].join('\n');
}

function readmeTemplate(epId, familyLabel, rendererName) {
  const buildCommand = rendererName === 'Manim' ? 'make manim-build EP=' + epId : 'make build EP=' + epId;
  return [
    '# ' + epId,
    '',
    '- Topic family: ' + familyLabel,
    '- Renderer: ' + rendererName,
    '',
    '## Build',
    '',
    '```bash',
    'make tts EP=' + epId,
    'make schedule EP=' + epId,
    buildCommand,
    '```',
    '',
  ].join('\n');
}

function hyperframesTemplate(epId) {
  return [
    '<!doctype html>',
    '<html lang="zh-CN">',
    '<head>',
    '  <meta charset="utf-8" />',
    '  <meta name="viewport" content="width=device-width, initial-scale=1" />',
    '  <title>' + epId + '</title>',
    '  <style>',
    '    html, body { margin: 0; width: 100%; height: 100%; background: #07111f; color: #f7fbff; font-family: -apple-system, BlinkMacSystemFont, Inter, sans-serif; }',
    '    #stage { width: 1920px; height: 1080px; position: relative; overflow: hidden; background: #07111f; }',
    '    .title { position: absolute; left: 120px; top: 120px; font-size: 72px; font-weight: 800; }',
    '    .subtitle { position: absolute; left: 120px; top: 230px; font-size: 34px; color: #9bdcff; }',
    '  </style>',
    '</head>',
    '<body>',
    '  <div id="stage" data-composition-id="' + epId + '" data-start="0" data-duration="40" data-width="1920" data-height="1080">',
    '    <div class="title">TODO: ' + epId + '</div>',
    '    <div class="subtitle">Replace this scaffold with the real information graphic.</div>',
    '  </div>',
    '  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>',
    '  <script>',
    '    window.__timelines = window.__timelines || {};',
    '    const tl = gsap.timeline({ paused: true });',
    "    tl.from('.title', { opacity: 0, y: 24, duration: 1 });",
    "    tl.from('.subtitle', { opacity: 0, y: 18, duration: 0.8 }, 0.4);",
    "    window.__timelines['" + epId + "'] = tl;",
    '  </script>',
    '</body>',
    '</html>',
    '',
  ].join('\n');
}
