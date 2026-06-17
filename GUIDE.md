# World Cup 2026 — Corners Model Guide

---

## STEP 1 — START EVERY SESSION

Paste into Claude Chat at the start of every new conversation:

    Load our World Cup 2026 Corners Betting Model:

    https://github.com/phildinh/world-cup-corners-model/blob/main/MODEL.md
    https://github.com/phildinh/world-cup-corners-model/blob/main/data/matches.csv
    https://github.com/phildinh/world-cup-corners-model/blob/main/data/teams.csv
    https://github.com/phildinh/world-cup-corners-model/blob/main/data/lessons.csv

---

## STEP 2 — GIVE ME ALL TODAY'S MATCHES

Paste all matches at once — Claude Chat researches everything together:

    Today's matches:
    1. [Home] vs [Away] — Group [X] — [Time]
    2. [Home] vs [Away] — Group [X] — [Time]
    3. [Home] vs [Away] — Group [X] — [Time]
    4. [Home] vs [Away] — Group [X] — [Time]

---

## STEP 3 — DROP ALL LINES AT ONCE

Send one screenshot per match of the Bet365 corners markets.
Make sure each screenshot shows:
- Asian Total Corners — line and odds
- AH Corners — line and odds
- 1H Asian Corners — line and odds

If Claude cannot read the screenshot clearly it will ask you to verify the numbers before making any decision.

---

## STEP 4 — PLACE THE BET

Place confirmed bets on Bet365.
Nothing else to do until matches finish.

---

## STEP 5 — AFTER ALL MATCHES FINISH

Paste all results at once:

    Results:
    1. [Home] vs [Away] — [score] — [total] corners ([Home] X, [Away] X) — [game state] — [won/lost/skip]
    2. [Home] vs [Away] — [score] — [total] corners ([Home] X, [Away] X) — [game state] — [won/lost/skip]
    3. [Home] vs [Away] — [score] — [total] corners ([Home] X, [Away] X) — [game state] — [won/lost/skip]

Example:

    Results:
    1. France vs Morocco — 2-0 — 11 corners (France 8, Morocco 3) — normal — won
    2. Belgium vs Tunisia — 1-1 — 9 corners (Belgium 6, Tunisia 3) — normal — skip
    3. Argentina vs Nigeria — 3-0 — 7 corners (Argentina 5, Nigeria 2) — blowout — skip

Claude Chat generates all update commands at once.

---

## STEP 6 — RUN IN CLAUDE CODE

Copy paste each command Claude Chat generates:

    python main.py update [all args auto-filled]

Then one git push for the whole day:

    git add data/
    git commit -m "data: matchday [X] results"
    git push

---

## QUICK RULES

- Max 1 bet per match
- Max 2 bets per day unless 3+ strong independent edges exist
- Default market is always Asian Total Corners Over/Under
- Never AH Corners when opponent has counter-threat
- Pre-match only — no live betting
- No multis — single bets only
- Skip if no clean edge — never force a bet

---

## GAME STATE REFERENCE

| State | When |
|---|---|
| normal | No major early goal or blowout |
| underdog_scored_early | Underdog scored before 30th minute |
| blowout | Favourite won 3+ goals scored centrally |

---

## YOUR TIME PER DAY

| Task | Time |
|---|---|
| Start session and paste matches | 1 minute |
| Screenshot all lines | 1 minute |
| Place bets | 1 minute |
| Post match results | 1 minute |
| Run commands and git push | 1 minute |
| Total | ~5 minutes |

---

## REPO STRUCTURE

    world-cup-corners-model/
    ├── GUIDE.md               — you are here
    ├── CLAUDE.md              — Claude Code instructions
    ├── MODEL.md               — full corners framework v3.0
    ├── main.py                — single entry point
    ├── data/
    │   ├── matches.csv        — every match result
    │   ├── teams.csv          — team profiles and averages
    │   ├── bets.csv           — betting ledger and P&L
    │   ├── predictions.csv    — pre-match predictions
    │   └── lessons.csv        — lessons learned log
    ├── scripts/
    │   ├── update_match.py
    │   ├── baseline_calculator.py
    │   └── model_stats.py
    └── .claude/
        ├── SKILL.md
        └── commands/
            ├── update.md
            ├── baseline.md
            ├── stats.md
            └── report.md