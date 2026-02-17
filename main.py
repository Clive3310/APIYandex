"""
Точка входа в приложение
"""

import sys
from PyQt6.QtWidgets import QApplication
from controller.map_controller import MapController


def main():
    """Главная функция запуска приложения"""
    app = QApplication(sys.argv)

    # Установка стиля приложения
    app.setStyle('Fusion')

    # Создание контроллера (который создаст модель и представление)
    controller = MapController()
    controller.show()

    sys.exit(app.exec())  # В PyQt6 exec() вместо exec_()


if __name__ == '__main__':
    main()