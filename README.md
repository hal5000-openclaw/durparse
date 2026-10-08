# durparse

A small, stdlib-only Python 3 CLI that parses human duration strings and prints
total seconds (or another unit, or a normalized human form).

## Why

Scripts keep needing "1h30m" or "01:30:45" turned into a number. durparse does
that one thing, with no dependencies.

## Install

    pip install .          # provides the `durparse` command
    # or run without installing:
    python -m durparse 1h30m

## Usage

    $ durparse 1h30m 2d4h 90s 1.5h 1w2d 01:30:45
    5400
    187200
    90
    5400
    777600
    5445

    $ durparse --to m 90s
    1.5
    $ durparse --human 5445
    1h 30m 45s
    $ printf '1m\n2m\n' | durparse        # stdin lines when no args
    60
    120

- Units: ms, s, m, h, d, w (plus long forms like `minutes`, `hrs`). Decimals allowed.
- Clock forms: `HH:MM:SS` and `MM:SS` (seconds may be fractional).
- A bare number is seconds. Parts may be separated by spaces or commas.
- `--to {ms,s,m,h,d}` converts the output; `--human` prints e.g. `1h 30m`
  (largest unit is days).
- Invalid input prints a message to stderr and the exit code is 1 (valid
  items are still printed).

## Tests

    python -m unittest discover -s tests

## License

MIT
