# Payment case

The Payment case demonstrates an intentionally asymmetric boundary. A left-side amount in cents becomes a right-side
decimal amount, while the reverse direction converts dollars back to cents with its own callable. Both directions
receive
the keyword-only `ctx` context for the minor-unit policy and currency.


## Example

```python
from dataclasses import dataclass

from betwixt import Betwixt, field_refs, map_leftward, map_rightward, reduce_rightward

@dataclass
class Payment:
    cents: int

@dataclass
class PaymentView:
    dollars: float
    currency: str

left, right = field_refs(Payment, PaymentView)

class PaymentMapping(Betwixt):
    left = Payment
    right = PaymentView
    dollars = map_rightward(left=left.cents, right=right.dollars,
                            rightward=lambda cents, *, ctx: cents / ctx["minor_units"])
    currency = reduce_rightward(right=right.currency,
                                rightward=lambda _payment, *, ctx: ctx["currency"])
    cents = map_leftward(right=right.dollars, left=left.cents,
                         leftward=lambda dollars, *, ctx: round(dollars * ctx["minor_units"]))

mapping = PaymentMapping()
context = {"minor_units": 100, "currency": "USD"}
right = mapping.rightward(Payment(1210), context=context)
left = mapping.leftward(PaymentView(12.10, "USD"), context=context)
patch = mapping.leftward_partial({"dollars": 12.10}, context=context)

assert right.dollars == 12.10
assert right.currency == "USD"
assert left == Payment(1210)
assert patch == {"cents": 1210}
```
