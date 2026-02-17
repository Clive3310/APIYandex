"""
Конфигурация приложения
"""

# API настройки
NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/search"
REVERSE_GEOCODE_URL = "https://nominatim.openstreetmap.org/reverse"
TILE_SERVER = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"

# Настройки карты по умолчанию
DEFAULT_LATITUDE = 55.7558
DEFAULT_LONGITUDE = 37.6173
DEFAULT_ZOOM = 12

# Ограничения
MIN_ZOOM = 1
MAX_ZOOM = 18
MIN_LATITUDE = -90
MAX_LATITUDE = 90
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180

# UI настройки
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Карта с API (MVC) - PyQt6"

# User Agent для API запросов
USER_AGENT = "MapAppPyQt6/1.0"