import pandas as pd
import os
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

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

    # ── FORMATTING ──────────────────────────────────
    divider = "=" * 60
    thin = "-" * 60

    # ── HEADER ──────────────────────────────────────
    print(f"\n{divider}")
    print("  WORLD CUP 2026 — CORNERS MODEL BRIEFING")
    print(f"  Generated: {date.today().isoformat()}")
    print(divider)

    # ── BETTING RECORD ──────────────────────────────
    print("\n  BETTING RECORD")
    print(thin)
    print(f"  Bets:          {total_bets} ({won}W {lost}L)")
    print(f"  Win rate:      {win_rate}%")
    print(f"  P&L:           {'+' if total_pl >= 0 else ''}{total_pl} units")
    print(f"  ROI:           {'+' if roi >= 0 else ''}{roi}%")
    print(f"  Skips:         {total_skips} total — {correct_skips} correct ({skip_accuracy}%)")

    # ── MARKET BREAKDOWN ────────────────────────────
    print("\n  MARKET BREAKDOWN")
    print(thin)
    for _, row in market_stats.iterrows():
        pl = row['pl']
        print(f"  {row['market']:<20} "
              f"{int(row['won'])}W {int(row['bets'] - row['won'])}L  "
              f"Win rate: {row['win_rate']}%  "
              f"P&L: {'+' if pl >= 0 else ''}{round(pl, 3)}")

    # ── ALL BETS PLACED ─────────────────────────────
    print("\n  ALL BETS PLACED")
    print(thin)
    for _, row in bets.iterrows():
        icon = '✅' if row['outcome'] == 'won' else '❌'
        print(f"  {icon} {row['home_team']} vs {row['away_team']:<15} "
              f"{row['market']:<15} {row['selection']:<15} "
              f"@ {row['odds']}  {row['outcome'].upper()}  "
              f"P&L: {'+' if row['profit_loss'] >= 0 else ''}{row['profit_loss']}")

    # ── ALL MATCH RESULTS ───────────────────────────
    print("\n  ALL MATCH RESULTS")
    print(thin)
    for _, row in matches.iterrows():
        print(f"  {row['date']}  "
              f"{row['home_team']} {row['home_score']}-{row['away_score']} "
              f"{row['away_team']:<15}  "
              f"Corners: {row['total_corners']} "
              f"({row['home_corners']}H / {row['away_corners']}A)  "
              f"State: {row['game_state']}")

    # ── TEAM CORNER AVERAGES ─────────────────────────
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

    # ── ALL LESSONS LEARNED ──────────────────────────
    print("\n  ALL LESSONS LEARNED")
    print(thin)
    for _, row in lessons.iterrows():
        print(f"  [{row['lesson_id']}] {row['date']}  [{row['category']}]")
        print(f"      Lesson: {row['lesson']}")
        print(f"      Rule:   {row['rule_added']}")
        print()

    # ── ALL PREDICTIONS LOG ──────────────────────────
    print("\n  ALL PREDICTIONS LOG")
    print(thin)
    print(f"  {'Match':<30} {'Baseline':>9} {'Line':>5} {'Tier':<12} "
          f"{'Bet?':>5} {'Lean':<7} {'Outcome'}")
    print(thin)
    for _, row in predictions.iterrows():
        match = f"{row['home_team']} vs {row['away_team']}"
        bet_placed = 'YES' if row['bet_placed'] else 'NO'
        lean = str(row.get('skip_lean', '')).strip()
        if pd.isna(row.get('skip_lean', '')):
            lean = ''
        print(f"  {match:<30} "
              f"{row['combined_baseline']:>9.2f} "
              f"{row['line_offered']:>5.1f} "
              f"{row['tier']:<12} "
              f"{bet_placed:>5} {lean:<7} "
              f"{row['outcome']}")

    # ── MODEL VERSION HISTORY ────────────────────────
    try:
        versions = load_csv('model_versions.csv')
        print(f"\n  MODEL VERSION HISTORY")
        print(thin)
        for _, row in versions.iterrows():
            print(f"  {row['version']}  {row['date']}  "
                  f"Matches: {row['matches_at_change']}  "
                  f"Win rate: {row['win_rate_at_change']}  "
                  f"ROI: {row['roi_at_change']}")
            print(f"    Changed: {row['rule_changed']}")
            print(f"    Trigger: {row['trigger']}")
            print()
    except Exception:
        pass

    # ── FULL MODEL FRAMEWORK ─────────────────────────
    try:
        model_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'MODEL.md'))
        with open(model_path, 'r', encoding='utf-8') as f:
            model_content = f.read()
        print(f"\n{divider}")
        print("  FULL MODEL FRAMEWORK")
        print(divider)
        print(model_content)
    except Exception as e:
        print(f"\n  WARNING: MODEL.md not found — {e}")

    # ── WORKFLOW REFERENCE ───────────────────────────
    print(f"\n{divider}")
    print("  WORKFLOW REFERENCE")
    print(divider)
    print("""
  HOW TO USE THIS BRIEFING
  Paste entire output into Claude Chat — it loads full context instantly.
  Then give Claude today's matches and send Bet365 screenshots per match.
  If Claude cannot read a screenshot it will ask you to verify the numbers.

  RESULTS FORMAT TO GIVE CLAUDE AFTER MATCHES:
  Results:
  1. [Home] vs [Away] — [score] — [total] corners ([Home] X, [Away] X) — [game state] — [won/lost/skip]
  2. [Home] vs [Away] — [score] — [total] corners ([Home] X, [Away] X) — [game state] — [won/lost/skip]

  COMMAND TEMPLATE — MATCH WITH BET:
  python main.py update
    --home [Home] --away [Away]
    --home-score [X] --away-score [X]
    --total-corners [X] --home-corners [X] --away-corners [X]
    --group [X] --game-state [normal/underdog_scored_early/blowout]
    --notes "[one line summary]"
    --market [total_over/total_under/ah_corners/1h_over/1h_under]
    --selection "[e.g. Over 9.5]"
    --odds [X.XXX] --stake 1.00 --bet-outcome [won/lost/void]
    --tier [tier_1/tier_2/tier_3] --confidence [high/medium/low]
    --line [X.X] --home-avg [X.XX] --away-avg [X.XX]
    --lesson "[lesson learned]"
    --lesson-category [baseline_accuracy/market_selection/
                       style_classification/game_state/skip_accuracy]
    --rule "[new rule added to model]"

  COMMAND TEMPLATE — SKIPPED MATCH:
  python main.py update
    --home [Home] --away [Away]
    --home-score [X] --away-score [X]
    --total-corners [X] --home-corners [X] --away-corners [X]
    --group [X] --game-state [normal/underdog_scored_early/blowout]
    --notes "[one line summary]"
    --skip-lean [over/under/none]

  VALID VALUES:
  market:     total_over / total_under / ah_corners / 1h_over / 1h_under
  game_state: normal / underdog_scored_early / blowout
  tier:       tier_1 / tier_2 / tier_3
  confidence: high / medium / low / skip
  category:   baseline_accuracy / market_selection / style_classification
              game_state / skip_accuracy
  """)

    # ── FOOTER ──────────────────────────────────────
    print(divider)
    print(f"  MODEL: v3.0  |  MATCHES LOGGED: {len(matches)}  "
          f"|  TEAMS TRACKED: {len(teams)}")
    print(f"  Paste this entire output into Claude Chat to load full context.")
    print(divider + "\n")


if __name__ == '__main__':
    generate_briefing()