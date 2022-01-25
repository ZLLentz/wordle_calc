from pathlib import Path

WORDS_FILE = Path(__file__).parent / 'sgb-words.txt'

def get_words() -> str:
    with WORDS_FILE.open('r') as fd:
        return fd.read().splitlines()
