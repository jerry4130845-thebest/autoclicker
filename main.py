import json
import os
import random
import threading
import time
from pynput import keyboard, mouse
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

class HotkeyDialog(QDialog):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(320, 135)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 14)
        layout.setSpacing(10)
        
        label = QLabel("按下一个按键设置热键")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; font-weight: bold; color: #89b4fa;")
        layout.addWidget(label)
        
        hint = QLabel("Esc 取消")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setObjectName("muted")
        layout.addWidget(hint)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

class KeyTagWidget(QFrame):
    deleted = pyqtSignal(str)

    def __init__(self, key_name: str, parent=None):
        super().__init__(parent)
        self.key_name = key_name
        self.setObjectName("keyTag")
        self.setStyleSheet("""
            QFrame#keyTag {
                background-color: #45475a;
                border: 1px solid #585b70;
                border-radius: 6px;
                padding: 2px 6px;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(6)

        self.label = QLabel(key_name)
        self.label.setStyleSheet("color: #cdd6f4; font-weight: bold; font-size: 13px;")
        layout.addWidget(self.label)

        self.del_btn = QPushButton("×")
        self.del_btn.setFixedSize(18, 18)
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #f38ba8;
                font-weight: bold;
                font-size: 14px;
                padding: 0px;
                margin: 0px;
                border: none;
            }
            QPushButton:hover {
                background-color: #f38ba8;
                color: #1e1e2e;
                border-radius: 9px;
            }
        """)
        self.del_btn.clicked.connect(lambda: self.deleted.emit(self.key_name))
        layout.addWidget(self.del_btn)
        self.del_btn.hide()

    def enterEvent(self, event):
        super().enterEvent(event)
        self.del_btn.show()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.del_btn.hide()


class BoosterSkipCard(QFrame):
    request_delete = pyqtSignal(object)
    request_add = pyqtSignal(object)
    changed = pyqtSignal()

    def __init__(self, parent_window, initial_keys=None, parent=None):
        super().__init__(parent)
        self.parent_window = parent_window
        self.setObjectName("card")
        self.setStyleSheet("""
            QFrame#card {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 12px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        lbl1 = QLabel("当按下")
        lbl1.setStyleSheet("color: #cdd6f4; font-size: 13px;")
        layout.addWidget(lbl1)

        self.key_combo = QComboBox()
        self.key_combo.setMinimumWidth(80)
        self.key_combo.setStyleSheet("""
            QComboBox {
                background-color: #45475a;
                color: #cdd6f4;
                border: 1px solid #585b70;
                border-radius: 6px;
                padding: 4px 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #313244;
                color: #cdd6f4;
                selection-background-color: #89b4fa;
            }
        """)
        layout.addWidget(self.key_combo)

        lbl2 = QLabel("后")
        lbl2.setStyleSheet("color: #cdd6f4; font-size: 13px;")
        layout.addWidget(lbl2)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["跳过一次", "连续跳过"])
        self.mode_combo.setStyleSheet(self.key_combo.styleSheet())
        layout.addWidget(self.mode_combo)

        self.side_combo = QComboBox()
        self.side_combo.addItems(["左键", "右键"])
        self.side_combo.setStyleSheet(self.key_combo.styleSheet())
        layout.addWidget(self.side_combo)

        lbl3 = QLabel("cps booster")
        lbl3.setStyleSheet("color: #cdd6f4; font-size: 13px;")
        layout.addWidget(lbl3)

        layout.addStretch()

        self.update_keys(initial_keys or [])
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def update_keys(self, keys: list, keep_current=True):
        cur_text = self.key_combo.currentText() if keep_current else ""
        self.key_combo.blockSignals(True)
        self.key_combo.clear()
        for k in keys:
            self.key_combo.addItem(str(k))
        if cur_text and cur_text in keys:
            self.key_combo.setCurrentText(cur_text)
        elif keys:
            self.key_combo.setCurrentIndex(0)
        self.key_combo.blockSignals(False)

    def get_rule(self):
        return {
            "key": self.key_combo.currentText().strip(),
            "mode": self.mode_combo.currentText().strip(),
            "side": self.side_combo.currentText().strip()
        }

    def set_rule(self, key: str, mode: str, side: str):
        self.key_combo.blockSignals(True)
        self.mode_combo.blockSignals(True)
        self.side_combo.blockSignals(True)
        if key:
            if self.key_combo.findText(key) == -1: self.key_combo.addItem(key)
            self.key_combo.setCurrentText(key)
        if mode in ["跳过一次", "连续跳过"]: self.mode_combo.setCurrentText(mode)
        if side in ["左键", "右键"]: self.side_combo.setCurrentText(side)
        self.key_combo.blockSignals(False)
        self.mode_combo.blockSignals(False)
        self.side_combo.blockSignals(False)

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        total_cards = len(getattr(self.parent_window, "booster_skip_cards", []))
        del_action = QAction("删除当前卡片", menu)
        del_action.setEnabled(total_cards > 1)
        del_action.triggered.connect(lambda: self.request_delete.emit(self))
        menu.addAction(del_action)
        add_action = QAction("添加新卡片", menu)
        add_action.triggered.connect(lambda: self.request_add.emit(self))
        menu.addAction(add_action)
        menu.exec(self.mapToGlobal(pos))



class AutoClicker(QMainWindow):
    ui_status = pyqtSignal(str)
    ui_current_cps = pyqtSignal(str)
    ui_toggle_clicking = pyqtSignal()
    ui_toggle_left = pyqtSignal()
    ui_toggle_right = pyqtSignal()
    ui_error = pyqtSignal(str, str)
    ui_capture_hotkey = pyqtSignal(object, str)
    ui_cancel_hotkey = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("自动点击器")
        self.setFixedSize(470, 620)
        
        self.clicking = False
        self.click_thread = None
        self.listener_running = False
        self.hotkey_listener = None
        self.mouse_listener = None
        self.setting_hotkey = False
        self._setting_hotkey_target = None
        self._hotkey_dialog = None
        self._pressed_hotkeys = set()
        self._simulating = False
        self._sim_lock = threading.Lock()
        self.config_file = "option.txt"
        self._closing = False
        
        self.cps_mode = "fixed"
        self.cps_fixed = 10.0
        self.cps_min = 5.0
        self.cps_max = 15.0
        self.click_button = "left"
        self.hotkey_keycode = Key.f6
        self.hotkey_display = "F6"
        
        self.booster_left_enabled = False
        self.booster_left_hotkey = KeyCode.from_char("1")
        self.booster_left_hotkey_display = "1"
        self.booster_left_count = 2
        self.booster_left_min = 1
        self.booster_left_max = 3
        self.booster_left_use_random = False
        
        self.booster_right_enabled = False
        self.booster_right_hotkey = KeyCode.from_char("2")
        self.booster_right_hotkey_display = "2"
        self.booster_right_count = 2
        self.booster_right_min = 1
        self.booster_right_max = 3
        self.booster_right_use_random = False
        
        self.wasd_left_boost_enabled = False
        self.wasd_right_boost_enabled = False
        self._wasd_pressed = set()
        self._wasd_lock = threading.Lock()
        
        self._runtime_click_button = "left"
        self._runtime_cps_mode = "fixed"
        self._runtime_cps_fixed = 10.0
        self._runtime_cps_min = 5.0
        self._runtime_cps_max = 15.0
        self.extra_click_interval = 1.0 / 19.0

        self.managed_keys = []
        self.booster_skip_cards = []
        self.booster_skip_state = {
            "left": {"skip_once": False, "continuous_skip": False, "active_key": None},
            "right": {"skip_once": False, "continuous_skip": False, "active_key": None}
        }
        self._skip_lock = threading.Lock()
        
        self._build_ui()
        self._connect_signals()
        self.load_config()
        self.start_hotkey_listener()
        self.start_mouse_listener()

    def _is_same_key(self, k1, k2):
        if isinstance(k1, Key) and isinstance(k2, Key):
            return k1 == k2
        if isinstance(k1, KeyCode) and isinstance(k2, KeyCode):
            if k1.vk is not None and k2.vk is not None:
                return k1.vk == k2.vk
            if k1.char is not None and k2.char is not None:
                return k1.char.lower() == k2.char.lower()
            if k1.vk is not None and k2.char is not None:
                try:
                    return KeyCode(vk=k1.vk).char == k2.char.lower()
                except Exception:
                    pass
            if k2.vk is not None and k1.char is not None:
                try:
                    return KeyCode(vk=k2.vk).char == k1.char.lower()
                except Exception:
                    pass
        return k1 == k2

    def _normalize_key(self, key):
        if isinstance(key, KeyCode):
            if key.char:
                return KeyCode.from_char(key.char.lower())
            elif key.vk is not None:
                return KeyCode(vk=key.vk)
        return key

    def _build_ui(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
                font-size: 13px;
            }
            QWidget {
                background-color: transparent;
                color: #cdd6f4;
            }
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #313244;
                color: #a6adc8;
                border: none;
                padding: 10px 20px;
                margin-right: 5px;
                border-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #45475a;
                color: #cdd6f4;
            }
            QTabBar::tab:selected {
                background: #89b4fa;
                color: #1e1e2e;
            }
            QFrame#card {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 12px;
            }
            QLabel#sectionTitle {
                color: #89b4fa;
                font-size: 16px;
                font-weight: bold;
            }
            QLabel#label {
                color: #a6adc8;
            }
            QLabel#value {
                color: #a6e3a1;
                font-weight: bold;
            }
            QLabel#muted {
                color: #6c7086;
            }
            QDoubleSpinBox, QSpinBox {
                background-color: #45475a;
                border: 1px solid #585b70;
                border-radius: 6px;
                padding: 6px 10px;
                color: #cdd6f4;
                selection-background-color: #89b4fa;
            }
            QDoubleSpinBox:focus, QSpinBox:focus {
                border: 1px solid #89b4fa;
            }
            QRadioButton, QCheckBox {
                spacing: 8px;
                color: #cdd6f4;
            }
            QRadioButton::indicator, QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
            QPushButton:pressed {
                background-color: #89dceb;
            }
            QPushButton:disabled {
                background-color: #45475a;
                color: #6c7086;
            }
            QPushButton#danger {
                background-color: #f38ba8;
            }
            QPushButton#danger:hover {
                background-color: #eba0ac;
            }
            QPushButton#save {
                background-color: #a6e3a1;
            }
            QPushButton#save:hover {
                background-color: #94e2d5;
            }
            QPushButton#secondary {
                background-color: #45475a;
                color: #cdd6f4;
            }
            QPushButton#secondary:hover {
                background-color: #585b70;
            }
            QDialog {
                background-color: #1e1e2e;
            }
            QDialogButtonBox QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
            }
            QDialogButtonBox QPushButton:hover {
                background-color: #585b70;
            }
        """)
        
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(14, 12, 14, 12)
        main.setSpacing(10)
        
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        main.addWidget(tabs)
        
        auto_tab = QWidget()
        auto_layout = QVBoxLayout(auto_tab)
        auto_layout.setContentsMargins(2, 8, 2, 2)
        auto_layout.setSpacing(10)
        
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 15, 16, 15)
        layout.setSpacing(12)
        
        title = QLabel("自动点击")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("模式", objectName="label"))
        self.fixed_radio = QRadioButton("固定 CPS")
        self.random_radio = QRadioButton("波动 CPS")
        self.cps_mode_group = QButtonGroup(self)
        self.cps_mode_group.setExclusive(True)
        self.cps_mode_group.addButton(self.fixed_radio)
        self.cps_mode_group.addButton(self.random_radio)
        self.fixed_radio.setChecked(True)
        self.fixed_radio.toggled.connect(self.toggle_cps_mode)
        mode_row.addWidget(self.fixed_radio)
        mode_row.addWidget(self.random_radio)
        mode_row.addStretch()
        layout.addLayout(mode_row)
        
        self.fixed_widget = QWidget()
        fixed_form = QFormLayout(self.fixed_widget)
        fixed_form.setContentsMargins(0, 0, 0, 0)
        fixed_form.setHorizontalSpacing(14)
        self.cps_fixed_spin = QDoubleSpinBox()
        self.cps_fixed_spin.setRange(0.01, 9999.0)
        self.cps_fixed_spin.setDecimals(2)
        self.cps_fixed_spin.setValue(10.0)
        self.cps_fixed_spin.setSuffix(" CPS")
        fixed_form.addRow("固定速度", self.cps_fixed_spin)
        layout.addWidget(self.fixed_widget)
        
        self.random_widget = QWidget()
        random_form = QFormLayout(self.random_widget)
        random_form.setContentsMargins(0, 0, 0, 0)
        random_form.setHorizontalSpacing(14)
        self.cps_min_spin = QDoubleSpinBox()
        self.cps_min_spin.setRange(0.01, 9999.0)
        self.cps_min_spin.setDecimals(2)
        self.cps_min_spin.setValue(5.0)
        self.cps_min_spin.setSuffix(" CPS")
        self.cps_max_spin = QDoubleSpinBox()
        self.cps_max_spin.setRange(0.01, 9999.0)
        self.cps_max_spin.setDecimals(2)
        self.cps_max_spin.setValue(15.0)
        self.cps_max_spin.setSuffix(" CPS")
        random_form.addRow("最小速度", self.cps_min_spin)
        random_form.addRow("最大速度", self.cps_max_spin)
        self.random_widget.setVisible(False)
        layout.addWidget(self.random_widget)
        
        button_row = QHBoxLayout()
        button_row.addWidget(QLabel("点击按键", objectName="label"))
        self.left_radio = QRadioButton("左键")
        self.right_radio = QRadioButton("右键")
        self.click_button_group = QButtonGroup(self)
        self.click_button_group.setExclusive(True)
        self.click_button_group.addButton(self.left_radio)
        self.click_button_group.addButton(self.right_radio)
        self.left_radio.setChecked(True)
        button_row.addWidget(self.left_radio)
        button_row.addWidget(self.right_radio)
        button_row.addStretch()
        layout.addLayout(button_row)
        
        hotkey_row = QHBoxLayout()
        hotkey_row.addWidget(QLabel("触发热键", objectName="label"))
        self.auto_hotkey_label = QLabel(self.hotkey_display)
        self.auto_hotkey_label.setObjectName("value")
        hotkey_row.addWidget(self.auto_hotkey_label)
        hotkey_row.addStretch()
        self.auto_hotkey_btn = QPushButton("设置热键")
        self.auto_hotkey_btn.setObjectName("secondary")
        hotkey_row.addWidget(self.auto_hotkey_btn)
        layout.addLayout(hotkey_row)
        
        auto_layout.addWidget(card)
        
        status_card = QFrame()
        status_card.setObjectName("card")
        status_layout = QHBoxLayout(status_card)
        status_layout.setContentsMargins(16, 12, 16, 12)
        self.status_label = QLabel("状态：停止")
        self.status_label.setObjectName("muted")
        self.current_cps_label = QLabel("")
        self.current_cps_label.setObjectName("value")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.current_cps_label)
        auto_layout.addWidget(status_card)
        
        control_row = QHBoxLayout()
        self.start_button = QPushButton("启动")
        self.stop_button = QPushButton("停止")
        self.stop_button.setObjectName("danger")
        self.stop_button.setEnabled(False)
        control_row.addWidget(self.start_button)
        control_row.addWidget(self.stop_button)
        auto_layout.addLayout(control_row)
        
        auto_layout.addStretch()
        tabs.addTab(auto_tab, "自动点击")
        
        booster_tab = QWidget()
        booster_layout = QVBoxLayout(booster_tab)
        booster_layout.setContentsMargins(2, 8, 2, 2)
        booster_layout.setSpacing(10)
        booster_layout.addWidget(self._build_booster_group("左键 Booster", "left"))
        booster_layout.addWidget(self._build_booster_group("右键 Booster", "right"))
        
        info = QLabel("随机波动会在设定范围内每次触发时重新随机。")
        info.setObjectName("muted")
        booster_layout.addWidget(info)
        booster_layout.addStretch()
        tabs.addTab(booster_tab, "CPS Booster")
        
        settings_tab = QWidget()
        settings_main_layout = QVBoxLayout(settings_tab)
        settings_main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        settings_layout = QVBoxLayout(scroll_content)
        
        # 1. 顶部按键列表管理卡片
        key_mgr_card = QFrame()
        key_mgr_card.setObjectName("card")
        key_mgr_layout = QVBoxLayout(key_mgr_card)
        key_mgr_layout.addWidget(QLabel("按键列表管理"))
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("输入按键")
        self.key_input.returnPressed.connect(self._on_add_key_clicked)
        key_mgr_layout.addWidget(self.key_input)
        
        self.key_tags_container = QWidget()
        self.key_tags_layout = QHBoxLayout(self.key_tags_container)
        key_mgr_layout.addWidget(self.key_tags_container)
        settings_layout.addWidget(key_mgr_card)

        # 2. WASD 检测卡片
        settings_card = QFrame()
        settings_card.setObjectName("card")
        settings_card_layout = QVBoxLayout(settings_card)
        settings_title = QLabel("设置")
        settings_title.setObjectName("sectionTitle")
        settings_card_layout.addWidget(settings_title)
        
        self.wasd_left_check = QCheckBox("如果检测到WASD被按着，则执行左键Boost CPS")
        self.wasd_right_check = QCheckBox("如果检测到WASD被按着，则执行右键Boost CPS")
        settings_card_layout.addWidget(self.wasd_left_check)
        settings_card_layout.addWidget(self.wasd_right_check)
        settings_layout.addWidget(settings_card)

        # 3. Booster 跳过规则容器
        self.booster_cards_layout = QVBoxLayout()
        settings_layout.addLayout(self.booster_cards_layout)
        self._add_booster_skip_card()

        settings_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        settings_main_layout.addWidget(scroll_area)
        tabs.addTab(settings_tab, "设置")
        
        save_button = QPushButton("保存所有选项")
        save_button.setObjectName("save")
        main.addWidget(save_button)
        save_button.clicked.connect(self.save_config)
        
        self.toggle_cps_mode()

    def _build_booster_group(self, title, side):
        box = QFrame()
        box.setObjectName("card")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(16, 15, 16, 15)
        layout.setSpacing(11)
        
        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)
        
        row1 = QHBoxLayout()
        status = QLabel("关闭")
        status.setObjectName("value")
        hotkey_label = QLabel(
            self.booster_left_hotkey_display if side == "left" else self.booster_right_hotkey_display
        )
        hotkey_label.setObjectName("value")
        
        row1.addWidget(QLabel("状态", objectName="label"))
        row1.addWidget(status)
        row1.addSpacing(16)
        row1.addWidget(QLabel("热键", objectName="label"))
        row1.addWidget(hotkey_label)
        row1.addStretch()
        
        toggle_btn = QPushButton("切换")
        toggle_btn.setObjectName("secondary")
        hotkey_btn = QPushButton("设置热键")
        hotkey_btn.setObjectName("secondary")
        
        row1.addWidget(toggle_btn)
        row1.addWidget(hotkey_btn)
        layout.addLayout(row1)
        
        count_row = QHBoxLayout()
        count_spin = QSpinBox()
        count_spin.setRange(1, 9999)
        count_spin.setValue(2)
        random_check = QCheckBox("随机波动")
        
        count_row.addWidget(QLabel("固定点击数", objectName="label"))
        count_row.addWidget(count_spin)
        count_row.addWidget(random_check)
        count_row.addStretch()
        layout.addLayout(count_row)
        
        random_row = QHBoxLayout()
        min_spin = QSpinBox()
        min_spin.setRange(1, 9999)
        min_spin.setValue(1)
        max_spin = QSpinBox()
        max_spin.setRange(1, 9999)
        max_spin.setValue(3)
        
        random_row.addWidget(QLabel("随机范围", objectName="label"))
        random_row.addWidget(min_spin)
        random_row.addWidget(QLabel("至", objectName="label"))
        random_row.addWidget(max_spin)
        random_row.addStretch()
        layout.addLayout(random_row)
        
        if side == "left":
            self.booster_left_status = status
            self.booster_left_hotkey_label = hotkey_label
            self.booster_left_count_spin = count_spin
            self.booster_left_random_check = random_check
            self.booster_left_min_spin = min_spin
            self.booster_left_max_spin = max_spin
            toggle_btn.clicked.connect(self.toggle_booster_left)
            hotkey_btn.clicked.connect(lambda: self.set_hotkey_dialog("booster_left"))
            random_check.toggled.connect(self.on_left_random_toggle)
        else:
            self.booster_right_status = status
            self.booster_right_hotkey_label = hotkey_label
            self.booster_right_count_spin = count_spin
            self.booster_right_random_check = random_check
            self.booster_right_min_spin = min_spin
            self.booster_right_max_spin = max_spin
            toggle_btn.clicked.connect(self.toggle_booster_right)
            hotkey_btn.clicked.connect(lambda: self.set_hotkey_dialog("booster_right"))
            random_check.toggled.connect(self.on_right_random_toggle)
            
        return box

    def _connect_signals(self):
        self.start_button.clicked.connect(self.start_clicking)
        self.stop_button.clicked.connect(self.stop_clicking)
        self.auto_hotkey_btn.clicked.connect(lambda: self.set_hotkey_dialog("auto"))
        self.cps_fixed_spin.valueChanged.connect(lambda v: setattr(self, "_runtime_cps_fixed", float(v)))
        self.cps_min_spin.valueChanged.connect(lambda v: setattr(self, "_runtime_cps_min", float(v)))
        self.cps_max_spin.valueChanged.connect(lambda v: setattr(self, "_runtime_cps_max", float(v)))
        self.left_radio.toggled.connect(lambda checked: setattr(self, "_runtime_click_button", "left") if checked else None)
        self.right_radio.toggled.connect(lambda checked: setattr(self, "_runtime_click_button", "right") if checked else None)
        self.booster_left_count_spin.valueChanged.connect(lambda v: setattr(self, "booster_left_count", int(v)))
        self.booster_left_min_spin.valueChanged.connect(lambda v: setattr(self, "booster_left_min", int(v)))
        self.booster_left_max_spin.valueChanged.connect(lambda v: setattr(self, "booster_left_max", int(v)))
        self.booster_right_count_spin.valueChanged.connect(lambda v: setattr(self, "booster_right_count", int(v)))
        self.booster_right_min_spin.valueChanged.connect(lambda v: setattr(self, "booster_right_min", int(v)))
        self.booster_right_max_spin.valueChanged.connect(lambda v: setattr(self, "booster_right_max", int(v)))
        self.ui_status.connect(self.status_label.setText)
        self.ui_current_cps.connect(self.current_cps_label.setText)
        self.ui_toggle_clicking.connect(self.toggle_clicking)
        self.ui_toggle_left.connect(self.toggle_booster_left)
        self.ui_toggle_right.connect(self.toggle_booster_right)
        self.ui_error.connect(self._show_error)
        self.ui_capture_hotkey.connect(self._finish_hotkey_from_listener)
        self.ui_cancel_hotkey.connect(self._cancel_hotkey_from_listener)

    def toggle_cps_mode(self):
        self.cps_mode = "fixed" if self.fixed_radio.isChecked() else "random"
        self._runtime_cps_mode = self.cps_mode
        self.fixed_widget.setVisible(self.cps_mode == "fixed")
        self.random_widget.setVisible(self.cps_mode == "random")


    def _on_add_key_clicked(self):
        k = self.key_input.text().strip().lower()
        if k and k not in self.managed_keys:
            self.managed_keys.append(k)
            self._refresh_key_tags()
            self._refresh_booster_card_key_choices()
        self.key_input.clear()

    def _remove_key(self, key_name: str):
        if key_name in self.managed_keys:
            self.managed_keys.remove(key_name)
            self._refresh_key_tags()
            self._refresh_booster_card_key_choices()

    def _refresh_key_tags(self):
        while self.key_tags_layout.count() > 0:
            item = self.key_tags_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for k in self.managed_keys:
            tag = KeyTagWidget(k, self)
            tag.deleted.connect(self._remove_key)
            self.key_tags_layout.addWidget(tag)
        self.key_tags_layout.addStretch()

    def _refresh_booster_card_key_choices(self):
        for card in self.booster_skip_cards: card.update_keys(self.managed_keys)

    def _add_booster_skip_card(self, rule_data=None):
        if not isinstance(rule_data, dict):
            rule_data = None
        card = BoosterSkipCard(self, self.managed_keys)
        card.request_delete.connect(self._delete_booster_skip_card)
        card.request_add.connect(self._add_booster_skip_card)
        if rule_data: card.set_rule(rule_data.get("key", ""), rule_data.get("mode", ""), rule_data.get("side", ""))
        self.booster_skip_cards.append(card)
        self.booster_cards_layout.addWidget(card)

    def _delete_booster_skip_card(self, card):
        if len(self.booster_skip_cards) > 1:
            self.booster_skip_cards.remove(card)
            self.booster_cards_layout.removeWidget(card)
            card.deleteLater()

    def save_config(self):
        try:
            self.wasd_left_boost_enabled = bool(self.wasd_left_check.isChecked()) if hasattr(self, 'wasd_left_check') else bool(getattr(self, 'wasd_left_boost_enabled', False))
            self.wasd_right_boost_enabled = bool(self.wasd_right_check.isChecked()) if hasattr(self, 'wasd_right_check') else bool(getattr(self, 'wasd_right_boost_enabled', False))
            config = {
                "cps_mode": self.cps_mode,
                "cps_fixed": self.cps_fixed_spin.value(),
                "cps_min": self.cps_min_spin.value(),
                "cps_max": self.cps_max_spin.value(),
                "click_button": "left" if self.left_radio.isChecked() else "right",
                "auto_hotkey": self.hotkey_display,
                "booster_left_enabled": self.booster_left_enabled,
                "booster_left_hotkey": self.booster_left_hotkey_display,
                "booster_left_count": self.booster_left_count_spin.value(),
                "booster_left_min": self.booster_left_min_spin.value(),
                "booster_left_max": self.booster_left_max_spin.value(),
                "booster_left_use_random": self.booster_left_random_check.isChecked(),
                "booster_right_enabled": self.booster_right_enabled,
                "booster_right_hotkey": self.booster_right_hotkey_display,
                "booster_right_count": self.booster_right_count_spin.value(),
                "booster_right_min": self.booster_right_min_spin.value(),
                "booster_right_max": self.booster_right_max_spin.value(),
                "booster_right_use_random": self.booster_right_random_check.isChecked(),
                "wasd_left_boost_enabled": self.wasd_left_boost_enabled,
                "wasd_right_boost_enabled": self.wasd_right_boost_enabled,
                "managed_keys": self.managed_keys,
                "booster_skip_rules": [card.get_rule() for card in self.booster_skip_cards],
            }
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "成功", "配置已保存。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败：{e}")

    def load_config(self):
        if not os.path.exists(self.config_file):
            self.on_left_random_toggle(self.booster_left_random_check.isChecked())
            self.on_right_random_toggle(self.booster_right_random_check.isChecked())
            return
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            # BUG FIX: Load booster state FIRST, independent of CPS settings
            self.booster_left_enabled = bool(config.get("booster_left_enabled", False))
            self.booster_left_count = int(config.get("booster_left_count", 2))
            self.booster_left_min = int(config.get("booster_left_min", 1))
            self.booster_left_max = int(config.get("booster_left_max", 3))
            self.booster_left_use_random = bool(config.get("booster_left_use_random", False))
            self.booster_right_enabled = bool(config.get("booster_right_enabled", False))
            self.booster_right_count = int(config.get("booster_right_count", 2))
            self.booster_right_min = int(config.get("booster_right_min", 1))
            self.booster_right_max = int(config.get("booster_right_max", 3))
            self.booster_right_use_random = bool(config.get("booster_right_use_random", False))
            self.booster_left_count_spin.setValue(self.booster_left_count)
            self.booster_left_min_spin.setValue(self.booster_left_min)
            self.booster_left_max_spin.setValue(self.booster_left_max)
            self.booster_left_random_check.setChecked(self.booster_left_use_random)
            self._update_booster_status("left")
            self.booster_right_count_spin.setValue(self.booster_right_count)
            self.booster_right_min_spin.setValue(self.booster_right_min)
            self.booster_right_max_spin.setValue(self.booster_right_max)
            self.booster_right_random_check.setChecked(self.booster_right_use_random)
            self._update_booster_status("right")
            if "booster_left_hotkey" in config:
                self._restore_hotkey(config["booster_left_hotkey"], "booster_left")
            if "booster_right_hotkey" in config:
                self._restore_hotkey(config["booster_right_hotkey"], "booster_right")
            self.cps_mode = config.get("cps_mode", "fixed")
            self.cps_fixed_spin.setValue(float(config.get("cps_fixed", 10.0)))
            self.cps_min_spin.setValue(float(config.get("cps_min", 5.0)))
            self.cps_max_spin.setValue(float(config.get("cps_max", 15.0)))
            self.left_radio.setChecked(config.get("click_button", "left") == "left")
            self.right_radio.setChecked(not self.left_radio.isChecked())
            if self.cps_mode == "random":
                self.random_radio.setChecked(True)
            else:
                self.fixed_radio.setChecked(True)
            self.toggle_cps_mode()
            if "auto_hotkey" in config:
                self._restore_hotkey(config["auto_hotkey"], "auto")
            self.wasd_left_boost_enabled = bool(config.get("wasd_left_boost_enabled", False))
            self.wasd_right_boost_enabled = bool(config.get("wasd_right_boost_enabled", False))
            if hasattr(self, 'wasd_left_check'):
                self.wasd_left_check.setChecked(self.wasd_left_boost_enabled)
            if hasattr(self, 'wasd_right_check'):
                self.wasd_right_check.setChecked(self.wasd_right_boost_enabled)
            self.on_left_random_toggle(self.booster_left_random_check.isChecked())
            self.on_right_random_toggle(self.booster_right_random_check.isChecked())

            self.managed_keys = [str(k) for k in config.get("managed_keys", [])]
            self._refresh_key_tags()
            
            for card in list(self.booster_skip_cards):
                self.booster_cards_layout.removeWidget(card)
                card.deleteLater()
            self.booster_skip_cards.clear()
            for rule in config.get("booster_skip_rules", []):
                self._add_booster_skip_card(rule)
            if not self.booster_skip_cards:
                self._add_booster_skip_card()
            self._refresh_booster_card_key_choices()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载配置失败：{e}")

    def _restore_hotkey(self, hotkey_str, target):
        key_map = {
            "F1": Key.f1, "F2": Key.f2, "F3": Key.f3, "F4": Key.f4, "F5": Key.f5, "F6": Key.f6,
            "F7": Key.f7, "F8": Key.f8, "F9": Key.f9, "F10": Key.f10, "F11": Key.f11, "F12": Key.f12,
            "Enter": Key.enter, "Esc": Key.esc, "Space": Key.space, "Tab": Key.tab, "Backspace": Key.backspace,
            "Delete": Key.delete, "Shift": Key.shift, "Ctrl": Key.ctrl, "Alt": Key.alt,
            "Up": Key.up, "Down": Key.down, "Left": Key.left, "Right": Key.right,
            "PageUp": Key.page_up, "PageDown": Key.page_down, "Home": Key.home, "End": Key.end,
            "Insert": Key.insert, "Pause": Key.pause, "PrintScreen": Key.print_screen,
            "ScrollLock": Key.scroll_lock, "NumLock": Key.num_lock, "CapsLock": Key.caps_lock,
            "Left Alt": Key.alt_l, "Right Alt": Key.alt_r,
            "Left Ctrl": Key.ctrl_l, "Right Ctrl": Key.ctrl_r,
            "Right Shift": Key.shift_r,
        }
        hotkey_str = str(hotkey_str)
        if len(hotkey_str) == 1 and hotkey_str.isprintable():
            key = KeyCode.from_char(hotkey_str.lower())
        elif hotkey_str in key_map:
            key = key_map[hotkey_str]
        else:
            key = getattr(Key, hotkey_str.lower(), Key.f6)
        self._apply_hotkey(key, hotkey_str, target)

    @staticmethod
    def key_to_display(key):
        if isinstance(key, KeyCode):
            if key.char:
                return key.char.upper()
            if key.vk is not None:
                return f"VK{key.vk}"
        # Handle left/right modifiers
        text = str(key)
        if text == "Key.alt_l":
            return "Left Alt"
        if text == "Key.alt_r":
            return "Right Alt"
        if text == "Key.ctrl_l":
            return "Left Ctrl"
        if text == "Key.ctrl_r":
            return "Right Ctrl"
        if text == "Key.shift_r":
            return "Right Shift"
        # General fallback
        return text.replace("Key.", "").replace("_", " ").title().replace(" ", "")

    def _apply_hotkey(self, key, display, target):
        if target == "auto":
            self.hotkey_keycode = key
            self.hotkey_display = display
            self.auto_hotkey_label.setText(display)
        elif target == "booster_left":
            self.booster_left_hotkey = key
            self.booster_left_hotkey_display = display
            self.booster_left_hotkey_label.setText(display)
        elif target == "booster_right":
            self.booster_right_hotkey = key
            self.booster_right_hotkey_display = display
            self.booster_right_hotkey_label.setText(display)

    def set_hotkey_dialog(self, target):
        if self.setting_hotkey or self._closing:
            return
        names = {
            "auto": "自动点击热键",
            "booster_left": "左键 Booster 热键",
            "booster_right": "右键 Booster 热键",
        }
        if target not in names:
            return
        self.setting_hotkey = True
        self._setting_hotkey_target = target
        self._pressed_hotkeys.clear()
        dialog = HotkeyDialog(self, f"设置{names[target]}")
        self._hotkey_dialog = dialog
        dialog.exec()
        self.setting_hotkey = False
        self._setting_hotkey_target = None
        self._hotkey_dialog = None
        self._pressed_hotkeys.clear()

    def _finish_hotkey_from_listener(self, key, display):
        if not self.setting_hotkey or not self._setting_hotkey_target:
            return
        target = self._setting_hotkey_target
        self._apply_hotkey(key, display, target)
        if self._hotkey_dialog is not None:
            self._hotkey_dialog.accept()

    def _cancel_hotkey_from_listener(self):
        if not self.setting_hotkey:
            return
        if self._hotkey_dialog is not None:
            self._hotkey_dialog.reject()

    def start_hotkey_listener(self):
        if self.listener_running:
            return
        def on_press(key):
            if self._closing:
                return
            # Track WASD state only.
            try:
                k_names = set()
                if isinstance(key, KeyCode) and key.char:
                    k_names.add(key.char.lower())
                if hasattr(key, "name") and key.name:
                    k_names.add(key.name.lower())
                # also support display name conversion or direct string matching
                disp = self.key_to_display(key).lower()
                k_names.add(disp)

                if any(k in ['w', 'a', 's', 'd'] for k in k_names):
                    for k in ['w', 'a', 's', 'd']:
                        if k in k_names:
                            with self._wasd_lock: self._wasd_pressed.add(k)

                with self._skip_lock:
                    for side in ["left", "right"]:
                        st = self.booster_skip_state[side]
                        if st["continuous_skip"] and any(k in self.managed_keys for k in k_names) and not (st["active_key"] in k_names):
                            st["continuous_skip"] = False
                            st["active_key"] = None
                    for card in self.booster_skip_cards:
                        r = card.get_rule()
                        rule_k = r["key"].lower()
                        if rule_k in k_names:
                            side = "left" if "左" in r["side"] else "right"
                            if r["mode"] == "跳过一次":
                                self.booster_skip_state[side]["skip_once"] = True
                            else:
                                self.booster_skip_state[side]["continuous_skip"] = True
                                self.booster_skip_state[side]["active_key"] = rule_k
            except Exception: pass
            if self.setting_hotkey:
                if key == Key.esc:
                    self.ui_cancel_hotkey.emit()
                    return
                display = self.key_to_display(key)
                self.ui_capture_hotkey.emit(key, display)
                return
            norm_key = self._normalize_key(key)
            try:
                if norm_key in self._pressed_hotkeys:
                    return
                self._pressed_hotkeys.add(norm_key)
            except TypeError:
                pass
            if self._is_same_key(key, self.hotkey_keycode):
                self.ui_toggle_clicking.emit()
            elif self._is_same_key(key, self.booster_left_hotkey):
                self.ui_toggle_left.emit()
            elif self._is_same_key(key, self.booster_right_hotkey):
                self.ui_toggle_right.emit()

        def on_release(key):
            norm_key = self._normalize_key(key)
            try:
                self._pressed_hotkeys.discard(norm_key)
            except TypeError:
                pass
            # Track WASD release
            try:
                if isinstance(key, KeyCode) and key.char:
                    c = key.char.lower()
                    if c in ['w', 'a', 's', 'd']:
                        with self._wasd_lock:
                            self._wasd_pressed.discard(c)
            except Exception:
                pass

        self.hotkey_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.hotkey_listener.start()
        self.listener_running = True

    def toggle_booster_left(self):
        self.booster_left_enabled = not self.booster_left_enabled
        self._update_booster_status("left")

    def toggle_booster_right(self):
        self.booster_right_enabled = not self.booster_right_enabled
        self._update_booster_status("right")

    def _update_booster_status(self, side):
        if side == "left":
            enabled = self.booster_left_enabled
            label = self.booster_left_status
        else:
            enabled = self.booster_right_enabled
            label = self.booster_right_status
        label.setText("开启" if enabled else "关闭")
        label.setStyleSheet(
            "color: #a6e3a1; font-weight: 600;" if enabled else "color: #f38ba8; font-weight: 600;"
        )

    def on_left_random_toggle(self, enabled):
        self.booster_left_use_random = bool(enabled)
        self.booster_left_count_spin.setEnabled(not enabled)

    def on_right_random_toggle(self, enabled):
        self.booster_right_use_random = bool(enabled)
        self.booster_right_count_spin.setEnabled(not enabled)

    def start_mouse_listener(self):
        if self.mouse_listener and self.mouse_listener.running:
            return
        def on_click(x, y, button, pressed):
            if self._closing or not pressed:
                return
            with self._sim_lock:
                if self._simulating:
                    return
            if button == Button.left and self.booster_left_enabled and self._booster_should_fire("left"):
                total = (
                    random.randint(self.booster_left_min, self.booster_left_max)
                    if self.booster_left_use_random
                    else self.booster_left_count
                )
                threading.Thread(
                    target=self._perform_booster_click, args=(Button.left, total), daemon=True
                ).start()
            elif button == Button.right and self.booster_right_enabled and self._booster_should_fire("right"):
                total = (
                    random.randint(self.booster_right_min, self.booster_right_max)
                    if self.booster_right_use_random
                    else self.booster_right_count
                )
                threading.Thread(
                    target=self._perform_booster_click, args=(Button.right, total), daemon=True
                ).start()

        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.mouse_listener.start()

    def _booster_should_fire(self, side):
        with self._skip_lock:
            st = self.booster_skip_state[side]
            if st["skip_once"]:
                st["skip_once"] = False
                return False
            if st["continuous_skip"]:
                return False
        if side == "left":
            wasd_required = self.wasd_left_boost_enabled
        else:
            wasd_required = self.wasd_right_boost_enabled
        if not wasd_required:
            return True
        with self._wasd_lock:
            return len(self._wasd_pressed) > 0

    def _perform_booster_click(self, button, total_clicks):
        if total_clicks <= 1:
            return
        controller = mouse.Controller()
        for _ in range(total_clicks - 1):
            if self._closing:
                break
            time.sleep(self.extra_click_interval)
            with self._sim_lock:
                self._simulating = True
            try:
                controller.click(button)
            finally:
                with self._sim_lock:
                    self._simulating = False

    def toggle_clicking(self):
        if self.clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

    def get_next_interval(self):
        if self._runtime_cps_mode == "fixed":
            cps = self._runtime_cps_fixed
            if cps <= 0:
                return None
            return 1.0 / cps
        mn = self._runtime_cps_min
        mx = self._runtime_cps_max
        if mn <= 0 or mx <= 0 or mn > mx:
            return None
        cps = random.uniform(mn, mx)
        self.ui_current_cps.emit(f"{cps:.2f} CPS")
        return 1.0 / cps

    def start_clicking(self):
        if self.clicking:
            return
        self._runtime_cps_mode = self.cps_mode
        self._runtime_cps_fixed = self.cps_fixed_spin.value()
        self._runtime_cps_min = self.cps_min_spin.value()
        self._runtime_cps_max = self.cps_max_spin.value()
        self._runtime_click_button = "left" if self.left_radio.isChecked() else "right"
        if self.cps_mode == "fixed":
            if self._runtime_cps_fixed <= 0:
                self._show_error("错误", "固定 CPS 必须大于 0。")
                return
        else:
            mn = self._runtime_cps_min
            mx = self._runtime_cps_max
            if mn <= 0 or mx <= 0:
                self._show_error("错误", "CPS 范围必须大于 0。")
                return
            if mn > mx:
                self._show_error("错误", "最小 CPS 不能大于最大 CPS。")
                return
        self.clicking = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("状态：点击中")
        self.ui_current_cps.emit("波动模式已启动" if self.cps_mode == "random" else "")
        self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
        self.click_thread.start()

    def stop_clicking(self):
        self.clicking = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.ui_current_cps.emit("")
        self.status_label.setText("状态：停止")

    def click_loop(self):
        button = Button.left if self._runtime_click_button == "left" else Button.right
        controller = mouse.Controller()
        while self.clicking and not self._closing:
            interval = self.get_next_interval()
            if interval is None:
                self.clicking = False
                self.ui_status.emit("状态：停止")
                self.ui_current_cps.emit("")
                self.ui_error.emit("错误", "CPS 配置无效。")
                break
            with self._sim_lock:
                self._simulating = True
            try:
                controller.click(button)
            finally:
                with self._sim_lock:
                    self._simulating = False
            time.sleep(0.001)
            time.sleep(interval)

    def _show_error(self, title, text):
        QMessageBox.critical(self, title, text)

    def closeEvent(self, event: QCloseEvent):
        self._closing = True
        self.clicking = False
        self.setting_hotkey = False
        self._setting_hotkey_target = None
        if self.hotkey_listener and self.hotkey_listener.running:
            self.hotkey_listener.stop()
        if self.mouse_listener and self.mouse_listener.running:
            self.mouse_listener.stop()
        event.accept()

def main():
    app = QApplication([])
    window = AutoClicker()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()