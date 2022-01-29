from __future__ import annotations

from enum import IntEnum
from pathlib import Path


class WordList(IntEnum):
    ALL = 0
    SGB = 1
    CHEAT = 2

    def get(self) -> list[str]:
        return get_words(self)


HERE = Path(__file__).parent
FILES = {
    WordList.ALL: HERE / 'dictionary.txt',
    WordList.SGB: HERE / 'sgb-words.txt',
    WordList.CHEAT: HERE / 'cheater.txt',
}

def get_words(source: WordList) -> list[str]:
    with FILES[source].open('r') as fd:
        return fd.read().splitlines()
