import csv
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import srv
from cypher import (
    decrypt_message,
    encrypt_message,
    get_available_algorithms,
    normalize_algorithm,
)


@pytest.fixture()
def client(tmp_path, monkeypatch):
    csv_path = tmp_path / "messages.csv"
    monkeypatch.setattr(srv, "CSV_FILE", csv_path)
    srv.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with srv.app.test_client() as test_client:
        yield test_client, csv_path


def test_all_registered_algorithms_roundtrip():
    source = "Привет, Cipher Web 123!"
    algorithm_ids = {algorithm["id"] for algorithm in get_available_algorithms()}

    assert {"caesar", "atbash", "vigenere"}.issubset(algorithm_ids)

    for algorithm_id in algorithm_ids:
        encrypted = encrypt_message(source, algorithm=algorithm_id)
        assert decrypt_message(encrypted, algorithm=algorithm_id) == source


def test_unknown_algorithm_falls_back_to_caesar():
    assert normalize_algorithm("unknown") == "caesar"


def test_main_routes_and_visual_requirements(client):
    test_client, _csv_path = client

    response = test_client.get("/")
    assert response.status_code == 302

    response = test_client.get(f"/{srv.STUDENT_ID}")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Cipher Web" in html
    assert "Шифрование сообщений" in html
    assert "data-sidebar-toggle" in html
    assert "sidebar-collapsed" in html
    assert "v4.2 · Атбаш · светлая тема" not in html
    assert "Студенческий проект" not in html
    assert "Настройки" not in html
    assert "Виженер" in html
    assert "algorithm-stats-scroll" in html


@pytest.mark.parametrize("algorithm", ["caesar", "atbash", "vigenere"])
def test_post_message_for_each_algorithm(client, algorithm):
    test_client, csv_path = client
    text = f"Сообщение для {algorithm}"

    response = test_client.post(
        f"/{srv.STUDENT_ID}",
        data={"text": text, "algorithm": algorithm},
        follow_redirects=False,
    )

    assert response.status_code == 302

    rows = list(csv.reader(csv_path.open("r", encoding="utf-8", newline="")))
    assert len(rows) == 1
    assert rows[0][3] == algorithm
    assert rows[0][4] != text

    messages = srv.read_messages()
    assert len(messages) == 1
    assert messages[0]["text"] == text
    assert messages[0]["algorithm"] == algorithm


def test_stats_are_dynamic_and_admin_is_left_metric(client):
    _test_client, _csv_path = client

    srv.write_message("one", "127.0.0.1", algorithm="caesar")
    srv.write_message("two", "127.0.0.1", algorithm="atbash")
    srv.write_message("three", "admin", algorithm="vigenere")

    stats = srv.build_stats(srv.read_messages())
    counters = {item["id"]: item["count"] for item in stats["algorithm_cards"]}

    assert stats["total"] == 3
    assert stats["admin"] == 1
    assert counters["caesar"] == 1
    assert counters["atbash"] == 1
    assert counters["vigenere"] == 1


def test_json_returns_decrypted_messages(client):
    test_client, _csv_path = client
    srv.write_message("JSON проверка", "127.0.0.1", algorithm="vigenere")

    response = test_client.get("/get_all.json")
    data = response.get_json()

    assert response.status_code == 200
    assert data["messages"][0]["text"] == "JSON проверка"
    assert data["messages"][0]["algorithm"] == "vigenere"


def test_old_four_column_csv_is_still_supported(client):
    _test_client, csv_path = client
    encrypted = encrypt_message("Старая строка", algorithm="caesar")
    csv_path.write_text(f"1,2026-06-08 12:00:00,127.0.0.1,{encrypted}\n", encoding="utf-8")

    messages = srv.read_messages()

    assert len(messages) == 1
    assert messages[0]["algorithm"] == "caesar"
    assert messages[0]["text"] == "Старая строка"


def test_easter_page_links_to_telegram_quest(client):
    test_client, csv_path = client

    response = test_client.post(
        f"/{srv.STUDENT_ID}",
        data={"text": "Чай", "algorithm": "vigenere"},
        follow_redirects=True,
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Пасхалка найдена" in html
    assert "Перейти на следующий этап квеста" in html
    assert "https://t.me/TeaQuizzesBot" in html
    assert 'target="_blank"' in html
    assert "Чай сохранён для перерыва между шифрами." not in html
    assert "Вернуться на главную" in html
    assert not csv_path.exists() or csv_path.read_text(encoding="utf-8") == ""


def test_algorithm_scroll_uses_fixed_window_classes(client):
    test_client, _csv_path = client

    response = test_client.get(f"/{srv.STUDENT_ID}")
    html = response.get_data(as_text=True)
    css = (PROJECT_ROOT / "static" / "css" / "style.css").read_text(encoding="utf-8")

    assert response.status_code == 200
    assert "algorithm-stats-column" in html
    assert "algorithm-stats-scroll" in html
    assert "--algorithm-card-gap" in css
    assert "align-self: stretch;" in css
    assert "height: 100%;" in css
    assert "max-height: 100%;" in css
    assert "flex: 0 0 calc(50% - 7px);" in css
    assert "overflow: hidden;" in css
