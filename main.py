#!/usr/bin/env python3
"""
AnkiDroid — приложение для изучения карточек с интервальными повторениями.
Основано на Kivy/KivyMD, поддерживает pinch-to-zoom.

Запуск:
    python main.py
"""

import sys
import os
import traceback

# Добавляем корневую папку проекта в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main_app import AnkiDroidApp


def main():
    try:
        app = AnkiDroidApp()
        app.run()
    except Exception as e:
        # Запись ошибки в файл (на Android можно найти через logcat)
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash.log"), "w") as f:
            f.write(f"Error: {e}\n")
            traceback.print_exc(file=f)
        raise


if __name__ == "__main__":
    main()
