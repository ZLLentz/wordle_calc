from .game import SingleGame
from .solve import BruteForce, prune_words
from .words import get_words

NUMBER_WORDS = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth']

def user_analysis(game_instance: SingleGame):
    print()
    print(f'Analyzing this game for answer {game_instance.answer}:')
    print()
    print(game_instance)
    print()
    all_words = get_words()
    words = all_words
    for num, clue in enumerate(game_instance.clues):
        prev_words = words
        words = prune_words(words, [clue])
        prev_count = len(prev_words)
        new_count = len(words)
        if clue.correct:
            print(
                f'The {NUMBER_WORDS[num]} guess "{clue.word}" was correct! '
            )
            if prev_count == 1:
                print('There was 1 left to choose from.')
            else:
                print(f'There were {prev_count} left to choose from.')
            if prev_count == 1:
                print('That was the only remaining word!')
            elif prev_count < 10:
                word_str = '", "'.join(prev_words)
                print(f'The remaining words were "{word_str}"')
            else:
                print('That was a lucky guess!')
        else:
            print(f'The {NUMBER_WORDS[num]} guess was "{clue.word}".')
            if prev_count == 1:
                print(
                    'Before this guess, the only possible answer '
                    f'was {prev_words[0]}'
                )
            elif prev_count < 10:
                word_str = '", "'.join(prev_words)
                print(
                    'Before this guess, the remaining words were '
                    f'"{word_str}"'
                )
            if prev_count > 1:
                if prev_count == new_count:
                    print('This had no change on the possibility space.')
                else:
                    print(
                        'This decreased the number of possible answers '
                        f'from {prev_count} to {new_count}.'
                    )
                    pct = (1 - (new_count / prev_count)) * 100
                    print(f'This removed {pct:.2f}% of the options.')
            if num == 0:
                optimal = BruteForce.precalculated
            elif prev_count <= 2:
                optimal = prev_words[0]
            else:
                optimal = BruteForce.brute_force(prev_words, all_words)
            if clue.word == optimal:
                print('This is the same word as the algorithm!')
            else:
                print(f'The brute force algorithm picked "{optimal}".')
                if optimal == game_instance.answer:
                    print('This is the answer.')
                else:
                    optimal_continuation = SingleGame(
                        answer=game_instance.answer,
                        clues=game_instance.clues[:num],
                        words=all_words,
                    )
                    clue = optimal_continuation.make_guess(optimal)
                    optimal_new_words = prune_words(prev_words, [clue])
                    print(
                        f'Picking "{optimal}" would have dropped the count '
                        f'to {len(optimal_new_words)} instead of {new_count}.'
                    )
                    if len(optimal_new_words) == 1:
                        print(
                            f'After guessing "{optimal}", the only possible '
                            f'answer is "{optimal_new_words[0]}"'
                        )
                    elif len(optimal_new_words) < 10:
                        word_str = '", "'.join(optimal_new_words)
                        print(
                            f'After guessing {optimal}, the only possible '
                            f'answers are "{word_str}"'
                        )
            print()