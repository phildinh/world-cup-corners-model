import pandas as pd
import os
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    return pd.read_csv(path)

def generate_briefing():
    matches = load_csv('matches.csv')
    teams = load_csv('teams.csv')
    bets = load_csv('bets.csv')
    predictions = load_csv('predictions.csv')
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
    skips = predictions[predictions['bet_placed'] == False]
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

    # ── OUTPUT ──────────────────────────────────────
    divider = "=" * 60
    thin = "-" * 60

    print(f"\n{divider}")
    print("  WORLD CUP 2026 — CORNERS MODEL BRIEFING")
    print(f"  Generated: {date.today().isoformat()}")
    print(divider)

    # RECORD
    print("\n  BETTING RECORD")
    print(thin)
    print(f"  Bets:          {total_bets} ({won}W {lost}L)")
    print(f"  Win rate:      {win_rate}%")
    print(f"  P&L:           {'+' if total_pl >= 0 else ''}{total_pl} units")
    print(f"  ROI:           {'+' if roi >= 0 else ''}{roi}%")
    print(f"  Skips:         {total_skips} total — {correct_skips} correct ({skip_accuracy}%)")

    # MARKET BREAKDOWN
    print("\n  MARKET BREAKDOWN")
    print(thin)
    for _, row in market_stats.iterrows():
        pl = row['pl']
        print(f"  {row['market']:<20} "
              f"{int(row['won'])}W {int(row['bets'] - row['won'])}L  "
              f"Win rate: {row['win_rate']}%  "
              f"P&L: {'+' if pl >= 0 else ''}{round(pl, 3)}")

    # ALL BETS PLACED
    print("\n  ALL BETS PLACED")
    print(thin)
    for _, row in bets.iterrows():
        icon = '✅' if row['outcome'] == 'won' else '❌'
        print(f"  {icon} {row['home_team']} vs {row['away_team']:<15} "
              f"{row['market']:<15} {row['selection']:<15} "
              f"@ {row['odds']}  {row['outcome'].upper()}  "
              f"P&L: {'+' if row['profit_loss'] >= 0 else ''}{row['profit_loss']}")

    # ALL MATCH RESULTS
    print("\n  ALL MATCH RESULTS")
    print(thin)
    for _, row in matches.iterrows():
        print(f"  {row['date']}  "
              f"{row['home_team']} {row['home_score']}-{row['away_score']} {row['away_team']:<15}  "
              f"Corners: {row['total_corners']} "
              f"({row['home_corners']}H / {row['away_corners']}A)  "
              f"State: {row['game_state']}")

    # TEAM CORNER AVERAGES — FULL TABLE
    print("\n  TEAM CORNER AVERAGES")
    print(thin)
    print(f"  {'Team':<20} {'Taken':>6} {'Conceded':>9} {'Played':>7}  "
          f"{'Attack Type':<25} {'Def Type'}")
    print(thin)
    teams_sorted = teams.sort_values('avg_corners_taken', ascending=False)
    for _, row in teams_sorted.iterrows():
        print(f"  {row['team_name']:<20} "
              f"{row['avg_corners_taken']:>6.2f} "
              f"{row['avg_corners_conceded']:>9.2f} "
              f"{row['matches_played']:>7}  "
              f"{row['attack_type']:<25} "
              f"{row['defensive_type']}")

    # ALL LESSONS LEARNED
    print("\n  ALL LESSONS LEARNED")
    print(thin)
    for _, row in lessons.iterrows():
        print(f"  [{row['lesson_id']}] {row['date']}  [{row['category']}]")
        print(f"      Lesson: {row['lesson']}")
        print(f"      Rule:   {row['rule_added']}")
        print()

    # ALL PREDICTIONS LOG
    print("\n  ALL PREDICTIONS LOG")
    print(thin)
    print(f"  {'Match':<30} {'Baseline':>9} {'Line':>5} {'Tier':<12} "
          f"{'Bet?':>5} {'Outcome'}")
    print(thin)
    for _, row in predictions.iterrows():
        match = f"{row['home_team']} vs {row['away_team']}"
        bet_placed = 'YES' if row['bet_placed'] else 'NO'
        print(f"  {match:<30} "
              f"{row['combined_baseline']:>9.2f} "
              f"{row['line_offered']:>5.1f} "
              f"{row['tier']:<12} "
              f"{bet_placed:>5}  "
              f"{row['outcome']}")

    # MODEL INFO
    print(f"\n{divider}")
    print(f"  MODEL: v3.0  |  MATCHES LOGGED: {len(matches)}  "
          f"|  TEAMS TRACKED: {len(teams)}")
    print(f"  Paste this entire output into Claude Chat to load full context.")
    print(f"{divider}\n")


if __name__ == '__main__':
    generate_briefing()