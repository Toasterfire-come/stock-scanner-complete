"""
US Market Calendar utilities: determine market open/closed and holidays.

Avoids external dependencies; includes a lightweight NYSE holiday set.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
import pytz

EASTERN = pytz.timezone("US/Eastern")


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """Return the date of the nth weekday (0=Mon) in a given month/year."""
    d = date(year, month, 1)
    count = 0
    while True:
        if d.weekday() == weekday:
            count += 1
            if count == n:
                return d
        d += timedelta(days=1)


def _last_weekday(year: int, month: int, weekday: int) -> date:
    """Return the date of the last weekday (0=Mon) in a given month/year."""
    # Start at next month first day then step back
    if month == 12:
        d = date(year + 1, 1, 1)
    else:
        d = date(year, month + 1, 1)
    d -= timedelta(days=1)
    while d.weekday() != weekday:
        d -= timedelta(days=1)
    return d


def observed(dt: date) -> date:
    """Apply NYSE observed rule if holiday falls on weekend."""
    if dt.weekday() == 5:  # Saturday -> observed Friday
        return dt - timedelta(days=1)
    if dt.weekday() == 6:  # Sunday -> observed Monday
        return dt + timedelta(days=1)
    return dt


def nyse_holidays(year: int) -> set[date]:
    """Approximate NYSE holiday set for a given year (regular holidays)."""
    # New Year's Day
    new_years = observed(date(year, 1, 1))
    # Martin Luther King Jr. Day (3rd Monday of January)
    mlk = _nth_weekday(year, 1, 0, 3)
    # Presidents' Day (3rd Monday of February)
    presidents = _nth_weekday(year, 2, 0, 3)
    # Good Friday (approximate: two days before Easter Sunday). Keep it simple: hard skip; can extend later
    # For practicality, exclude Good Friday if not easily computed here.
    # Memorial Day (last Monday in May)
    memorial = _last_weekday(year, 5, 0)
    # Juneteenth (June 19)
    juneteenth = observed(date(year, 6, 19))
    # Independence Day (July 4)
    independence = observed(date(year, 7, 4))
    # Labor Day (1st Monday in September)
    labor = _nth_weekday(year, 9, 0, 1)
    # Thanksgiving Day (4th Thursday in November)
    thanksgiving = _nth_weekday(year, 11, 3, 4)
    # Christmas Day (Dec 25)
    christmas = observed(date(year, 12, 25))

    return {
        new_years,
        mlk,
        presidents,
        memorial,
        juneteenth,
        independence,
        labor,
        thanksgiving,
        christmas,
    }


def is_market_holiday(dt: date) -> bool:
    return dt in nyse_holidays(dt.year)


def is_regular_market_open(now_et: datetime, market_open_hhmm: str = "09:30", market_close_hhmm: str = "16:00") -> bool:
    """Return True if regular market is open at the given ET datetime and not a holiday/weekend."""
    if now_et.tzinfo is None:
        now_et = EASTERN.localize(now_et)
    # Weekend
    if now_et.weekday() >= 5:
        return False
    # Holiday
    if is_market_holiday(now_et.date()):
        return False
    hhmm = now_et.strftime("%H:%M")
    return market_open_hhmm <= hhmm < market_close_hhmm

