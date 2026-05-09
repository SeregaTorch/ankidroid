from datetime import datetime, timedelta
import random


def sm2_schedule(card: dict, quality: int) -> dict:
    """
    Алгоритм интервальных повторений SM-2.

    quality — оценка пользователя (0-5):
        0-1: Снова (полный сброс)
        2-3: Тяжело (частичное увеличение)
        4:   Хорошо (стандартное увеличение)
        5:   Легко (максимальное увеличение)
    """
    card = card.copy()

    # Получаем или инициализируем параметры
    repetitions = card.get("repetitions", 0)
    interval = card.get("interval", 0)
    ease_factor = card.get("ease_factor", 2.5)

    if quality < 2:
        # Сброс — карточка отправляется на повтор сегодня или завтра
        repetitions = 0
        interval = 0
        ease_factor = max(1.3, ease_factor - 0.2)
        next_review = datetime.now() + timedelta(minutes=10)
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)

        repetitions += 1

        # Корректировка ease_factor
        ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ease_factor = max(1.3, ease_factor)

        next_review = datetime.now() + timedelta(days=interval)

    card["repetitions"] = repetitions
    card["interval"] = interval
    card["ease_factor"] = round(ease_factor, 2)
    card["next_review"] = next_review.isoformat()
    card["last_reviewed"] = datetime.now().isoformat()

    return card


def get_review_order(cards: list[dict]) -> list[dict]:
    """
    Возвращает карточки в порядке приоритета для изучения.
    Новые карточки (без повторений) перемешиваются случайно.
    Те, которые нужно повторить, идут в порядке возрастания интервала.
    """
    new_cards = [c for c in cards if c.get("repetitions", 0) == 0]
    review_cards = [c for c in cards if c.get("repetitions", 0) > 0]

    random.shuffle(new_cards)
    review_cards.sort(key=lambda c: c.get("interval", 0))

    return review_cards + new_cards
