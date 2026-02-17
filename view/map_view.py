"""
Представление (View) для отображения карты
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QLabel, QComboBox,
                             QListWidget, QGroupBox, QMessageBox, QSpinBox)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import pyqtSignal
import config


class MapView(QMainWindow):
    """Класс представления карты"""

    # Сигналы для взаимодействия с контроллером
    location_changed = pyqtSignal(float, float, int)
    search_requested = pyqtSignal(str)
    geocode_requested = pyqtSignal(str)
    preset_selected = pyqtSignal(str)
    marker_add_requested = pyqtSignal(float, float, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        self.init_ui()

    def init_ui(self):
        """Инициализация UI"""
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Левая панель
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, stretch=1)

        # Карта
        self.map_view = QWebEngineView()
        main_layout.addWidget(self.map_view, stretch=3)

    def create_left_panel(self) -> QWidget:
        """Создание левой панели управления"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Группа: Координаты
        coords_group = QGroupBox("Координаты")
        coords_layout = QVBoxLayout()

        # Широта
        lat_layout = QHBoxLayout()
        lat_layout.addWidget(QLabel("Широта:"))
        self.lat_input = QLineEdit(str(config.DEFAULT_LATITUDE))
        lat_layout.addWidget(self.lat_input)
        coords_layout.addLayout(lat_layout)

        # Долгота
        lon_layout = QHBoxLayout()
        lon_layout.addWidget(QLabel("Долгота:"))
        self.lon_input = QLineEdit(str(config.DEFAULT_LONGITUDE))
        lon_layout.addWidget(self.lon_input)
        coords_layout.addLayout(lon_layout)

        # Масштаб
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Масштаб:"))
        self.zoom_input = QSpinBox()
        self.zoom_input.setRange(config.MIN_ZOOM, config.MAX_ZOOM)
        self.zoom_input.setValue(config.DEFAULT_ZOOM)
        zoom_layout.addWidget(self.zoom_input)
        coords_layout.addLayout(zoom_layout)

        # Кнопка показать
        self.show_btn = QPushButton("Показать на карте")
        self.show_btn.clicked.connect(self.on_show_location)
        coords_layout.addWidget(self.show_btn)

        coords_group.setLayout(coords_layout)
        layout.addWidget(coords_group)

        # Группа: Поиск по адресу
        search_group = QGroupBox("Поиск")
        search_layout = QVBoxLayout()

        # Поиск по адресу
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Введите адрес...")
        self.address_input.returnPressed.connect(self.on_geocode)
        search_layout.addWidget(self.address_input)

        geocode_btn = QPushButton("Найти адрес")
        geocode_btn.clicked.connect(self.on_geocode)
        search_layout.addWidget(geocode_btn)

        # Поиск мест
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск мест...")
        self.search_input.returnPressed.connect(self.on_search)
        search_layout.addWidget(self.search_input)

        search_btn = QPushButton("Искать места")
        search_btn.clicked.connect(self.on_search)
        search_layout.addWidget(search_btn)

        # Список результатов
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_result_selected)
        search_layout.addWidget(self.results_list)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Группа: Предустановленные локации
        preset_group = QGroupBox("Быстрый доступ")
        preset_layout = QVBoxLayout()

        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Москва",
            "Санкт-Петербург",
            "Париж",
            "Лондон",
            "Нью-Йорк",
            "Токио",
            "Сидней"
        ])
        preset_layout.addWidget(self.preset_combo)

        preset_btn = QPushButton("Перейти")
        preset_btn.clicked.connect(self.on_preset_selected)
        preset_layout.addWidget(preset_btn)

        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)

        # Информация
        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout()

        self.info_label = QLabel("Готов к работе")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()

        return panel

    def on_show_location(self):
        """Обработка нажатия кнопки показа локации"""
        try:
            lat = float(self.lat_input.text())
            lon = float(self.lon_input.text())
            zoom = self.zoom_input.value()
            self.location_changed.emit(lat, lon, zoom)
        except ValueError:
            self.show_error("Ошибка", "Неверный формат координат")

    def on_geocode(self):
        """Обработка поиска по адресу"""
        address = self.address_input.text().strip()
        if address:
            self.geocode_requested.emit(address)

    def on_search(self):
        """Обработка поиска мест"""
        query = self.search_input.text().strip()
        if query:
            self.search_requested.emit(query)

    def on_preset_selected(self):
        """Обработка выбора предустановленной локации"""
        preset = self.preset_combo.currentText()
        self.preset_selected.emit(preset)

    def on_result_selected(self, item):
        """Обработка выбора результата поиска"""
        # В PyQt6 используем Qt.ItemDataRole.UserRole
        from PyQt6.QtCore import Qt
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.location_changed.emit(data['lat'], data['lon'], 14)

    def update_map(self, html: str):
        """Обновление HTML карты"""
        self.map_view.setHtml(html)

    def update_coordinates(self, lat: float, lon: float, zoom: int):
        """Обновление полей ввода координат"""
        self.lat_input.setText(f"{lat:.6f}")
        self.lon_input.setText(f"{lon:.6f}")
        self.zoom_input.setValue(zoom)

    def update_search_results(self, results: list):
        """Обновление списка результатов поиска"""
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QListWidgetItem

        self.results_list.clear()
        for result in results:
            item_text = f"{result['display_name']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, result)
            self.results_list.addItem(item)

    def update_info(self, text: str):
        """Обновление информационной панели"""
        self.info_label.setText(text)

    def show_error(self, title: str, message: str):
        """Показать сообщение об ошибке"""
        QMessageBox.critical(self, title, message)

    def show_info(self, title: str, message: str):
        """Показать информационное сообщение"""
        QMessageBox.information(self, title, message)