"""Fixture for out-of-scope occurrence reporting in the solid-coding eval suite.

The eval scopes the run to this file only. `_format_cents` below re-implements
`money.format_cents` — the same display rule, not coincidentally similar code,
so a change to how the shop renders money must be made in lockstep (DRY
violation). receipt.py and refund.py carry identical copies, but they sit
outside the requested scope: the skill must report them as out-of-scope
occurrences for the user to act on, and must not edit them.
"""


def _format_cents(cents):
    return f"${cents // 100}.{cents % 100:02d}"


def invoice_line(description, cents):
    return f"{description}: {_format_cents(cents)}"
