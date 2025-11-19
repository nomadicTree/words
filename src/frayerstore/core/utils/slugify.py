import re


def slugify(s: str) -> str:
    """Slugify a string"""
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")
