"""Temporary file for a Claude review smoke test. Do not merge."""


def chunk(items, size):
    """Split items into consecutive lists of at most `size` items."""
    return [items[i:i + size] for i in range(0, len(items) - size, size)]
