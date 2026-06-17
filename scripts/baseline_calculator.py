import pandas as pd
import argparse
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def load_teams():
    path = os.path.join(DATA_DIR, 'teams.csv')
    return pd.read_csv(path)

def get_team(teams, name):
    match = teams[teams['team_name'].str.lower() == name.lower()]
    if match.empty:
        print(f"❌ Team not found: {name}")
        print(f"   Available teams: {', '.join(teams['team_name'].tolist())}")
        sys.exit(1)
    return match.iloc[0]

def classify_tier(baseline, line):
    diff = baseline - line
    if diff >= 1.5:
        return 'tier_1', 'STRONG OVER — Bet', 'high'
    elif diff >= 1.0:
        return 'tier_2', 'CONSIDER OVER — Check odds', 'medium'
    elif diff <= -1.5:
        return 'tier_1_under', 'STRONG UNDER — Bet', 'high'
    elif diff <= -1.0:
        return 'tier_2_under', 'CONSIDER UNDER — Check odds', 'medium'
    else:
        return 'tier_3', 'SKIP — No clean edge', 'skip'

def recommend_market(home, away, tier):
    home_type = home['attack_type']
    away_type = away['attack_type']
    home_def = home['defensive_type']
    away_def = away['defensive_type']

    # AH corners only when pure deep block opponent
    if away_def == 'pure_deep_block' and 'under' not in tier:
        return 'Asian Total Corners Over — or AH Corners (home team)'
    elif home_def == 'pure_deep_block' and 'under' not in tier:
        return 'Asian Total Corners Over — or AH Corners (away team)'
    elif 'under' in tier:
        return 'Asian Total Corners Under'
    else:
        return 'Asian Total Corners Over'

def calculate_baseline(home_name, away_name, line=None):
    teams = load_teams()
    home = get_team(teams, home_name)
    away = get_team(teams, away_name)

    home_taken = home['avg_corners_taken']
    away_taken = away['avg_corners_taken']
    home_conceded = home['avg_corners_conceded']
    away_conceded = away['avg_corners_conceded']

    # Combined baseline — average of two methods
    method1 = round(home_taken + away_taken, 2)
    method2 = round((home_taken + away_conceded) / 2 +
                    (away_taken + home_conceded) / 2, 2)
    baseline = round((method1 + method2) / 2, 2)

    print("\n" + "="*50)
    print(f"  BASELINE: {home_name} vs {away_name}")
    print("="*50)
    print(f"\n  {home_name}:")
    print(f"    Avg corners taken:    {home_taken}")
    print(f"    Avg corners conceded: {home_conceded}")
    print(f"    Attack type:          {home['attack_type']}")
    print(f"    Defensive type:       {home['defensive_type']}")
    print(f"\n  {away_name}:")
    print(f"    Avg corners taken:    {away_taken}")
    print(f"    Avg corners conceded: {away_conceded}")
    print(f"    Attack type:          {away['attack_type']}")
    print(f"    Defensive type:       {away['defensive_type']}")
    print(f"\n  Combined Baseline (Method 1 — taken+taken): {method1}")
    print(f"  Combined Baseline (Method 2 — taken+conceded): {method2}")
    print(f"  Combined Baseline (Average):  {baseline}")

    if line:
        tier, recommendation, confidence = classify_tier(baseline, line)
        market = recommend_market(home, away, tier)
        diff = round(baseline - line, 2)
        print(f"\n  Bet365 Line:          {line}")
        print(f"  Baseline vs Line:     {'+' if diff >= 0 else ''}{diff}")
        print(f"  Tier:                 {tier}")
        print(f"  Confidence:           {confidence}")
        print(f"  Recommendation:       {recommendation}")
        print(f"  Market:               {market}")
    else:
        print(f"\n  ⚠️  No line provided — pass --line to get tier classification")

    print("="*50 + "\n")
    return baseline

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Calculate corners baseline for a matchup')
    parser.add_argument('--home', required=True,
                        help='Home team name')
    parser.add_argument('--away', required=True,
                        help='Away team name')
    parser.add_argument('--line', type=float, default=None,
                        help='Bet365 corners line (optional)')
    args = parser.parse_args()

    calculate_baseline(args.home, args.away, args.line)