import tempfile
import unittest
from pathlib import Path

import srv
from cypher import encrypt


class Stage3FlaskTests(unittest.TestCase):
    def setUp(self):
        self.old_csv_file = srv.CSV_FILE
        self.temp_dir = tempfile.TemporaryDirectory()
        srv.CSV_FILE = Path(self.temp_dir.name) / "messages.csv"
        srv.app.config.update(TESTING=True)
        self.client = srv.app.test_client()

    def tearDown(self):
        srv.CSV_FILE = self.old_csv_file
        self.temp_dir.cleanup()

    def test_get_student_page_opens_form(self):
        response = self.client.get("/70193935")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Введите сообщение".encode("utf-8"), response.data)

    def test_index_redirects_to_student_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/70193935", response.location)

    def test_post_message_creates_csv_row(self):
        response = self.client.post(
            "/70193935",
            data={"text": "Привет"},
            environ_overrides={"REMOTE_ADDR": "127.0.0.1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(srv.CSV_FILE.exists())

        rows = srv.read_messages_raw()
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(rows[0]), 4)
        self.assertEqual(rows[0][0], "1")
        self.assertEqual(rows[0][2], "127.0.0.1")
        self.assertEqual(rows[0][3], encrypt("Привет"))
        self.assertIn("Сообщение сохранено".encode("utf-8"), response.data)

    def test_get_all_json_returns_decrypted_text(self):
        self.client.post(
            "/70193935",
            data={"text": "Hello"},
            environ_overrides={"REMOTE_ADDR": "127.0.0.1"},
        )
        response = self.client.get("/get_all.json")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("messages", data)
        self.assertEqual(data["messages"][0]["text"], "Hello")
        self.assertEqual(data["messages"][0]["ip"], "127.0.0.1")

    def test_reset_clears_csv(self):
        self.client.post(
            "/70193935",
            data={"text": "Test"},
            environ_overrides={"REMOTE_ADDR": "127.0.0.1"},
        )
        response = self.client.get("/reset")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(srv.read_messages_raw(), [])
        self.assertIn("messages.csv стёрт".encode("utf-8"), response.data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
