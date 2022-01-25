from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
from random import choice

from .words import get_words


class LetterEval(Enum):
    WRONG = 0
    MOVED = 1
    GOOD = 2


@dataclass
class WordEval:
    word: str
    eval: list[LetterEval]

    @classmethod
    def from_guess(cls, guess, answer):
        eval = []
        for letter, ans in zip(guess, answer):
            if letter == ans:
                eval.append(LetterEval.GOOD)
            elif letter in answer:
                eval.append(LetterEval.MOVED)
            else:
                eval.append(LetterEval.WRONG)
        return WordEval(
            word=guess,
            eval=eval,
        )

    def __str__(self) -> str:
        text = ''
        for letter, eval in zip(self.word, self.eval):
            if eval == LetterEval.WRONG:
                text += f' {letter} '
            elif eval == LetterEval.MOVED:
                text += f':{letter}:'
            elif eval == LetterEval.GOOD:
                text += f'|{letter}|'
            else:
                text += '_?_'
        return text


@dataclass
class SingleGame:
    answer: str
    clues: list[WordEval]
    words: list[str]

    @classmethod
    def begin(cls, answer: Optional[str] = None) -> SingleGame:
        words = get_words()
        if answer is None:
            answer = choice(words)
        return SingleGame(
            answer=answer,
            clues=[],
            words=words,
        )

    def make_guess(self, guess: str) -> Optional[WordEval]:
        if guess not in self.words:
            return None
        clue = WordEval.from_guess(guess, self.answer)
        self.clues.append(clue)

    def __str__(self) -> str:
        return 'Wordle\n------\n' + '\n'.join(str(clue) for clue in self.clues)
