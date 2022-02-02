"""
Let's try to crack absurdle
https://qntm.org/files/absurdle/absurdle.html
"""
from itertools import product
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
    if possible_answers == [guess]:
        return WordEval(
            word=guess,
            eval=all_five_letter_evals[-1],
            correct=True,
        ), []
    worst_score = 0
    worst_pruned = WordList.ALL.get()
    worst_hint = None
    for five_letter_eval in all_five_letter_evals:
        word_eval = WordEval(
            word=guess,
            eval=five_letter_eval,
            correct=False,
        )
        pruned = [ans for ans in possible_answers if word_eval.allows(ans)]
        score = len(pruned)
        if score > worst_score:
            worst_score = score
            worst_pruned = pruned
            worst_hint = word_eval
    return worst_hint, worst_pruned


def find_best_absurdle_paths(
    valid_guesses: WordList = WordList.CHEAT,
    valid_answers: WordList = WordList.CHEAT,
    width: int = 5,
    depth: int = 10,
) -> list[tuple[list[WordList], list[str]]]:
    start = time.monotonic()
    paths = [([], valid_answers.get())]
    wins = []
    valid_guesses = valid_guesses.get()
    for depth_num in range(depth):
        if not paths:
            break
        if len(wins) >= width:
            break
        new_paths = []
        for path_num, (clues, words) in enumerate(paths):
            for guess_num, guess in enumerate(valid_guesses):
                hint, remaining = antagonize(guess, words)
                new_paths.append((
                    clues + [hint], remaining
                ))
                logger.debug(
                    'Checking word %d/%d in path %d/%d on '
                    'guess %d/%d, %d min elapsed',
                    guess_num + 1,
                    len(valid_guesses),
                    path_num + 1,
                    len(paths),
                    depth_num + 1,
                    depth,
                    (time.monotonic() - start) / 60,
                )
        paths = sorted(new_paths, key=lambda path: len(path[1]))[:width]
        for num, path in enumerate(paths):
            if len(path[1]) == 0:
                wins.append(path)
            else:
                break
        paths = paths[num:]
        logger.info('Current wins: %s', wins)
        logger.info('Current paths: %s', paths)
    return wins
