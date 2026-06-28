import datetime as dt
from zoneinfo import ZoneInfo

import app.main as main


def test_nearest_contact_date_skips_fully_booked_day(monkeypatch) -> None:
    timezone_name = "Europe/Paris"
    tz = ZoneInfo(timezone_name)
    today = dt.datetime.now(tz).date()
    busy_periods = [
        (
            dt.datetime.combine(today, dt.time(0, 0), tzinfo=tz),
            dt.datetime.combine(today + dt.timedelta(days=1), dt.time(0, 0), tzinfo=tz),
        )
    ]

    monkeypatch.setattr(
        main,
        "_contact_calendar_busy_periods",
        lambda *_args, **_kwargs: (busy_periods, None),
    )

    selected_date, error = main._nearest_contact_available_date(
        30,
        timezone_name,
        horizon_days=2,
    )

    assert error is None
    assert selected_date == today + dt.timedelta(days=1)


def test_contact_slots_exclude_busy_periods() -> None:
    timezone_name = "Europe/Paris"
    tz = ZoneInfo(timezone_name)
    selected_date = dt.datetime.now(tz).date() + dt.timedelta(days=1)
    busy_periods = [
        (
            dt.datetime.combine(selected_date, dt.time(10, 0), tzinfo=tz),
            dt.datetime.combine(selected_date, dt.time(11, 0), tzinfo=tz),
        )
    ]

    available = main._contact_slots_outside_busy_periods(
        selected_date,
        30,
        timezone_name,
        [dt.time(9, 30), dt.time(10, 0), dt.time(10, 30), dt.time(11, 0)],
        busy_periods,
    )

    assert available == [dt.time(9, 30), dt.time(11, 0)]
