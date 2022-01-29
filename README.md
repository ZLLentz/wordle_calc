# Wordle Calc
This is a pet project to help me understand what kinds of strategies are most effective for solving Wordle puzzles.
You can play Wordle at https://www.powerlanguage.co.uk/wordle/.
I am not affiliated with Wordle nor do I have any rights to the game.

Wordle's source code comes with a Copyright (c) by Microsoft, along with a very standard open source license that I've also included in this repository. That means it should be OK to make projects like this so long as you're not creating a copy or near copy of Wordle for commercial reasons. I also think it is OK for you to use/edit my code here for your own purposes, again being sure not to violate Microsoft's copyright.

## What is this exactly?
This Python code can be used to:
- Play a worse version of Wordle in your terminal, with a random answer word or with a specific word (perhaps, to replay a past day of Wordle?).
- Check how a particular "Strategy" would fare in general or against a particular answer.
- Analyze a game of Wordle you played previously, to see how a particular Strategy would evaluate your choices.

This Python code can't efficiently be used to cheat and help you complete your daily Wordle puzzle. That wouldn't be much fun anyway.

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