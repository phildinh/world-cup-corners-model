# /stats — Model Performance Stats

Display full model performance statistics and P&L.

## What This Does
1. Reads data/bets.csv for betting record
2. Reads data/predictions.csv for skip accuracy
3. Reads data/matches.csv for corner distributions
4. Reads data/lessons.csv for lesson summary
5. Outputs formatted stats table

## Usage
Run: python main.py stats

## Output
- Betting record (W/L/win rate/ROI)
- Skip accuracy
- Market breakdown
- Tier breakdown
- Baseline accuracy
- Corner volume distribution
- Lessons summary