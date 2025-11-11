"""
数据表格控件
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
    QHeaderView, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from datetime import datetime


class DataTableWidget(QWidget):
    """数据表格控件"""
    
    # 信号定义
    query_requested = Signal(str, str)  # 请求查询（object_code, data_code）
    write_requested = Signal(str, str, str)  # 请求写值（object_code, data_code, value）
    batch_write_requested = Signal()  # 请求批量写值
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        
        # 查询面板
        query_panel = QHBoxLayout()
        
        query_panel.addWidget(QLabel("设备编码:"))
        self.object_code_input = QLineEdit()
        self.object_code_input.setPlaceholderText("请输入 object_code")
        query_panel.addWidget(self.object_code_input)
        
        query_panel.addWidget(QLabel("点位编码:"))
        self.data_code_input = QLineEdit()
        self.data_code_input.setPlaceholderText("请输入 data_code")
        query_panel.addWidget(self.data_code_input)
        
        self.query_btn = QPushButton("查询实时值")
        self.query_btn.clicked.connect(self.on_query_clicked)
        query_panel.addWidget(self.query_btn)
        
        self.add_batch_btn = QPushButton("加入批量")
        self.add_batch_btn.clicked.connect(self.on_add_batch_clicked)
        query_panel.addWidget(self.add_batch_btn)
        
        layout.addLayout(query_panel)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "设备编码", "点位编码", "当前值", "单位", 
            "更新时间", "操作"
        ])
        
        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        self.batch_write_btn = QPushButton("批量写值")
        self.batch_write_btn.clicked.connect(lambda: self.batch_write_requested.emit())
        bottom_layout.addWidget(self.batch_write_btn)
        
        layout.addLayout(bottom_layout)
    
    def on_query_clicked(self):
        """查询按钮点击"""
        object_code = self.object_code_input.text().strip()
        data_code = self.data_code_input.text().strip()
        
        if not object_code or not data_code:
            QMessageBox.warning(self, "警告", "请输入设备编码和点位编码")
            return
        
        self.query_requested.emit(object_code, data_code)
    
    def on_add_batch_clicked(self):
        """加入批量按钮点击"""
        object_code = self.object_code_input.text().strip()
        data_code = self.data_code_input.text().strip()
        
        if not object_code or not data_code:
            QMessageBox.warning(self, "警告", "请输入设备编码和点位编码")
            return
        
        # 添加到表格
        self.add_row(object_code, data_code, "", "", "")
    
    def add_row(self, object_code: str, data_code: str, value: str, unit: str, update_time: str):
        """添加一行数据"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        self.table.setItem(row, 0, QTableWidgetItem(object_code))
        self.table.setItem(row, 1, QTableWidgetItem(data_code))
        self.table.setItem(row, 2, QTableWidgetItem(str(value)))
        self.table.setItem(row, 3, QTableWidgetItem(unit))
        self.table.setItem(row, 4, QTableWidgetItem(update_time))
        
        # 操作按钮
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(2, 2, 2, 2)
        
        write_btn = QPushButton("写值")
        write_btn.clicked.connect(lambda: self.on_write_clicked(row))
        btn_layout.addWidget(write_btn)
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(lambda: self.on_refresh_clicked(row))
        btn_layout.addWidget(refresh_btn)
        
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(lambda: self.on_delete_clicked(row))
        btn_layout.addWidget(delete_btn)
        
        self.table.setCellWidget(row, 5, btn_widget)
    
    def on_write_clicked(self, row: int):
        """写值按钮点击"""
        object_code = self.table.item(row, 0).text()
        data_code = self.table.item(row, 1).text()
        
        # 弹出对话框输入新值
        from PySide6.QtWidgets import QInputDialog
        value, ok = QInputDialog.getText(self, "写值", "请输入新值:")
        
        if ok and value:
            self.write_requested.emit(object_code, data_code, value)
    
    def on_refresh_clicked(self, row: int):
        """刷新按钮点击"""
        object_code = self.table.item(row, 0).text()
        data_code = self.table.item(row, 1).text()
        self.query_requested.emit(object_code, data_code)
    
    def on_delete_clicked(self, row: int):
        """删除按钮点击"""
        self.table.removeRow(row)
    
    def update_row(self, object_code: str, data_code: str, value: str, unit: str = ""):
        """更新行数据"""
        # 查找对应的行
        for row in range(self.table.rowCount()):
            if (self.table.item(row, 0).text() == object_code and
                self.table.item(row, 1).text() == data_code):
                self.table.item(row, 2).setText(str(value))
                self.table.item(row, 3).setText(unit)
                self.table.item(row, 4).setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                return
        
        # 如果没找到，添加新行
        self.add_row(object_code, data_code, value, unit, 
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def clear_table(self):
        """清空表格"""
        self.table.setRowCount(0)
    
    def get_all_points(self):
        """获取所有点位"""
        points = []
        for row in range(self.table.rowCount()):
            object_code = self.table.item(row, 0).text()
            data_code = self.table.item(row, 1).text()
            points.append({
                'object_code': object_code,
                'data_code': data_code
            })
        return points
    
    def set_loading(self, loading: bool):
        """设置加载状态"""
        self.query_btn.setEnabled(not loading)
        self.add_batch_btn.setEnabled(not loading)
        self.batch_write_btn.setEnabled(not loading)
