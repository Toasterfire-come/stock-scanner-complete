from datetime import datetime, timezone


def next_month_first_utc(now: datetime | None = None) -> datetime:
    """Return a datetime at 00:00:00 UTC on the first day of the next month.
    Safe for year boundaries.
    """
    now = now or datetime.now(timezone.utc)
    year = now.year
    month = now.month
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1
    return datetime(next_year, next_month, 1, 0, 0, 0, tzinfo=timezone.utc)
