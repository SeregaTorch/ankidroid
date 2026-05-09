import json
import os
from datetime import datetime, timedelta
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")


def _get_data_path(filename: str) -> str:
    """Получить полный путь к файлу данных."""
    return os.path.join(DATA_DIR, filename)


def load_json(filename: str) -> list | dict:
    """Загрузить JSON-файл из папки data/."""
    path = _get_data_path(filename)
    if not os.path.exists(path):
        return [] if filename.endswith("s.json") else {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filename: str, data: list | dict) -> None:
    """Сохранить данные в JSON-файл в папку data/."""
    path = _get_data_path(filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------
# Decks
# ---------------------------------------------------------------------

def get_all_decks() -> list[dict]:
    """Получить список всех колод."""
    return load_json("decks.json")


def get_deck(deck_id: str) -> Optional[dict]:
    """Получить колоду по ID."""
    decks = get_all_decks()
    for deck in decks:
        if deck["id"] == deck_id:
            return deck
    return None


def save_deck(deck: dict) -> None:
    """Сохранить или обновить колоду."""
    decks = get_all_decks()
    for i, d in enumerate(decks):
        if d["id"] == deck["id"]:
            decks[i] = deck
            break
    else:
        decks.append(deck)
    save_json("decks.json", decks)


# ---------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------

def get_all_cards() -> list[dict]:
    """Получить список всех карточек."""
    return load_json("cards.json")


def get_cards_by_deck(deck_id: str) -> list[dict]:
    """Получить карточки для конкретной колоды."""
    cards = get_all_cards()
    return [c for c in cards if c.get("deck_id") == deck_id]


def get_card(card_id: str) -> Optional[dict]:
    """Получить карточку по ID."""
    cards = get_all_cards()
    for card in cards:
        if card["id"] == card_id:
            return card
    return None


def save_card(card: dict) -> None:
    """Сохранить или обновить карточку."""
    cards = get_all_cards()
    for i, c in enumerate(cards):
        if c["id"] == card["id"]:
            cards[i] = card
            break
    else:
        cards.append(card)
    save_json("cards.json", cards)


def get_due_cards(deck_id: str) -> list[dict]:
    """Получить карточки, запланированные для повторения сегодня."""
    cards = get_cards_by_deck(deck_id)
    today = datetime.now().date()
    due = []
    for card in cards:
        next_review = card.get("next_review")
        if next_review is None:
            due.append(card)
        else:
            try:
                review_date = datetime.fromisoformat(next_review).date()
                if review_date <= today:
                    due.append(card)
            except (ValueError, TypeError):
                due.append(card)
    return due
