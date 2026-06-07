import tempfile
import unittest
from pathlib import Path

import app
from cypher import decrypt, encrypt


class Stage2GuiLogicTests(unittest.TestCase):
    def test_validate_lines_accepts_allowed_symbols(self):
        lines = ["Привет, мир!", "Hello, World!", "Тест 123 / test."]
        self.assertEqual(app.validate_lines(lines), (True, None))

    def test_validate_lines_rejects_invalid_symbols(self):
        lines = ["Нормальная строка", "Строка с ё"]
        self.assertEqual(app.validate_lines(lines), (False, 2))

    def test_read_text_file_returns_lines(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            file_path = Path(temp_dir_name) / "sample.txt"
            file_path.write_text("one\ntwo\n", encoding="utf-8")
            self.assertEqual(app.read_text_file(file_path), ["one", "two"])

    def test_prepare_encrypted_lines_encrypts_before_save(self):
        lines = ["Привет", "Hello"]
        encrypted = app.prepare_encrypted_lines(lines)
        self.assertEqual(encrypted, [encrypt("Привет"), encrypt("Hello")])

    def test_load_encrypted_messages_decrypts_after_load(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            file_path = Path(temp_dir_name) / "sample.txt"
            original = ["Привет", "Hello"]
            file_path.write_text("\n".join(encrypt(line) for line in original), encoding="utf-8")
            self.assertEqual(app.load_encrypted_messages(file_path), original)

    def test_save_encrypted_messages_saves_encrypted_text(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            file_path = Path(temp_dir_name) / "out.txt"
            app.save_encrypted_messages(file_path, ["Привет", "Hello"])
            saved = app.read_text_file(file_path)
            self.assertEqual(saved, [encrypt("Привет"), encrypt("Hello")])
            self.assertEqual([decrypt(line) for line in saved], ["Привет", "Hello"])

    def test_calculated_widget_sizes_for_student_id(self):
        self.assertEqual(app.get_display_rows(70193935), 11)
        self.assertEqual(app.get_input_rows(70193935), 6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
