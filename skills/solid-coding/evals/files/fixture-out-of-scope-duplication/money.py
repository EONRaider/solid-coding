"""The shop's single rule for rendering an amount in cents for display."""


def format_cents(cents):
    return f"${cents // 100}.{cents % 100:02d}"
