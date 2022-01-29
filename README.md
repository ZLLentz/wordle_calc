# Wordle Calc
This is a pet project to help me understand what kinds of strategies are most effective for solving Wordle puzzles.
You can play Wordle at https://www.powerlanguage.co.uk/wordle/.
I am not affiliated with Wordle nor do I have any rights to the game. The creator of Wordle currently does not intend to monetize it.

Feel free to use this code for whatever purpose you'd like. Hopefully you find it interesting.

## What is this exactly?
This Python code can be used to:
- Play a worse version of Wordle in your terminal, with a random answer word or with a specific word (perhaps, to replay a past day of Wordle?).
- Check how a particular "Strategy" would fare in general or against a particular answer.
- Analyze a game of Wordle you played previously, to see how the computer would evaluate your choices.

This Python code can't efficiently be used to cheat and help you complete your daily Wordle puzzle. That wouldn't be much fun anyway.

## Sample Usage
Starting a game:
```
python -m wordle

    Wordle    
---------------


guess

    Wordle
---------------
 g  u  e  s  s
```

See how a strategy would approach a specific game:
```
python -m wordle --word apple --strategy BruteForce
    Wordle    
---------------
 t :a: r :e: s
 b :l: i  n  d
 m :e::a:|l| y
|a||p||p||l||e|
```

Ask for feedback about one of your games:
```
python -m wordle --word penny --analyze haiku stole hyena funny penny

Analyzing this game for answer penny:

    Wordle
---------------
 h  a  i  k  u
 s  t  o  l :e:
 h :y::e:|n| a
 f  u |n||n||y|
|p||e||n||n||y|

The first guess was "haiku".
This decreased the number of possible answers from 5757 to 1174.
This removed 79.61% of the options.
The brute force algorithm picked "tares".
Picking "tares" would have dropped the count to 239 instead of 1174.

The second guess was "stole".
This decreased the number of possible answers from 1174 to 69.
This removed 94.12% of the options.
The brute force algorithm picked "roles".
Picking "roles" would have dropped the count to 28 instead of 69.

The third guess was "hyena".
This decreased the number of possible answers from 69 to 4.
This removed 94.20% of the options.
The brute force algorithm picked "nerdy".
Picking "nerdy" would have dropped the count to 4 instead of 4.
After guessing nerdy, the only possible answers are "penny", "jenny", "weeny", "fenny"

The fourth guess was "funny".
Before this guess, the remaining words were "penny", "ferny", "jenny", "fenny"
This decreased the number of possible answers from 4 to 2.
This removed 50.00% of the options.
The brute force algorithm picked "proof".
Picking "proof" would have dropped the count to 1 instead of 2.
After guessing "proof", the only possible answer is "penny"

The fifth guess "penny" was correct!
There were 2 left to choose from.
The remaining words were "penny", "jenny"
```

## Caveats
- This repository doesn't properly follow the rules of Wordle quite how it is done in the real game. I haven't bothered fixing edge cases with multiple letters, for example, which are hinted differently in Wordle than they are here.
- The brute force algorithm gives the best results, but is very slow to run. It tries to leverage multiprocessing to speed itself up, which typically pegs your CPU, and it tries to take some shortcuts but still ends up being slow.
- Only the brute force algorithm is currently available for the analysis
- The analysis differs slightly from the way the algorithm plays the game itself, due to poor architecture choices.

## Word lists
- dictionary.txt is the actual list that Wordle uses to validate your guesses.
- cheater.txt is the list of words that Wordle can pick from to pick today's answer. Don't look at this list if you don't want to be spoiled.
- sgb-words.txt is a list of words from a Stanford website that I found when setting up this project. It's a reasonable compromise between the two previous lists, and is the list currently used by the algorithm here, but I plan to phase it out and implement code that leverages dictionary.txt (and, optionally, cheater.txt for a less kosher speedup).

## Strategies
- InOrder is a strategy that just guesses words in order that haven't been explicitly ruled out yet. It does surprisingly well (and words really fast, for obvious reasons), but often fails to find an answer because its guesses are not strategic.
- SudokuChannel is a strategy based on some commentary from the Youtube channel "Cracking the Cryptic", where they laid out a reasonable approach of guessing "siren" and "octal" first to eliminate 10 letters in two words. A follow-up video indicated using "dumpy" next. This strategy stops going down its list once there are only 1 or 2 valid answers remaining or once it runs out of pre-selected words. At this point, it reverts back to InOrder.
- BruteForce is a strategy that tries to pick the best word by checking every possible Wordle game that continues from the current point, and seeing which word has the best overall result across all of them, measured in "number of possible words eliminated".

## Remaining to-do items
- use the real word lists, dictionary.txt and cheater.txt appropriately
- allow the engine to self-analyze
- track down discrepency in brute force algorithm's self-eval in --word mount --analyze tares chino mount
- add hard mode (no guessing things outside of the possibilities list)
- come up with a few other interesting algorithms to implement as strategies
- make some simple file format output I can use to compare the performance of the different strategies (distribution, solve time)