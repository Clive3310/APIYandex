"""
Клиент для работы с API
"""

import requests
from typing import Dict, Optional, List
import config


class APIClient:
    """Клиент для работы с картографическими API"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT
        })

    def geocode(self, address: str) -> Optional[Dict]:
        """
        Геокодирование адреса (преобразование адреса в координаты)

        Args:
            address: Адрес для поиска

        Returns:
            Словарь с данными о локации или None
        """
        try:
            params = {
                'q': address,
                'format': 'json',
                'limit': 1
            }

            response = self.session.get(
                config.NOMINATIM_API_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            if data:
                return {
                    'lat': float(data[0]['lat']),
                    'lon': float(data[0]['lon']),
                    'display_name': data[0]['display_name']
                }
            return None

        except Exception as e:
            print(f"Ошибка геокодирования: {e}")
            return None

    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """
        Обратное геокодирование (преобразование координат в адрес)

        Args:
            lat: Широта
            lon: Долгота

        Returns:
            Адрес или None
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json'
            }

            response = self.session.get(
                config.REVERSE_GEOCODE_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            return data.get('display_name', 'Адрес не найден')

        except Exception as e:
            print(f"Ошибка обратного геокодирования: {e}")
            return None

    def search_places(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Поиск мест по запросу

        Args:
            query: Поисковый запрос
            limit: Максимальное количество результатов

        Returns:
            Список найденных мест
        """
        try:
            params = {
                'q': query,
                'format': 'json',
                'limit': limit
            }

            response = self.session.get(
                config.NOMINATIM_API_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            return [
                {
                    'lat': float(item['lat']),
                    'lon': float(item['lon']),
                    'display_name': item['display_name'],
                    'type': item.get('type', 'unknown')
                }
                for item in data
            ]

        except Exception as e:
            print(f"Ошибка поиска: {e}")
            return []