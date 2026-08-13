#!/usr/bin/env python3
"""
Migration Fortune
=================

A tiny, self-contained feature that hands back a random, encouraging (or
mildly sarcastic) fortune to brighten up a Python 2 -> 3 migration session.

Why? Migrating code is tedious, and a little bit of random silliness in the
terminal can make the grind more tolerable. The module keeps its own small
catalog of fortunes so it has no dependencies beyond the standard library.
"""

import random


FORTUNES = [
    "A print statement is neither a function nor a statement; it is a way of life. In Python 3, it is finally a function too.",
    "You are xrange days away from falling in love with range. Actually, you now just have range.",
    "The second argument to map is iterable, not a list. Breathe; it is going to be okay.",
    "Long live Unicode strings, for you shall not see enough of bytes.",
    "Fortune favors the bold who remember to call super().__init__().",
    "Your except-blocks will soon stop silently swallowing exceptions. Clarity is coming.",
    "Raise from the ashes, and carry the original traceback with you wherever you go.",
    "Integer division no longer rounds down against your will. Embrace the float.",
    "That old metaclass you feared is now just a class keyword argument away.",
    "Your dictionary views are dynamic. Enjoy the view.",
    "Unpacking arguments has never looked this clean; your future self thanks you.",
    "A generator expression is more than a tuple; it is an idea whose time has come.",
    "Colon-free print lines are a memory now. The future prints through a portal called sys.stdout.",
    "Zip returns an iterator in the future; do not rely on its length, trust its spirit.",
    "The input() of the future does not eval. Security is a lifestyle.",
    "Enumerate is your friend, and range(len(...)) is your former roommate.",
    "File operations use open() everywhere now. Encoding is explicit, and that is a good thing.",
    "Your bytes are immutable, your memoryview is a window, and your future is bright.",
]


class MigrationFortune:
    """Random fortune generator for migration-themed motivation.

    Primarily useful for decoration and morale. Supports a ``seed`` so tests
    (and anyone else) can get deterministic output.
    """

    def __init__(self, seed=None):
        self._rng = random.Random(seed)

    def get_fortune(self):
        """Return a uniformly random fortune string from the catalog."""
        return self._rng.choice(FORTUNES)

    @property
    def count(self):
        """Number of fortunes in the catalog."""
        return len(FORTUNES)


def main():
    """Print a single random fortune to stdout."""
    print(MigrationFortune().get_fortune())


if __name__ == "__main__":
    main()