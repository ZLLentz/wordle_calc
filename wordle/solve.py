from collections import defaultdict
from tokenize import Single

from .game import SingleGame, WordEval
from .words import get_words


class Strategy:
    def guess(self) -> str:
        raise NotImplementedError

    def simulate_all_games(self) -> dict[int: list[str]]:
        all_words = get_words()
        print(f"Simulating all {len(all_words)} games.")
        results = defaultdict(list)
        incr = 0
        count = 0
        for word in all_words:
            results[self.simulate_game(word, do_print=False)].append(word)
            count += 1
            incr -= 1
            if incr <= 0:
                incr = len(all_words) / 10
                print(f'Simulated {count} games...')
        print("Our score is:")
        print(sorted({val: len(words) for val, words in results.items()}))
        print("We got these words in 1 guess:")
        print(results[1])
        print("We got these words in 2 guesses:")
        print(results[2])
        print("We failed to solve these words:")
        print(results[7])

    def simulate_game(self, answer, do_print=True) -> int:
        self.initialize_game(answer)
        while self.game_instance.running:
            self.simulate_turn()
        if do_print:
            print(self.game_instance)
        if self.game_instance.victory:
            return len(self.game_instance.clues)
        else:
            return 7

    def initialize_game(self, answer):
        self.words = get_words()
        self.game_instance = SingleGame.begin(answer)

    def simulate_turn(self):
        self.game_instance.make_guess(self.guess())
        self.words = prune_words(self.words, self.game_instance.clues)


def prune_words(words: list[str], clues: list[WordEval]) -> list[str]:
    new_words = []
    for word in words:
        if all(clue.allows(word) for clue in clues):
            new_words.append(word)
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
        if len(self.words) == 1:
            return self.words[0]
        if len(self.game_instance.clues) == 0:
            return 'siren'
        if len(self.game_instance.clues) == 1:
            return 'octal'
        if len(self.game_instance.clues) == 2:
            return 'dumpy'
        return self.words[0]