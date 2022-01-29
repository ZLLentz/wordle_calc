from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional
from random import choice
import logging

from .words import WordList

logger = logging.getLogger(__name__)


class LetterEval(IntEnum):
    WRONG = 0
    MOVED = 1
    GOOD = 2


@dataclass
class WordEval:
    word: str
    eval: list[LetterEval]
    correct: bool

    def __post_init__(self):
        self.eval_map = self.get_eval_map()

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

    def get_eval_map(self):
        final_map = {}
        for eval_int in (LetterEval.GOOD, LetterEval.MOVED, LetterEval.WRONG):
            final_map[eval_int] = [
                index for index, eval in enumerate(self.eval)
                if eval == eval_int
            ]
        return final_map

    def allows(self, word: str) -> bool:
        for index in self.eval_map[LetterEval.GOOD]:
            if word[index] != self.word[index]:
                return False
        for index in self.eval_map[LetterEval.MOVED]:
            if (
                word[index] == self.word[index]
                or self.word[index] not in word
            ):
                return False
        for index in self.eval_map[LetterEval.WRONG]:
            if self.word[index] in word:
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
    def begin(
        cls,
        answer: Optional[str] = None,
        valid_guesses: WordList = WordList.ALL,
        valid_answers: WordList = WordList.ALL,
    ) -> SingleGame:
        if answer is None:
            answer = choice(valid_answers.get())
        return SingleGame(
            answer=answer,
            clues=[],
            words=valid_guesses.get(),
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
