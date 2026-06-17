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

    flat_pl = round(sum(
        (row['odds'] - 1) if row['outcome'] == 'won' else -1.0
        for _, row in bets.iterrows()
    ), 3)
    flat_staked = total_bets
    flat_roi = round((flat_pl / flat_staked) * 100, 1) if flat_staked > 0 else 0

    weighted_staked = bets['stake'].sum()
    weighted_pl = round(bets['profit_loss'].sum(), 3)
    weighted_roi = round((weighted_pl / weighted_staked) * 100, 1) if weighted_staked > 0 else 0

    # ── SKIP ACCURACY ───────────────────────────────
    skips = predictions[predictions['bet_placed'].astype(str).str.upper() == 'FALSE']
    correct_skips = len(skips[skips['outcome'] == 'correct'])
    total_skips = len(skips)
    skip_accuracy = round(
        (correct_skips / total_skips) * 100, 1
    ) if total_skips > 0 else 0

    # ── SHADOW PORTFOLIO ────────────────────────────
    shadow = predictions[predictions['shadow_bet'].astype(str).str.upper() == 'TRUE']
    shadow_total = len(shadow)
    shadow_won = len(shadow[shadow['shadow_outcome'] == 'won'])
    shadow_wr = round((shadow_won / shadow_total) * 100, 1) if shadow_total > 0 else 0
    shadow_pl = shadow_won - len(shadow[shadow['shadow_outcome'] == 'lost'])

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
    print(f"  Bets:              {total_bets} ({won}W {lost}L)")
    print(f"  Win rate:          {win_rate}%")
    print(f"  P&L (flat):        {'+' if flat_pl >= 0 else ''}{flat_pl} units")
    print(f"  P&L (weighted):    {'+' if weighted_pl >= 0 else ''}{weighted_pl} units")
    print(f"  ROI (flat):        {'+' if flat_roi >= 0 else ''}{flat_roi}%")
    print(f"  ROI (weighted):    {'+' if weighted_roi >= 0 else ''}{weighted_roi}%")
    print(f"  Skips:             {total_skips} total — {correct_skips} correct ({skip_accuracy}%)")
    print(f"  Shadow portfolio:  {shadow_total} tracked — {shadow_won} won ({shadow_wr}%) — "
          f"{'+' if shadow_pl >= 0 else ''}{shadow_pl}.0 shadow units")

    # ── DATA CONFIDENCE WARNINGS ────────────────────
    low_conf = predictions[predictions.get('data_confidence', pd.Series(dtype=str)).astype(str) == 'low']
    if len(low_conf) > 0:
        print(f"\n  LOW DATA CONFIDENCE WARNINGS")
        print(thin)
        for _, row in low_conf.iterrows():
            print(f"  {row['home_team']} vs {row['away_team']} — "
                  f"tier demoted due to low data confidence")

    # ── MARKET BREAKDOWN ────────────────────────────
    print("\n  MARKET BREAKDOWN")
    print(thin)
    market_stats = bets.groupby('market').agg(
        bets=('outcome', 'count'),
        won=('outcome', lambda x: (x == 'won').sum()),
        pl=('profit_loss', 'sum')
    ).reset_index()
    market_stats['win_rate'] = round(
        (market_stats['won'] / market_stats['bets']) * 100, 1)
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
        icon = 'W' if row['outcome'] == 'won' else 'L'
        print(f"  [{icon}] {row['home_team']} vs {row['away_team']:<15} "
              f"{row['market']:<15} {row['selection']:<15} "
              f"@ {row['odds']}  {row['outcome'].upper()}  "
              f"P&L: {'+' if row['profit_loss'] >= 0 else ''}{row['profit_loss']}")

    # ── ALL MATCH RESULTS ───────────────────────────
    print("\n  ALL MATCH RESULTS")
    print(thin)
    for _, row in matches.iterrows():
        mt = str(row.get('match_type', '')).strip()
        if pd.isna(row.get('match_type', '')):
            mt = ''
        mt_str = f"  Type: {mt}" if mt else ""
        print(f"  {row['date']}  "
              f"{row['home_team']} {row['home_score']}-{row['away_score']} "
              f"{row['away_team']:<15}  "
              f"Corners: {row['total_corners']} "
              f"({row['home_corners']}H / {row['away_corners']}A)  "
              f"State: {row['game_state']}{mt_str}")

    # ── MATCH TYPE PERFORMANCE ──────────────────────
    if 'match_type' in matches.columns:
        mt_stats = matches.groupby('match_type').agg(
            count=('total_corners', 'count'),
            avg_corners=('total_corners', 'mean')
        ).reset_index()
        mt_stats['avg_corners'] = mt_stats['avg_corners'].round(1)

        has_meaningful = len(mt_stats[mt_stats['count'] >= 3]) > 0
        if has_meaningful or len(matches) >= 5:
            print("\n  MATCH TYPE PERFORMANCE")
            print(thin)
            mt_preds = predictions.merge(
                matches[['match_id', 'total_corners']], on='match_id', how='left')
            for _, row in mt_stats.sort_values('avg_corners', ascending=False).iterrows():
                flag = " *" if row['count'] >= 3 else ""
                mt_bets = mt_preds[
                    (mt_preds['match_type'] == row['match_type']) &
                    (mt_preds['bet_placed'].astype(str).str.upper() == 'TRUE')
                ]
                bet_info = ""
                if len(mt_bets) > 0:
                    mt_won = len(mt_bets[mt_bets['outcome'] == 'won'])
                    bet_info = f"  Bets: {mt_won}W {len(mt_bets)-mt_won}L"
                print(f"  {row['match_type']:<20} "
                      f"{int(row['count'])} match{'es' if row['count'] > 1 else ''}  "
                      f"avg {row['avg_corners']:>5.1f} corners{bet_info}{flag}")

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
    print(f"  {'Match':<30} {'Baseline':>8} {'Line':>5} {'Tier':<7} "
          f"{'Bet?':>4} {'Lean':<6} {'DC':<4} {'Type':<16} {'Outcome'}")
    print(thin)
    for _, row in predictions.iterrows():
        match = f"{row['home_team']} vs {row['away_team']}"
        bet_placed = 'YES' if str(row['bet_placed']).upper() == 'TRUE' else 'NO'
        lean = str(row.get('skip_lean', '')).strip()
        if pd.isna(row.get('skip_lean', '')):
            lean = ''
        dc = str(row.get('data_confidence', 'high')).strip()
        if pd.isna(row.get('data_confidence', '')):
            dc = 'high'
        dc_short = dc[0].upper() if dc else 'H'
        mt = str(row.get('match_type', '')).strip()
        if pd.isna(row.get('match_type', '')):
            mt = ''
        ct = str(row.get('counter_threat', '')).strip()
        ct_flag = " CT" if ct == 'yes' else ""
        print(f"  {match:<30} "
              f"{row['combined_baseline']:>8.2f} "
              f"{row['line_offered']:>5.1f} "
              f"{row['tier']:<7} "
              f"{bet_placed:>4} {lean:<6} "
              f"{dc_short:<4} {mt:<16} "
              f"{row['outcome']}{ct_flag}")

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
        print(f"  Current: Flat P&L {'+' if flat_pl >= 0 else ''}{flat_pl} | "
              f"Weighted P&L {'+' if weighted_pl >= 0 else ''}{weighted_pl}")
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
    --data-confidence [high/medium/low]
    --counter-threat [yes/no/auto]
    --match-type [wide_vs_deep/wide_vs_counter/central_vs_deep/direct_vs_direct/wide_vs_open/mixed]
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

  OPTIONAL V4.0 FLAGS (all have sensible defaults):
    --data-confidence [high/medium/low]    default: high
    --counter-threat [yes/no/auto]         default: auto (derived from team DB)
    --counter-scorer                       flag: opponent scored on counter
    --transition-xg [value]                opponent transition xG per game
    --altitude [yes/no]                    default: no
    --venue "[stadium name]"               auto-detects altitude
    --debut-opponent                       flag: opponent first World Cup
    --match-type [type]                    default: auto-derived from team DB

  VALID VALUES:
  market:          total_over / total_under / ah_corners / 1h_over / 1h_under
  game_state:      normal / underdog_scored_early / blowout
  tier:            tier_1 / tier_2 / tier_3
  confidence:      high / medium / low / skip
  data_confidence: high / medium / low
  counter_threat:  yes / no / auto
  match_type:      wide_vs_deep / wide_vs_counter / central_vs_deep /
                   direct_vs_direct / wide_vs_open / mixed
  category:        baseline_accuracy / market_selection / style_classification
                   game_state / skip_accuracy
  """)

    # ── FOOTER ──────────────────────────────────────
    print(divider)
    print(f"  MODEL: v4.0  |  MATCHES LOGGED: {len(matches)}  "
          f"|  TEAMS TRACKED: {len(teams)}")
    print(f"  Paste this entire output into Claude Chat to load full context.")
    print(divider + "\n")


if __name__ == '__main__':
    generate_briefing()
