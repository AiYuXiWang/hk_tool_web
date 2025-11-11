"""
设备树控件
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QLabel,
    QComboBox, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon


class DeviceTreeWidget(QWidget):
    """设备树控件"""
    
    # 信号定义
    node_selected = Signal(dict)  # 节点被选中
    refresh_requested = Signal(bool)  # 请求刷新（参数：是否使用测试数据）
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree_data = []
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 顶部工具栏
        toolbar = QHBoxLayout()
        
        # 标题
        title_label = QLabel("设备树")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        toolbar.addWidget(title_label)
        
        toolbar.addStretch()
        
        # 刷新按钮
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(lambda: self.refresh_requested.emit(False))
        toolbar.addWidget(self.refresh_btn)
        
        # 测试按钮
        self.test_btn = QPushButton("测试")
        self.test_btn.clicked.connect(lambda: self.refresh_requested.emit(True))
        toolbar.addWidget(self.test_btn)
        
        layout.addLayout(toolbar)
        
        # 搜索框
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索设备或点位...")
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # 线路和车站选择
        selector_layout = QVBoxLayout()
        
        line_layout = QHBoxLayout()
        line_layout.addWidget(QLabel("线路:"))
        self.line_combo = QComboBox()
        self.line_combo.currentTextChanged.connect(self.on_line_changed)
        line_layout.addWidget(self.line_combo)
        selector_layout.addLayout(line_layout)
        
        station_layout = QHBoxLayout()
        station_layout.addWidget(QLabel("车站:"))
        self.station_combo = QComboBox()
        self.station_combo.currentTextChanged.connect(self.on_station_changed)
        station_layout.addWidget(self.station_combo)
        selector_layout.addLayout(station_layout)
        
        layout.addLayout(selector_layout)
        
        # 树形控件
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["设备/点位"])
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree)
    
    def set_line_configs(self, configs: dict):
        """设置线路配置"""
        self.line_combo.clear()
        self.line_configs = configs
        
        # 提取线路列表
        lines = [k for k in configs.keys() if k.startswith('M')]
        self.line_combo.addItems(lines)
    
    def on_line_changed(self, line: str):
        """线路变更"""
        if not line or line not in self.line_configs:
            return
        
        # 更新车站列表
        self.station_combo.clear()
        stations = self.line_configs[line]
        
        if isinstance(stations, list):
            for station in stations:
                if isinstance(station, dict):
                    station_name = station.get('station_name', station.get('station_ip', ''))
                    station_ip = station.get('station_ip', '')
                    self.station_combo.addItem(station_name, station_ip)
    
    def on_station_changed(self, station: str):
        """车站变更"""
        pass
    
    def load_tree_data(self, data: list):
        """加载树数据"""
        self.tree_data = data
        self.tree.clear()
        
        if not data:
            return
        
        # 递归构建树
        for node in data:
            self._add_tree_node(None, node)
        
        # 展开第一级
        self.tree.expandToDepth(0)
    
    def _add_tree_node(self, parent, node: dict):
        """添加树节点"""
        # 创建节点
        label = node.get('label', 'Unknown')
        item = QTreeWidgetItem([label])
        
        # 存储节点数据
        item.setData(0, Qt.ItemDataRole.UserRole, node)
        
        # 设置图标（根据节点类型）
        meta = node.get('meta', {})
        if meta.get('is_point'):
            item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon))
            if meta.get('is_writable'):
                item.setText(0, f"{label} [可写]")
        elif meta.get('object_type') == 'device':
            item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        else:
            item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_DirIcon))
        
        # 添加到父节点或根节点
        if parent is None:
            self.tree.addTopLevelItem(item)
        else:
            parent.addChild(item)
        
        # 递归添加子节点
        children = node.get('children', [])
        for child in children:
            self._add_tree_node(item, child)
    
    def on_item_clicked(self, item, column):
        """节点被点击"""
        node_data = item.data(0, Qt.ItemDataRole.UserRole)
        if node_data:
            self.node_selected.emit(node_data)
    
    def on_search(self, text: str):
        """搜索过滤"""
        # 简单的过滤实现
        if not text:
            # 显示所有项
            iterator = QTreeWidgetItemIterator(self.tree)
            while iterator.value():
                item = iterator.value()
                item.setHidden(False)
                iterator += 1
        else:
            # 过滤项
            text = text.lower()
            iterator = QTreeWidgetItemIterator(self.tree)
            while iterator.value():
                item = iterator.value()
                item_text = item.text(0).lower()
                item.setHidden(text not in item_text)
                iterator += 1
    
    def get_current_station_ip(self) -> str:
        """获取当前选中的车站 IP"""
        return self.station_combo.currentData() or ""
    
    def set_loading(self, loading: bool):
        """设置加载状态"""
        self.refresh_btn.setEnabled(not loading)
        self.test_btn.setEnabled(not loading)
        self.tree.setEnabled(not loading)
