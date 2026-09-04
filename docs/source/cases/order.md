# Order case

Orders bring several mapping ideas together. This example contains an `identifier`, an optional `address`, a list of
`items`, and an optional `note`. It does not contain a customer field.
Nested mappings preserve scalar, optional, and list shapes. A context derivation passes order-level request context to
every line-item mapping once per nested boundary.


## Example

```python
from dataclasses import dataclass

from betwixt import Betwixt, field_refs, nested_rightward

@dataclass
class Order:
    identifier: int
    address: None
    items: list

@dataclass
class OrderView:
    identifier: int
    address: None
    items: list

left, right = field_refs(Order, OrderView)

class OrderMapping(Betwixt):
    left = Order
    right = OrderView
    address = nested_rightward(left=left.address, right=right.address, via=None,
                               rightward=lambda value: value,
                               context_rightward=lambda context: context)
    items = nested_rightward(left=left.items, right=right.items, via=None,
                             rightward=lambda value: value,
                             context_rightward=lambda context: context)

mapping = OrderMapping()
translated = mapping.rightward(Order(42, None, []), context={"minor_units": 100})
patch = mapping.rightward_partial({"items": []})
```

The patch is sparse: omitted fields stay omitted, present `None` stays present, and defaults never appear in a partial
result.
