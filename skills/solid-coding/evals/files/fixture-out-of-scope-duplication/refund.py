def _format_cents(cents):
    return f"${cents // 100}.{cents % 100:02d}"


def refund_notice(cents):
    return f"Refunded: {_format_cents(cents)}"
