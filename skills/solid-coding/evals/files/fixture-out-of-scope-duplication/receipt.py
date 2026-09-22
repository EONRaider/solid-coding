def _format_cents(cents):
    return f"${cents // 100}.{cents % 100:02d}"


def receipt_total(cents):
    return f"Total paid: {_format_cents(cents)}"
