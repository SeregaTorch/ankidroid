from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDFloatingActionButton, MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard

from app.data.storage import get_all_decks, save_deck, get_cards_by_deck
from kivy.app import App


class DeckCard(MDCard):
    """Карточка колоды для списка."""

    def __init__(self, deck_data: dict, **kwargs):
        super().__init__(**kwargs)
        self.deck_data = deck_data
        self.orientation = "vertical"
        self.padding = dp(12)
        self.size_hint_y = None
        self.height = dp(80)
        self.spacing = dp(4)
        self.radius = dp(12)
        self.md_bg_color = (0.15, 0.15, 0.3, 1)
        self.ripple_behavior = True
        self.on_release = self._open_deck

        # Название колоды
        title = deck_data.get("title", "Без названия")
        self.title_label = MDLabel(
            text=title,
            font_style="H6",
            size_hint_y=None,
            height=dp(28),
        )
        self.add_widget(self.title_label)

        # Описание
        desc = deck_data.get("description", "")
        if desc:
            desc_label = MDLabel(
                text=desc,
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(20),
                font_size=dp(13),
            )
            self.add_widget(desc_label)

        # Количество карточек
        card_count = len(get_cards_by_deck(deck_data["id"]))
        count_label = MDLabel(
            text=f"Карточек: {card_count}",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(18),
            font_size=dp(12),
        )
        self.add_widget(count_label)

    def _open_deck(self):
        """Открыть колоду для изучения."""
        app = App.get_running_app()
        study_screen = app.root.get_screen("study")
        study_screen.load_deck(self.deck_data["id"])
        app.root.current = "study"


class DeckScreen(Screen):
    """Экран выбора колоды."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dialog = None
        self._build_ui()

    def _build_ui(self):
        """Построить интерфейс экрана."""
        from kivymd.uix.toolbar import MDTopAppBar

        self.layout = BoxLayout(orientation="vertical")

        # Верхняя панель
        toolbar = MDTopAppBar(
            title="AnkiDroid",
            md_bg_color=(0.1, 0.1, 0.3, 1),
            specific_text_color=(1, 1, 1, 1),
        )
        self.layout.add_widget(toolbar)

        # ScrollView со списком колод
        self.scroll = MDScrollView()
        self.list_layout = BoxLayout(
            orientation="vertical",
            padding=[dp(12), dp(8), dp(12), dp(8)],
            spacing=dp(8),
            size_hint_y=None,
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.scroll.add_widget(self.list_layout)
        self.layout.add_widget(self.scroll)

        # Кнопка добавления колоды
        add_btn = MDFloatingActionButton(
            icon="plus",
            pos_hint={"center_x": 0.9, "center_y": 0.1},
            on_release=self._show_add_deck_dialog,
        )
        self.layout.add_widget(add_btn)

        self.add_widget(self.layout)

    def on_enter(self):
        self._refresh_decks()

    def _refresh_decks(self):
        """Обновить список колод."""
        self.list_layout.clear_widgets()
        decks = get_all_decks()

        if not decks:
            label = MDLabel(
                text="Нет колод.\nНажмите + чтобы добавить",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(200),
            )
            self.list_layout.add_widget(label)
            return

        for deck in decks:
            card = DeckCard(deck_data=deck)
            self.list_layout.add_widget(card)

    def _show_add_deck_dialog(self, *args):
        """Показать диалог добавления новой колоды."""
        title_field = MDTextField(hint_text="Название колоды*")
        desc_field = MDTextField(hint_text="Описание (необязательно)")

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(160),
        )
        content.add_widget(title_field)
        content.add_widget(desc_field)

        self._dialog = MDDialog(
            title="Новая колода",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="ОТМЕНА",
                    on_release=lambda x: self._dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="СОЗДАТЬ",
                    on_release=lambda x: self._create_deck(
                        title_field.text,
                        desc_field.text,
                    ),
                ),
            ],
        )
        self._dialog.open()

    def _create_deck(self, title: str, description: str):
        """Создать новую колоду."""
        if not title.strip():
            return

        import uuid
        deck = {
            "id": f"deck_{uuid.uuid4().hex[:8]}",
            "title": title.strip(),
            "description": description.strip(),
            "created": "2025-01-01T00:00:00",
        }
        save_deck(deck)
        if self._dialog:
            self._dialog.dismiss()
            self._dialog = None
        self._refresh_decks()
