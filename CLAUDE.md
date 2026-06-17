# World Cup 2026 — Corners Betting Model

## What This Repo Is
A data-driven corners betting model for FIFA World Cup 2026.
Built collaboratively between Phil (owner), Claude Chat (research/analysis),
and Claude Code (data engineering/automation).

## Stack
- Python 3.x + pandas + argparse
- CSV flat files (no database — 64 match scale)
- GitHub as shared memory between Claude Chat and Claude Code

## Project Structure

    data/
      matches.csv              # Every match result and corners
      teams.csv                # Team profiles and rolling corner averages
      bets.csv                 # Betting ledger and P&L
      predictions.csv          # Pre-match predictions and tier classifications
      lessons.csv              # Model lessons learned log
    scripts/
      update_match.py          # Append match result and recalculate averages
      baseline_calculator.py   # Calculate combined corners baseline
      model_stats.py           # Win rate, ROI, skip accuracy tracker
    main.py                    # Single entry point for all commands
    MODEL.md                   # Full corners model framework v3.0
    CLAUDE.md                  # This file

## Commands

    python main.py update       # Log match result → updates all CSVs
    python main.py stats        # Show model stats and P&L
    python main.py baseline     # Calculate baseline for a matchup
    python main.py report       # Generate full model report
    python main.py analyse      # Run full model analysis
    python main.py log-version  # Log model version change

## Trigger Phrases

### "data update: [match], [score], [corners], [outcome]"
1. Parse all fields from the message
2. Append row to data/matches.csv
3. Recalculate team rolling averages in data/teams.csv
4. Update data/bets.csv with P&L if bet was placed
5. Append lesson to data/lessons.csv
6. Run model_stats.py and output current record

### "model stats"
1. Read data/bets.csv and data/predictions.csv
2. Calculate win rate, ROI, skip accuracy, best market
3. Output clean summary table

### "baseline [Team A] vs [Team B]"
1. Look up both teams in data/teams.csv
2. Calculate combined baseline
3. Compare to MODEL.md tier thresholds
4. Output tier classification and recommended market

### "build report"
1. Read all CSVs
2. Output full model performance summary
3. Include lessons learned and model evolution log

### "python main.py analyse"
Runs scripts/analyse_model.py
Outputs full pattern analysis across all 7 sections
Run this every 5 matches to detect model improvement opportunities

### "python main.py log-version --version [X] --change [X] --trigger [X]"
Runs scripts/log_version.py
Appends new version row to data/model_versions.csv
Run this whenever MODEL.md rules are updated

## Staking Rules
- Tier 1 high confidence  → stake 2.00 units
- Tier 2 medium confidence → stake 1.00 units
- Never stake more than 4 units total per day
- Shadow bets are tracked in predictions.csv only — never in bets.csv

When generating update commands for Claude Chat:
- If tier=tier_1 → always set --stake 2.00
- If tier=tier_2 → always set --stake 1.00
- If no bet placed → no stake argument needed

## Schema Rules
- Every row appended must match exact column order in each CSV
- Run scripts/update_match.py — never edit CSVs manually
- Always validate row count before and after appending
- match_id is zero-padded 3 digits: 001, 002, 003...
- All stakes stored as unit stakes (1.00 = 1 unit)

## Division of Labour
- Phil provides: Bet365 lines, final corners count, final score
- Claude Chat provides: match research, analysis, tier classification
- Claude Code provides: data logging, calculations, stats tracking

## Git Workflow
After every data update run:

    git add data/
    git commit -m "data: [HomeTeam] vs [AwayTeam] — [corners] corners — [outcome]"
    git push

## Key Constraints
- Never edit CSV files manually — always use scripts
- Never skip schema validation
- Never modify MODEL.md without Phil's approval
- match_id zero-padded 3 digits: 001, 002...