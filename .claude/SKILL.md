# Claude Code Skills — World Cup 2026 Corners Model

## Context
This repo is a data-driven corners betting model for FIFA World Cup 2026.
Built collaboratively between Phil (owner), Claude Chat (analyst), 
and Claude Code (data engineer).

## Core Skills Required

### 1. Data Engineering
- Always read existing CSV before appending — never overwrite
- Validate row count before and after every write operation
- Match schema exactly — column order matters
- match_id, bet_id, prediction_id, lesson_id are zero-padded 3 digits
- Rolling averages must be recalculated using existing matches_played value
- Never hardcode IDs — always derive from max existing ID + 1

### 2. Python
- Use pandas for all CSV operations
- Use argparse for all CLI interfaces
- Always use relative paths via os.path — never hardcode absolute paths
- Wrap file operations in try/except with clear error messages
- Print confirmation after every successful write

### 3. Schema Enforcement
Always validate against these schemas before writing:

**matches.csv**
match_id, date, group, home_team, away_team, home_score, away_score,
total_corners, home_corners, away_corners, game_state, notes

**teams.csv**
team_id, team_name, confederation, group, attack_type, defensive_type,
avg_corners_taken, avg_corners_conceded, matches_played, last_updated, notes

**bets.csv**
bet_id, match_id, date, home_team, away_team, market, selection,
odds, stake, outcome, profit_loss, notes

**predictions.csv**
prediction_id, match_id, date, home_team, away_team, home_avg_corners,
away_avg_corners, combined_baseline, tier, recommended_market,
recommended_direction, confidence, line_offered, bet_placed, outcome, notes

**lessons.csv**
lesson_id, match_id, date, category, lesson, rule_added, model_version

### 4. Model Domain Knowledge
Apply these rules when generating analysis or data:

**Attack Types:**
- wide_possession → high corners 7+ per game
- central_possession → medium corners 4-6 per game
- direct_physical → low corners 3-5 per game
- counter_attacking → low when winning, high when chasing
- set_piece_specialist → adds 1-2 corners regardless of style

**Defensive Types:**
- pure_deep_block → maximum corners for dominant team
- compact_mid_block → moderate corners
- open_attack_minded → end-to-end both teams contribute
- high_press → fewer corners transitions-based

**Tier System:**
- tier_1 → baseline 1.5+ above line → bet high confidence
- tier_2 → baseline 1.0-1.5 above line → consider medium confidence
- tier_3 → baseline within 0.5 of line → skip

**Market Rules:**
- Default market: Asian Total Corners Over/Under
- AH Corners only when opponent is pure_deep_block with zero counter-threat
- Never AH corners when opponent has counter_attacking style

### 5. Git Workflow
After every data update:
- Stage only data/ directory changes
- Commit message format:
  data: [HomeTeam] vs [AwayTeam] — [X] corners — [won/lost/skip]
- Push to main

### 6. Error Handling
- If team not found in teams.csv → print available teams, exit cleanly
- If CSV missing → print clear error with expected path
- If schema mismatch → print expected vs actual columns, exit cleanly
- Never silently fail — always print what went wrong

## What Claude Code Should Never Do
- Never edit CSV files manually outside of scripts
- Never modify MODEL.md without Phil's explicit approval
- Never hardcode file paths
- Never skip schema validation
- Never overwrite existing data — always append
- Never commit without a descriptive message