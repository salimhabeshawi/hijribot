import unittest
from datetime import datetime

from main import days_until_ramadan, format_hijri_date


class TestHijriHelpers(unittest.TestCase):
    def test_format_hijri_date_at_ramadan_start(self):
        # 2023-03-23 Gregorian is 1 Ramadan 1444 AH
        dt = datetime(2023, 3, 23)
        self.assertEqual(format_hijri_date(dt), "1 Ramadan 1444 AH")

    def test_days_until_ramadan_before_start(self):
        dt = datetime(2023, 3, 20)  # three days before Ramadan 1444
        self.assertEqual(days_until_ramadan(dt), 3)

    def test_days_until_ramadan_on_start(self):
        dt = datetime(2023, 3, 23)
        self.assertEqual(days_until_ramadan(dt), 0)


if __name__ == "__main__":
    unittest.main()
