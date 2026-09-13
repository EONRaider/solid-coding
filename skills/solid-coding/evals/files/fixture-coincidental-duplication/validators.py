"""Fixture for the DRY-vs-AHA tension: these two functions look identical
today but validate independently-changing business rules (a price floor
and an age floor). A naive DRY pass would merge them into one
`validate_positive` helper — that is the wrong call, and the eval checks
that the skill does not propose it.
"""


def validate_price(value):
    if value <= 0:
        raise ValueError("price must be positive")
    return value


def validate_age(value):
    if value <= 0:
        raise ValueError("age must be positive")
    return value
