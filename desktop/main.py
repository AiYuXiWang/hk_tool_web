#!/usr/bin/env python3
"""
环控平台维护工具 - 桌面版
基于 PySide6 的原生跨平台桌面应用
"""

import sys
import os
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QSplitter, QMessageBox,
    QFileDialog
)
from PySide6.QtGui import QIcon, QAction

from api_client import APIClient
from dialogs import SettingsDialog
from widgets import DeviceTreeWidget, DataTableWidget, ExportPanelWidget, LogPanelWidget

# 配置文件路径
CONFIG_DIR = Path.home() / ".hk-tool-desktop"
CONFIG_FILE = CONFIG_DIR / "config.json"


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        import json
        self.config_file = CONFIG_FILE
        self.config_dir = CONFIG_DIR
        self._ensure_config_dir()
        self.config = self._load_config()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self):
        """加载配置"""
        import json
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
        
        return {
            'apiBaseUrl': 'http://localhost:8000',
            'windowBounds': {'width': 1400, 'height': 900},
            'lastUsedLine': '',
            'lastUsedStation': '',
            'operatorId': 'desktop-user'
        }
    
    def save_config(self):
        """保存配置"""
        import json
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
        self.api_client = APIClient(config_manager.get('apiBaseUrl'))
        self.init_ui()
        self.restore_geometry()
        
        # 加载线路配置
        self.load_line_configs()
    
    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("环控平台维护工具 - 桌面版")
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # 设备控制页面
        self.device_page = self.create_device_page()
        self.tab_widget.addTab(self.device_page, "设备控制")
        
        # 数据导出页面
        self.export_page = self.create_export_page()
        self.tab_widget.addTab(self.export_page, "数据导出")
        
        layout.addWidget(self.tab_widget)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建状态栏
        self.statusBar().showMessage("就绪")
    
    def create_device_page(self) -> QWidget:
        """创建设备控制页面"""
        page = QWidget()
        layout = QHBoxLayout(page)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：设备树
        self.device_tree = DeviceTreeWidget()
        self.device_tree.setMinimumWidth(300)
        self.device_tree.refresh_requested.connect(self.on_device_tree_refresh)
        self.device_tree.node_selected.connect(self.on_device_node_selected)
        splitter.addWidget(self.device_tree)
        
        # 右侧：数据表格和日志
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 数据表格
        self.data_table = DataTableWidget()
        self.data_table.query_requested.connect(self.on_query_point)
        self.data_table.write_requested.connect(self.on_write_point)
        self.data_table.batch_write_requested.connect(self.on_batch_write)
        right_layout.addWidget(self.data_table, stretch=3)
        
        # 操作日志
        self.log_panel = LogPanelWidget()
        right_layout.addWidget(self.log_panel, stretch=1)
        
        splitter.addWidget(right_widget)
        
        # 设置分割比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        layout.addWidget(splitter)
        
        return page
    
    def create_export_page(self) -> QWidget:
        """创建数据导出页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        self.export_panel = ExportPanelWidget()
        self.export_panel.export_requested.connect(self.on_export_data)
        layout.addWidget(self.export_panel)
        
        return page
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        export_action = QAction("导出数据(&E)", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
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
        
        refresh_action = QAction("刷新(&R)", self)
        refresh_action.setShortcut("Ctrl+R")
        refresh_action.triggered.connect(self.on_refresh)
        view_menu.addAction(refresh_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
    
    def load_line_configs(self):
        """加载线路配置"""
        try:
            result = self.api_client.get_line_configs()
            if result:
                self.device_tree.set_line_configs(result)
                self.export_panel.set_line_configs(result)
                self.log_panel.add_success("线路配置加载成功")
        except Exception as e:
            self.log_panel.add_error(f"加载线路配置失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"加载线路配置失败:\n{str(e)}")
    
    def on_device_tree_refresh(self, use_test_data: bool):
        """刷新设备树"""
        station_ip = self.device_tree.get_current_station_ip()
        if not station_ip:
            QMessageBox.warning(self, "警告", "请先选择车站")
            return
        
        self.device_tree.set_loading(True)
        self.statusBar().showMessage("正在加载设备树...")
        
        try:
            result = self.api_client.get_device_tree(station_ip, use_test_data)
            tree_data = result.get('tree', [])
            self.device_tree.load_tree_data(tree_data)
            self.log_panel.add_success(f"设备树加载成功，共 {len(tree_data)} 个根节点")
            self.statusBar().showMessage("设备树加载成功", 3000)
        except Exception as e:
            self.log_panel.add_error(f"加载设备树失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"加载设备树失败:\n{str(e)}")
            self.statusBar().showMessage("设备树加载失败", 3000)
        finally:
            self.device_tree.set_loading(False)
    
    def on_device_node_selected(self, node_data: dict):
        """设备树节点被选中"""
        meta = node_data.get('meta', {})
        if meta.get('is_point'):
            # 是点位，填充到查询框
            object_code = meta.get('object_code', '')
            data_code = meta.get('data_code', '')
            self.data_table.object_code_input.setText(object_code)
            self.data_table.data_code_input.setText(data_code)
            self.log_panel.add_info(f"选中点位: {node_data.get('label')}")
    
    def on_query_point(self, object_code: str, data_code: str):
        """查询点位"""
        station_ip = self.device_tree.get_current_station_ip()
        
        self.data_table.set_loading(True)
        self.statusBar().showMessage("正在查询点位...")
        
        try:
            queries = [{'object_code': object_code, 'data_code': data_code}]
            result = self.api_client.query_realtime_points(queries, station_ip)
            
            if result.get('results'):
                point_data = result['results'][0]
                value = point_data.get('value', '')
                unit = point_data.get('unit', '')
                self.data_table.update_row(object_code, data_code, value, unit)
                self.log_panel.add_success(f"查询成功: {object_code}/{data_code} = {value} {unit}")
            else:
                self.log_panel.add_warning(f"查询失败: 未找到数据")
            
            self.statusBar().showMessage("查询完成", 3000)
        except Exception as e:
            self.log_panel.add_error(f"查询失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"查询失败:\n{str(e)}")
            self.statusBar().showMessage("查询失败", 3000)
        finally:
            self.data_table.set_loading(False)
    
    def on_write_point(self, object_code: str, data_code: str, value: str):
        """写值"""
        station_ip = self.device_tree.get_current_station_ip()
        operator_id = self.config_manager.get('operatorId', 'desktop-user')
        
        self.statusBar().showMessage("正在写值...")
        
        try:
            commands = [{
                'object_code': object_code,
                'data_code': data_code,
                'value': value
            }]
            result = self.api_client.write_points(commands, operator_id, station_ip)
            
            if result.get('success'):
                self.log_panel.add_success(f"写值成功: {object_code}/{data_code} = {value}")
                # 刷新数据
                self.on_query_point(object_code, data_code)
            else:
                self.log_panel.add_error(f"写值失败: {result.get('message', '未知错误')}")
            
            self.statusBar().showMessage("写值完成", 3000)
        except Exception as e:
            self.log_panel.add_error(f"写值失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"写值失败:\n{str(e)}")
            self.statusBar().showMessage("写值失败", 3000)
    
    def on_batch_write(self):
        """批量写值"""
        points = self.data_table.get_all_points()
        if not points:
            QMessageBox.warning(self, "警告", "没有要写值的点位")
            return
        
        # TODO: 实现批量写值对话框
        QMessageBox.information(self, "提示", f"批量写值功能开发中\n共有 {len(points)} 个点位")
    
    def on_export_data(self, data_type: str, line: str, start_time: str, end_time: str):
        """导出数据"""
        self.export_panel.set_loading(True)
        self.export_panel.set_progress(0, "开始导出...")
        self.statusBar().showMessage("正在导出数据...")
        
        try:
            # 调用导出 API
            if data_type == "electricity":
                result = self.api_client.export_electricity_data(line, start_time, end_time)
            else:
                result = self.api_client.export_sensor_data(line, start_time, end_time)
            
            self.export_panel.set_progress(50, "正在生成文件...")
            
            if result.get('success'):
                file_path = result.get('file_path', '')
                
                # 下载文件
                file_data = self.api_client.download_export_file(file_path)
                
                self.export_panel.set_progress(80, "正在保存文件...")
                
                # 选择保存位置
                default_name = f"{data_type}_{line}_{start_time[:10]}.xlsx"
                save_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "保存文件",
                    default_name,
                    "Excel 文件 (*.xlsx);;所有文件 (*)"
                )
                
                if save_path:
                    with open(save_path, 'wb') as f:
                        f.write(file_data)
                    
                    self.export_panel.set_progress(100, f"导出成功! 文件已保存到: {save_path}")
                    self.statusBar().showMessage("导出成功", 3000)
                    QMessageBox.information(self, "成功", f"数据已成功导出到:\n{save_path}")
                else:
                    self.export_panel.add_log("导出已取消")
            else:
                error_msg = result.get('message', '未知错误')
                self.export_panel.add_log(f"导出失败: {error_msg}")
                QMessageBox.critical(self, "错误", f"导出失败:\n{error_msg}")
            
            self.export_panel.reset_progress()
        except Exception as e:
            self.export_panel.add_log(f"导出失败: {str(e)}")
            self.export_panel.reset_progress()
            QMessageBox.critical(self, "错误", f"导出失败:\n{str(e)}")
            self.statusBar().showMessage("导出失败", 3000)
        finally:
            self.export_panel.set_loading(False)
    
    def on_settings(self):
        """打开设置"""
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            # 更新 API 客户端
            self.api_client.set_base_url(self.config_manager.get('apiBaseUrl'))
            self.log_panel.add_info("设置已更新")
            # 重新加载线路配置
            self.load_line_configs()
    
    def on_refresh(self):
        """刷新当前页面"""
        current_index = self.tab_widget.currentIndex()
        if current_index == 0:  # 设备控制页面
            self.on_device_tree_refresh(False)
        elif current_index == 1:  # 数据导出页面
            self.load_line_configs()
    
    def on_about(self):
        """关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            "环控平台维护工具 - 桌面版\n\n"
            "版本: 2.0.0\n\n"
            "功能：数据导出、数据写值\n\n"
            "技术栈：PySide6 (Qt6)\n\n"
            "© 2024 HK Platform Team"
        )
    
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
