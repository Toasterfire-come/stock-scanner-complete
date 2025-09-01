import os
import re
import math
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from motor.motor_asyncio import AsyncIOMotorDatabase


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def make_month_year(dt: Optional[datetime] = None) -> str:
    dt = dt or datetime.utcnow()
    return dt.strftime("%Y-%m")


def to_int(val: Any, default: int = 0) -> int:
    try:
        return int(val)
    except Exception:
        return default


def to_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except Exception:
        return default


async def get_next_sequence(db: AsyncIOMotorDatabase, name: str) -> int:
    doc = await db.counters.find_one_and_update(
        {"name": name}, {"$inc": {"seq": 1}}, upsert=True, return_document=True
    )
    # motor may return None on upsert fetch_old; guard
    seq = (doc or {}).get("seq", 1)
    return seq


def paginate(items: List[Dict[str, Any]], page: int = 1, limit: int = 20) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    limit = max(1, min(limit, 100))
    page = max(1, page)
    start = (page - 1) * limit
    end = start + limit
    total = len(items)
    return items[start:end], {"page": page, "limit": limit, "total": total, "pages": math.ceil(total / limit) if limit else 1}


def normalize_ticker(ticker: str) -> str:
    return (ticker or "").strip().upper()


def str_uuid() -> str:
    return str(uuid.uuid4())