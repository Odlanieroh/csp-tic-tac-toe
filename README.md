# CSP Tic-Tac-Toe AI

A Python desktop game exploring constraint-based board modeling and adversarial search. Play as **X** against an AI playing **O** through a dark-themed Tkinter interface.

## Features

- Detects immediate winning moves and blocks immediate threats.
- Uses minimax with alpha-beta pruning for remaining decisions.
- Displays the reason for the AI move.
- Tracks wins and ties during the session.
- Highlights winning lines and supports new games and score resets.

## Run

Requires Python 3 with Tkinter and a desktop display. No third-party Python packages are required.

```bash
python tic_tac_toe.py
```

Check Tkinter availability with `python -m tkinter`. On Ubuntu/Debian, install the system package `python3-tk` if needed.

## How it works

The board contains nine cells with values X, O, or empty. Legal moves target empty cells; eight lines define winning positions. The AI first checks immediate wins and blocks, then searches the game tree with minimax and alpha-beta pruning.

The project uses CSP concepts to describe board constraints. Its decision engine is a tactical rule layer plus adversarial search, rather than a general-purpose CSP solver or an implementation of AC-3.

## Validation

An exhaustive traversal of all human move sequences against the deterministic AI from an empty board produced **386 AI wins, 183 ties, and zero human wins**. These are terminal path counts, not probabilities or unique board counts. The traversal also checked that AI decisions are legal and leave the input board unchanged.

## Project structure

- `tic_tac_toe.py`: game model, AI search, and Tkinter interface.

## Author

Odlanier Hernandez Solano
