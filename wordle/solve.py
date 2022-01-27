import logging
import multiprocessing
import time
from collections import defaultdict
from functools import partial

from .game import SingleGame, WordEval
from .words import get_words

logger = logging.getLogger(__name__)
logger.spam = partial(logger.log, 5)


class Strategy:
    def guess(self) -> str:
        raise NotImplementedError

    def simulate_all_games(self) -> dict[int: list[str]]:
        all_words = get_words()
        logger.info(
            "Simulating all %s games.",
            len(all_words)
        )
        results = defaultdict(list)
        incr = 0
        count = 0
        for word in all_words:
            results[self.simulate_game(word)].append(word)
            count += 1
            incr -= 1
            if incr <= 0:
                incr = len(all_words) / 10
                logger.info(f'Simulated {count} games...')
        logger.info("Our score is:")
        logger.info(sorted({val: len(words) for val, words in results.items()}))
        logger.info("We got these words in 1 guess:")
        logger.info(results[1])
        logger.info("We got these words in 2 guesses:")
        logger.info(results[2])
        logger.info("We failed to solve these words:")
        logger.info(results[7])

    def simulate_game(self, answer) -> int:
        self.initialize_game(answer)
        while self.game_instance.running:
            self.simulate_turn()
        logger.info('\n%s', self.game_instance)
        if self.game_instance.victory:
            return len(self.game_instance.clues)
        else:
            return 7

    def initialize_game(self, answer):
        self.words = get_words()
        self.game_instance = SingleGame.begin(answer)

    def simulate_turn(self):
        self.game_instance.make_guess(self.guess())
        logger.debug('\n%s', self.game_instance)
        self.words = prune_words(self.words, self.game_instance.clues)


def prune_words(words: list[str], clues: list[WordEval]) -> list[str]:
    new_words = []
    for word in words:
        if all(clue.allows(word) for clue in clues):
            new_words.append(word)
    logger.debug('%d words remaining: %s', len(new_words), new_words)
    return new_words


class InOrder(Strategy):
    """
    Guess the valid words in order.
    """
    def guess(self) -> str:
        try:
            return self.words[0]
        except IndexError:
            return 'fails'


class SudokuChannel(Strategy):
    """
    Guess the words the Sudoku guys recommend
    Until only one word is possible or until all are used
    """
    def guess(self) -> str:
        if len(self.words) == 0:
            return 'fails'
        if len(self.words) <= 2:
            return self.words[0]
        if len(self.game_instance.clues) == 0:
            return 'siren'
        if len(self.game_instance.clues) == 1:
            return 'octal'
        if len(self.game_instance.clues) == 2:
            return 'dumpy'
        return self.words[0]


class BruteForce(Strategy):
    """
    Pick the word with the highest avg possible words removed
    for all the possible answers.
    """
    precalculated = 'tares'

    def __init__(self):
        self.all_words = get_words()

    def guess(self) -> str:
        if len(self.words) == 0:
            return 'fails'
        if len(self.words) <= 2:
            return self.words[0]
        if len(self.game_instance.clues) == 0:
            return self.precalculated
        if len(self.words) > 100:
            return self.brute_force(
                self.words,
                self.get_likely_guesses(),
            )
        return self.brute_force(self.words, self.all_words)

    def get_likely_guesses(self) -> list[str]:
        guessed = ''.join(clue.word for clue in self.game_instance.clues)
        likely = [
            word for word in self.all_words
            if not any(char in guessed for char in word)
        ]
        logger.debug('Likely guesses are %s', likely)
        return likely
    
    @staticmethod
    def brute_force(
        words: list[str],
        all_words: list[str],
    ) -> str:
        cpus = multiprocessing.cpu_count() - 1
        with multiprocessing.Pool(cpus) as pool:
            scores = pool.imap_unordered(
                partial(
                    BruteForce._check_proc,
                    remaining_ok=words,
                ),
                NoisyList(all_words),
            )
            best_word = all_words[0]
            best_score = 0
            for word, score in scores:
                if score > best_score:
                    logger.debug(
                        "New record! Score for %s is %s!",
                        word,
                        score,
                    )
                    best_word = word
                    best_score = score
        return best_word

    @staticmethod
    def _check_proc(word, remaining_ok) -> tuple[str, int]:
        return word, BruteForce.check_one(
            word,
            remaining_ok,
        )

    @staticmethod
    def check_one(word, remaining_ok) -> int:
        word_score = 0
        for possibility in remaining_ok:
            # If the answer was possibility, how many words are eliminated
            eval = WordEval.from_guess(word, possibility)
            local_score = 0
            for other in remaining_ok:
                if not eval.allows(other):
                    local_score += 1
            # If all the words are eliminated, that is bad, not good!
            if local_score < len(remaining_ok):
                word_score += local_score
        return word_score

    @staticmethod
    def precompute() -> str:
        logger.info('Running precompute...')
        words = get_words()
        ans = BruteForce.brute_force(words, words)
        logger.info('Best word is %s', ans)
        return ans

    @staticmethod
    def check_one_for_profile():
        words = get_words()
        start_time = time.monotonic()
        while time.monotonic() - start_time < 10:
            BruteForce.check_one('check', words)


class NoisyList:
    def __init__(self, words):
        self.words = words
        self.reinit()

    def reinit(self):
        self._iter_words = iter(self.words)
        self.start = time.monotonic()
        self.count = 0

    def __iter__(self):
        self.reinit()
        return self

    def __next__(self):
        word = next(self._iter_words)
        self.count += 1
        logger.spam(
            'Doing %s, (%d / %d), %.2f mins elapsed',
            word,
            self.count,
            len(self.words),
            (time.monotonic() - self.start) / 60,
        )
        return word