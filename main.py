#!/usr/bin/env python3
"""
AnkiDroid — приложение для изучения карточек с интервальными повторениями.
Основано на Kivy/KivyMD, поддерживает pinch-to-zoom.

Запуск:
    python main.py
"""

import sys
import os

# Добавляем корневую папку проекта в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main_app import AnkiDroidApp


def main():
    app = AnkiDroidApp()
    app.run()


if __name__ == "__main__":
    main()
