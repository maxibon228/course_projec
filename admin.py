import csv
import string
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, ttk

from cypher import decrypt_message, encrypt_message, get_algorithm_title, get_available_algorithms, normalize_algorithm


DEFAULT_CSV_NAME = "messages.csv"
RUS_LOWER = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
RUS_UPPER = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


def build_allowed_characters():
    """Символы, допустимые для нового сообщения администратора."""
    return (
        string.digits
        + RUS_LOWER
        + RUS_UPPER
        + string.ascii_lowercase
        + string.ascii_uppercase
        + string.punctuation
        + " \n"
    )


def validate_message_text(text):
    allowed = set(build_allowed_characters())
    return all(char in allowed for char in text)


def is_csv_file(file_path):
    return Path(file_path).suffix.lower() == ".csv"


def ensure_csv_exists(csv_path):
    path = Path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)
    return path


def read_messages(csv_path):
    """Возвращает сообщения для отображения: текст уже расшифрован.

    Поддерживаются старые CSV-строки из 4 полей и новые строки из 5 полей:
    id, datetime, ip, algorithm, encrypted_text.
    """
    path = ensure_csv_exists(csv_path)
    messages = []
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
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
                continue

            messages.append(
                {
                    "id": message_id,
                    "datetime": created_at,
                    "ip": ip_address,
                    "algorithm": algorithm,
                    "algorithm_title": get_algorithm_title(algorithm),
                    "text": decrypt_message(encrypted_text, algorithm=algorithm),
                }
            )
    return messages


def write_messages(csv_path, messages):
    """Сохраняет сообщения в CSV в зашифрованном виде."""
    path = ensure_csv_exists(csv_path)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        for message in messages:
            algorithm = normalize_algorithm(message.get("algorithm", "caesar"))
            writer.writerow(
                [
                    message["id"],
                    message["datetime"],
                    message["ip"],
                    algorithm,
                    encrypt_message(message["text"], algorithm=algorithm),
                ]
            )


def renumber_messages(messages):
    """Пересчитывает id по текущему порядку записей."""
    for index, message in enumerate(messages, start=1):
        message["id"] = str(index)
    return messages


def add_message(csv_path, text, ip="admin", algorithm="caesar", now_value=None):
    """Добавляет сообщение администратора и сразу сохраняет CSV."""
    messages = read_messages(csv_path)
    created_at = now_value or datetime.now().isoformat(timespec="seconds")
    algorithm = normalize_algorithm(algorithm)
    messages.append(
        {
            "id": str(len(messages) + 1),
            "datetime": created_at,
            "ip": ip,
            "algorithm": algorithm,
            "algorithm_title": get_algorithm_title(algorithm),
            "text": text,
        }
    )
    renumber_messages(messages)
    write_messages(csv_path, messages)
    return messages


def delete_message(csv_path, index):
    messages = read_messages(csv_path)
    if 0 <= index < len(messages):
        del messages[index]
        renumber_messages(messages)
        write_messages(csv_path, messages)
    return messages


def move_message_up(csv_path, index):
    messages = read_messages(csv_path)
    if 0 < index < len(messages):
        messages[index - 1], messages[index] = messages[index], messages[index - 1]
        renumber_messages(messages)
        write_messages(csv_path, messages)
    return messages


def move_message_down(csv_path, index):
    messages = read_messages(csv_path)
    if 0 <= index < len(messages) - 1:
        messages[index], messages[index + 1] = messages[index + 1], messages[index]
        renumber_messages(messages)
        write_messages(csv_path, messages)
    return messages


class AdminApp(tk.Tk):
    """Административная панель для управления messages.csv."""

    def __init__(self):
        super().__init__()
        self.title("Администратор сообщений")
        self.geometry("1100x700")

        self.current_csv = None
        self.status_var = tk.StringVar(value="Выберите CSV-файл")

        self._build_widgets()
        # При запуске приложение предлагает выбрать CSV, как требуется в задании.
        self.after(100, self.choose_csv_file)

    def _build_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top_frame = tk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        tk.Button(top_frame, text="Открыть CSV", command=self.choose_csv_file).grid(row=0, column=0, padx=(0, 10))
        tk.Button(top_frame, text="Создать CSV", command=self.create_csv_file).grid(row=0, column=1, padx=(0, 10))
        tk.Button(top_frame, text="Обновить", command=self.refresh_table).grid(row=0, column=2)

        table_frame = tk.Frame(self)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("id", "datetime", "ip", "algorithm", "text")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.heading("id", text="id")
        self.tree.heading("datetime", text="datetime")
        self.tree.heading("ip", text="ip")
        self.tree.heading("algorithm", text="algorithm")
        self.tree.heading("text", text="text")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("datetime", width=190, anchor="w")
        self.tree.column("ip", width=120, anchor="center")
        self.tree.column("algorithm", width=120, anchor="center")
        self.tree.column("text", width=560, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_changed)

        actions_frame = tk.Frame(self)
        actions_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.up_button = tk.Button(actions_frame, text="↑ Вверх", command=self.move_selected_up, state="disabled")
        self.up_button.grid(row=0, column=0, padx=(0, 10))

        self.down_button = tk.Button(actions_frame, text="↓ Вниз", command=self.move_selected_down, state="disabled")
        self.down_button.grid(row=0, column=1, padx=(0, 10))

        self.delete_button = tk.Button(actions_frame, text="✕ Удалить", command=self.delete_selected, state="disabled")
        self.delete_button.grid(row=0, column=2)

        add_frame = tk.Frame(self)
        add_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        add_frame.columnconfigure(0, weight=1)

        tk.Label(add_frame, text="Новое сообщение").grid(row=0, column=0, sticky="w")
        self.new_message_text = tk.Text(add_frame, height=4, wrap="word")
        self.new_message_text.grid(row=1, column=0, sticky="ew", pady=(5, 5))

        algorithm_frame = tk.Frame(add_frame)
        algorithm_frame.grid(row=2, column=0, sticky="w", pady=(0, 5))
        tk.Label(algorithm_frame, text="Алгоритм:").grid(row=0, column=0, padx=(0, 8))
        self.algorithm_var = tk.StringVar(value="caesar")
        self.algorithm_combo = ttk.Combobox(
            algorithm_frame,
            textvariable=self.algorithm_var,
            state="readonly",
            values=[algorithm["id"] for algorithm in get_available_algorithms()],
            width=16,
        )
        self.algorithm_combo.grid(row=0, column=1)

        tk.Button(add_frame, text="Добавить", command=self.add_new_message).grid(row=3, column=0, sticky="w")

        tk.Label(self, textvariable=self.status_var, anchor="w", relief="sunken").grid(
            row=4, column=0, sticky="ew", padx=10, pady=(0, 10)
        )

    def _set_status(self, text):
        self.status_var.set(text)

    def _selected_index(self):
        selected = self.tree.selection()
        if not selected:
            return None
        item_id = selected[0]
        children = list(self.tree.get_children())
        return children.index(item_id)

    def _on_selection_changed(self, _event=None):
        self._update_action_buttons()

    def _update_action_buttons(self):
        index = self._selected_index()
        messages = self._get_current_messages()

        if index is None:
            self.up_button.configure(state="disabled")
            self.down_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")
            return

        self.delete_button.configure(state="normal")
        self.up_button.configure(state="normal" if index > 0 else "disabled")
        self.down_button.configure(state="normal" if index < len(messages) - 1 else "disabled")

    def _get_current_messages(self):
        if self.current_csv is None:
            return []
        return read_messages(self.current_csv)

    def choose_csv_file(self):
        default_path = Path(__file__).resolve().parent / DEFAULT_CSV_NAME
        file_path = filedialog.askopenfilename(
            title="Выберите CSV-файл",
            initialdir=default_path.parent,
            initialfile=default_path.name,
            filetypes=[("CSV файлы", "*.csv")],
        )
        if not file_path:
            self._set_status("Открытие файла отменено")
            return
        if not is_csv_file(file_path):
            self._set_status("нужно выбрать файл формата .csv")
            return
        self.current_csv = Path(file_path)
        ensure_csv_exists(self.current_csv)
        self.refresh_table()
        self._set_status(f"Открыт файл: {self.current_csv.name}")

    def create_csv_file(self):
        default_path = Path(__file__).resolve().parent / DEFAULT_CSV_NAME
        file_path = filedialog.asksaveasfilename(
            title="Создать CSV-файл",
            initialdir=default_path.parent,
            initialfile=default_path.name,
            defaultextension=".csv",
            filetypes=[("CSV файлы", "*.csv")],
        )
        if not file_path:
            self._set_status("Создание файла отменено")
            return
        if not is_csv_file(file_path):
            self._set_status("нужно выбрать файл формата .csv")
            return
        self.current_csv = Path(file_path)
        ensure_csv_exists(self.current_csv)
        self.refresh_table()
        self._set_status(f"Создан файл: {self.current_csv.name}")

    def refresh_table(self):
        if self.current_csv is None:
            self._set_status("Сначала выберите CSV-файл")
            return

        selected_index = self._selected_index()
        for item in self.tree.get_children():
            self.tree.delete(item)

        for message in read_messages(self.current_csv):
            self.tree.insert(
                "",
                "end",
                values=(
                    message["id"],
                    message["datetime"],
                    message["ip"],
                    message.get("algorithm_title", get_algorithm_title(message.get("algorithm", "caesar"))),
                    message["text"],
                ),
            )

        children = list(self.tree.get_children())
        if selected_index is not None and children:
            selected_index = max(0, min(selected_index, len(children) - 1))
            self.tree.selection_set(children[selected_index])

        self._update_action_buttons()
        self._set_status(f"Таблица обновлена: {self.current_csv.name}")

    def add_new_message(self):
        if self.current_csv is None:
            self._set_status("Сначала выберите CSV-файл")
            return

        text = self.new_message_text.get("1.0", "end-1c").strip()
        if not text:
            self._set_status("Введите текст сообщения")
            return
        if not validate_message_text(text):
            self._set_status("Сообщение содержит недопустимые символы")
            return

        add_message(self.current_csv, text, ip="admin", algorithm=self.algorithm_var.get())
        self.new_message_text.delete("1.0", "end")
        self.refresh_table()
        self._set_status("Сообщение добавлено")

    def delete_selected(self):
        if self.current_csv is None:
            self._set_status("Сначала выберите CSV-файл")
            return
        index = self._selected_index()
        if index is None:
            self._set_status("Не выбрана строка для удаления")
            return
        delete_message(self.current_csv, index)
        self.refresh_table()
        self._set_status("Сообщение удалено")

    def move_selected_up(self):
        if self.current_csv is None:
            self._set_status("Сначала выберите CSV-файл")
            return
        index = self._selected_index()
        if index is None:
            self._set_status("Не выбрана строка для перемещения")
            return
        move_message_up(self.current_csv, index)
        self.refresh_table()
        new_items = self.tree.get_children()
        if index - 1 >= 0 and index - 1 < len(new_items):
            self.tree.selection_set(new_items[index - 1])
        self._set_status("Сообщение перемещено вверх")

    def move_selected_down(self):
        if self.current_csv is None:
            self._set_status("Сначала выберите CSV-файл")
            return
        index = self._selected_index()
        if index is None:
            self._set_status("Не выбрана строка для перемещения")
            return
        move_message_down(self.current_csv, index)
        self.refresh_table()
        new_items = self.tree.get_children()
        if index + 1 < len(new_items):
            self.tree.selection_set(new_items[index + 1])
        self._set_status("Сообщение перемещено вниз")


if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()
