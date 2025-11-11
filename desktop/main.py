#!/usr/bin/env python3
"""
环控平台维护工具 - 桌面版
基于 PySide6 的跨平台桌面应用
"""

import sys
import os
import json
from pathlib import Path

from PySide6.QtCore import QUrl, QSettings, Qt, QTimer, Signal, QObject
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QFileDialog,
    QVBoxLayout, QWidget, QSystemTrayIcon, QMenu
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PySide6.QtGui import QIcon, QAction

# 配置文件路径
CONFIG_DIR = Path.home() / ".hk-tool-desktop"
CONFIG_FILE = CONFIG_DIR / "config.json"


class WebEnginePage(QWebEnginePage):
    """自定义 WebEngine 页面，处理控制台消息"""
    
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        """输出 JavaScript 控制台消息到终端"""
        levels = {
            QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel: "INFO",
            QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel: "WARNING",
            QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel: "ERROR"
        }
        level_str = levels.get(level, "LOG")
        print(f"[WebEngine {level_str}] {message} (line: {lineNumber})")


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.config_dir = CONFIG_DIR
        self._ensure_config_dir()
        self.config = self._load_config()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self):
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
        
        # 返回默认配置
        return {
            'apiBaseUrl': 'http://localhost:8000',
            'windowBounds': {'width': 1400, 'height': 900},
            'lastUsedLine': '',
            'lastUsedStation': ''
        }
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get(self, key, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置值"""
        self.config[key] = value
        self.save_config()


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.init_ui()
        self.restore_geometry()
    
    def init_ui(self):
        """初始化 UI"""
        # 设置窗口标题和图标
        self.setWindowTitle("环控平台维护工具 - 桌面版")
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建 WebEngine 视图
        self.web_view = QWebEngineView()
        
        # 设置自定义页面
        page = WebEnginePage(self.web_view)
        self.web_view.setPage(page)
        
        layout.addWidget(self.web_view)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建系统托盘
        self.create_tray_icon()
        
        # 加载前端页面
        self.load_frontend()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        export_action = QAction("导出数据(&E)", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.on_export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction("设置(&S)", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.on_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        reload_action = QAction("重新加载(&R)", self)
        reload_action.setShortcut("Ctrl+R")
        reload_action.triggered.connect(self.on_reload)
        view_menu.addAction(reload_action)
        
        fullscreen_action = QAction("全屏(&F)", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        view_menu.addSeparator()
        
        devtools_action = QAction("开发者工具(&D)", self)
        devtools_action.setShortcut("Ctrl+Shift+I")
        devtools_action.triggered.connect(self.on_devtools)
        view_menu.addAction(devtools_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
        
        usage_action = QAction("使用说明(&U)", self)
        usage_action.triggered.connect(self.on_usage)
        help_menu.addAction(usage_action)
    
    def create_tray_icon(self):
        """创建系统托盘图标"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("环控平台维护工具")
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        show_action = QAction("显示", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
    
    def load_frontend(self):
        """加载前端页面"""
        # 获取 API 基础 URL
        api_url = self.config_manager.get('apiBaseUrl', 'http://localhost:8000')
        
        # 开发模式：加载 Vite 开发服务器
        if '--dev' in sys.argv:
            frontend_url = "http://localhost:5173"
        else:
            # 生产模式：加载打包后的文件
            renderer_path = Path(__file__).parent / "renderer" / "index.html"
            if renderer_path.exists():
                frontend_url = f"file://{renderer_path.absolute()}"
            else:
                # 如果没有打包文件，尝试加载开发服务器
                frontend_url = "http://localhost:5173"
        
        print(f"加载前端页面: {frontend_url}")
        self.web_view.setUrl(QUrl(frontend_url))
    
    def restore_geometry(self):
        """恢复窗口几何"""
        bounds = self.config_manager.get('windowBounds', {'width': 1400, 'height': 900})
        self.resize(bounds.get('width', 1400), bounds.get('height', 900))
    
    def save_geometry(self):
        """保存窗口几何"""
        self.config_manager.set('windowBounds', {
            'width': self.width(),
            'height': self.height()
        })
    
    def closeEvent(self, event):
        """关闭事件"""
        self.save_geometry()
        event.accept()
    
    # 菜单动作处理
    
    def on_export_data(self):
        """导出数据"""
        # 发送消息到前端，切换到导出页面
        self.web_view.page().runJavaScript(
            "if (window.activeTab) { window.activeTab.value = 'export'; }"
        )
    
    def on_settings(self):
        """打开设置"""
        from dialogs import SettingsDialog
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            # 设置已更改，重新加载页面
            self.load_frontend()
    
    def on_reload(self):
        """重新加载页面"""
        self.web_view.reload()
    
    def toggle_fullscreen(self):
        """切换全屏"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def on_devtools(self):
        """打开开发者工具"""
        # PySide6 的 WebEngine 开发者工具需要额外配置
        QMessageBox.information(
            self,
            "开发者工具",
            "请在启动时添加 --remote-debugging-port=9222 参数，\n"
            "然后在 Chrome 浏览器中访问 localhost:9222"
        )
    
    def on_about(self):
        """关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            "环控平台维护工具 - 桌面版\n\n"
            "版本: 1.0.0\n\n"
            "功能：数据导出、数据写值\n\n"
            "© 2024 HK Platform Team\n\n"
            "基于 PySide6 构建"
        )
    
    def on_usage(self):
        """使用说明"""
        QMessageBox.information(
            self,
            "使用说明",
            "功能说明：\n\n"
            "1. 数据导出：支持电耗数据和传感器数据导出\n"
            "2. 数据写值：支持单点和批量写值控制\n\n"
            "请确保后端服务已启动\n"
            "（默认：http://localhost:8000）"
        )
    
    def on_tray_activated(self, reason):
        """托盘图标激活"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()


def main():
    """主函数"""
    # 启用高 DPI 支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("环控平台维护工具")
    app.setOrganizationName("HK Platform")
    app.setOrganizationDomain("hk-platform.com")
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 创建主窗口
    window = MainWindow(config_manager)
    window.show()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
