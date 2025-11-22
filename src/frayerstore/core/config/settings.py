from dataclasses import dataclass
from functools import lru_cache
import tomllib
import pandas as pd

from frayerstore.paths import CONFIG_PATH


def parse_ttl(value: str | int | None) -> int | None:
    """
    Parse cache TTL from config.

    Returns:
        None → no expiration
        int → number of seconds
    """
    if value is None:
        return None

    # already numeric → treat as seconds
    if isinstance(value, int):
        return value

    text = str(value).strip().lower()

    # explicit "no expiry"
    if text in ("none", "off", "false", "infinite", "forever"):
        return None

    try:
        td = pd.Timedelta(text)
        return int(td.total_seconds())
    except Exception:
        raise ValueError(f"Invalid TTL value: {value!r}")


@dataclass(frozen=True)
class CacheSettings:
    db_connection_ttl: int | None
    frequent_query_ttl: int | None
    search_ttl: int | None


@dataclass(frozen=True)
class Settings:
    cache: CacheSettings


@lru_cache
def load_settings() -> Settings:
    """Load settings to Settings object"""
    with CONFIG_PATH.open("rb") as f:
        raw = tomllib.load(f)

    raw_cache = raw["cache"]

    cache_settings = CacheSettings(
        db_connection_ttl=parse_ttl(raw_cache["db_connection_ttl"]),
        frequent_query_ttl=parse_ttl(raw_cache["frequent_query_ttl"]),
        search_ttl=parse_ttl(raw_cache["search_ttl"]),
    )
    return Settings(cache_settings)
