from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.metrics import sp, dp
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle
import os


class ZoomableCard(BoxLayout):
    """
    Виджет карточки с поддержкой pinch-to-zoom.
    ScatterLayout находится ВНУТРИ, чтобы не перехватывать события кнопок.
    Текст центрирован по середине.
    """

    front_text = StringProperty("")
    back_text = StringProperty("")
    front_image = StringProperty("")
    back_image = StringProperty("")
    is_flipped = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # ScatterLayout для pinch-to-zoom
        self.scatter = ScatterLayout(
            do_rotation=False,
            do_translation=True,
            do_scale=True,
            scale_min=0.5,
            scale_max=3.0,
            translation_touches=2,
            size_hint=(1, 1),
        )

        self._my_last_touch_time = 0
        self._my_last_touch_pos = (0, 0)

        # Внутренняя часть карточки (фон + изображение + текст)
        self.card_inner = RelativeLayout(size_hint=(1, 1))

        # Рисуем фон — скруглённый прямоугольник
        with self.card_inner.canvas.before:
            Color(0.15, 0.15, 0.25, 1)
            self.bg_rect = RoundedRectangle(
                pos=self.card_inner.pos,
                size=self.card_inner.size,
                radius=[dp(16)],
            )

        def update_bg(inst, val):
            self.bg_rect.pos = inst.pos
            self.bg_rect.size = inst.size
        self.card_inner.bind(pos=update_bg, size=update_bg)

        # Изображение (фон внутри карточки)
        self.card_image = Image(
            size_hint=(1, 1),
            mipmap=True,
            opacity=0,
        )
        self.card_inner.add_widget(self.card_image)

        # Текст карточки — ПО ЦЕНТРУ
        self.card_label = Label(
            text=self.front_text,
            font_size=sp(20),
            halign="center",
            valign="middle",
            color=(1, 1, 1, 1),
        )
        # Привязываем text_size к размеру Label, чтобы текст был ровно по центру
        self.card_label.bind(
            size=lambda lbl, _: setattr(lbl, "text_size", lbl.size)
        )
        self.card_inner.add_widget(self.card_label)

        self.scatter.add_widget(self.card_inner)
        self.add_widget(self.scatter)

    # --- Свойства ---

    def on_front_text(self, instance, value):
        if hasattr(self, "card_label") and not self.is_flipped:
            self.card_label.text = value

    def on_back_text(self, instance, value):
        if hasattr(self, "card_label") and self.is_flipped:
            self.card_label.text = value

    def on_front_image(self, instance, value):
        if hasattr(self, "card_image") and not self.is_flipped:
            self._set_image(value)

    def on_back_image(self, instance, value):
        if hasattr(self, "card_image") and self.is_flipped:
            self._set_image(value)

    def _set_image(self, path):
        if path and (os.path.exists(path) or path.startswith(("http://", "https://"))):
            self.card_image.source = path
            self.card_image.opacity = 0.5
        else:
            self.card_image.source = ""
            self.card_image.opacity = 0

    def flip_card(self):
        self.is_flipped = not self.is_flipped
        if self.is_flipped:
            self.card_label.text = self.back_text
            self._set_image(self.back_image)
        else:
            self.card_label.text = self.front_text
            self._set_image(self.front_image)

    # --- Обработка касаний для ScatterLayout ---

    def on_touch_down(self, touch):
        # Проверяем, касание внутри нашего виджета
        if not self.collide_point(touch.x, touch.y):
            return False

        # Пробрасываем двойной тап в ScatterLayout
        now = Clock.get_time()
        dt = now - self._my_last_touch_time
        dx = abs(touch.x - self._my_last_touch_pos[0])
        dy = abs(touch.y - self._my_last_touch_pos[1])

        if dt < 0.3 and dx < dp(50) and dy < dp(50):
            self._my_last_touch_time = 0
            self._on_double_tap(touch)
            return True

        self._my_last_touch_time = now
        self._my_last_touch_pos = (touch.x, touch.y)

        # Пробрасываем касание в scatter (для зума)
        return self.scatter.on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self.scatter:
            return self.scatter.on_touch_move(touch)
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self.scatter:
            return self.scatter.on_touch_up(touch)
        return super().on_touch_up(touch)

    def _on_double_tap(self, touch):
        anim = Animation(scale=1.0, x=0, y=0, duration=0.3)
        anim.start(self.scatter)

    def reset_zoom(self):
        anim = Animation(scale=1.0, x=0, y=0, duration=0.3)
        anim.start(self.scatter)


class StudyCard(ZoomableCard):
    on_show_answer = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._answer_visible = False

    def flip_card(self):
        super().flip_card()
        self._answer_visible = not self._answer_visible
        if self._answer_visible and self.on_show_answer:
            self.on_show_answer()
