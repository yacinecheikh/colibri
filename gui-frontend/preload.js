// preload.js
const { contextBridge, ipcRenderer } = require('electron/renderer')

let ipc = ipcRenderer

contextBridge.exposeInMainWorld("client", {
  run: async (command, stdin) => {
    return await ipc.invoke('client', command, stdin)
  }
})

