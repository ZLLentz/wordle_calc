"""
Let's try to crack absurdle
https://qntm.org/files/absurdle/absurdle.html
"""
from itertools import product
from typing import Callable, Union, Optional
import logging
import time

from .game import LetterEval, WordEval
from .words import WordList


logger = logging.getLogger(__name__)
all_five_letter_evals = list(product(LetterEval, LetterEval, LetterEval, LetterEval, LetterEval))


def antagonize(
    guess: str,
    possible_answers: list[str],
) -> tuple[WordEval, list[str]]:
    """Give the least helpful hint possible."""
    worst_score = 0
    worst_pruned = None
    worst_hint = None
    for five_letter_eval in all_five_letter_evals:
        word_eval = WordEval(
            word=guess,
            eval=five_letter_eval,
            correct=(five_letter_eval == all_five_letter_evals[-1])
        )
        pruned = [ans for ans in possible_answers if word_eval.allows(ans)]
        score = len(pruned)
        if score > worst_score:
            worst_score = score
            worst_pruned = pruned
            worst_hint = word_eval
    return worst_hint, worst_pruned


def simulate_all_absurdle_games(
    valid_guesses: Union[WordList, list] = WordList.ALL,
    valid_answers: Union[WordList, list] = WordList.CHEAT,
    max_depth: int = 4,
    prune: Optional[Callable] = None,
    inner_depth = None,
) -> list[list[WordEval]]:
    if inner_depth is None:
        inner_depth = max_depth
        start = time.monotonic()
    if isinstance(valid_guesses, WordList):
        valid_guesses = valid_guesses.get()
    if isinstance(valid_answers, WordList):
        valid_answers = valid_answers.get()
    all_games = []
    for num, guess in enumerate(valid_guesses):
        guess_hint, next_answers = antagonize(guess, valid_answers)
        if inner_depth > 0:
            inner_games = simulate_all_absurdle_games(
                valid_guesses=valid_guesses,
                valid_answers=next_answers,
                max_depth=max_depth,
                inner_depth=inner_depth - 1,
            )
            all_games.append([[guess_hint] + game for game in inner_games])
        else:
            all_games.append([guess_hint])
        if inner_depth == max_depth:
            logger.info('Checked all games that begin with %s', guess)
            logger.info('%d minutes elapsed', (start - time.monotonic()) / 60)
        logger.debug(
            'Finished word %d/%d at depth %d/%d',
            num + 1,
            len(valid_guesses),
            max_depth - inner_depth,
            max_depth,
        )
    if prune is None:
        return all_games
    else:
        return prune(all_games)


def get_winning_absurdle_games(
    depth: int = 4,
) -> list[list[WordEval]]:
    def prune(
        all_games: list[list[WordEval]],
    ) -> list[list[WordEval]]:
        winning = [game for game in all_games if game[-1].correct]
        if len(winning) > 0:
            logger.info('Found %d winning games in branch', len(winning))
        return winning
    
    return simulate_all_absurdle_games(
        max_depth=depth,
        prune=prune,
    )
