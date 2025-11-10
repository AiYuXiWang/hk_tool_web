const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const path = require('path');
const fs = require('fs');
const axios = require('axios');
const Store = require('electron-store');

// 初始化配置存储
const store = new Store({
  name: 'hk-tool-config',
  defaults: {
    apiBaseUrl: 'http://localhost:8000',
    windowBounds: { width: 1400, height: 900 },
    lastUsedLine: '',
    lastUsedStation: ''
  }
});

let mainWindow = null;

function createWindow() {
  // 获取上次保存的窗口大小
  const bounds = store.get('windowBounds');

  mainWindow = new BrowserWindow({
    width: bounds.width,
    height: bounds.height,
    minWidth: 1024,
    minHeight: 768,
    title: '环控平台维护工具 - 桌面版',
    icon: path.join(__dirname, 'assets', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: true
    },
    backgroundColor: '#ffffff',
    show: false
  });

  // 设置应用菜单
  createMenu();

  // 加载渲染页面
  const isDev = process.argv.includes('--dev');
  
  if (isDev) {
    // 开发模式：加载 Vite 开发服务器
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    // 生产模式：加载打包后的文件
    const indexPath = path.join(__dirname, 'renderer', 'index.html');
    mainWindow.loadFile(indexPath);
  }

  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // 保存窗口大小
  mainWindow.on('resize', () => {
    const bounds = mainWindow.getBounds();
    store.set('windowBounds', bounds);
  });

  // 窗口关闭
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function createMenu() {
  const template = [
    {
      label: '文件',
      submenu: [
        {
          label: '导出数据',
          accelerator: 'CmdOrCtrl+E',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.send('menu-action', 'export');
            }
          }
        },
        { type: 'separator' },
        {
          label: '设置',
          accelerator: 'CmdOrCtrl+,',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.send('menu-action', 'settings');
            }
          }
        },
        { type: 'separator' },
        {
          label: '退出',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: '编辑',
      submenu: [
        { label: '撤销', accelerator: 'CmdOrCtrl+Z', role: 'undo' },
        { label: '重做', accelerator: 'Shift+CmdOrCtrl+Z', role: 'redo' },
        { type: 'separator' },
        { label: '剪切', accelerator: 'CmdOrCtrl+X', role: 'cut' },
        { label: '复制', accelerator: 'CmdOrCtrl+C', role: 'copy' },
        { label: '粘贴', accelerator: 'CmdOrCtrl+V', role: 'paste' },
        { label: '全选', accelerator: 'CmdOrCtrl+A', role: 'selectAll' }
      ]
    },
    {
      label: '视图',
      submenu: [
        {
          label: '重新加载',
          accelerator: 'CmdOrCtrl+R',
          click: () => {
            if (mainWindow) {
              mainWindow.reload();
            }
          }
        },
        {
          label: '切换全屏',
          accelerator: process.platform === 'darwin' ? 'Ctrl+Command+F' : 'F11',
          click: () => {
            if (mainWindow) {
              mainWindow.setFullScreen(!mainWindow.isFullScreen());
            }
          }
        },
        {
          label: '开发者工具',
          accelerator: process.platform === 'darwin' ? 'Alt+Command+I' : 'Ctrl+Shift+I',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.toggleDevTools();
            }
          }
        }
      ]
    },
    {
      label: '帮助',
      submenu: [
        {
          label: '关于',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: '关于',
              message: '环控平台维护工具 - 桌面版',
              detail: '版本: 1.0.0\n\n功能：数据导出、数据写值\n\n© 2024 HK Platform Team',
              buttons: ['确定']
            });
          }
        },
        {
          label: '使用说明',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: '使用说明',
              message: '功能说明',
              detail: '1. 数据导出：支持电耗数据和传感器数据导出\n2. 数据写值：支持单点和批量写值控制\n\n请确保后端服务已启动（默认：http://localhost:8000）',
              buttons: ['确定']
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// 应用启动
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// 所有窗口关闭
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC 处理程序

// 获取配置
ipcMain.handle('get-config', async (event, key) => {
  if (key) {
    return store.get(key);
  }
  return store.store;
});

// 设置配置
ipcMain.handle('set-config', async (event, key, value) => {
  store.set(key, value);
  return true;
});

// 选择文件保存路径
ipcMain.handle('select-save-path', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    title: options.title || '保存文件',
    defaultPath: options.defaultPath || 'export.xlsx',
    filters: options.filters || [
      { name: 'Excel 文件', extensions: ['xlsx'] },
      { name: 'CSV 文件', extensions: ['csv'] },
      { name: '所有文件', extensions: ['*'] }
    ]
  });

  if (!result.canceled) {
    return result.filePath;
  }
  return null;
});

// 保存文件
ipcMain.handle('save-file', async (event, filePath, data) => {
  try {
    // data 可以是 Buffer 或 String
    fs.writeFileSync(filePath, data);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// API 请求代理
ipcMain.handle('api-request', async (event, config) => {
  try {
    const baseUrl = store.get('apiBaseUrl');
    const fullUrl = `${baseUrl}${config.url}`;
    
    const response = await axios({
      method: config.method || 'GET',
      url: fullUrl,
      data: config.data,
      params: config.params,
      headers: config.headers || {},
      timeout: config.timeout || 60000,
      responseType: config.responseType || 'json'
    });

    return {
      success: true,
      data: response.data,
      status: response.status,
      headers: response.headers
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      status: error.response?.status,
      data: error.response?.data
    };
  }
});

// 显示消息对话框
ipcMain.handle('show-message', async (event, options) => {
  const result = await dialog.showMessageBox(mainWindow, {
    type: options.type || 'info',
    title: options.title || '提示',
    message: options.message || '',
    detail: options.detail || '',
    buttons: options.buttons || ['确定']
  });
  return result.response;
});

// 打开文件选择对话框
ipcMain.handle('select-file', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: options.title || '选择文件',
    defaultPath: options.defaultPath,
    filters: options.filters || [{ name: '所有文件', extensions: ['*'] }],
    properties: options.properties || ['openFile']
  });

  if (!result.canceled) {
    return result.filePaths;
  }
  return null;
});

// 显示通知
ipcMain.handle('show-notification', async (event, options) => {
  const { Notification } = require('electron');
  
  if (Notification.isSupported()) {
    const notification = new Notification({
      title: options.title || '通知',
      body: options.body || '',
      silent: options.silent || false
    });
    notification.show();
    return true;
  }
  return false;
});

// 应用信息
ipcMain.handle('get-app-info', async () => {
  return {
    name: app.getName(),
    version: app.getVersion(),
    platform: process.platform,
    arch: process.arch,
    electronVersion: process.versions.electron,
    nodeVersion: process.versions.node,
    chromeVersion: process.versions.chrome
  };
});
