# /baseline — Calculate Corners Baseline

Calculate combined corners baseline for any matchup.

## What This Does
1. Looks up both teams in data/teams.csv
2. Calculates combined baseline using two methods
3. Compares baseline to line if provided
4. Outputs tier classification and market recommendation

## Usage
Run: python main.py baseline --home [Team] --away [Team] --line [X.X]

## Output
- Team corner averages and style classifications
- Combined baseline (two calculation methods)
- Tier classification
- Market recommendation
- Confidence level

## Notes
- If line not provided outputs baseline only
- If team not found prints available teams