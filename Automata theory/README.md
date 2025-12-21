# Pushdown Automaton (PDA) Project

This project implements a simple Pushdown Automaton (PDA) that validates strings in the format:

$$a^n / b^n / c^n$$

Examples:
- Valid: `a/b/c`, `aa/bb/cc`
- Invalid: `aa/b/cc` (extra `a`), `a/bb/cc` (extra `b`), `aa/bb/ccc` (extra `c`)

## What It Does

The automaton processes the input left-to-right and uses two stacks:
- Stack 1 tracks the count of `a` symbols.
- Stack 2 tracks the count of `b` symbols to match against `c` symbols.

The input must contain exactly two separators `/`, and the characters must appear in the order `a.../b.../c...`.



### Interactive mode

```bash
python PDA.py
```

You will be prompted for input like `aa/bb/cc`.

### Run tests

```bash
python test_pda.py
```

