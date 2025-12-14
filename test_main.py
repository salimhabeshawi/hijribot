import pytest
from datetime import datetime

from main import days_until_ramadan, format_hijri_date


def test_format_hijri_date_at_ramadan_start():
    # 2023-03-23 Gregorian is 1 Ramadan 1444 AH
    dt = datetime(2023, 3, 23)
    assert format_hijri_date(dt) == "1 Ramadan 1444 AH"


def test_days_until_ramadan_before_start():
    # Three days before Ramadan 1444 began
    dt = datetime(2023, 3, 20)
    assert days_until_ramadan(dt) == 3


def test_days_until_ramadan_on_start():
    dt = datetime(2023, 3, 23)
    assert days_until_ramadan(dt) == 0
