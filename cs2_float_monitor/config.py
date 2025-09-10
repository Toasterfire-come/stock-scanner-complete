from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

import yaml
from pydantic import BaseModel, Field, HttpUrl, ValidationError, field_validator


class ItemConfig(BaseModel):
    id: int
    url: HttpUrl
    max_float: float = Field(gt=0.0, lt=1.0)
    max_price: float = Field(gt=0.0)
    max_open: int = Field(default=1, ge=1)


class AppConfig(BaseModel):
    polling_interval_seconds: float = Field(default=1.0, gt=0.1)
    country: str = Field(default="US", min_length=2, max_length=2)
    currency: int = Field(default=1)
    user_agent: str = Field(default=(
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ))
    max_concurrent_float_lookups: int = Field(default=4, ge=1, le=8)
    listing_page_count: int = Field(default=20, ge=10, le=100)
    items: List[ItemConfig]

    @field_validator("items")
    @classmethod
    def validate_items(cls, items: List[ItemConfig]) -> List[ItemConfig]:
        ids = set()
        for item in items:
            if item.id in ids:
                raise ValueError(f"Duplicate item id: {item.id}")
            ids.add(item.id)
        return items


def load_config(path: str) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    try:
        return AppConfig.model_validate(raw)
    except ValidationError as e:
        raise SystemExit(f"Config validation error: {e}")

