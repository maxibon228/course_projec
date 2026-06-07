import string
from pathlib import Path


def encrypt(message, sid=70193935):
    """Шифрует сообщение шифром Цезаря с учётом студенческого ID."""
    shift = sid % 11
    alphabet = _get_alphabet()
    alphabet_size = len(alphabet)
    result = []

    for char in message:
        if char in alphabet:
            old_index = alphabet.index(char)
            new_index = (old_index + shift) % alphabet_size
            result.append(alphabet[new_index])
        else:
            # Неизвестные символы не ломают программу, а остаются без изменений.
            result.append(char)

    return "".join(result)


def decrypt(message, sid=70193935):
    """Расшифровывает сообщение, зашифрованное функцией encrypt."""
    shift = sid % 11
    alphabet = _get_alphabet()
    alphabet_size = len(alphabet)
    result = []

    for char in message:
        if char in alphabet:
            old_index = alphabet.index(char)
            new_index = (old_index - shift) % alphabet_size
            result.append(alphabet[new_index])
        else:
            # Неизвестные символы не ломают программу, а остаются без изменений.
            result.append(char)

    return "".join(result)


# Константы алфавита вынесены ниже функций, чтобы encrypt и decrypt были вверху файла.
DIGITS = string.digits
RUS_LOWER = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
RUS_UPPER = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
LAT_LOWER = string.ascii_lowercase
LAT_UPPER = string.ascii_uppercase
SPACE = " "


def _get_alphabet():
    """Возвращает общий круговой алфавит в порядке из задания."""
    return DIGITS + RUS_LOWER + RUS_UPPER + LAT_LOWER + LAT_UPPER + string.punctuation + SPACE


def _base_dir():
    """Возвращает папку, где расположен файл cypher.py."""
    return Path(__file__).resolve().parent


def _read_lines(file_name):
    """Читает строки из файла без символа переноса строки в конце."""
    path = _base_dir() / file_name
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        return [line.rstrip("\n") for line in file]


def _write_lines(file_name, lines):
    """Записывает строки в файл в кодировке UTF-8."""
    path = _base_dir() / file_name
    with path.open("w", encoding="utf-8") as file:
        for line in lines:
            file.write(f"{line}\n")


def _run_demo():
    """Тестовый запуск: читает входные файлы и создаёт файлы с результатами."""
    encrypt_source = _read_lines("encrypt.txt")
    decrypt_source = _read_lines("decrypt.txt")

    encrypt_result = [encrypt(line) for line in encrypt_source]
    decrypt_result = [decrypt(line) for line in decrypt_source]

    _write_lines("encrypt_result.txt", encrypt_result)
    _write_lines("decrypt_result.txt", decrypt_result)

    print("Результаты шифрования:")
    for line in encrypt_result:
        print(line)

    print("\nРезультаты дешифрования:")
    for line in decrypt_result:
        print(line)


if __name__ == "__main__":
    _run_demo()
