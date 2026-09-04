# Examples

These standalone source files follow the teaching arc from basic mappings through optional integrations.


## Teaching arc

- [`basics.py`](https://github.com/dusktreader/betwixt/blob/main/examples/basics.py): implicit same-name dataclass
  mapping
- [`constructs.py`](https://github.com/dusktreader/betwixt/blob/main/examples/constructs.py): field, object, nested,
  and control constructs
- [`expansion.py`](https://github.com/dusktreader/betwixt/blob/main/examples/expansion.py): expansion and reverse
  mapping
- [`composition.py`](https://github.com/dusktreader/betwixt/blob/main/examples/composition.py): declaration order and
  last-write-wins behavior
- [`pydantic.py`](https://github.com/dusktreader/betwixt/blob/main/examples/pydantic.py): dataclass source and Pydantic
  destination
- [`sqlalchemy.py`](https://github.com/dusktreader/betwixt/blob/main/examples/sqlalchemy.py): dataclass source and
  SQLAlchemy destination
- [`combined.py`](https://github.com/dusktreader/betwixt/blob/main/examples/combined.py): bidirectional Pydantic and
  SQLAlchemy boundary mapping
- [`checkout.py`](https://github.com/dusktreader/betwixt/blob/main/examples/checkout.py): a complete checkout mapping
  with nested lines, runtime currency context, aliases, and a persisted total

The reference files are source examples, not a Python package or command-line interface. Run `betwixt-demo` for the
guided, executable walkthrough. The demo is implemented separately under `betwixt_demo`.

```shell
uv run betwixt-demo
```
