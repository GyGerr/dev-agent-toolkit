"""An intentionally defective parser for review/regression evaluation."""


def parse_count(value):
    """Parse a non-negative decimal count; invalid values raise ValueError."""
    return int(value)
