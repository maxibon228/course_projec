import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import cypher


class Stage1CypherTests(unittest.TestCase):
    def test_decrypt_encrypt_returns_original_text(self):
        test_cases = [
            "Привет, мир!",
            "Hello, World!",
            "Тест 123 / test.",
            "ID 70193935",
            "",
        ]
        for text in test_cases:
            with self.subTest(text=text):
                encrypted = cypher.encrypt(text)
                decrypted = cypher.decrypt(encrypted)
                self.assertEqual(decrypted, text)

    def test_functions_work_with_explicit_sid(self):
        text = "Проверка sid"
        encrypted = cypher.encrypt(text, sid=70193935)
        decrypted = cypher.decrypt(encrypted, sid=70193935)
        self.assertEqual(decrypted, text)

    def test_main_block_is_not_executed_on_import(self):
        source_dir = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            shutil.copy(source_dir / "cypher.py", temp_dir / "cypher.py")
            shutil.copy(source_dir / "encrypt.txt", temp_dir / "encrypt.txt")
            shutil.copy(source_dir / "decrypt.txt", temp_dir / "decrypt.txt")

            spec = importlib.util.spec_from_file_location("cypher_temp", temp_dir / "cypher.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self.assertFalse((temp_dir / "encrypt_result.txt").exists())
            self.assertFalse((temp_dir / "decrypt_result.txt").exists())

    def test_direct_run_creates_result_files(self):
        source_dir = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            shutil.copy(source_dir / "cypher.py", temp_dir / "cypher.py")
            shutil.copy(source_dir / "encrypt.txt", temp_dir / "encrypt.txt")
            shutil.copy(source_dir / "decrypt.txt", temp_dir / "decrypt.txt")

            completed = subprocess.run(
                [sys.executable, "cypher.py"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                check=True,
            )

            self.assertIn("Результаты шифрования", completed.stdout)
            self.assertTrue((temp_dir / "encrypt_result.txt").exists())
            self.assertTrue((temp_dir / "decrypt_result.txt").exists())
            self.assertGreater((temp_dir / "encrypt_result.txt").stat().st_size, 0)
            self.assertGreater((temp_dir / "decrypt_result.txt").stat().st_size, 0)

    def test_expected_shift_for_student_id(self):
        self.assertEqual(70193935 % 11, 9)

    def test_alphabet_order_contains_required_parts(self):
        alphabet = cypher._get_alphabet()
        self.assertTrue(alphabet.startswith("0123456789"))
        self.assertIn("абвг", alphabet)
        self.assertIn("АБВГ", alphabet)
        self.assertIn("abcd", alphabet)
        self.assertIn("ABCD", alphabet)
        self.assertTrue(alphabet.endswith(" "))


if __name__ == "__main__":
    unittest.main(verbosity=2)
