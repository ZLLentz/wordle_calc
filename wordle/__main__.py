from argparse import ArgumentParser

from .game import SingleGame
from . import solve

if __name__ == "__main__":
    parser = ArgumentParser('world_calc')
    parser.add_argument('--word', action='store', default=None)
    parser.add_argument('--strategy', action='store', default=None)
    parser.add_argument('--method', action='store', default=None)
    parser.add_argument('--all-words', action='store_true')
    args = parser.parse_args()
    if args.strategy is None:
        game_instance = SingleGame.begin(args.word)
        print()
        while game_instance.running:
            print(game_instance)
            print()
            guess = input()
            print()
            game_instance.make_guess(guess)
        print(game_instance)
        print(f'\nAnswer was {game_instance.answer}')
    else:
        SolverClass = getattr(solve, args.strategy)
        if args.method is None:
            solver_inst = SolverClass()
            if args.all_words:
                solver_inst.simulate_all_games()
            else:
                solver_inst.simulate_game(args.word)
        else:
            callable = getattr(SolverClass, args.method)
            callable()