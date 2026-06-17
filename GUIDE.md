# World Cup 2026 — Corners Model Guide

## STEP 1 — START EVERY SESSION
Paste this into Claude Chat at the start of every new conversation:

---
Load our World Cup 2026 Corners Betting Model before we start:

https://github.com/phildinh/world-cup-corners-model/blob/main/MODEL.md
https://github.com/phildinh/world-cup-corners-model/blob/main/data/matches.csv
https://github.com/phildinh/world-cup-corners-model/blob/main/data/teams.csv
https://github.com/phildinh/world-cup-corners-model/blob/main/data/lessons.csv

Once loaded give me:
1. Current model version and record
2. Last 3 lessons learned
3. Any team corner average updates
Then I will give you today's matches.
---

---

## STEP 2 — GIVE ME ALL TODAY'S MATCHES AT ONCE

---
Today's matches:
1. [Home] vs [Away] — Group [X] — [Time]
2. [Home] vs [Away] — Group [X] — [Time]
3. [Home] vs [Away] — Group [X] — [Time]
4. [Home] vs [Away] — Group [X] — [Time]
---

## STEP 3 — DROP ALL LINES AT ONCE

---
Lines:
1. [Home] vs [Away]: [X.X] Over @ [odds] / Under @ [odds] / 
   AH [Home] [handicap] @ [odds] / 1H [X.X] Over @ [odds]
2. [Home] vs [Away]: [X.X] Over @ [odds] / Under @ [odds] /
   AH [Home] [handicap] @ [odds] / 1H [X.X] Over @ [odds]
---

Example:
---
Lines:
- Asian Total Corners: 9.5 Over @ 1.850 / Under @ 1.950
- AH Corners: Argentina -3.0 @ 1.900 / Morocco +3.0 @ 1.850
- 1H Asian Corners: 4.5 Over @ 1.825 / Under @ 1.975
---

Claude Chat confirms bet or skip instantly.

---

## STEP 4 — PLACE THE BET
Open Bet365 and place the bet Claude Chat confirmed.
Nothing else to do until the match finishes.

---

## STEP 5 — AFTER MATCH FINISHED
Paste this into Claude Chat — fill in the blanks:

---
data update:
match: [Home] vs [Away]
score: [X-X]
corners: [total] ([Home] X, [Away] X)
game state: [normal / underdog_scored_early / blowout]
bet: [market] [selection] @ [odds] — [won / lost / skip]
notes: [one line about how the match went]
---

Example:
---
data update:
match: Argentina vs Morocco
score: 2-0
corners: 11 (Argentina 8, Morocco 3)
game state: normal
bet: total_over Over 9.5 @ 1.850 — won
notes: Argentina dominant Messi scored twice wide threats delivered
---

Claude Chat generates the full update command for you.

---

## STEP 6 — RUN IN CLAUDE CODE
Copy paste the command Claude Chat generates:

---
python main.py update \
  --home [Home] --away [Away] \
  [all args auto-filled by Claude Chat]
---

Then push to GitHub:

---
git add data/
git commit -m "data: [Home] vs [Away] — [X] corners — [won/lost/skip]"
git push
---

---

## STEP 7 — CHECK STATS ANYTIME

---
python main.py stats
python main.py report
python main.py baseline --home [Team] --away [Team] --line [X.X]
---

---

## DIVISION OF LABOUR

| Task | Who |
|---|---|
| Match research and analysis | Claude Chat |
| Tier classification and recommendation | Claude Chat |
| Drop Bet365 lines | You |
| Confirm final corners count | You |
| Confirm final score | You |
| Place the bet | You |
| Generate update command | Claude Chat |
| Run update command | You (Claude Code) |
| Git push | You |
| Everything else | Automated |

---

## YOUR TIME PER MATCH

| Task | Time |
|---|---|
| Start session (paste URLs) | 5 seconds |
| Request analysis | 5 seconds |
| Drop lines | 30 seconds |
| Place bet | 30 seconds |
| Post match data update | 30 seconds |
| Run command and git push | 30 seconds |
| **Total per match** | **~2 minutes** |

---

## GAME STATE REFERENCE

| Game State | When To Use |
|---|---|
| normal | Game played out without major early goal |
| underdog_scored_early | Underdog scored before 30th minute |
| blowout | Favourite won by 3+ goals scored centrally |

---

## QUICK RULES REMINDER

- Maximum 1 bet per match
- Only bet Tier 1 or strong Tier 2
- Default market is always Asian Total Corners Over/Under
- Never use AH Corners when opponent has counter-threat
- Skip if no clean edge — never force a bet
- No live betting — pre-match only
- No multis — single bets only

---

## REPO STRUCTURE

    world-cup-corners-model/
    ├── GUIDE.md               ← you are here
    ├── CLAUDE.md              ← Claude Code instructions
    ├── MODEL.md               ← full corners framework v3.0
    ├── main.py                ← single entry point
    ├── data/
    │   ├── matches.csv        ← every match result
    │   ├── teams.csv          ← team profiles and averages
    │   ├── bets.csv           ← betting ledger and P&L
    │   ├── predictions.csv    ← pre-match predictions
    │   └── lessons.csv        ← lessons learned log
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