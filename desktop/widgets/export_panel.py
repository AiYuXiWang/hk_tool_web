"""
数据导出面板控件
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QDateTimeEdit, QRadioButton, QLabel,
    QGroupBox, QProgressBar, QTextEdit, QButtonGroup
)
from PySide6.QtCore import Signal, Qt, QDateTime
from datetime import datetime, timedelta


class ExportPanelWidget(QWidget):
    """数据导出面板控件"""
    
    # 信号定义
    export_requested = Signal(str, str, str, str)  # 数据类型, 线路, 开始时间, 结束时间
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        
        # 数据类型选择
        type_group = QGroupBox("数据类型")
        type_layout = QHBoxLayout()
        
        self.type_group = QButtonGroup()
        self.electricity_radio = QRadioButton("电耗数据")
        self.electricity_radio.setChecked(True)
        self.sensor_radio = QRadioButton("传感器数据")
        
        self.type_group.addButton(self.electricity_radio, 0)
        self.type_group.addButton(self.sensor_radio, 1)
        
        type_layout.addWidget(self.electricity_radio)
        type_layout.addWidget(self.sensor_radio)
        type_layout.addStretch()
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # 线路选择
        line_layout = QHBoxLayout()
        line_layout.addWidget(QLabel("选择线路:"))
        self.line_combo = QComboBox()
        line_layout.addWidget(self.line_combo)
        line_layout.addStretch()
        layout.addLayout(line_layout)
        
        # 时间范围
        time_group = QGroupBox("时间范围")
        time_layout = QVBoxLayout()
        
        # 快捷时间按钮
        quick_layout = QHBoxLayout()
        self.today_btn = QPushButton("今天")
        self.today_btn.clicked.connect(lambda: self.set_time_preset("today"))
        quick_layout.addWidget(self.today_btn)
        
        self.yesterday_btn = QPushButton("昨天")
        self.yesterday_btn.clicked.connect(lambda: self.set_time_preset("yesterday"))
        quick_layout.addWidget(self.yesterday_btn)
        
        self.last_7d_btn = QPushButton("最近7天")
        self.last_7d_btn.clicked.connect(lambda: self.set_time_preset("last_7d"))
        quick_layout.addWidget(self.last_7d_btn)
        
        self.last_30d_btn = QPushButton("最近30天")
        self.last_30d_btn.clicked.connect(lambda: self.set_time_preset("last_30d"))
        quick_layout.addWidget(self.last_30d_btn)
        
        quick_layout.addStretch()
        time_layout.addLayout(quick_layout)
        
        # 自定义时间
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("开始时间:"))
        self.start_time = QDateTimeEdit()
        self.start_time.setCalendarPopup(True)
        self.start_time.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.start_time.setDateTime(QDateTime.currentDateTime().addDays(-1))
        custom_layout.addWidget(self.start_time)
        
        custom_layout.addWidget(QLabel("结束时间:"))
        self.end_time = QDateTimeEdit()
        self.end_time.setCalendarPopup(True)
        self.end_time.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_time.setDateTime(QDateTime.currentDateTime())
        custom_layout.addWidget(self.end_time)
        
        time_layout.addLayout(custom_layout)
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        
        # 导出按钮
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        self.export_btn = QPushButton("开始导出")
        self.export_btn.setMinimumWidth(150)
        self.export_btn.clicked.connect(self.on_export_clicked)
        export_layout.addWidget(self.export_btn)
        layout.addLayout(export_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 日志
        log_group = QGroupBox("导出日志")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        layout.addStretch()
    
    def set_line_configs(self, configs: dict):
        """设置线路配置"""
        self.line_combo.clear()
        lines = [k for k in configs.keys() if k.startswith('M')]
        self.line_combo.addItems(lines)
    
    def set_time_preset(self, preset: str):
        """设置快捷时间"""
        now = QDateTime.currentDateTime()
        
        if preset == "today":
            start = now.addSecs(-now.time().secsTo(now.time().addSecs(-now.time().hour() * 3600 - now.time().minute() * 60 - now.time().second())))
            self.start_time.setDateTime(start)
            self.end_time.setDateTime(now)
        
        elif preset == "yesterday":
            yesterday = now.addDays(-1)
            start = yesterday.addSecs(-yesterday.time().secsTo(yesterday.time().addSecs(-yesterday.time().hour() * 3600 - yesterday.time().minute() * 60 - yesterday.time().second())))
            end = start.addDays(1)
            self.start_time.setDateTime(start)
            self.end_time.setDateTime(end)
        
        elif preset == "last_7d":
            self.start_time.setDateTime(now.addDays(-7))
            self.end_time.setDateTime(now)
        
        elif preset == "last_30d":
            self.start_time.setDateTime(now.addDays(-30))
            self.end_time.setDateTime(now)
    
    def on_export_clicked(self):
        """导出按钮点击"""
        # 获取数据类型
        data_type = "electricity" if self.electricity_radio.isChecked() else "sensor"
        
        # 获取线路
        line = self.line_combo.currentText()
        if not line:
            self.add_log("错误: 请选择线路")
            return
        
        # 获取时间范围
        start_time = self.start_time.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_time = self.end_time.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        
        self.add_log(f"开始导出 {data_type} 数据...")
        self.add_log(f"线路: {line}")
        self.add_log(f"时间范围: {start_time} 至 {end_time}")
        
        self.export_requested.emit(data_type, line, start_time, end_time)
    
    def add_log(self, message: str):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def set_progress(self, value: int, message: str = ""):
        """设置进度"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(value)
        if message:
            self.add_log(message)
    
    def reset_progress(self):
        """重置进度"""
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
    
    def set_loading(self, loading: bool):
        """设置加载状态"""
        self.export_btn.setEnabled(not loading)
        self.line_combo.setEnabled(not loading)
        self.start_time.setEnabled(not loading)
        self.end_time.setEnabled(not loading)
