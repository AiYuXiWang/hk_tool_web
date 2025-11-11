"""
对话框模块
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QDialogButtonBox
)
from PySide6.QtCore import Qt


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("设置")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 表单布局
        form_layout = QFormLayout()
        
        # API 基础 URL
        self.api_url_edit = QLineEdit()
        self.api_url_edit.setText(
            self.config_manager.get('apiBaseUrl', 'http://localhost:8000')
        )
        self.api_url_edit.setPlaceholderText("http://localhost:8000")
        form_layout.addRow("后端 API 地址:", self.api_url_edit)
        
        # 最后使用的线路
        self.last_line_edit = QLineEdit()
        self.last_line_edit.setText(
            self.config_manager.get('lastUsedLine', '')
        )
        self.last_line_edit.setPlaceholderText("例如: M1")
        form_layout.addRow("默认线路:", self.last_line_edit)
        
        # 最后使用的车站
        self.last_station_edit = QLineEdit()
        self.last_station_edit.setText(
            self.config_manager.get('lastUsedStation', '')
        )
        self.last_station_edit.setPlaceholderText("例如: 192.168.1.1")
        form_layout.addRow("默认车站 IP:", self.last_station_edit)
        
        layout.addLayout(form_layout)
        
        # 说明文字
        help_label = QLabel(
            "提示：修改 API 地址后需要重新加载页面才能生效。"
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(help_label)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def accept(self):
        """接受对话框"""
        # 保存配置
        self.config_manager.set('apiBaseUrl', self.api_url_edit.text().strip())
        self.config_manager.set('lastUsedLine', self.last_line_edit.text().strip())
        self.config_manager.set('lastUsedStation', self.last_station_edit.text().strip())
        super().accept()
