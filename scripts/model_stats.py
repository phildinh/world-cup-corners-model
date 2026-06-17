import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    return pd.read_csv(path)

def print_divider(char='=', width=50):
    print(char * width)

def model_stats():
    bets = load_csv('bets.csv')
    predictions = load_csv('predictions.csv')
    matches = load_csv('matches.csv')
    lessons = load_csv('lessons.csv')

    # ── BETTING RECORD ──────────────────────────────
    total_bets = len(bets)
    won = len(bets[bets['outcome'] == 'won'])
    lost = len(bets[bets['outcome'] == 'lost'])
    win_rate = round((won / total_bets) * 100, 1) if total_bets > 0 else 0
    total_staked = bets['stake'].sum()
    total_pl = round(bets['profit_loss'].sum(), 3)
    roi = round((total_pl / total_staked) * 100, 1) if total_staked > 0 else 0

    # ── SKIP ACCURACY ───────────────────────────────
    skips = predictions[predictions['bet_placed'].astype(str).str.upper() == 'FALSE']
    correct_skips = len(skips[skips['outcome'] == 'correct'])
    total_skips = len(skips)
    skip_accuracy = round(
        (correct_skips / total_skips) * 100, 1
    ) if total_skips > 0 else 0

    # ── MARKET BREAKDOWN ────────────────────────────
    market_stats = bets.groupby('market').agg(
        bets=('outcome', 'count'),
        won=('outcome', lambda x: (x == 'won').sum()),
        pl=('profit_loss', 'sum')
    ).reset_index()
    market_stats['win_rate'] = round(
        (market_stats['won'] / market_stats['bets']) * 100, 1)
    market_stats['pl'] = market_stats['pl'].round(3)

    # ── TIER BREAKDOWN ──────────────────────────────
    tier_stats = predictions[
        predictions['bet_placed'].astype(str).str.upper() == 'TRUE'
    ].groupby('tier').agg(
        bets=('outcome', 'count'),
        won=('outcome', lambda x: (x == 'won').sum())
    ).reset_index()
    tier_stats['win_rate'] = round(
        (tier_stats['won'] / tier_stats['bets']) * 100, 1)

    # ── BASELINE ACCURACY ───────────────────────────
    merged = predictions.merge(
        matches[['match_id', 'total_corners']], on='match_id', how='left')
    merged['baseline_diff'] = (
        merged['combined_baseline'] - merged['total_corners']).abs()
    avg_baseline_error = round(merged['baseline_diff'].mean(), 2)

    # ── CORNER VOLUME DISTRIBUTION ──────────────────
    low = len(matches[matches['total_corners'] <= 7])
    mid = len(matches[
        (matches['total_corners'] >= 8) &
        (matches['total_corners'] <= 10)])
    high = len(matches[matches['total_corners'] >= 11])

    # ── OUTPUT ──────────────────────────────────────
    print("\n")
    print_divider()
    print("  WORLD CUP 2026 — CORNERS MODEL STATS")
    print_divider()

    print("\n  BETTING RECORD")
    print_divider('-')
    print(f"  Total bets:       {total_bets}")
    print(f"  Won:              {won}")
    print(f"  Lost:             {lost}")
    print(f"  Win rate:         {win_rate}%")
    print(f"  Total staked:     {total_staked:.2f} units")
    print(f"  Total P&L:        {'+' if total_pl >= 0 else ''}{total_pl} units")
    print(f"  ROI:              {'+' if roi >= 0 else ''}{roi}%")

    print("\n  SKIP ACCURACY")
    print_divider('-')
    print(f"  Total skips:      {total_skips}")
    print(f"  Correct skips:    {correct_skips}")
    print(f"  Skip accuracy:    {skip_accuracy}%")

    print("\n  MARKET BREAKDOWN")
    print_divider('-')
    for _, row in market_stats.iterrows():
        print(f"  {row['market']:<20} "
              f"{int(row['won'])}W {int(row['bets'] - row['won'])}L  "
              f"Win rate: {row['win_rate']}%  "
              f"P&L: {'+' if row['pl'] >= 0 else ''}{row['pl']}")

    print("\n  TIER BREAKDOWN")
    print_divider('-')
    for _, row in tier_stats.iterrows():
        print(f"  {row['tier']:<15} "
              f"{int(row['won'])}W {int(row['bets'] - row['won'])}L  "
              f"Win rate: {row['win_rate']}%")

    print("\n  BASELINE ACCURACY")
    print_divider('-')
    print(f"  Avg baseline error: {avg_baseline_error} corners")

    print("\n  CORNER VOLUME DISTRIBUTION")
    print_divider('-')
    print(f"  Low  (0-7):        {low} matches")
    print(f"  Mid  (8-10):       {mid} matches")
    print(f"  High (11+):        {high} matches")

    print("\n  LESSONS LEARNED")
    print_divider('-')
    print(f"  Total lessons logged: {len(lessons)}")
    cats = lessons['category'].value_counts()
    for cat, count in cats.items():
        print(f"  {cat:<25} {count} lessons")

    print_divider()
    print()

if __name__ == '__main__':
    model_stats()