from datetime import timedelta, date

from box2adls.util import get_last_friday


def test_get_last_friday():
    today = date(year=2020, month=8, day=1)

    assert get_last_friday(today) == date(year=2020, month=7, day=31)

    today = today + timedelta(days=1)

    assert get_last_friday(today) == date(year=2020, month=7, day=31)

    today = today + timedelta(days=7)

    assert get_last_friday(today) == date(year=2020, month=8, day=7)

    today = today + timedelta(days=7)

    assert get_last_friday(today) == date(year=2020, month=8, day=14)
