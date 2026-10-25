// Builds the parts library that comes with WaughForm 3D (desktop\parts-library.json), from the Fritzing
// parts installed on this computer, so people without Fritzing get the same parts to choose from.
// Run from the "claude code" folder with the desktop app's Electron:
//   desktop\node_modules\electron\dist\electron.exe tools\build-parts-library.js
// It reads each part (core, contrib and user; obsolete parts are left out) with the app's own part reader,
// so every part comes in exactly as "Import pins..." would bring it in: name, description, properties,
// pins with their positions, board size and a small picture.
// The Fritzing parts are © Fritzing contributors, licensed CC BY-SA 3.0: the library keeps that credit and
// licence (https://creativecommons.org/licenses/by-sa/3.0/), and so must anything made from it.
// © 2026 David John Waugh
const {app, BrowserWindow} = require('electron');
const fs = require('fs'), path = require('path');

const ROOTS = [
  path.join(process.env.ProgramFiles || 'C:\\Program Files', 'Fritzing', 'fritzing-parts'),
  path.join(process.env['ProgramFiles(x86)'] || 'C:\\Program Files (x86)', 'Fritzing', 'fritzing-parts'),
  path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Fritzing', 'fritzing-parts'),
];
const FOLDERS = ['core', 'contrib', 'user'];
const OUT = path.join(__dirname, '..', 'desktop', 'parts-library.json');
const PICTURE_PX = 360;// longest side of each part's picture

function listParts() {
  const out = [], seen = new Set();
  for (const root of ROOTS) for (const folder of FOLDERS) {
    let names; try { names = fs.readdirSync(path.join(root, folder)); } catch (e) { continue; }
    for (const n of names) if (/\.fzp$/i.test(n) && !seen.has(n.toLowerCase())) { seen.add(n.toLowerCase()); out.push({root, folder, file: n}); }
  }
  return out;
}
function breadboardSvg(p, fzp) {
  const m = fzp.match(/<breadboardView[^>]*>[\s\S]*?<layers[^>]*image=["']([^"']+)["']/i);
  if (!m || /\.\./.test(m[1])) return null;
  for (const f of [p.folder, 'core', 'contrib', 'user']) {
    try { return fs.readFileSync(path.join(p.root, 'svg', f, m[1]), 'utf8'); } catch (e) {}
  }
  return null;
}

app.whenReady().then(async () => {
  const parts = listParts();
  if (!parts.length) { console.log('No Fritzing parts found. Looked in:\n  ' + ROOTS.join('\n  ')); app.exit(1); return; }
  console.log(parts.length + ' parts to read');
  const win = new BrowserWindow({show: false, width: 1200, height: 900, webPreferences: {sandbox: true}});
  await win.loadFile(path.join(__dirname, '..', 'desktop', 'app.html'));
  for (let i = 0; i < 80 && !(await win.webContents.executeJavaScript('!!(window.WFEnclosure&&WFEnclosure.fritzingData)')); i++) await new Promise(r => setTimeout(r, 250));
  const lib = [], skipped = [];
  const t0 = Date.now();
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i];
    try {
      const fzp = fs.readFileSync(path.join(p.root, p.folder, p.file), 'utf8');
      const svg = breadboardSvg(p, fzp);
      const d = await Promise.race([
        win.webContents.executeJavaScript(`WFEnclosure.fritzingData(${JSON.stringify(fzp)},${JSON.stringify(svg)},${JSON.stringify(p.file)},${PICTURE_PX})`),
        new Promise((_, rej) => setTimeout(() => rej(new Error('timed out')), 20000))]);
      if (!d || d.error) { skipped.push(p.file + ': ' + (d ? d.error : 'unreadable')); continue; }
      // keep only the pin positions the part uses, rounded
      if (d.g) { const pos = {}; for (const c of d.conns) if (c.svgId && d.g.pos[c.svgId]) pos[c.svgId] = d.g.pos[c.svgId].map(v => +v.toFixed(3)); d.g.pos = pos; d.g.w = +d.g.w.toFixed(3); d.g.h = +d.g.h.toFixed(3); }
      for (const c of d.conns) { c.desc = (c.desc || '').replace(/\s+/g, ' ').trim().slice(0, 100); if (!c.desc) delete c.desc; if (!c.svgId) delete c.svgId; }
      lib.push({title: d.title, folder: p.folder, file: p.file, info: d.info, conns: d.conns, g: d.g});
    } catch (e) { skipped.push(p.file + ': ' + (e.message || e)); }
    if ((i + 1) % 100 === 0) console.log('  ' + (i + 1) + ' / ' + parts.length + '  (' + Math.round((Date.now() - t0) / 1000) + ' s)');
  }
  lib.sort((a, b) => a.title.localeCompare(b.title));
  const out = {
    name: 'WaughForm 3D parts library',
    made: new Date().toISOString().slice(0, 10),
    source: 'Fritzing parts library (fritzing-parts: core, contrib, user)',
    credit: 'Part data and pictures © Fritzing contributors, licensed under CC BY-SA 3.0 (https://creativecommons.org/licenses/by-sa/3.0/). Converted for WaughForm 3D; parts made from them must keep this credit and licence.',
    parts: lib,
  };
  fs.writeFileSync(OUT, JSON.stringify(out));
  console.log('Wrote ' + OUT + ': ' + lib.length + ' parts, ' + Math.round(fs.statSync(OUT).size / 1024 / 1024 * 10) / 10 + ' MB, ' + skipped.length + ' skipped, ' + Math.round((Date.now() - t0) / 1000) + ' s');
  if (skipped.length) fs.writeFileSync(OUT.replace(/\.json$/, '-skipped.txt'), skipped.join('\n'));
  app.exit(0);
});
