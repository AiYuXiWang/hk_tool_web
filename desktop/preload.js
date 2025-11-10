const { contextBridge, ipcRenderer } = require('electron');

// 暴露安全的 API 给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 配置管理
  getConfig: (key) => ipcRenderer.invoke('get-config', key),
  setConfig: (key, value) => ipcRenderer.invoke('set-config', key, value),

  // 文件操作
  selectSavePath: (options) => ipcRenderer.invoke('select-save-path', options),
  saveFile: (filePath, data) => ipcRenderer.invoke('save-file', filePath, data),
  selectFile: (options) => ipcRenderer.invoke('select-file', options),

  // API 请求
  apiRequest: (config) => ipcRenderer.invoke('api-request', config),

  // 对话框
  showMessage: (options) => ipcRenderer.invoke('show-message', options),
  showNotification: (options) => ipcRenderer.invoke('show-notification', options),

  // 应用信息
  getAppInfo: () => ipcRenderer.invoke('get-app-info'),

  // 菜单事件监听
  onMenuAction: (callback) => {
    ipcRenderer.on('menu-action', (event, action) => callback(action));
  },

  // 平台信息
  platform: process.platform,
  isElectron: true
});

// 开发工具
if (process.env.NODE_ENV === 'development') {
  contextBridge.exposeInMainWorld('__ELECTRON_DEV__', {
    ipcRenderer: {
      send: (channel, ...args) => ipcRenderer.send(channel, ...args),
      on: (channel, func) => ipcRenderer.on(channel, (event, ...args) => func(...args))
    }
  });
}
