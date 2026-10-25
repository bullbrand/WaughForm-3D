// Prints manual\manual.html to "manual\WaughForm 3D User Manual.pdf" (A4, page numbers in the footer).
// Run from the "claude code" folder with the desktop app's Electron:
//   desktop\node_modules\electron\dist\electron.exe tools\make-manual.js
// © 2026 David John Waugh
const {app, BrowserWindow} = require('electron');
const fs = require('fs');
const path = require('path');

const dir = path.join(__dirname, '..', 'manual');
const version = require(path.join(__dirname, '..', 'desktop', 'package.json')).version;

app.whenReady().then(async () => {
  const win = new BrowserWindow({show: false, width: 1000, height: 1400, webPreferences: {sandbox: true}});
  await win.loadFile(path.join(dir, 'manual.html'));
  await new Promise(r => setTimeout(r, 800)); // let the pictures finish loading
  // the version number (cover, file names) comes from package.json
  await win.webContents.executeJavaScript(`document.querySelectorAll('.ver').forEach(e => e.textContent = ${JSON.stringify(version)})`);
  const small = 'font-family:Segoe UI,sans-serif;font-size:8px;color:#5c6575;width:100%;padding:0 16mm;display:flex;justify-content:space-between';
  const pdf = await win.webContents.printToPDF({
    pageSize: 'A4',
    printBackground: true,
    preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: `<div style="${small}"><span>WaughForm 3D User Manual · version ${version}</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>`,
  });
  const out = path.join(dir, 'WaughForm 3D User Manual.pdf');
  fs.writeFileSync(out, pdf);
  console.log('Wrote ' + out + ' (' + Math.round(pdf.length / 1024) + ' KB)');
  app.quit();
});
