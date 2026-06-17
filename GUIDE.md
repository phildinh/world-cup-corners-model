# World Cup 2026 — Corners Model Guide

---

## STEP 1 — START EVERY SESSION

Run this locally before starting a new Claude Chat:

    python main.py briefing

Copy the entire output and paste it into Claude Chat.
Then also paste the full contents of this GUIDE.md file.
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
    3. Argentina vs Nigeria — 3-0 — 7 corners (Argentina 5, Nigeria 2) — blowout — skip

Claude generates all update commands at once using the template below.

---

## UPDATE COMMAND TEMPLATE

When Claude receives match results it generates this command for each match.

For matches where a bet was placed:

    python main.py update \
      --home [Home] \
      --away [Away] \
      --home-score [X] \
      --away-score [X] \
      --total-corners [X] \
      --home-corners [X] \
      --away-corners [X] \
      --group [X] \
      --game-state [normal/underdog_scored_early/blowout] \
      --notes "[one line summary]" \
      --market [total_over/total_under/ah_corners/1h_over] \
      --selection "[e.g. Over 9.5]" \
      --odds [X.XXX] \
      --stake 1.00 \
      --bet-outcome [won/lost/void] \
      --tier [tier_1/tier_2/tier_3] \
      --confidence [high/medium/low] \
      --line [X.X] \
      --home-avg [X.XX] \
      --away-avg [X.XX] \
      --lesson "[lesson learned from this match]" \
      --lesson-category [baseline_accuracy/market_selection/style_classification/game_state/skip_accuracy] \
      --rule "[new rule added to model if any]"

For skipped matches:

    python main.py update \
      --home [Home] \
      --away [Away] \
      --home-score [X] \
      --away-score [X] \
      --total-corners [X] \
      --home-corners [X] \
      --away-corners [X] \
      --group [X] \
      --game-state [normal/underdog_scored_early/blowout] \
      --notes "[one line summary]"

---

## CSV SCHEMA REFERENCE

Claude uses these schemas to generate correct update commands:

matches.csv
    match_id, date, group, home_team, away_team, home_score, away_score,
    total_corners, home_corners, away_corners, game_state, notes

teams.csv
    team_id, team_name, confederation, group, attack_type, defensive_type,
    avg_corners_taken, avg_corners_conceded, matches_played, last_updated, notes

bets.csv
    bet_id, match_id, date, home_team, away_team, market, selection,
    odds, stake, outcome, profit_loss, notes

predictions.csv
    prediction_id, match_id, date, home_team, away_team, home_avg_corners,
    away_avg_corners, combined_baseline, tier, recommended_market,
    recommended_direction, confidence, line_offered, bet_placed, outcome, notes

lessons.csv
    lesson_id, match_id, date, category, lesson, rule_added, model_version

---

## STEP 6 — RUN IN CLAUDE CODE

Copy paste each command Claude generates:

    python main.py update [all args auto-filled by Claude]

Then one git push for the whole day:

    git add data/
    git commit -m "data: matchday [X] results"
    git push

---

## STEP 7 — VERIFY MODEL IS UPDATED

Run briefing again to confirm all data is correct:

    python main.py briefing

If anything looks wrong tell Claude and fix before next session.

---

## QUICK RULES

- Max 1 bet per match
- Default market is always Asian Total Corners Over/Under
- Pre-match only — no live betting
- Skip if no clean edge — never force a bet

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

## ATTACK TYPE REFERENCE

| Type | Corner Output | Examples |
|---|---|---|
| wide_possession | High 7+ per game | Spain, France, Belgium |
| central_possession | Medium 4-6 per game | Argentina, Norway |
| direct_physical | Low 3-5 per game | Uruguay, Iran, Saudi Arabia |
| counter_attacking | Low winning, high chasing | Egypt, Senegal, Algeria |
| set_piece_specialist | Adds 1-2 regardless of style | Norway, Iraq, New Zealand |

---

## DEFENSIVE TYPE REFERENCE

| Type | Effect on Corners |
|---|---|
| pure_deep_block | Maximum corners for dominant team |
| compact_mid_block | Moderate corners |
| open_attack_minded | End-to-end both teams contribute |
| high_press | Fewer corners transitions-based |

---

## YOUR TIME PER DAY

| Task | Time |
|---|---|
| Run briefing and paste output | 1 minute |
| Paste GUIDE.md | 30 seconds |
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