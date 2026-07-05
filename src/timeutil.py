from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Optional


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_date(value: str) -> Optional[datetime]:
    if not value:
        return None
    value = value.strip()
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def within_days(dt: Optional[datetime], days: int) -> bool:
    if dt is None:
        return True
    return dt >= now_utc() - timedelta(days=days)

