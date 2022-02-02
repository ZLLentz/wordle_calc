from argparse import ArgumentParser
from cProfile import Profile
from io import StringIO
from pstats import Stats, SortKey
import logging
import time

from . import solve
from .analyze import user_analysis
from .antagonize import get_winning_absurdle_games
from .game import SingleGame
from .words import WordList

if __name__ == "__main__":
    parser = ArgumentParser('world_calc')
    parser.add_argument('--word', action='store', default=None)
    parser.add_argument('--strategy', action='store', default=None)
    parser.add_argument('--method', action='store', default=None)
    parser.add_argument('--all-words', action='store_true')
    parser.add_argument('--time', action='store_true')
    parser.add_argument('--profile', action='store_true')
    parser.add_argument('--analyze', action='extend', nargs='*')
    parser.add_argument('--use-cheat-list', action='store_true')
    parser.add_argument('--solve-antagonize', action='store_true')
    parser.add_argument('--verbose', '-v', action='count', default=0)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO - (args.verbose * 10))
    logging.addLevelName(5, 'spam')
    if args.profile:
        profiler = Profile()
        profiler.enable()
    if args.time:
        start_time = time.monotonic()
    if args.use_cheat_list:
        answers = WordList.CHEAT
    else:
        answers = WordList.ALL
    if args.strategy is not None:
        SolverClass = getattr(solve, args.strategy)
        if args.method is None:
            solver_inst = SolverClass(
                valid_answers=answers,
                strategy_answers=answers,
            )
            if args.all_words:
                solver_inst.simulate_all_games()
            else:
                solver_inst.simulate_game(args.word)
                print(solver_inst.game_instance)
        else:
            callable = getattr(SolverClass, args.method)
            callable()
    elif args.analyze:
        game_instance = SingleGame.begin(
            args.word,
            valid_answers=answers,
        )
        for word in args.analyze:
            game_instance.make_guess(word)
        user_analysis(game_instance, answers)
    elif args.solve_antagonize:
        winning_games = get_winning_absurdle_games()
        print('Won the following absurdle games:')
        for winning in winning_games:
            print()
            for hint in winning:
                print(hint)
            print()

    else:
        game_instance = SingleGame.begin(
            args.word,
            valid_answers=WordList.CHEAT,
        )
        print()
        while game_instance.running:
            print(game_instance)
            print()
            guess = input()
            print()
            game_instance.make_guess(guess)
        print(game_instance)
        print(f'\nAnswer was {game_instance.answer}')
        if args.analyze is not None:
            user_analysis(game_instance)
    if args.time:
        print(f'{time.monotonic() - start_time}s elapsed.')
    if args.profile:
        profiler.disable()
        stream = StringIO()
        stats = Stats(profiler, stream=stream).sort_stats(SortKey.CUMULATIVE)
        stats.print_stats()
        print(stream.getvalue())