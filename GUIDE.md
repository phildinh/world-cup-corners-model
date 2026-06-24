# World Cup 2026 — Corners Model Guide

NOTE: As of June 2026, the primary workflow uses a Claude Project with
data/ and MODEL.md uploaded to Knowledge, re-uploaded after each Claude Code
session — no need to paste briefing.py output into a fresh chat each time.
The original briefing-paste flow below still works as a fallback/verification
step (e.g. to sanity-check the Project's knowledge matches the repo).

---

## STEP 1 — START EVERY SESSION

Run this in PowerShell before starting a new Claude Chat:

    python main.py briefing

Copy the entire output and paste it into Claude Chat along with the
session starter prompt saved in your notes.
Claude will confirm everything is loaded then ask for today's matches.

---

## STEP 2 — GIVE ME ALL TODAY'S MATCHES

Paste all matches at once — Claude researches everything together:

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

If Claude cannot read the screenshot clearly it will ask you
to verify the numbers before making any decision.

---

## STEP 4 — PLACE THE BETS

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
    3. Argentina vs Algeria — 3-0 — 4 corners (Argentina 2, Algeria 2) — blowout — skip

Claude generates all update commands at once.

---

## STEP 6 — RUN IN POWERSHELL

Claude generates commands in PowerShell format using backtick continuation.
Copy paste each command exactly as Claude generates it.

MATCH WITH BET — PowerShell format:

    python main.py update `
      --home [Home] `
      --away [Away] `
      --home-score [X] `
      --away-score [X] `
      --total-corners [X] `
      --home-corners [X] `
      --away-corners [X] `
      --group [X] `
      --game-state [normal/underdog_scored_early/blowout] `
      --notes "[one line summary]" `
      --market [total_over/total_under/ah_corners/1h_over/1h_under] `
      --selection "[e.g. Over 9.5]" `
      --odds [X.XXX] `
      --stake 1.00 `
      --bet-outcome [won/lost/void] `
      --tier [tier_1/tier_2/tier_3] `
      --confidence [high/medium/low] `
      --line [X.X] `
      --home-avg [X.XX] `
      --away-avg [X.XX] `
      --lesson "[lesson learned]" `
      --lesson-category [baseline_accuracy/market_selection/style_classification/game_state/skip_accuracy] `
      --rule "[new rule added to model]"

SKIPPED MATCH — PowerShell format:

    python main.py update `
      --home [Home] `
      --away [Away] `
      --home-score [X] `
      --away-score [X] `
      --total-corners [X] `
      --home-corners [X] `
      --away-corners [X] `
      --group [X] `
      --game-state [normal/underdog_scored_early/blowout] `
      --notes "[one line summary]" `
      --skip-lean [over/under/none]

BET-ONLY (second bet on same match, e.g. 1H market) — PowerShell format:

    python main.py update `
      --bet-only `
      --match-id [XXX] `
      --home [Home] `
      --away [Away] `
      --home-score [X] `
      --away-score [X] `
      --total-corners [X] `
      --home-corners [X] `
      --away-corners [X] `
      --group [X] `
      --notes "[one line summary]" `
      --market [total_over/total_under/ah_corners/1h_over/1h_under] `
      --selection "[e.g. 1H Over 4.5]" `
      --odds [X.XXX] `
      --stake 1.00 `
      --bet-outcome [won/lost/void] `
      --tier [tier_1/tier_2/tier_3] `
      --confidence [high/medium/low] `
      --line [X.X] `
      --home-avg [X.XX] `
      --away-avg [X.XX]

OR use single line format — no continuation needed:

    python main.py update --home [Home] --away [Away] --home-score [X] --away-score [X] --total-corners [X] --home-corners [X] --away-corners [X] --group [X] --game-state [normal] --notes "[summary]" --skip-lean [over/under/none]

Then push to GitHub:

    git add data/
    git commit -m "data: matchday [X] results"
    git push

---

## STEP 7 — VERIFY MODEL IS UPDATED

Run briefing again to confirm all data is correct:

    python main.py briefing

If anything looks wrong tell Claude and fix before next session.

---

## UPDATE COMMAND TEMPLATE FOR CLAUDE

When Claude receives results it always generates PowerShell format
using backtick ` for line continuation — never backslash \.

---

## QUICK RULES

- Max 1 bet per market per match (same-match multi-market bets must reflect genuinely independent edges)
- Max 2 bets per day unless 3+ strong independent edges exist
- Default market is always Asian Total Corners Over/Under
- Never AH Corners when opponent has counter-threat
- Pre-match only — no live betting
- No multis — single bets only
- Skip if no clean edge — never force a bet
- Tier 1 (high confidence) → stake 2 units
- Tier 2 (medium confidence) → stake 1 unit
- Max 4 units total per day
- Shadow portfolio tracked automatically — no action needed

---

## GAME STATE REFERENCE

| State | When |
|---|---|
| normal | No major early goal or blowout |
| underdog_scored_early | Underdog scored before 30th minute |
| blowout | Favourite won 3+ goals scored centrally |

---

## MARKET REFERENCE

| Market Key | Description |
|---|---|
| total_over | Asian Total Corners Over |
| total_under | Asian Total Corners Under |
| ah_corners | Asian Handicap Corners |
| 1h_over | 1st Half Asian Corners Over |
| 1h_under | 1st Half Asian Corners Under |

---

## VALID VALUES

    market:          total_over / total_under / ah_corners / 1h_over / 1h_under
    game_state:      normal / underdog_scored_early / blowout
    tier:            tier_1 / tier_2 / tier_3
    confidence:      high / medium / low / skip
    data_confidence: high / medium / low
    counter_threat:  yes / no / auto
    match_type:      wide_vs_deep / wide_vs_counter / central_vs_deep /
                     direct_vs_direct / wide_vs_open / mixed
    category:        baseline_accuracy / market_selection / style_classification
                     game_state / skip_accuracy

---

## YOUR TIME PER DAY

| Task | Time |
|---|---|
| Run briefing and paste output | 1 minute |
| Paste today's matches | 10 seconds |
| Screenshot all lines | 1 minute |
| Place bets | 1 minute |
| Paste all results | 30 seconds |
| Run update commands and git push | 1 minute |
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
    │   ├── model_stats.py
    │   └── briefing.py
    └── .claude/
        ├── SKILL.md
        └── commands/
            ├── update.md
            ├── baseline.md
            ├── stats.md
            └── report.md