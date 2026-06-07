import csv
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request

from cypher import decrypt, encrypt


STUDENT_ID = 70193935
BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "messages.csv"

app = Flask(__name__)


def ensure_csv_exists():
    """Создаёт messages.csv, если файла ещё нет."""
    CSV_FILE.parent.mkdir(parents=True, exist_ok=True)
    CSV_FILE.touch(exist_ok=True)


def read_messages_raw():
    """Читает csv-файл как список строк без расшифровки текста."""
    ensure_csv_exists()
    with CSV_FILE.open("r", encoding="utf-8", newline="") as file:
        return [row for row in csv.reader(file) if row]


def write_messages_raw(rows):
    """Полностью перезаписывает csv-файл."""
    CSV_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CSV_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def append_message(text, ip_address):
    """Шифрует и сохраняет новое сообщение в messages.csv."""
    rows = read_messages_raw()
    message_id = len(rows) + 1
    created_at = datetime.now().isoformat(timespec="seconds")
    encrypted_text = encrypt(text)
    row = [str(message_id), created_at, ip_address or "", encrypted_text]
    rows.append(row)
    write_messages_raw(rows)
    return row


def get_all_messages_decrypted():
    """Возвращает все сообщения как JSON-готовые словари с расшифрованным текстом."""
    result = []
    for row in read_messages_raw():
        if len(row) != 4:
            continue
        result.append(
            {
                "id": row[0],
                "datetime": row[1],
                "ip": row[2],
                "text": decrypt(row[3]),
            }
        )
    return result


@app.route("/")
def index():
    """Удобный переход на основную страницу по ID."""
    return redirect(f"/{STUDENT_ID}")


@app.route(f"/{STUDENT_ID}", methods=["GET", "POST"])
def message_form():
    """Показывает форму и принимает отправленные сообщения."""
    if request.method == "POST":
        text = request.form.get("text", "")
        append_message(text, request.remote_addr)
        return render_template("saved.html", msg=text)
    return render_template("form.html")


@app.route("/reset", methods=["GET"])
def reset_messages():
    """Стирает все сообщения на сервере."""
    write_messages_raw([])
    return render_template("reset.html")


@app.route("/get_all.json", methods=["GET"])
def get_all_json():
    """Возвращает все сообщения в JSON с расшифрованным текстом."""
    return jsonify({"messages": get_all_messages_decrypted()})


if __name__ == "__main__":
    ensure_csv_exists()
    app.run(host="127.0.0.1", port=5000, debug=False)
