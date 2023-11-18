import string
import typing


class PrintableCharacter():
    RANGE: typing.List[str] = string.ascii_letters \
        + string.digits \
        + string.punctuation \
        + " "

    def __init__(self, c: str) -> None:
        assert type(c) == str
        self.c: str = c
        self.i: int = self.RANGE.index(self.c)

    def __str__(self) -> str:
        return self.c

    def __int__(self) -> int:
        return self.i

    def __add__(self, other: 'PrintableCharacter') -> 'PrintableCharacter':
        return PrintableCharacter(self.RANGE[(self.i + other.i) % len(self.RANGE)])

    def __neg__(self) -> 'PrintableCharacter':
        return PrintableCharacter(self.RANGE[(len(self.RANGE) - self.i) % len(self.RANGE)])
