"""
操作日志面板控件
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTextCharFormat, QFont
from datetime import datetime


class LogPanelWidget(QWidget):
    """操作日志面板控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        
        # 标题栏
        header_layout = QHBoxLayout()
        title_label = QLabel("操作日志")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self.clear_logs)
        header_layout.addWidget(self.clear_btn)
        
        layout.addLayout(header_layout)
        
        # 日志文本
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)
    
    def add_log(self, message: str, log_type: str = "info"):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 根据类型设置颜色
        color = {
            "success": "#52c41a",
            "error": "#ff4d4f",
            "warning": "#faad14",
            "info": "#1890ff"
        }.get(log_type, "#000000")
        
        # 添加带颜色的日志
        self.log_text.append(
            f'<span style="color: {color};">[{timestamp}] {message}</span>'
        )
        
        # 滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_logs(self):
        """清空日志"""
        self.log_text.clear()
    
    def add_success(self, message: str):
        """添加成功日志"""
        self.add_log(f"✓ {message}", "success")
    
    def add_error(self, message: str):
        """添加错误日志"""
        self.add_log(f"✗ {message}", "error")
    
    def add_warning(self, message: str):
        """添加警告日志"""
        self.add_log(f"⚠ {message}", "warning")
    
    def add_info(self, message: str):
        """添加信息日志"""
        self.add_log(f"ℹ {message}", "info")
