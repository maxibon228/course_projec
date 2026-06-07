import string
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from cypher import decrypt, encrypt


DEFAULT_SID = 70193935
DEFAULT_OPEN_FILE = "encrypt.txt"
DEFAULT_SAVE_FILE = "encrypt_2.txt"
RUS_LOWER = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
RUS_UPPER = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


class InvalidFileContentError(ValueError):
    """Ошибка для случая, когда в файле встретились недопустимые символы."""

    def __init__(self, line_number):
        super().__init__(f"файл содержит недопустимые символы на стр. №{line_number}")
        self.line_number = line_number


def recursive_digit_sum(number):
    """Считает рекурсивную сумму цифр до одной цифры."""
    value = abs(int(number))
    while value >= 10:
        value = sum(int(digit) for digit in str(value))
    return value


def get_display_rows(sid=DEFAULT_SID):
    """Количество строк для поля вывода по формуле из задания."""
    return 10 + recursive_digit_sum(sid)


def get_input_rows(sid=DEFAULT_SID):
    """Количество строк для поля ввода по формуле из задания."""
    return 3 + (sid % 4)


def build_allowed_characters():
    """Полный набор символов, которые разрешены в txt-файлах."""
    return (
        string.digits
        + RUS_LOWER
        + RUS_UPPER
        + string.ascii_lowercase
        + string.ascii_uppercase
        + string.punctuation
        + " "
    )


def validate_lines(lines):
    """Проверяет строки на наличие недопустимых символов."""
    allowed = set(build_allowed_characters())
    for line_number, line in enumerate(lines, start=1):
        for char in line:
            if char not in allowed:
                return False, line_number
    return True, None


def read_text_file(file_path):
    """Читает txt-файл и возвращает список строк без символов переноса."""
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as file:
        return [line.rstrip("\n") for line in file]


def load_encrypted_messages(file_path):
    """Читает зашифрованный txt-файл и возвращает расшифрованные строки."""
    lines = read_text_file(file_path)
    is_valid, bad_line = validate_lines(lines)
    if not is_valid:
        raise InvalidFileContentError(bad_line)
    return [decrypt(line) for line in lines]


def prepare_encrypted_lines(lines):
    """Шифрует строки перед сохранением."""
    return [encrypt(line) for line in lines]


def save_encrypted_messages(file_path, decrypted_lines):
    """Сохраняет строки в файл уже в зашифрованном виде."""
    encrypted_lines = prepare_encrypted_lines(decrypted_lines)
    path = Path(file_path)
    with path.open("w", encoding="utf-8") as file:
        for line in encrypted_lines:
            file.write(f"{line}\n")


def get_default_open_path():
    return Path(__file__).resolve().parent / DEFAULT_OPEN_FILE


def get_default_save_path():
    return Path(__file__).resolve().parent / DEFAULT_SAVE_FILE


class CypherApp(tk.Tk):
    """Оконное приложение для работы с зашифрованными txt-файлами."""

    def __init__(self):
        super().__init__()
        self.title("Шифровальщик сообщений")
        self.geometry("980x700")

        self.current_file = None
        self.messages = []
        self.display_rows = get_display_rows(DEFAULT_SID)
        self.input_rows = get_input_rows(DEFAULT_SID)
        self.status_var = tk.StringVar(value="Готово к работе")

        self._build_widgets()
        self._update_output_area()
        self._update_input_line_numbers()

    def _build_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(4, weight=1)

        button_frame = tk.Frame(self)
        button_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        tk.Button(button_frame, text="Загрузить файл", command=self.load_file).grid(row=0, column=0, padx=(0, 10))
        tk.Button(button_frame, text="Добавить", command=self.add_lines).grid(row=0, column=1, padx=(0, 10))
        tk.Button(button_frame, text="Зашифровать и сохранить", command=self.save_file).grid(row=0, column=2)

        tk.Label(self, text="Расшифрованные строки").grid(row=1, column=0, sticky="w", padx=10)

        display_frame = tk.Frame(self)
        display_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        display_frame.columnconfigure(1, weight=1)
        display_frame.rowconfigure(0, weight=1)

        self.display_numbers = tk.Text(display_frame, width=4, height=self.display_rows, state="disabled", wrap="none")
        self.display_numbers.grid(row=0, column=0, sticky="ns")

        self.display_text = tk.Text(display_frame, height=self.display_rows, state="disabled", wrap="word")
        self.display_text.grid(row=0, column=1, sticky="nsew")

        self.display_scrollbar = tk.Scrollbar(display_frame, command=self._on_display_scroll)
        self.display_scrollbar.grid(row=0, column=2, sticky="ns")
        self.display_text.configure(yscrollcommand=self.display_scrollbar.set)
        self.display_numbers.configure(yscrollcommand=self.display_scrollbar.set)

        tk.Label(self, text="Новые строки").grid(row=3, column=0, sticky="w", padx=10)

        input_frame = tk.Frame(self)
        input_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        input_frame.rowconfigure(0, weight=1)

        self.input_numbers = tk.Text(input_frame, width=4, height=self.input_rows, state="disabled", wrap="none")
        self.input_numbers.grid(row=0, column=0, sticky="ns")

        self.input_text = tk.Text(input_frame, height=self.input_rows, wrap="word")
        self.input_text.grid(row=0, column=1, sticky="nsew")
        self.input_text.bind("<KeyRelease>", self._on_input_changed)

        self.input_scrollbar = tk.Scrollbar(input_frame, command=self._on_input_scroll)
        self.input_scrollbar.grid(row=0, column=2, sticky="ns")
        self.input_text.configure(yscrollcommand=self.input_scrollbar.set)
        self.input_numbers.configure(yscrollcommand=self.input_scrollbar.set)

        status_label = tk.Label(self, textvariable=self.status_var, anchor="w", relief="sunken")
        status_label.grid(row=5, column=0, sticky="ew", padx=10, pady=(0, 10))

    def _set_status(self, text):
        self.status_var.set(text)

    def _on_display_scroll(self, *args):
        self.display_text.yview(*args)
        self.display_numbers.yview(*args)

    def _on_input_scroll(self, *args):
        self.input_text.yview(*args)
        self.input_numbers.yview(*args)

    def _on_input_changed(self, _event=None):
        self._update_input_line_numbers()
        self._update_scrollbar_visibility(self.input_text, self.input_scrollbar)

    def _set_text_safely(self, widget, text, readonly=False):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        if readonly:
            widget.configure(state="disabled")

    def _number_block(self, line_count):
        return "\n".join(str(index) for index in range(1, max(1, line_count) + 1))

    def _update_output_area(self):
        content = "\n".join(self.messages)
        self._set_text_safely(self.display_text, content, readonly=True)
        self._set_text_safely(self.display_numbers, self._number_block(len(self.messages)), readonly=True)
        self._update_scrollbar_visibility(self.display_text, self.display_scrollbar)

    def _update_input_line_numbers(self):
        text = self.input_text.get("1.0", "end-1c")
        line_count = max(1, len(text.split("\n")))
        self._set_text_safely(self.input_numbers, self._number_block(line_count), readonly=True)

    def _update_scrollbar_visibility(self, text_widget, scrollbar):
        self.update_idletasks()
        first, last = text_widget.yview()
        if first == 0.0 and last == 1.0:
            scrollbar.grid_remove()
        else:
            scrollbar.grid()

    def load_file(self):
        default_path = get_default_open_path()
        file_path = filedialog.askopenfilename(
            title="Выберите txt-файл",
            initialdir=default_path.parent,
            initialfile=default_path.name,
            filetypes=[("Текстовые файлы", "*.txt")],
        )
        if not file_path:
            self._set_status("Загрузка отменена")
            return

        try:
            decrypted_lines = load_encrypted_messages(file_path)
        except InvalidFileContentError as error:
            self._set_status(str(error))
            return
        except OSError:
            self._set_status("не удалось открыть файл")
            return

        self.current_file = Path(file_path)
        self.messages = decrypted_lines
        self._update_output_area()
        self._set_status(f"Файл загружен: {self.current_file.name}")

    def add_lines(self):
        raw_text = self.input_text.get("1.0", "end-1c")
        new_lines = [line for line in raw_text.splitlines() if line]

        if not new_lines:
            self._set_status("Нет новых строк для добавления")
            return

        is_valid, bad_line = validate_lines(new_lines)
        if not is_valid:
            self._set_status(f"введены недопустимые символы на стр. №{bad_line}")
            return

        self.messages.extend(new_lines)
        self._update_output_area()
        self.input_text.delete("1.0", "end")
        self._update_input_line_numbers()
        self._set_status("Строки добавлены")

    def save_file(self):
        target_path = self.current_file

        if target_path is None:
            default_path = get_default_save_path()
            selected = filedialog.asksaveasfilename(
                title="Сохранить файл",
                initialdir=default_path.parent,
                initialfile=default_path.name,
                defaultextension=".txt",
                filetypes=[("Текстовые файлы", "*.txt")],
            )
            if not selected:
                self._set_status("Сохранение отменено")
                return
            target_path = Path(selected)
            self.current_file = target_path

        try:
            save_encrypted_messages(target_path, self.messages)
        except OSError:
            self._set_status("файл недоступен для записи")
            return

        self._set_status(f"Файл сохранён: {target_path.name}")


if __name__ == "__main__":
    app = CypherApp()
    app.mainloop()
