import string
from pathlib import Path


def encrypt(message, sid=70193935):
    """Старая функция из курсовой: шифрует текст шифром Цезаря.

    Функция оставлена в начале файла для совместимости с первоначальным
    заданием и старым кодом проекта. Новая универсальная архитектура шифров
    находится ниже.
    """
    return encrypt_message(message, algorithm="caesar", sid=sid)


def decrypt(message, sid=70193935):
    """Старая функция из курсовой: расшифровывает текст шифром Цезаря."""
    return decrypt_message(message, algorithm="caesar", sid=sid)


# Константы алфавита вынесены ниже функций, чтобы encrypt и decrypt
# оставались в верхней части файла, как требовалось в исходной курсовой.
DIGITS = string.digits
RUS_LOWER = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
RUS_UPPER = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
LAT_LOWER = string.ascii_lowercase
LAT_UPPER = string.ascii_uppercase
SPACE = " "
ALPHABET = DIGITS + RUS_LOWER + RUS_UPPER + LAT_LOWER + LAT_UPPER + string.punctuation + SPACE


def _get_alphabet():
    """Возвращает общий круговой алфавит в порядке из задания."""
    return ALPHABET


def caesar_encrypt(message, sid=70193935):
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


def caesar_decrypt(message, sid=70193935):
    """Расшифровывает сообщение, зашифрованное шифром Цезаря."""
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
            result.append(char)

    return "".join(result)


def atbash_encrypt(message, sid=70193935):
    """Шифрует сообщение шифром Атбаш.

    Атбаш заменяет символ на зеркальный символ из общего алфавита.
    Параметр sid оставлен для единого интерфейса всех шифров.
    """
    alphabet = _get_alphabet()
    last_index = len(alphabet) - 1
    result = []

    for char in message:
        if char in alphabet:
            old_index = alphabet.index(char)
            result.append(alphabet[last_index - old_index])
        else:
            result.append(char)

    return "".join(result)


def atbash_decrypt(message, sid=70193935):
    """Расшифровывает сообщение шифром Атбаш.

    Атбаш симметричен, поэтому дешифрование совпадает с шифрованием.
    """
    return atbash_encrypt(message, sid=sid)


# Словарь алгоритмов — основа для дальнейшего расширения проекта.
# Чтобы добавить новый шифр, достаточно написать две функции и добавить запись.
ALGORITHMS = {
    "caesar": {
        "title": "Цезарь",
        "encrypt": caesar_encrypt,
        "decrypt": caesar_decrypt,
    },
    "atbash": {
        "title": "Атбаш",
        "encrypt": atbash_encrypt,
        "decrypt": atbash_decrypt,
    },
}


def normalize_algorithm(algorithm):
    """Возвращает корректный ID алгоритма или caesar по умолчанию."""
    if algorithm in ALGORITHMS:
        return algorithm
    return "caesar"


def encrypt_message(message, algorithm="caesar", sid=70193935):
    """Универсальная функция шифрования выбранным алгоритмом."""
    algorithm = normalize_algorithm(algorithm)
    return ALGORITHMS[algorithm]["encrypt"](message, sid=sid)


def decrypt_message(message, algorithm="caesar", sid=70193935):
    """Универсальная функция расшифровки выбранным алгоритмом."""
    algorithm = normalize_algorithm(algorithm)
    return ALGORITHMS[algorithm]["decrypt"](message, sid=sid)


def get_available_algorithms():
    """Возвращает список алгоритмов для выпадающего списка в интерфейсе."""
    return [
        {"id": algorithm_id, "title": data["title"]}
        for algorithm_id, data in ALGORITHMS.items()
    ]


def get_algorithm_title(algorithm):
    """Возвращает красивое название алгоритма."""
    algorithm = normalize_algorithm(algorithm)
    return ALGORITHMS[algorithm]["title"]


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

    print("Результаты шифрования Цезарем:")
    for line in encrypt_result:
        print(line)

    print("\nРезультаты дешифрования Цезарем:")
    for line in decrypt_result:
        print(line)

    print("\nДоступные алгоритмы:")
    for algorithm in get_available_algorithms():
        print(f"- {algorithm['title']} ({algorithm['id']})")


if __name__ == "__main__":
    _run_demo()
