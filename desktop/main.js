// WaughForm 3D desktop app: opens the WaughForm 3D page in its own window. Works offline; the only
// internet use is the optional part look-up (AI key and photo downloads, only when asked).
// © 2026 David John Waugh
const {app, BrowserWindow, Menu, dialog, shell, ipcMain, net} = require('electron');
const path = require('path');

// Download a product photo the part look-up found. Web pages can't read pictures from other sites
// (browser security), so the app does it here - pictures only, size-limited, nothing else.
const IMAGE_TYPES = /^image\/(png|jpe?g|webp|gif)$/i;
ipcMain.handle('fetch-image', async (e, url) => {
  if (typeof url !== 'string' || !/^https?:\/\//i.test(url) || url.length > 2000) throw new Error('not a web address');
  const ctrl = new AbortController(), timer = setTimeout(() => ctrl.abort(), 20000);
  try {
    const r = await net.fetch(url, {signal: ctrl.signal, headers: {Accept: 'image/*'}});
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const type = (r.headers.get('content-type') || '').split(';')[0].trim();
    if (!IMAGE_TYPES.test(type)) throw new Error('not a picture');
    const buf = Buffer.from(await r.arrayBuffer());
    if (buf.length > 12e6) throw new Error('picture too big');
    return {mime: type.toLowerCase(), b64: buf.toString('base64')};
  } finally { clearTimeout(timer); }
});

// Download a PDF datasheet the look-up used, so its dimension drawing can be read. PDFs only, size-limited.
ipcMain.handle('fetch-pdf', async (e, url) => {
  if (typeof url !== 'string' || !/^https?:\/\//i.test(url) || url.length > 2000) throw new Error('not a web address');
  const ctrl = new AbortController(), timer = setTimeout(() => ctrl.abort(), 30000);
  try {
    const r = await net.fetch(url, {signal: ctrl.signal, headers: {Accept: 'application/pdf'}});
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const type = (r.headers.get('content-type') || '').split(';')[0].trim().toLowerCase();
    const buf = Buffer.from(await r.arrayBuffer());
    if (type !== 'application/pdf' && buf.subarray(0, 5).toString('latin1') !== '%PDF-') throw new Error('not a PDF');
    if (buf.length > 15e6) throw new Error('PDF too big');
    return {mime: 'application/pdf', b64: buf.toString('base64')};
  } finally { clearTimeout(timer); }
});

// Fritzing parts installed on this computer (read only): a list of their titles, then one part's
// description (.fzp) and its breadboard picture (.svg). Only files inside the Fritzing parts folders.
const fs = require('fs');
const FRITZING_ROOTS = [
  path.join(process.env.ProgramFiles || 'C:\\Program Files', 'Fritzing', 'fritzing-parts'),
  path.join(process.env['ProgramFiles(x86)'] || 'C:\\Program Files (x86)', 'Fritzing', 'fritzing-parts'),
  path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Fritzing', 'fritzing-parts'),
  path.join(app.getPath('documents'), 'Fritzing', 'parts'),
];
let fritzingParts = null;
async function scanFritzing() {
  if (fritzingParts) return fritzingParts;
  const out = [];
  if (process.env.WF_NO_FRITZING) return (fritzingParts = out);// for testing: behave as if Fritzing isn't installed
  for (const root of FRITZING_ROOTS) {
    for (const folder of ['core', 'contrib', 'user', 'obsolete']) {
      const dir = path.join(root, folder);
      let names; try { names = await fs.promises.readdir(dir); } catch (e) { continue; }
      for (const n of names) {
        if (!/\.fzp$/i.test(n)) continue;
        try {
          const text = await fs.promises.readFile(path.join(dir, n), 'utf8');
          const clean = s => (s || '').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&amp;/g, '&')
            .replace(/<(style|script)[\s\S]*?<\/\1>/gi, ' ').replace(/<[^>]+>/g, ' ').replace(/^\s*p,\s*li\s*\{[^}]*\}/, '').replace(/\s+/g, ' ').trim();
          const m = text.match(/<title>([\s\S]*?)<\/title>/i), d = text.match(/<description>([\s\S]*?)<\/description>/i), f = text.match(/<property\s+name=["']family["'][^>]*>([\s\S]*?)<\/property>/i);
          const tags = [...text.matchAll(/<tag>([\s\S]*?)<\/tag>/gi)].map(t => clean(t[1])).filter(Boolean);
          out.push({root, folder, file: n, title: clean(m ? m[1] : n), family: clean(f && f[1]), tags, desc: clean(d && d[1]).slice(0, 300)});
        } catch (e) {}
      }
    }
  }
  return (fritzingParts = out);
}
// The parts library that comes with the app (made from the Fritzing parts by tools\build-parts-library.js),
// used when Fritzing isn't installed here. Read once, when first needed.
let library = null;
function partsLibrary() {
  if (library) return library;
  try { library = JSON.parse(fs.readFileSync(path.join(__dirname, 'parts-library.json'), 'utf8')).parts || []; }
  catch (e) { library = []; }
  return library;
}
const useLibrary = async () => !(await scanFritzing()).length;
// The list to search: name, kind (family), tags and the start of the description of every part.
ipcMain.handle('fritzing-list', async () => (await useLibrary())
  ? partsLibrary().map((p, id) => ({id, title: p.title, folder: p.folder, library: true, family: p.info.family || '', tags: p.info.tags || [], desc: (p.info.description || '').slice(0, 300)}))
  : (await scanFritzing()).filter(p => p.folder !== 'obsolete').map(p => ({...p, id: fritzingParts.indexOf(p)})).map(p => ({id: p.id, title: p.title, folder: p.folder, family: p.family, tags: p.tags, desc: p.desc})));
ipcMain.handle('fritzing-load', async (e, id) => {
  if (await useLibrary()) {
    const d = partsLibrary()[id];
    if (!d) throw new Error('no such part');
    return {data: {title: d.title, conns: d.conns, info: d.info, g: d.g, file: d.file}};
  }
  const p = (await scanFritzing())[id];
  if (!p) throw new Error('no such part');
  const fzp = await fs.promises.readFile(path.join(p.root, p.folder, p.file), 'utf8');
  const m = fzp.match(/<breadboardView[^>]*>[\s\S]*?<layers[^>]*image=["']([^"']+)["']/i);
  let svg = null;
  if (m && !/\.\./.test(m[1])) {
    const file = path.join(p.root, 'svg', p.folder, m[1]);
    if (file.startsWith(path.join(p.root, 'svg'))) { try { svg = await fs.promises.readFile(file, 'utf8'); } catch (err) {} }
  }
  return {title: p.title, file: p.file, fzp, svg};
});

// Download the text of a web page the look-up used, so the page can pick out its product photo
// (shops and makers label it for link previews). Web pages only, size-limited; nothing is run.
ipcMain.handle('fetch-page', async (e, url) => {
  if (typeof url !== 'string' || !/^https?:\/\//i.test(url) || url.length > 2000) throw new Error('not a web address');
  const ctrl = new AbortController(), timer = setTimeout(() => ctrl.abort(), 15000);
  try {
    const r = await net.fetch(url, {signal: ctrl.signal, headers: {Accept: 'text/html,application/xhtml+xml'}});
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const type = (r.headers.get('content-type') || '').split(';')[0].trim().toLowerCase();
    if (type !== 'text/html' && type !== 'application/xhtml+xml') throw new Error('not a web page');
    const text = await r.text();
    return {url: r.url || url, html: text.slice(0, 3e6)};
  } finally { clearTimeout(timer); }
});

// Check an ESPHome YAML file with the ESPHome on this computer (ESPHome Device Builder's own copy, or one on
// the PATH), the same check as Validate in ESPHome. The file goes in a temporary folder with stand-in secrets;
// nothing is compiled or flashed, and the user's own ESPHome folder is not touched.
const {execFile} = require('child_process');
function findEsphome() {
  const local = process.env.LOCALAPPDATA || '';
  // the ESPHome Device Builder's own copy (newer installs keep it in io.esphome.builder), else one on the PATH
  for (const dir of ['io.esphome.builder', 'ESPHome Device Builder']) {
    const py = path.join(local, dir, 'python', 'python.exe');
    if (fs.existsSync(py)) return {cmd: py, args: ['-m', 'esphome']};
  }
  return {cmd: 'esphome', args: []};
}
// ---- Send a device file straight to ESPHome Device Builder: it lists every .yaml in its devices folder
// (%USERPROFILE%\esphome), so the file is saved there and the dashboard opened. An existing file is only
// replaced when the user says so.
const ESPHOME_URL = 'http://127.0.0.1:6052';
function esphomeFolder() {
  if (process.env.WF_ESPHOME_DIR) return process.env.WF_ESPHOME_DIR;// for testing
  const d = path.join(require('os').homedir(), 'esphome');
  return fs.existsSync(d) ? d : null;
}
ipcMain.handle('app-version', () => app.getVersion());
ipcMain.handle('esphome-send', async (e, yaml, slug, overwrite) => {
  if (typeof yaml !== 'string' || yaml.length > 500000) throw new Error('no YAML');
  const dir = esphomeFolder();
  if (!dir) return {found: false};
  const file = path.join(dir, String(slug || 'device').replace(/[^a-z0-9-]/gi, '-').slice(0, 40) + '.yaml');
  if (fs.existsSync(file) && !overwrite) return {found: true, exists: true, file};
  fs.writeFileSync(file, yaml, 'utf8');
  // does ESPHome have the Wi-Fi secrets the file uses?
  let secrets = '';
  try { secrets = fs.readFileSync(path.join(dir, 'secrets.yaml'), 'utf8'); } catch (err) {}
  const secretsOk = /^\s*wifi_ssid\s*:/m.test(secrets) && /^\s*wifi_password\s*:/m.test(secrets);
  // open the dashboard: in the browser if ESPHome is running, else start ESPHome Device Builder (it opens it)
  let opened = false;
  if (!process.env.WF_NO_OPEN) {
    let running = false;
    try { const ctrl = new AbortController(), t = setTimeout(() => ctrl.abort(), 1500); running = (await net.fetch(ESPHOME_URL + '/', {signal: ctrl.signal})).ok; clearTimeout(t); } catch (err) {}
    if (running) { await shell.openExternal(ESPHOME_URL); opened = 'dashboard'; }
    else {
      const exe = path.join(process.env.LOCALAPPDATA || '', 'ESPHome Device Builder', 'esphome-desktop.exe');
      if (fs.existsSync(exe)) { require('child_process').spawn(exe, [], {detached: true, stdio: 'ignore'}).unref(); opened = 'started'; }
    }
  }
  return {found: true, file, secretsOk, opened};
});
ipcMain.handle('esphome-check', async (e, yaml, name) => {
  if (typeof yaml !== 'string' || yaml.length > 500000) throw new Error('no YAML');
  const dir = path.join(app.getPath('temp'), 'waughform-esphome');
  fs.mkdirSync(dir, {recursive: true});
  const file = path.join(dir, String(name || 'device').replace(/[^a-z0-9-]/gi, '-').slice(0, 40) + '.yaml');
  fs.writeFileSync(file, yaml, 'utf8');
  fs.writeFileSync(path.join(dir, 'secrets.yaml'), 'wifi_ssid: "check"\nwifi_password: "checking123"\n', 'utf8');
  const {cmd, args} = findEsphome();
  return await new Promise(resolve => {
    execFile(cmd, [...args, 'config', file], {cwd: dir, timeout: 180000, windowsHide: true, maxBuffer: 8e6}, (err, stdout, stderr) => {
      if (err && err.code === 'ENOENT') return resolve({found: false, ok: false, out: ''});
      const out = (String(stdout) + '\n' + String(stderr)).replace(/\x1b\[[0-9;]*m/g, '');
      resolve({found: true, ok: !err, out: out.slice(-20000)});
    });
  });
});

// Draw in standard sRGB colour. Without this, HDR / wide-colour displays show the 3D view washed out.
app.commandLine.appendSwitch('force-color-profile', 'srgb');

function createWindow() {
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 900,
    minHeight: 600,
    title: 'WaughForm 3D',
    icon: path.join(__dirname, 'icon.ico'),
    backgroundColor: '#ececec',
    show: false,
    webPreferences: {contextIsolation: true, sandbox: true, preload: path.join(__dirname, 'preload.js')},
  });
  Menu.setApplicationMenu(null); // the app has its own toolbar
  win.loadFile(path.join(__dirname, 'app.html'));
  win.once('ready-to-show', () => { win.maximize(); win.show(); });

  // Stay inside the app: no pop-up windows or navigating away. Web links the app opens on purpose
  // (searching for a part's drawing, getting an AI key) go to the normal web browser instead.
  win.webContents.setWindowOpenHandler(({url}) => {
    if (/^https:\/\//i.test(url)) shell.openExternal(url);
    return {action: 'deny'};
  });
  win.webContents.on('will-navigate', e => e.preventDefault());

  // Right-click menu for text: Cut / Copy / Paste / Select All (Electron has none by default).
  win.webContents.on('context-menu', (e, p) => {
    const items = [];
    if (p.isEditable) items.push({role: 'cut', enabled: p.editFlags.canCut}, {role: 'copy', enabled: p.editFlags.canCopy},
      {role: 'paste', enabled: p.editFlags.canPaste}, {type: 'separator'}, {role: 'selectAll'});
    else if (p.selectionText && p.selectionText.trim()) items.push({role: 'copy'});
    if (items.length) Menu.buildFromTemplate(items).popup({window: win});
  });

  // The page asks before closing with unsaved changes; show a proper Windows dialog for it.
  win.webContents.on('will-prevent-unload', e => {
    const choice = dialog.showMessageBoxSync(win, {
      type: 'question',
      buttons: ['Close without saving', 'Cancel'],
      defaultId: 1,
      cancelId: 1,
      title: 'Unsaved changes',
      message: 'You have unsaved changes. Close WaughForm 3D anyway?',
      detail: 'Your work is also autosaved and will come back next time you open the app.',
    });
    if (choice === 0) e.preventDefault(); // allow the close
  });
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => app.quit());
