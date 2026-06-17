import pandas as pd
import os
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    return pd.read_csv(path)

def save_csv(df, filename):
    path = os.path.join(DATA_DIR, filename)
    df.to_csv(path, index=False)

def log_version(version, change, trigger):
    bets = load_csv('bets.csv')
    matches = load_csv('matches.csv')
    versions = load_csv('model_versions.csv')

    total_bets = len(bets)
    won = len(bets[bets['outcome'] == 'won'])
    win_rate = round((won / total_bets) * 100, 1) if total_bets > 0 else 0
    total_staked = bets['stake'].sum()
    total_pl = round(bets['profit_loss'].sum(), 3)
    roi = round((total_pl / total_staked) * 100, 1) if total_staked > 0 else 0

    match_count = len(matches)

    prev_value = versions.iloc[-1]['new_value'] if len(versions) > 0 else 'none'

    new_row = {
        'version': version,
        'date': date.today().isoformat(),
        'rule_changed': change,
        'old_value': prev_value,
        'new_value': change,
        'trigger': trigger,
        'matches_at_change': match_count,
        'win_rate_at_change': f"{win_rate}%",
        'roi_at_change': f"{'+' if roi >= 0 else ''}{roi}%"
    }

    versions = pd.concat([versions, pd.DataFrame([new_row])], ignore_index=True)
    save_csv(versions, 'model_versions.csv')

    print(f"\n✅ Version {version} logged")
    print(f"   Change:    {change}")
    print(f"   Trigger:   {trigger}")
    print(f"   Matches:   {match_count}")
    print(f"   Win rate:  {win_rate}%")
    print(f"   ROI:       {'+' if roi >= 0 else ''}{roi}%")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Log model version change')
    parser.add_argument('--version', required=True, help='Version number e.g. v3.1')
    parser.add_argument('--change', required=True, help='What rule changed')
    parser.add_argument('--trigger', required=True, help='Why it changed')
    args = parser.parse_args()
    log_version(args.version, args.change, args.trigger)
