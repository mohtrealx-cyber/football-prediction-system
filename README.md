# Football System V0.1 — Ticket Builder

This first version intentionally does NOT use live football data, bookmaker APIs, Telegram, or real-money betting.

It only tests the ticket-building rules with sample selections.

## Rules in V0.1
- 4 ticket types: SAFE, BALANCED, AGGRESSIVE, VALUE
- Stake allocation: 40%, 30%, 20%, 10%
- Minimum 3 matches per ticket
- Maximum 6 matches per ticket
- Never force a weak match just to reach 3
- No duplicate match inside a ticket
- Simple confidence/value thresholds

## Run the demo

```bash
python main.py
```

## Run tests

```bash
python -m unittest discover -s tests -v
```
