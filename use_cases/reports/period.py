from datetime import UTC, datetime, time, timedelta, timezone

from fastapi import HTTPException


JAKARTA = timezone(timedelta(hours=7), "Asia/Jakarta")


def resolve_period(query):
    date_to = query.date_to or datetime.now(JAKARTA).date()
    date_from = query.date_from or date_to.replace(day=1)
    if date_from > date_to:
        raise HTTPException(422, "date_from tidak boleh setelah date_to.")
    try:
        start = datetime.combine(date_from, time.min, JAKARTA).astimezone(UTC)
        end = datetime.combine(date_to + timedelta(days=1), time.min, JAKARTA).astimezone(UTC)
    except (OverflowError, ValueError):
        raise HTTPException(422, "Rentang tanggal tidak didukung.") from None
    return {"date_from": date_from, "date_to": date_to, "timezone": "Asia/Jakarta", "inclusive": True}, start, end
