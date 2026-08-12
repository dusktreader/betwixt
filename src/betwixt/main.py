from textwrap import dedent

from betwixt.version import get_version

__version__ = get_version()


def main():
    print(
        dedent(
            """
            The only way you can get good, unless you're a genius, is to copy. That's the best thing. Just steal.
            --Ritchie Blackmore
            """
        ).strip()
    )
