# /update — Log Match Result

Log a completed match result and update all CSVs.

## What This Does
1. Appends row to data/matches.csv
2. Recalculates team rolling averages in data/teams.csv
3. Updates data/bets.csv if bet was placed
4. Appends prediction to data/predictions.csv
5. Appends lesson to data/lessons.csv
6. Runs git commit with standard message format

## Usage
Run: python main.py update with required args

## Required Info To Collect From Phil
- Home team and away team
- Final score
- Total corners + home corners + away corners
- Game state (normal / underdog_scored_early / blowout)
- Was a bet placed? If yes: market, selection, odds, outcome
- Any lesson learned?

## Validation
- Confirm team names exist in teams.csv before writing
- Confirm match_id does not already exist
- Print summary after update completes