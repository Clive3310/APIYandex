"""
Контроллер для управления картой
"""

from model.map_model import MapModel, Location
from view.map_view import MapView
from typing import Dict


class MapController:
    """Контроллер приложения карты"""

    # Предустановленные локации
    PRESETS = {
        "Москва": (55.7558, 37.6173, 12),
        "Санкт-Петербург": (59.9343, 30.3351, 12),
        "Париж": (48.8566, 2.3522, 12),
        "Лондон": (51.5074, -0.1278, 12),
        "Нью-Йорк": (40.7128, -74.0060, 11),
        "Токио": (35.6762, 139.6503, 12),
        "Сидней": (-33.8688, 151.2093, 12)
    }

    def __init__(self):
        self.model = MapModel()
        self.view = MapView()

        # Подключение сигналов к слотам
        self.connect_signals()

        # Показ начальной карты
        self.update_map()

    def connect_signals(self):
        """Подключение сигналов от view к методам контроллера"""
        self.view.location_changed.connect(self.on_location_changed)
        self.view.search_requested.connect(self.on_search_requested)
        self.view.geocode_requested.connect(self.on_geocode_requested)
        self.view.preset_selected.connect(self.on_preset_selected)

    def on_location_changed(self, lat: float, lon: float, zoom: int):
        """Обработка изменения локации"""
        if self.model.set_location(lat, lon, zoom):
            self.update_map()
            # Получить адрес для координат
            address = self.model.get_address(lat, lon)
            if address:
                self.view.update_info(f"Адрес: {address}")
        else:
            self.view.show_error("Ошибка", "Неверные координаты или масштаб")

    def on_geocode_requested(self, address: str):
        """Обработка запроса геокодирования"""
        self.view.update_info(f"Поиск адреса: {address}...")

        location = self.model.geocode_address(address)
        if location:
            self.model.set_location(
                location.latitude,
                location.longitude,
                location.zoom,
                location.name
            )
            self.view.update_coordinates(
                location.latitude,
                location.longitude,
                location.zoom
            )
            self.update_map()
            self.view.update_info(f"Найдено: {location.name}")
        else:
            self.view.show_error("Ошибка", "Адрес не найден")
            self.view.update_info("Адрес не найден")

    def on_search_requested(self, query: str):
        """Обработка запроса поиска мест"""
        self.view.update_info(f"Поиск: {query}...")

        results = self.model.search(query)
        if results:
            self.view.update_search_results(results)
            self.view.update_info(f"Найдено результатов: {len(results)}")
        else:
            self.view.update_search_results([])
            self.view.update_info("Ничего не найдено")

    def on_preset_selected(self, preset_name: str):
        """Обработка выбора предустановленной локации"""
        if preset_name in self.PRESETS:
            lat, lon, zoom = self.PRESETS[preset_name]
            self.model.set_location(lat, lon, zoom, preset_name)
            self.view.update_coordinates(lat, lon, zoom)
            self.update_map()
            self.view.update_info(f"Локация: {preset_name}")

    def generate_map_html(self) -> str:
        """Генерация HTML кода карты"""
        location = self.model.get_location()
        markers = self.model.get_markers()

        # Создание маркеров
        markers_js = ""
        for marker in markers:
            markers_js += f"""
            L.marker([{marker['lat']}, {marker['lon']}])
                .addTo(map)
                .bindPopup("{marker['title']}");
            """

        # Главный маркер
        main_marker = f"""
        var mainMarker = L.marker([{location.latitude}, {location.longitude}], {{
            icon: L.icon({{
                iconUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNSIgaGVpZ2h0PSI0MSIgdmlld0JveD0iMCAwIDI1IDQxIj48cGF0aCBmaWxsPSIjRUQxQzI0IiBkPSJNMTIuNSAwQzUuNiAwIDAgNS42IDAgMTIuNWMwIDEuNCAwLjIgMi44IDAuNyA0LjFMMTIuNSA0MWwxMS44LTI0LjRjMC40LTEuMyAwLjctMi43IDAuNy00LjFDMjUgNS42IDE5LjQgMCAxMi41IDB6IE0xMi41IDE3LjhjLTIuOSAwLTUuMy0yLjQtNS4zLTUuM3MyLjQtNS4zIDUuMy01LjMgNS4zIDIuNCA1LjMgNS4zUzE1LjQgMTcuOCAxMi41IDE3Ljh6Ii8+PC9zdmc+',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34]
            }})
        }}).addTo(map);

        mainMarker.bindPopup(`
            <b>Текущая локация</b><br>
            Широта: {location.latitude:.6f}<br>
            Долгота: {location.longitude:.6f}<br>
            {f'<i>{location.name}</i>' if location.name else ''}
        `).openPopup();
        """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                body {{ 
                    margin: 0; 
                    padding: 0; 
                    font-family: Arial, sans-serif;
                }}
                #map {{ 
                    width: 100%; 
                    height: 100vh; 
                }}
                .leaflet-popup-content {{
                    font-size: 14px;
                }}
                .leaflet-control-attribution {{
                    font-size: 10px;
                }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                // Создание карты
                var map = L.map('map').setView([{location.latitude}, {location.longitude}], {location.zoom});

                // Добавление тайлов
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                    maxZoom: 19
                }}).addTo(map);

                // Главный маркер
                {main_marker}

                // Дополнительные маркеры
                {markers_js}

                // Круг вокруг точки
                var circle = L.circle([{location.latitude}, {location.longitude}], {{
                    color: 'red',
                    fillColor: '#f03',
                    fillOpacity: 0.2,
                    radius: 500
                }}).addTo(map);

                // Обработка кликов по карте
                map.on('click', function(e) {{
                    console.log('Clicked at: ' + e.latlng);
                }});

                // Добавление контроля масштаба
                L.control.scale({{imperial: false, metric: true}}).addTo(map);
            </script>
        </body>
        </html>
        """
        return html

    def update_map(self):
        """Обновление отображения карты"""
        html = self.generate_map_html()
        self.view.update_map(html)

    def show(self):
        """Показать окно приложения"""
        self.view.show()