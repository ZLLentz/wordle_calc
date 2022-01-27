from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
from random import choice
import logging

from .words import get_words

logger = logging.getLogger(__name__)


class LetterEval(Enum):
    WRONG = 0
    MOVED = 1
    GOOD = 2


@dataclass
class WordEval:
    word: str
    eval: list[LetterEval]
    correct: bool

    @classmethod
    def from_guess(cls, guess: str, answer: str) -> WordEval:
        eval = []
        correct = True
        for letter, ans in zip(guess, answer):
            if letter == ans:
                eval.append(LetterEval.GOOD)
            elif letter in answer:
                eval.append(LetterEval.MOVED)
                correct = False
            else:
                eval.append(LetterEval.WRONG)
                correct = False
        return WordEval(
            word=guess,
            eval=eval,
            correct=correct,
        )

    def allows(self, word: str) -> bool:
        for guess, ans, eval in zip(word, self.word, self.eval):
            if eval == LetterEval.GOOD:
                if guess != ans:
                    return False
            elif eval == LetterEval.MOVED:
                if guess == ans or ans not in word:
                    return False
            elif eval == LetterEval.WRONG:
                if ans in word:
                    return False
        return True

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
    running: bool = True
    victory: bool = False

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
        logger.debug('Guessed %s', guess)
        if guess not in self.words:
            return None
        clue = WordEval.from_guess(guess, self.answer)
        self.clues.append(clue)
        if clue.correct or len(self.clues) >= 6:
            logger.debug('Game Complete!')
            self.running = False
            self.victory = clue.correct
        return clue

    def __str__(self) -> str:
        return (
            ' ' * 4 + 'Wordle' + ' ' * 4
            + '\n' + '-' * 15 + '\n'
            + '\n'.join(str(clue) for clue in self.clues)
        )
