import logging
import multiprocessing
import time
from functools import partial
from typing import Optional

from .game import SingleGame, WordEval
from .words import WordList

logger = logging.getLogger(__name__)
logger.spam = partial(logger.log, 5)


class Strategy:
    hardcoded = ()

    def __init__(
        self,
        valid_guesses: WordList = WordList.ALL,
        valid_answers: WordList = WordList.ALL,
        strategy_answers: WordList = WordList.ALL,
    ):
        self.valid_guesses = valid_guesses
        self.valid_answers = valid_answers
        self.strategy_answers = strategy_answers

    def guess(self) -> str:
        raise NotImplementedError

    def default_guess(self) -> Optional[str]:
        if len(self.remaining_words) == 0:
            return 'fails'
        if len(self.remaining_words) <= 2:
            return self.remaining_words[0]
        try:
            return self.hardcoded[len(self.game_instance.clues)]
        except IndexError:
            return

    def simulate_all_games(self) -> dict[int: list[str]]:
        start = time.monotonic()
        all_words = self.strategy_answers.get()
        game_count = len(all_words)
        logger.info(
            "Simulating all %s games.",
            game_count,
        )
        results = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
        full_incr = game_count / 100
        incr = full_incr
        count = 0
        for word in all_words:
            results[self.simulate_game(word)].append(word)
            count += 1
            incr -= 1
            if incr <= 0:
                incr = full_incr
                level = logging.INFO
            else:
                level = logging.DEBUG
            logger.log(
                level,
                'Simulated %d/%d games, %.1f min elapsed',
                count,
                game_count,
                (time.monotonic() - start) / 60,
            )
        logger.info("Our score is:")
        scores = {val: len(words) for val, words in results.items()}
        logger.info(scores)
        win_count = game_count - scores[7]
        logger.info(
            "We won %d out of %d games for a win rate of %.2f%%",
            win_count,
            game_count,
            win_count / game_count * 100,
        )
        logger.info(
            "In our wins, we had an average score of %.2f guesses per game.",
            (
                sum(key * value for key, value in scores.items() if key != 7)
                / win_count
            )
        )
        logger.info("We got these words in 1 guess:")
        logger.info(results[1])
        logger.info("We got these words in 2 guesses:")
        logger.info(results[2])
        logger.info("We got these words in 6 guesses, nearly failed!")
        logger.info(results[6])
        logger.info("We failed to solve these words:")
        logger.info(results[7])

    def simulate_game(self, answer: str) -> int:
        self.initialize_game(answer)
        while self.game_instance.running:
            self.simulate_turn()
        if self.game_instance.victory:
            return len(self.game_instance.clues)
        else:
            return 7

    def initialize_game(self, answer: str):
        self.remaining_words = self.strategy_answers.get()
        self.game_instance = SingleGame.begin(
            answer=answer,
            valid_guesses=self.valid_guesses,
            valid_answers=self.valid_answers,
        )

    def simulate_turn(self):
        guess = self.default_guess()
        if guess is None:
            guess = self.guess()
        self.game_instance.make_guess(guess)
        logger.debug('\n%s', self.game_instance)
        self.remaining_words = prune_words(self.remaining_words, self.game_instance.clues)


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
            return self.remaining_words[0]
        except IndexError:
            return 'fails'


class BruteForce(Strategy):
    """
    Pick the word with the highest avg possible words removed
    for all the possible answers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.hardcoded:
            if self.strategy_answers == WordList.ALL:
                self.hardcoded = ('later',)
            elif self.strategy_answers == WordList.SGB:
                self.hardcoded = ('tares',)
            elif self.strategy_answers == WordList.CHEAT:
                self.hardcoded = ('roate',)

    def guess(self) -> str:
        if len(self.remaining_words) == 0:
            return 'fails'
        if len(self.remaining_words) <= 2:
            return self.remaining_words[0]
        if len(self.game_instance.clues) == 0:
            return self.precalculated
        if len(self.remaining_words) > 100:
            return self.brute_force(
                self.remaining_words,
                self.get_likely_guesses(),
            )
        return self.brute_force(
            self.remaining_words,
            self.strategy_answers.get(),
        )

    def get_likely_guesses(self) -> list[str]:
        guessed = ''.join(clue.word for clue in self.game_instance.clues)
        likely = [
            word for word in self.strategy_answers.get()
            if not any(char in guessed for char in word)
        ]
        logger.debug('%d likely guesses: %s', len(likely), likely)
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
    def _check_proc(word: str, remaining_ok: list[str]) -> tuple[str, int]:
        return word, BruteForce.check_one(
            word,
            remaining_ok,
        )

    @staticmethod
    def check_one(word: str, remaining_ok: list[str]) -> int:
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
    def precompute(
        guesses: WordList = WordList.ALL,
        answers: WordList = WordList.ALL,
    ) -> str:
        logger.info('Running precompute...')
        ans = BruteForce.brute_force(answers.get(), guesses.get())
        logger.info('Best word is %s', ans)
        return ans

    @staticmethod
    def precompute_cheat():
        BruteForce.precompute(answers=WordList.CHEAT)

    @staticmethod
    def check_one_for_profile(
        guesses: WordList = WordList.ALL,
    ):
        start_time = time.monotonic()
        while time.monotonic() - start_time < 10:
            BruteForce.check_one('check', guesses.get())


class NoisyList:
    def __init__(self, words):
        self.remaining_words = words
        self.reinit()

    def reinit(self):
        self._iter_words = iter(self.remaining_words)
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
            len(self.remaining_words),
            (time.monotonic() - self.start) / 60,
        )
        return word


class SudokuChannel(BruteForce):
    """
    Guess the words the Sudoku guys recommend, then brute force it
    """
    hardcoded = ('siren', 'octal', 'dumpy')
