"""
Модель данных карты
"""

from typing import Optional, List, Dict
from dataclasses import dataclass
import config
from utils.api_client import APIClient


@dataclass
class Location:
    """Класс для представления локации"""
    latitude: float
    longitude: float
    zoom: int
    name: Optional[str] = None

    def is_valid(self) -> bool:
        """Проверка валидности координат"""
        return (config.MIN_LATITUDE <= self.latitude <= config.MAX_LATITUDE and
                config.MIN_LONGITUDE <= self.longitude <= config.MAX_LONGITUDE and
                config.MIN_ZOOM <= self.zoom <= config.MAX_ZOOM)


class MapModel:
    """Модель для работы с данными карты"""

    def __init__(self):
        self.api_client = APIClient()
        self.current_location = Location(
            latitude=config.DEFAULT_LATITUDE,
            longitude=config.DEFAULT_LONGITUDE,
            zoom=config.DEFAULT_ZOOM,
            name="Москва"
        )
        self.markers: List[Dict] = []
        self.search_results: List[Dict] = []

    def set_location(self, lat: float, lon: float, zoom: int, name: str = None) -> bool:
        """
        Установить текущую локацию

        Args:
            lat: Широта
            lon: Долгота
            zoom: Масштаб
            name: Название локации

        Returns:
            True если локация валидна и установлена
        """
        location = Location(lat, lon, zoom, name)
        if location.is_valid():
            self.current_location = location
            return True
        return False

    def get_location(self) -> Location:
        """Получить текущую локацию"""
        return self.current_location

    def geocode_address(self, address: str) -> Optional[Location]:
        """
        Получить координаты по адресу

        Args:
            address: Адрес для поиска

        Returns:
            Объект Location или None
        """
        result = self.api_client.geocode(address)
        if result:
            return Location(
                latitude=result['lat'],
                longitude=result['lon'],
                zoom=self.current_location.zoom,
                name=result['display_name']
            )
        return None

    def get_address(self, lat: float, lon: float) -> Optional[str]:
        """
        Получить адрес по координатам

        Args:
            lat: Широта
            lon: Долгота

        Returns:
            Адрес или None
        """
        return self.api_client.reverse_geocode(lat, lon)

    def search(self, query: str) -> List[Dict]:
        """
        Поиск мест

        Args:
            query: Поисковый запрос

        Returns:
            Список найденных мест
        """
        self.search_results = self.api_client.search_places(query)
        return self.search_results

    def add_marker(self, lat: float, lon: float, title: str = ""):
        """Добавить маркер на карту"""
        self.markers.append({
            'lat': lat,
            'lon': lon,
            'title': title
        })

    def clear_markers(self):
        """Очистить все маркеры"""
        self.markers.clear()

    def get_markers(self) -> List[Dict]:
        """Получить все маркеры"""
        return self.markers