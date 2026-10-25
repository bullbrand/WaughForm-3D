// WaughForm 3D desktop app: the extras the page can ask the app for - downloading a product photo,
// the page it came from (so the photo can be found on it), a PDF datasheet (for its drawing), and
// parts from the Fritzing install on this computer (for their pins), and checking an ESPHome YAML file
// with the ESPHome on this computer.
// © 2026 David John Waugh
const {contextBridge, ipcRenderer} = require('electron');

contextBridge.exposeInMainWorld('wfNative', {
  fetchImage: url => ipcRenderer.invoke('fetch-image', String(url)),
  fetchPage: url => ipcRenderer.invoke('fetch-page', String(url)),
  fetchPdf: url => ipcRenderer.invoke('fetch-pdf', String(url)),
  fritzingList: () => ipcRenderer.invoke('fritzing-list'),
  fritzingLoad: id => ipcRenderer.invoke('fritzing-load', Number(id)),
  version: () => ipcRenderer.invoke('app-version'),
  esphomeCheck: (yaml, name) => ipcRenderer.invoke('esphome-check', String(yaml), String(name || '')),
  esphomeSend: (yaml, name, overwrite) => ipcRenderer.invoke('esphome-send', String(yaml), String(name || ''), !!overwrite),
});
