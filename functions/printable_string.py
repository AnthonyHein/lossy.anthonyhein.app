from printable_character import PrintableCharacter

import random
import typing


class PrintableString():
    def __init__(self, s: str) -> None:
        assert type(s) == str
        self.cs: typing.List[PrintableCharacter] = []
        for c in s:
            try:
                self.cs.append(PrintableCharacter(c))
            except ValueError:
                self.cs = []
                raise ValueError

    def __len__(self) -> int:
        return len(self.cs)

    def __add__(self, other: 'PrintableString') -> 'PrintableString':
        s: str = ''.join(str(a + b) for a, b in zip(self.cs, other.cs))
        return PrintableString(s)

    def __neg__(self) -> 'PrintableString':
        s: str = ''.join(str(-c) for c in self.cs)
        return PrintableString(s)

    def __str__(self) -> str:
        s: str = ''.join(str(c) for c in self.cs)
        return s

    @ staticmethod
    def generate_key(length: int) -> 'PrintableString':
        s: str = ''.join(random.choices(PrintableCharacter.RANGE, k=length))
        return PrintableString(s)
