from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.core.window import Window

# Настройки окна для Windows (будет игнорироваться на Android)
Window.size = (400, 700)
Window.minimum_width = 360
Window.minimum_height = 600


class AnkiDroidApp(MDApp):
    """Главное приложение AnkiDroid."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = ScreenManager()

    def build(self):
        """Построить приложение."""
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.primary_hue = "700"

        # Импортируем экраны здесь, чтобы избежать циклических импортов
        from app.screens.deck_screen import DeckScreen
        from app.screens.study_screen import StudyScreen

        # Экран выбора колоды
        deck_screen = DeckScreen(name="decks")
        self.screen_manager.add_widget(deck_screen)

        # Экран изучения
        study_screen = StudyScreen(name="study")
        self.screen_manager.add_widget(study_screen)

        return self.screen_manager
