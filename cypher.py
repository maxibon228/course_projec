import string
from pathlib import Path


# ---------------------------------------------------------------------------
# 1. Backward-compatible API from the first version of the coursework
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# 2. Shared alphabet
# ---------------------------------------------------------------------------
# Константы алфавита вынесены ниже функций, чтобы encrypt и decrypt
# оставались в верхней части файла, как требовалось в исходной курсовой.
DIGITS = string.digits
RUS_LOWER = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
RUS_UPPER = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
LAT_LOWER = string.ascii_lowercase
LAT_UPPER = string.ascii_uppercase
SPACE = " "
ALPHABET = DIGITS + RUS_LOWER + RUS_UPPER + LAT_LOWER + LAT_UPPER + string.punctuation + SPACE
VIGENERE_KEY = "cipherweb"


def _get_alphabet():
    """Возвращает общий круговой алфавит в порядке из задания."""
    return ALPHABET


# ---------------------------------------------------------------------------
# 3. Cipher implementations
# ---------------------------------------------------------------------------
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


def _key_to_shifts(key):
    """Преобразует ключ Виженера в список сдвигов по общему алфавиту."""
    alphabet = _get_alphabet()
    shifts = [alphabet.index(char) for char in key if char in alphabet]
    return shifts or [1]


def vigenere_encrypt(message, sid=70193935, key=VIGENERE_KEY):
    """Шифрует сообщение шифром Виженера.

    Для учебного проекта используется фиксированный демонстрационный ключ
    VIGENERE_KEY. Сигнатура совместима с другими алгоритмами: message + sid.
    """
    alphabet = _get_alphabet()
    alphabet_size = len(alphabet)
    shifts = _key_to_shifts(key)
    result = []
    key_index = 0

    for char in message:
        if char in alphabet:
            old_index = alphabet.index(char)
            shift = shifts[key_index % len(shifts)]
            result.append(alphabet[(old_index + shift) % alphabet_size])
            key_index += 1
        else:
            result.append(char)

    return "".join(result)


def vigenere_decrypt(message, sid=70193935, key=VIGENERE_KEY):
    """Расшифровывает сообщение, зашифрованное шифром Виженера."""
    alphabet = _get_alphabet()
    alphabet_size = len(alphabet)
    shifts = _key_to_shifts(key)
    result = []
    key_index = 0

    for char in message:
        if char in alphabet:
            old_index = alphabet.index(char)
            shift = shifts[key_index % len(shifts)]
            result.append(alphabet[(old_index - shift) % alphabet_size])
            key_index += 1
        else:
            result.append(char)

    return "".join(result)


# ---------------------------------------------------------------------------
# 4. Extensible cipher registry
# ---------------------------------------------------------------------------
ALGORITHMS = {}


def register_algorithm(
    algorithm_id,
    title,
    encrypt_func,
    decrypt_func,
    description="",
    icon="🔐",
):
    """Регистрирует новый алгоритм в едином реестре.

    Чтобы добавить новый шифр в проект, достаточно:
    1. написать функцию шифрования;
    2. написать функцию расшифровки;
    3. вызвать register_algorithm(...).

    После этого алгоритм автоматически появится в форме, статистике,
    JSON и админке, потому что Flask и шаблоны читают ALGORITHMS динамически.
    """
    normalized_id = str(algorithm_id).strip().lower()
    if not normalized_id:
        raise ValueError("algorithm_id не может быть пустым")
    if not callable(encrypt_func) or not callable(decrypt_func):
        raise TypeError("encrypt_func и decrypt_func должны быть функциями")

    ALGORITHMS[normalized_id] = {
        "id": normalized_id,
        "title": title,
        "encrypt": encrypt_func,
        "decrypt": decrypt_func,
        "description": description,
        "icon": icon,
    }
    return ALGORITHMS[normalized_id]


register_algorithm(
    "caesar",
    "Цезарь",
    caesar_encrypt,
    caesar_decrypt,
    description="Классический сдвиг",
    icon="↻",
)
register_algorithm(
    "atbash",
    "Атбаш",
    atbash_encrypt,
    atbash_decrypt,
    description="Зеркальная замена",
    icon="⇄",
)
register_algorithm(
    "vigenere",
    "Виженер",
    vigenere_encrypt,
    vigenere_decrypt,
    description="Полиалфавитный шифр",
    icon="▦",
)


def normalize_algorithm(algorithm):
    """Возвращает корректный ID алгоритма или caesar по умолчанию."""
    algorithm_id = str(algorithm or "").strip().lower()
    if algorithm_id in ALGORITHMS:
        return algorithm_id
    return "caesar"


def get_algorithm_info(algorithm):
    """Возвращает метаданные алгоритма с безопасным fallback на Цезаря."""
    return ALGORITHMS[normalize_algorithm(algorithm)]


def encrypt_message(message, algorithm="caesar", sid=70193935):
    """Универсальная функция шифрования выбранным алгоритмом."""
    algorithm = normalize_algorithm(algorithm)
    return ALGORITHMS[algorithm]["encrypt"](message, sid=sid)


def decrypt_message(message, algorithm="caesar", sid=70193935):
    """Универсальная функция расшифровки выбранным алгоритмом."""
    algorithm = normalize_algorithm(algorithm)
    return ALGORITHMS[algorithm]["decrypt"](message, sid=sid)


def get_available_algorithms():
    """Возвращает список алгоритмов для выпадающего списка и статистики."""
    return [
        {
            "id": algorithm_id,
            "title": data["title"],
            "description": data.get("description", ""),
            "icon": data.get("icon", "🔐"),
        }
        for algorithm_id, data in ALGORITHMS.items()
    ]


def get_algorithm_title(algorithm):
    """Возвращает красивое название алгоритма."""
    return get_algorithm_info(algorithm)["title"]


# ---------------------------------------------------------------------------
# 5. Local demo mode for coursework files
# ---------------------------------------------------------------------------
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
