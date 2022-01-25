from .game import SingleGame

if __name__ == "__main__":
    game_instance = SingleGame.begin()
    print()
    while game_instance.running:
        print(game_instance)
        print()
        guess = input()
        print()
        game_instance.make_guess(guess)
    print(game_instance)
    print(f'\nAnswer was {game_instance.answer}')