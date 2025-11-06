def list_to_md(items):
    """Convert a list of strings to a markdown bullet list."""
    return "\n".join(f"- {item}" for item in items)
