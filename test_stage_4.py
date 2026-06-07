import csv
import tempfile
import unittest
from pathlib import Path

import admin
from cypher import encrypt


class Stage4AdminTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = Path(self.temp_dir.name) / "messages.csv"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_csv_file(self):
        admin.ensure_csv_exists(self.csv_path)
        self.assertTrue(self.csv_path.exists())

    def test_add_message_with_ip_admin(self):
        messages = admin.add_message(self.csv_path, "Привет", ip="admin", now_value="2026-06-07T12:00:00")
        self.assertEqual(messages[0]["ip"], "admin")
        self.assertEqual(messages[0]["id"], "1")
        self.assertEqual(messages[0]["text"], "Привет")

    def test_text_is_encrypted_in_csv_and_decrypted_on_display(self):
        admin.add_message(self.csv_path, "Hello", ip="admin", now_value="2026-06-07T12:00:00")

        with self.csv_path.open("r", encoding="utf-8", newline="") as file:
            rows = list(csv.reader(file))
        self.assertEqual(rows[0][3], encrypt("Hello"))
        self.assertNotEqual(rows[0][3], "Hello")

        messages = admin.read_messages(self.csv_path)
        self.assertEqual(messages[0]["text"], "Hello")

    def test_delete_message(self):
        admin.add_message(self.csv_path, "one", now_value="2026-06-07T12:00:00")
        admin.add_message(self.csv_path, "two", now_value="2026-06-07T12:00:01")
        messages = admin.delete_message(self.csv_path, 0)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["text"], "two")
        self.assertEqual(messages[0]["id"], "1")

    def test_move_message_up(self):
        admin.add_message(self.csv_path, "one", now_value="2026-06-07T12:00:00")
        admin.add_message(self.csv_path, "two", now_value="2026-06-07T12:00:01")
        messages = admin.move_message_up(self.csv_path, 1)
        self.assertEqual(messages[0]["text"], "two")
        self.assertEqual(messages[1]["text"], "one")
        self.assertEqual(messages[0]["id"], "1")
        self.assertEqual(messages[1]["id"], "2")

    def test_move_message_down(self):
        admin.add_message(self.csv_path, "one", now_value="2026-06-07T12:00:00")
        admin.add_message(self.csv_path, "two", now_value="2026-06-07T12:00:01")
        messages = admin.move_message_down(self.csv_path, 0)
        self.assertEqual(messages[0]["text"], "two")
        self.assertEqual(messages[1]["text"], "one")
        self.assertEqual(messages[0]["id"], "1")
        self.assertEqual(messages[1]["id"], "2")

    def test_is_csv_file_validation(self):
        self.assertTrue(admin.is_csv_file("messages.csv"))
        self.assertFalse(admin.is_csv_file("messages.txt"))

    def test_validation_rejects_yo_letter(self):
        self.assertFalse(admin.validate_message_text("текст с ё"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
