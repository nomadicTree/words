import unicodedata
import re


def safe_snake_case_filename(s: str = "word", extension: str = "txt") -> str:
    # Normalize unicode characters to ASCII equivalents
    if len(s) == 0:
        s = "word"
    s = (
        unicodedata.normalize("NFKD", s)
        .encode("ascii", "ignore")
        .decode("ascii")
    )

    # Replace illegal filename characters with underscore
    s = re.sub(r'[\/\\\:\*\?"<>\|]', "_", s)

    # Replace spaces, hyphens, and dots with underscore
    s = re.sub(r"[\s\-.]+", "_", s)

    # Add underscore before uppercase letters (CamelCase → snake_case)
    s = re.sub(r"(?<!^)(?=[A-Z])", "_", s)

    # Lowercase everything
    s = s.lower()

    # Collapse multiple underscores
    s = re.sub(r"_+", "_", s)

    # Strip leading/trailing underscores
    return f"{s.strip("_")}.{extension}"


def format_time_text(elapsed_time: float) -> str:
    """Format elapsed time into a human-readable string

    Args:
        time: elapsed time in seconds

    Returns:
        Formatted time string
    """
    if elapsed_time < 0.001:
        return f"{elapsed_time * 1_000_000:.1f} µs"
    else:
        return f"{elapsed_time * 1_000:.3f} ms"
