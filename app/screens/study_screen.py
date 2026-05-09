from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.animation import Animation
from kivy.metrics import dp, sp
from kivy.clock import Clock

from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField

from app.widgets.card_widget import StudyCard
from app.data.storage import (
    get_deck, get_due_cards, save_card,
    get_cards_by_deck,
)
from app.data.scheduler import sm2_schedule, get_review_order

import uuid


class StudyScreen(Screen):
    """Экран изучения карточек."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_deck_id = None
        self.current_deck = None
        self.cards = []
        self.current_index = 0
        self.current_card_data = None
        self._dialog = None
        self._build_ui()

    def _build_ui(self):
        """Построить интерфейс экрана."""
        self.layout = BoxLayout(orientation="vertical")

        # --- Верхняя панель ---
        self.toolbar = MDTopAppBar(
            title="Изучение",
            md_bg_color=(0.1, 0.1, 0.3, 1),
            specific_text_color=(1, 1, 1, 1),
        )
        self.toolbar.left_action_items = [["arrow-left", lambda x: self._go_back()]]
        self.toolbar.right_action_items = [
            ["dots-vertical", lambda x: self._show_deck_menu()]
        ]
        self.layout.add_widget(self.toolbar)

        # --- Область карточки (заполняет всё свободное место) ---
        self.card_area = RelativeLayout(size_hint=(1, 1))

        # Виджет карточки
        self.card = StudyCard(
            size_hint=(0.85, 0.78),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.card_area.add_widget(self.card)

        # --- Финишный слой (изначально скрыт) ---
        self.finish_layer = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            spacing=dp(20),
            padding=[dp(20), dp(60), dp(20), dp(40)],
            opacity=0,
            disabled=True,
        )

        self.finish_label = MDLabel(
            text="Колода завершена! 🎉\n\nВсе карточки на сегодня\nповторены.",
            halign="center",
            font_style="H4",
        )
        self.finish_layer.add_widget(self.finish_label)

        self.finish_back_btn = MDRaisedButton(
            text="Вернуться к колодам",
            size_hint=(0.7, None),
            height=dp(48),
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self._go_back(),
        )
        self.finish_layer.add_widget(self.finish_back_btn)

        self.card_area.add_widget(self.finish_layer)
        self.layout.add_widget(self.card_area)

        # --- Нижняя панель (фиксированная высота, не перекрывает карточку) ---
        self.bottom_panel = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=dp(130),
            spacing=dp(6),
            padding=[dp(8), dp(4), dp(8), dp(12)],
        )

        # Счётчик прогресса
        self.progress_label = MDLabel(
            text="",
            halign="center",
            size_hint=(1, None),
            height=dp(24),
            theme_text_color="Secondary",
        )
        self.bottom_panel.add_widget(self.progress_label)

        # Кнопка "Показать ответ"
        self.flip_btn = MDRaisedButton(
            text="Показать ответ",
            pos_hint={"center_x": 0.5},
            size_hint=(0.7, None),
            height=dp(48),
            on_release=lambda x: self._flip_card(),
        )
        self.bottom_panel.add_widget(self.flip_btn)

        # Кнопки оценки
        self.rate_layout = BoxLayout(
            orientation="horizontal",
            spacing=dp(6),
            size_hint=(1, None),
            height=dp(48),
        )

        self.btn_again = MDFlatButton(
            text="Снова",
            md_bg_color=(0.85, 0.15, 0.15, 1),
            text_color=(1, 1, 1, 1),
            size_hint=(0.25, 1),
            on_release=lambda x: self._rate_card(1),
        )
        self.btn_hard = MDFlatButton(
            text="Тяжело",
            md_bg_color=(0.85, 0.55, 0.05, 1),
            text_color=(1, 1, 1, 1),
            size_hint=(0.25, 1),
            on_release=lambda x: self._rate_card(3),
        )
        self.btn_good = MDFlatButton(
            text="Хорошо",
            md_bg_color=(0.15, 0.65, 0.15, 1),
            text_color=(1, 1, 1, 1),
            size_hint=(0.25, 1),
            on_release=lambda x: self._rate_card(4),
        )
        self.btn_easy = MDFlatButton(
            text="Легко",
            md_bg_color=(0.05, 0.45, 0.85, 1),
            text_color=(1, 1, 1, 1),
            size_hint=(0.25, 1),
            on_release=lambda x: self._rate_card(5),
        )

        self.rate_layout.add_widget(self.btn_again)
        self.rate_layout.add_widget(self.btn_hard)
        self.rate_layout.add_widget(self.btn_good)
        self.rate_layout.add_widget(self.btn_easy)
        self.rate_layout.opacity = 0

        self.bottom_panel.add_widget(self.rate_layout)
        self.layout.add_widget(self.bottom_panel)

        self.add_widget(self.layout)

    # ===================== ЗАГРУЗКА =====================

    def load_deck(self, deck_id: str):
        """Загрузить колоду для изучения."""
        self.current_deck_id = deck_id
        self.current_deck = get_deck(deck_id)
        if self.current_deck:
            self.toolbar.title = self.current_deck.get("title", "Изучение")

        all_cards = get_due_cards(deck_id)
        self.cards = get_review_order(all_cards)
        self.current_index = 0

        # Сбросить видимость
        self.finish_layer.opacity = 0
        self.finish_layer.disabled = True
        self.card.opacity = 1
        self.card.disabled = False
        self.bottom_panel.opacity = 1
        self.bottom_panel.disabled = False

        self._show_current_card()

    def _show_current_card(self):
        """Показать текущую карточку."""
        if self.current_index >= len(self.cards):
            self._show_finished()
            return

        self.current_card_data = self.cards[self.current_index]
        self.card.front_text = self.current_card_data.get("front", "")
        self.card.back_text = self.current_card_data.get("back", "")
        self.card.front_image = self.current_card_data.get("front_image", "")
        self.card.back_image = self.current_card_data.get("back_image", "")
        self.card.is_flipped = False
        self.card._answer_visible = False
        self.card.reset_zoom()

        # Сбросить на лицевую сторону
        self.card.card_label.text = self.card.front_text
        self.card.card_label.color = (1, 1, 1, 1)
        self.card._set_image(self.card.front_image)

        # Показать кнопку переворота, скрыть кнопки оценки
        self.flip_btn.opacity = 1
        self.flip_btn.disabled = False
        self.rate_layout.opacity = 0

        # Обновить прогресс
        total = len(self.cards)
        current = self.current_index + 1
        self.progress_label.text = f"Карточка {current} из {total}"

    # ===================== ПЕРЕВОРОТ =====================

    def _flip_card(self):
        """Перевернуть карточку — показать ответ."""
        if self.card._answer_visible:
            return
        self.card.flip_card()

        self.flip_btn.opacity = 0
        self.flip_btn.disabled = True
        self.rate_layout.opacity = 1

    # ===================== ОЦЕНКА =====================

    def _rate_card(self, quality: int):
        """Оценить карточку и перейти к следующей."""
        if not self.current_card_data:
            return

        updated_card = sm2_schedule(self.current_card_data, quality)
        save_card(updated_card)

        self.rate_layout.opacity = 0
        self.current_index += 1
        self._show_current_card()

    # ===================== ЗАВЕРШЕНИЕ =====================

    def _show_finished(self):
        """Показать экран завершения — карточка и кнопки исчезают."""
        self.card.opacity = 0
        self.card.disabled = True
        self.bottom_panel.opacity = 0
        self.bottom_panel.disabled = True
        self.rate_layout.opacity = 0
        self.flip_btn.opacity = 0

        self.finish_layer.opacity = 1
        self.finish_layer.disabled = False

    # ===================== ВОЗВРАТ =====================

    def _go_back(self):
        """Вернуться на экран колод."""
        self.finish_layer.opacity = 0
        self.finish_layer.disabled = True
        self.card.opacity = 1
        self.card.disabled = False
        self.bottom_panel.opacity = 1
        self.bottom_panel.disabled = False

        self.manager.current = "decks"

    # ===================== УПРАВЛЕНИЕ КАРТОЧКАМИ =====================

    def _show_deck_menu(self):
        """Показать список карточек + кнопку добавления."""
        self._show_manage_deck_dialog()

    # ===================== СПИСОК КАРТОЧЕК =====================

    def _show_manage_deck_dialog(self):
        """Диалог: список карточек + кнопка 'Добавить карточку'."""
        cards = get_cards_by_deck(self.current_deck_id)

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
            height=min(dp(450), len(cards) * dp(38) + dp(60)),
        )

        # Кнопка добавления — всегда первая
        add_btn = MDRaisedButton(
            text="＋ Добавить карточку",
            size_hint=(1, None),
            height=dp(42),
            md_bg_color=(0.1, 0.5, 0.1, 1),  # зелёная
            on_release=lambda x: self._show_add_card_dialog(),
        )
        content.add_widget(add_btn)

        if not cards:
            info = MDLabel(
                text="Нет карточек. Нажмите ＋ чтобы добавить.",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(40),
            )
            content.add_widget(info)
        else:
            for card in cards[:14]:
                text = card.get("front", "???")[:35]
                btn = MDRaisedButton(
                    text=text,
                    size_hint=(1, None),
                    height=dp(36),
                    on_release=lambda x, c=card: self._show_card_detail(c),
                )
                content.add_widget(btn)

            if len(cards) > 14:
                info = MDLabel(
                    text=f"... и ещё {len(cards) - 14} карточек",
                    halign="center",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(28),
                )
                content.add_widget(info)

        self._dialog = MDDialog(
            title=f"Управление колодой ({len(cards)} карточек)",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="ЗАКРЫТЬ",
                    on_release=lambda x: self._dialog.dismiss(),
                ),
            ],
        )
        self._dialog.open()

    # ===================== ДОБАВЛЕНИЕ КАРТОЧКИ =====================

    def _show_add_card_dialog(self):
        """Диалог добавления новой карточки."""
        if self._dialog:
            self._dialog.dismiss()
            self._dialog = None

        front_field = MDTextField(hint_text="Вопрос (лицевая сторона)*")
        back_field = MDTextField(hint_text="Ответ (обратная сторона)*")
        front_img_field = MDTextField(hint_text="Путь к картинке вопроса (опционально)")
        back_img_field = MDTextField(hint_text="Путь к картинке ответа (опционально)")

        info_label = MDLabel(
            text="Формат: data/images/photo.jpg\nили URL: https://example.com/img.png",
            halign="left",
            theme_text_color="Secondary",
            font_size=sp(12),
            size_hint_y=None,
            height=dp(40),
        )

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
            height=dp(320),
        )
        content.add_widget(front_field)
        content.add_widget(back_field)
        content.add_widget(front_img_field)
        content.add_widget(back_img_field)
        content.add_widget(info_label)

        self._dialog = MDDialog(
            title="Новая карточка",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="ОТМЕНА",
                    on_release=lambda x: self._show_manage_deck_dialog(),
                ),
                MDRaisedButton(
                    text="ДОБАВИТЬ",
                    on_release=lambda x: self._add_card(
                        front_field.text.strip(),
                        back_field.text.strip(),
                        front_img_field.text.strip(),
                        back_img_field.text.strip(),
                    ),
                ),
            ],
        )
        self._dialog.open()

    def _add_card(self, front: str, back: str, front_img: str, back_img: str):
        """Добавить новую карточку в текущую колоду и снова открыть диалог."""
        if not front or not back:
            return

        card = {
            "id": f"card_{uuid.uuid4().hex[:8]}",
            "deck_id": self.current_deck_id,
            "front": front,
            "back": back,
            "front_image": front_img,
            "back_image": back_img,
            "repetitions": 0,
            "interval": 0,
            "ease_factor": 2.5,
            "next_review": None,
            "last_reviewed": None,
        }
        save_card(card)

        # Добавить в текущий список изучения
        if self.cards is not None:
            self.cards.append(card)

        # Закрыть диалог и сразу открыть снова для следующей карточки
        if self._dialog:
            self._dialog.dismiss()
            self._dialog = None

        # Автоматически открыть снова для быстрого добавления
        Clock.schedule_once(lambda dt: self._show_add_card_dialog(), 0.1)

    # ===================== РЕДАКТИРОВАНИЕ КАРТОЧКИ =====================

    def _show_card_detail(self, card: dict):
        """Диалог просмотра и редактирования карточки."""
        if self._dialog:
            self._dialog.dismiss()
            self._dialog = None

        front_field = MDTextField(
            hint_text="Вопрос",
            text=card.get("front", ""),
        )
        back_field = MDTextField(
            hint_text="Ответ",
            text=card.get("back", ""),
        )

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
            height=dp(160),
        )
        content.add_widget(front_field)
        content.add_widget(back_field)

        self._dialog = MDDialog(
            title="Редактирование карточки",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="НАЗАД",
                    on_release=lambda x: self._show_manage_deck_dialog(),
                ),
                MDRaisedButton(
                    text="СОХРАНИТЬ",
                    on_release=lambda x: self._save_card_changes(
                        card,
                        front_field.text.strip(),
                        back_field.text.strip(),
                    ),
                ),
            ],
        )
        self._dialog.open()

    def _save_card_changes(self, card: dict, front: str, back: str):
        """Сохранить изменения в карточке."""
        if not front or not back:
            return

        card["front"] = front
        card["back"] = back
        save_card(card)

        if self._dialog:
            self._dialog.dismiss()
            self._dialog = None

        # Вернуться к списку
        self._show_manage_deck_dialog()
