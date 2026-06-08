import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from cypher import (
    decrypt_message,
    encrypt_message,
    get_algorithm_title,
    get_available_algorithms,
    normalize_algorithm,
)


STUDENT_ID = 70193935
BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "messages.csv"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

app = Flask(__name__)
# На время учебной разработки отключаем кэш статики, чтобы браузер сразу видел новые CSS/JS.
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
# Нужен для flash-сообщений после отправки формы.
app.secret_key = "cipher-web-coursework-70193935"


@app.after_request
def add_no_cache_headers(response):
    """Не даёт браузеру показывать старую версию CSS/JS после обновления проекта."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def ensure_csv_exists():
    """Создаёт messages.csv, если файла ещё нет."""
    CSV_FILE.parent.mkdir(parents=True, exist_ok=True)
    CSV_FILE.touch(exist_ok=True)


def read_messages_raw():
    """Читает messages.csv как список CSV-строк без расшифровки.

    Функция сохранена для совместимости со старой логикой проекта.
    Поддерживаются как старые строки из 4 полей, так и новые строки из 5 полей.
    """
    ensure_csv_exists()

    try:
        with CSV_FILE.open("r", encoding="utf-8", newline="") as file:
            return [row for row in csv.reader(file) if len(row) >= 4]
    except (OSError, UnicodeDecodeError, csv.Error):
        return []


def write_messages_raw(rows):
    """Полностью перезаписывает messages.csv переданными CSV-строками."""
    CSV_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CSV_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def _safe_int(value, default=0):
    """Аккуратно преобразует значение в int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_csv_row(row):
    """Преобразует CSV-строку в единый формат.

    Старый формат: id, datetime, ip, text
    Новый формат: id, datetime, ip, algorithm, text
    """
    if len(row) >= 5:
        message_id = row[0]
        created_at = row[1]
        ip_address = row[2]
        algorithm = normalize_algorithm(row[3])
        encrypted_text = ",".join(row[4:]) if len(row) > 5 else row[4]
    elif len(row) == 4:
        message_id, created_at, ip_address, encrypted_text = row
        algorithm = "caesar"
    else:
        return None

    return {
        "id": _safe_int(message_id),
        "datetime": created_at,
        "ip": ip_address or "unknown",
        "algorithm": algorithm,
        "algorithm_title": get_algorithm_title(algorithm),
        "encrypted_text": encrypted_text,
        "text": decrypt_message(encrypted_text, algorithm=algorithm),
    }


def read_messages():
    """Возвращает сообщения как словари с расшифрованным текстом."""
    messages = []

    for row in read_messages_raw():
        message = _parse_csv_row(row)
        if message is not None:
            messages.append(message)

    return messages


def get_next_id():
    """Вычисляет следующий ID по текущему содержимому CSV."""
    ids = []
    for row in read_messages_raw():
        if row:
            ids.append(_safe_int(row[0]))
    return max(ids, default=0) + 1


def write_message(text, ip, algorithm="caesar"):
    """Шифрует выбранным алгоритмом и добавляет сообщение в messages.csv."""
    ensure_csv_exists()
    algorithm = normalize_algorithm(algorithm)
    encrypted_text = encrypt_message(text, algorithm=algorithm)

    row = [
        str(get_next_id()),
        datetime.now().strftime(DATETIME_FORMAT),
        ip or "unknown",
        algorithm,
        encrypted_text,
    ]

    with CSV_FILE.open("a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(row)

    return row


def append_message(text, ip_address, algorithm="caesar"):
    """Старое имя функции сохранено для обратной совместимости."""
    return write_message(text, ip_address, algorithm=algorithm)


def clear_messages():
    """Очищает messages.csv."""
    write_messages_raw([])


def build_stats(messages):
    """Формирует статистику для dashboard под любое количество алгоритмов."""
    algorithm_counter = Counter(message.get("algorithm", "caesar") for message in messages)
    algorithms = get_available_algorithms()

    return {
        "total": len(messages),
        "admin": sum(1 for message in messages if message.get("ip") == "admin"),
        "algorithm_cards": [
            {
                "id": algorithm["id"],
                "title": algorithm["title"],
                "description": algorithm.get("description", ""),
                "icon": algorithm.get("icon", "🔐"),
                "count": algorithm_counter.get(algorithm["id"], 0),
            }
            for algorithm in algorithms
        ],
    }


def get_all_messages_decrypted():
    """Возвращает все сообщения в формате, подходящем для JSON."""
    return [
        {
            "id": message["id"],
            "datetime": message["datetime"],
            "ip": message["ip"],
            "algorithm": message["algorithm"],
            "algorithm_title": message["algorithm_title"],
            "text": message["text"],
        }
        for message in read_messages()
    ]


@app.route("/")
def index():
    """Удобный переход на основную страницу по студенческому ID."""
    return redirect(url_for("message_form"))


@app.route(f"/{STUDENT_ID}", methods=["GET", "POST"])
def message_form():
    """Показывает dashboard и принимает сообщения из формы."""
    if request.method == "POST":
        text = request.form.get("text", "")
        algorithm = normalize_algorithm(request.form.get("algorithm", "caesar"))

        # Пасхалка из предыдущего этапа оставлена, чтобы не ломать старое поведение.
        if text.strip() == "Чай":
            return render_template("easter.html", student_id=STUDENT_ID)

        if not text.strip():
            flash("Введите сообщение перед отправкой", "warning")
            return redirect(url_for("message_form"))

        write_message(text, request.remote_addr or "unknown", algorithm=algorithm)
        flash("Сообщение успешно сохранено", "success")
        return redirect(url_for("message_form", algorithm=algorithm))

    selected_algorithm = normalize_algorithm(request.args.get("algorithm", "caesar"))
    messages = read_messages()
    stats = build_stats(messages)
    return render_template(
        "form.html",
        student_id=STUDENT_ID,
        messages=messages,
        stats=stats,
        algorithms=get_available_algorithms(),
        selected_algorithm=selected_algorithm,
    )


@app.route("/reset", methods=["GET"])
def reset_messages():
    """Стирает все сообщения на сервере."""
    clear_messages()
    return render_template("reset.html", student_id=STUDENT_ID)


@app.route("/get_all.json", methods=["GET"])
def get_all_json():
    """Возвращает все сообщения в JSON с расшифрованным текстом."""
    return jsonify({"messages": get_all_messages_decrypted()})


if __name__ == "__main__":
    ensure_csv_exists()
    app.run(host="127.0.0.1", port=5000, debug=False)
