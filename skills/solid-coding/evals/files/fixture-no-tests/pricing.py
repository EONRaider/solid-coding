"""Deliberately flawed fixture for the solid-coding skill's eval suite.

Mixes persistence, business-rule application, and presentation formatting
in one function (SRP/SoC violation), and applies discounts through a
type-keyed conditional that grows with every new order type (OCP violation).
There is no test file anywhere in this fixture, on purpose.
"""

DATABASE = {
    "c1": {"name": "Ada Lovelace"},
    "c2": {"name": "Alan Turing"},
}


def process_order(order):
    # Persistence: reach into "the database" directly.
    customer = DATABASE[order["customer_id"]]

    # Business rule: a type-keyed conditional that grows with every new
    # order type — the OCP signal (see references/solid-principles.md).
    if order["type"] == "standard":
        price = order["base_price"]
    elif order["type"] == "premium":
        price = order["base_price"] * 0.9
    elif order["type"] == "bulk":
        price = order["base_price"] * 0.8 * order["quantity"]
    elif order["type"] == "clearance":
        price = order["base_price"] * 0.5
    else:
        price = order["base_price"]

    # Presentation: formatting mixed into the same function as the above two.
    formatted = f"${price:.2f}"
    print(f"Order for {customer['name']}: {formatted}")
    return formatted
