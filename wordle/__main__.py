from argparse import ArgumentParser
from cProfile import Profile
from io import StringIO
from pstats import Stats, SortKey
import logging
import time

from .game import SingleGame
from . import solve

if __name__ == "__main__":
    parser = ArgumentParser('world_calc')
    parser.add_argument('--word', action='store', default=None)
    parser.add_argument('--strategy', action='store', default=None)
    parser.add_argument('--method', action='store', default=None)
    parser.add_argument('--all-words', action='store_true')
    parser.add_argument('--time', action='store_true')
    parser.add_argument('--profile', action='store_true')
    parser.add_argument('--verbose', '-v', action='count', default=0)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO - (args.verbose * 10))
    logging.addLevelName(5, 'spam')
    if args.profile:
        profiler = Profile()
        profiler.enable()
    if args.time:
        start_time = time.monotonic()
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
    if args.time:
        print(f'{time.monotonic() - start_time}s elapsed.')
    if args.profile:
        profiler.disable()
        stream = StringIO()
        stats = Stats(profiler, stream=stream).sort_stats(SortKey.CUMULATIVE)
        stats.print_stats()
        print(stream.getvalue())