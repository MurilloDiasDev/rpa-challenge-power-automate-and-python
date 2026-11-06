import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook

spec = importlib.util.spec_from_file_location('challenge', Path(__file__).parents[1] / 'python' / 'challenge.py')
challenge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(challenge)


class Element:
    text = '100% success'
    def click(self):
        pass


class FakeDriver:
    def __init__(self, fail_at=None):
        self.calls = 0
        self.fail_at = fail_at
        self.closed = False
    def get(self, url):
        self.url = url
    def execute_script(self, script, *args):
        self.calls += 1
        if self.calls == self.fail_at:
            raise RuntimeError('falha simulada')
        return 'id-anterior'
    def find_element(self, *args):
        return Element()
    def save_screenshot(self, filename):
        Path(filename).write_bytes(b'png')
        return True
    def quit(self):
        self.closed = True


class FakeWait:
    def __init__(self, *args, **kwargs):
        pass
    def until(self, condition):
        return Element()


class ChallengeTests(unittest.TestCase):
    def make_excel(self, directory, n=10, empty=False):
        book = Workbook()
        sheet = book.active
        sheet.append(list(challenge.HEADERS))
        for i in range(n):
            row = [f'v{i}-{j}' for j in range(7)]
            if empty and i == 3:
                row[2] = None
            sheet.append(row)
        path = Path(directory) / 'input.xlsx'
        book.save(path)
        return path

    def test_reads_ten_rows_and_rejects_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(len(challenge.read_records(self.make_excel(tmp, n=12))), 10)
            with self.assertRaises(ValueError):
                challenge.read_records(self.make_excel(tmp, empty=True))
            with self.assertRaises(ValueError):
                challenge.read_records(self.make_excel(tmp, n=9))

    def test_success_creates_ten_results_and_screenshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_excel(tmp)
            driver = FakeDriver()
            with patch.object(challenge.webdriver, 'Chrome', return_value=driver), patch.object(challenge, 'WebDriverWait', FakeWait):
                self.assertEqual(challenge.run(path, Path(tmp) / 'out', 1), 0)
            result = next((Path(tmp) / 'out').glob('resultados_*.csv'))
            with result.open(encoding='utf-8-sig', newline='') as f:
                rows = list(csv.DictReader(f, delimiter=';'))
            self.assertEqual(len(rows), 10)
            self.assertTrue(all(row['status'] == 'OK' for row in rows))
            self.assertTrue(list((Path(tmp) / 'out').glob('resultado_final_*.png')))
            self.assertTrue(driver.closed)

    def test_failure_records_nok_and_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_excel(tmp)
            driver = FakeDriver(fail_at=3)
            with patch.object(challenge.webdriver, 'Chrome', return_value=driver), patch.object(challenge, 'WebDriverWait', FakeWait):
                self.assertEqual(challenge.run(path, Path(tmp) / 'out', 1), 1)
            result = next((Path(tmp) / 'out').glob('resultados_*.csv'))
            with result.open(encoding='utf-8-sig', newline='') as f:
                rows = list(csv.DictReader(f, delimiter=';'))
            self.assertEqual([row['status'] for row in rows], ['OK', 'OK', 'NOK'])
            self.assertIn('falha simulada', rows[-1]['observacao'])
            self.assertFalse(list((Path(tmp) / 'out').glob('resultado_final_*.png')))
            self.assertTrue(driver.closed)


if __name__ == '__main__':
    unittest.main()
