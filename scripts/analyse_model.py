import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    return pd.read_csv(path)

def analyse_model():
    matches = load_csv('matches.csv')
    predictions = load_csv('predictions.csv')
    bets = load_csv('bets.csv')
    teams = load_csv('teams.csv')

    divider = "=" * 60
    thin = "-" * 60

    print(f"\n{divider}")
    print("  WORLD CUP 2026 — MODEL ANALYSIS")
    print(divider)

    total_matches = len(matches)

    # ── SECTION 1 — TIER PERFORMANCE ────────────────
    print("\n  SECTION 1 — TIER PERFORMANCE")
    print(thin)

    bet_preds = predictions[predictions['bet_placed'].astype(str).str.upper() == 'TRUE']
    skip_preds = predictions[predictions['bet_placed'].astype(str).str.upper() == 'FALSE']

    merged_preds = bet_preds.merge(
        bets[['match_id', 'outcome', 'profit_loss']],
        on='match_id', how='left', suffixes=('_pred', '_bet'))

    for tier in ['tier_1', 'tier_2', 'tier_3']:
        tier_rows = merged_preds[merged_preds['tier'] == tier]
        if len(tier_rows) == 0:
            print(f"  {tier:<10} No bets placed")
            continue
        won = len(tier_rows[tier_rows['outcome_bet'] == 'won'])
        lost = len(tier_rows) - won
        wr = round((won / len(tier_rows)) * 100, 1)
        pl = round(tier_rows['profit_loss'].sum(), 3)
        print(f"  {tier:<10} {won}W {lost}L  Win rate: {wr}%  "
              f"P&L: {'+' if pl >= 0 else ''}{pl}")

    skip_tiers = skip_preds.groupby('tier').size()
    for tier, count in skip_tiers.items():
        tier_skips = skip_preds[skip_preds['tier'] == tier]
        correct = len(tier_skips[tier_skips['outcome'] == 'correct'])
        print(f"  {tier:<10} {count} skips — {correct} correct")

    if total_matches < 10:
        print(f"\n  ⚠️  Only {total_matches} matches — tier thresholds too early to adjust")
    else:
        print("\n  Recommendation: review tier thresholds based on performance above")

    # ── SECTION 2 — MARKET PERFORMANCE ──────────────
    print(f"\n  SECTION 2 — MARKET PERFORMANCE")
    print(thin)

    market_stats = bets.groupby('market').agg(
        count=('outcome', 'count'),
        won=('outcome', lambda x: (x == 'won').sum()),
        pl=('profit_loss', 'sum')
    ).reset_index()
    market_stats['win_rate'] = round(
        (market_stats['won'] / market_stats['count']) * 100, 1)
    market_stats['pl'] = market_stats['pl'].round(3)

    for _, row in market_stats.iterrows():
        lost = int(row['count'] - row['won'])
        pl = row['pl']
        print(f"  {row['market']:<20} {int(row['won'])}W {lost}L  "
              f"Win rate: {row['win_rate']}%  "
              f"P&L: {'+' if pl >= 0 else ''}{pl}")

    if len(market_stats) > 0:
        best = market_stats.loc[market_stats['pl'].idxmax()]
        worst = market_stats.loc[market_stats['pl'].idxmin()]
        print(f"\n  Best market:  {best['market']} "
              f"({'+' if best['pl'] >= 0 else ''}{best['pl']})")
        print(f"  Worst market: {worst['market']} "
              f"({'+' if worst['pl'] >= 0 else ''}{worst['pl']})")

    # ── SECTION 3 — BASELINE ACCURACY ───────────────
    print(f"\n  SECTION 3 — BASELINE ACCURACY")
    print(thin)

    merged = predictions.merge(
        matches[['match_id', 'total_corners']], on='match_id', how='left')
    merged['error'] = merged['combined_baseline'] - merged['total_corners']
    merged['abs_error'] = merged['error'].abs()

    avg_error = round(merged['abs_error'].mean(), 2)
    within_1 = len(merged[merged['abs_error'] <= 1.0])
    within_2 = len(merged[merged['abs_error'] <= 2.0])
    pct_1 = round((within_1 / len(merged)) * 100, 1)
    pct_2 = round((within_2 / len(merged)) * 100, 1)
    avg_direction = round(merged['error'].mean(), 2)

    print(f"  Avg absolute error:    {avg_error} corners")
    print(f"  Within 1.0 of actual:  {within_1}/{len(merged)} ({pct_1}%)")
    print(f"  Within 2.0 of actual:  {within_2}/{len(merged)} ({pct_2}%)")

    if avg_direction > 0:
        print(f"  Bias: OVERESTIMATING by {avg_direction} corners on average")
    elif avg_direction < 0:
        print(f"  Bias: UNDERESTIMATING by {abs(avg_direction)} corners on average")
    else:
        print(f"  Bias: perfectly calibrated")

    for _, row in merged.iterrows():
        match = f"{row['home_team']} vs {row['away_team']}"
        print(f"    {match:<30} baseline {row['combined_baseline']:>5.1f}  "
              f"actual {int(row['total_corners']):>3}  "
              f"error {row['error']:>+5.1f}")

    # ── SECTION 4 — ATTACK TYPE COMBINATIONS ────────
    print(f"\n  SECTION 4 — ATTACK TYPE COMBINATIONS")
    print(thin)

    match_types = matches.merge(
        teams[['team_name', 'attack_type', 'defensive_type']],
        left_on='home_team', right_on='team_name', how='left'
    ).rename(columns={'attack_type': 'home_attack', 'defensive_type': 'home_def'})
    match_types = match_types.merge(
        teams[['team_name', 'attack_type', 'defensive_type']],
        left_on='away_team', right_on='team_name', how='left'
    ).rename(columns={'attack_type': 'away_attack', 'defensive_type': 'away_def'})

    match_types['combo'] = (match_types['home_attack'] + ' vs '
                            + match_types['away_def'])

    combo_stats = match_types.groupby('combo').agg(
        matches=('total_corners', 'count'),
        avg_corners=('total_corners', 'mean')
    ).reset_index()
    combo_stats['avg_corners'] = combo_stats['avg_corners'].round(1)
    combo_stats = combo_stats.sort_values('avg_corners', ascending=False)

    for _, row in combo_stats.iterrows():
        flag = " ★" if row['matches'] >= 3 else ""
        print(f"  {row['combo']:<45} "
              f"avg {row['avg_corners']:>5.1f}  "
              f"({int(row['matches'])} match{'es' if row['matches'] > 1 else ''}){flag}")

    if total_matches < 10:
        print(f"\n  ⚠️  Only {total_matches} matches — no combination has 3+ matches yet")

    # ── SECTION 5 — GAME STATE IMPACT ───────────────
    print(f"\n  SECTION 5 — GAME STATE IMPACT")
    print(thin)

    for state in ['normal', 'underdog_scored_early', 'blowout']:
        state_matches = matches[matches['game_state'] == state]
        if len(state_matches) > 0:
            avg = round(state_matches['total_corners'].mean(), 1)
            count = len(state_matches)
            print(f"  {state:<30} avg {avg:>5.1f} corners  "
                  f"({count} match{'es' if count > 1 else ''})")
        else:
            print(f"  {state:<30} no matches")

    normal_avg = matches[matches['game_state'] == 'normal']['total_corners'].mean()
    for state in ['underdog_scored_early', 'blowout']:
        state_matches = matches[matches['game_state'] == state]
        if len(state_matches) > 0:
            state_avg = state_matches['total_corners'].mean()
            diff = round(state_avg - normal_avg, 1)
            print(f"  {state} vs normal: {'+' if diff >= 0 else ''}{diff} corners")

    # ── SECTION 6 — LINE ACCURACY ───────────────────
    print(f"\n  SECTION 6 — LINE ACCURACY")
    print(thin)

    line_merged = predictions.merge(
        matches[['match_id', 'total_corners']], on='match_id', how='left')
    line_merged = line_merged[line_merged['line_offered'] > 0]

    avg_line = round(line_merged['line_offered'].mean(), 1)
    avg_actual = round(line_merged['total_corners'].mean(), 1)
    diff = round(avg_actual - avg_line, 1)

    print(f"  Avg Bet365 line:       {avg_line}")
    print(f"  Avg actual corners:    {avg_actual}")
    print(f"  Difference:            {'+' if diff >= 0 else ''}{diff}")

    if diff > 0:
        print(f"  Market is UNDERPRICING corners by {diff} on average")
    elif diff < 0:
        print(f"  Market is OVERPRICING corners by {abs(diff)} on average")
    else:
        print(f"  Market is accurately pricing corners on average")

    # ── SECTION 7 — MODEL RECOMMENDATIONS ───────────
    print(f"\n  SECTION 7 — MODEL RECOMMENDATIONS")
    print(thin)

    # Skip lean analysis
    skips = predictions[predictions['bet_placed'].astype(str).str.upper() == 'FALSE'].copy()
    skips = skips.merge(
        matches[['match_id', 'total_corners']],
        on='match_id', how='left'
    )

    over_leans = skips[skips['skip_lean'] == 'over']
    under_leans = skips[skips['skip_lean'] == 'under']
    none_leans = skips[skips['skip_lean'] == 'none']

    print("\n  SKIP LEAN ANALYSIS")
    print(thin)

    if len(over_leans) > 0:
        avg_corners_over = round(over_leans['total_corners'].mean(), 1)
        avg_line_over = round(over_leans['line_offered'].mean(), 1)
        would_have_won = len(over_leans[
            over_leans['total_corners'] > over_leans['line_offered']])
        result = "WON" if would_have_won > (len(over_leans) - would_have_won) else "LOST"
        print(f"  Skipped Over leans:  {len(over_leans)} matches, "
              f"avg corners {avg_corners_over} — "
              f"would have {result} at avg line {avg_line_over}")
        for _, row in over_leans.iterrows():
            actual = row['total_corners']
            line = row['line_offered']
            verdict = "WON" if actual > line else "LOST"
            print(f"    {row['home_team']} vs {row['away_team']}: "
                  f"{int(actual)} corners vs line {line} -> {verdict}")
    else:
        print("  Skipped Over leans:  0 matches")

    print()

    if len(under_leans) > 0:
        avg_corners_under = round(under_leans['total_corners'].mean(), 1)
        avg_line_under = round(under_leans['line_offered'].mean(), 1)
        would_have_won = len(under_leans[
            under_leans['total_corners'] < under_leans['line_offered']])
        result = "WON" if would_have_won > (len(under_leans) - would_have_won) else "LOST"
        print(f"  Skipped Under leans: {len(under_leans)} matches, "
              f"avg corners {avg_corners_under} — "
              f"would have {result} at avg line {avg_line_under}")
        for _, row in under_leans.iterrows():
            actual = row['total_corners']
            line = row['line_offered']
            verdict = "WON" if actual < line else "LOST"
            print(f"    {row['home_team']} vs {row['away_team']}: "
                  f"{int(actual)} corners vs line {line} -> {verdict}")
    else:
        print("  Skipped Under leans: 0 matches")

    print()

    if len(none_leans) > 0:
        print(f"  Skipped No lean:     {len(none_leans)} matches")
    else:
        print("  Skipped No lean:     0 matches")

    total_leans = len(over_leans) + len(under_leans)
    if total_leans > 0:
        correct_over = len(over_leans[
            over_leans['total_corners'] > over_leans['line_offered']
        ]) if len(over_leans) > 0 else 0
        correct_under = len(under_leans[
            under_leans['total_corners'] < under_leans['line_offered']
        ]) if len(under_leans) > 0 else 0
        total_correct = correct_over + correct_under
        lean_accuracy = round((total_correct / total_leans) * 100, 1)
        print(f"\n  Skip lean accuracy:  {total_correct}/{total_leans} "
              f"directionally correct ({lean_accuracy}%)")
        if lean_accuracy >= 60:
            print("  -> We may be leaving money on the table by skipping "
                  "matches where we have a directional lean.")
        else:
            print("  -> Lean accuracy is low — skipping without clean edge "
                  "remains the right call.")

    # ── SECTION 8 — SHADOW PORTFOLIO AND STAKING ──────
    print(f"\n  SECTION 8A — SHADOW PORTFOLIO")
    print(thin)

    shadow = predictions[predictions['shadow_bet'].astype(str).str.upper() == 'TRUE'].copy()
    shadow = shadow.merge(
        matches[['match_id', 'total_corners']],
        on='match_id', how='left'
    )
    total_shadow = len(shadow)
    shadow_won = len(shadow[shadow['shadow_outcome'] == 'won'])
    shadow_lost = len(shadow[shadow['shadow_outcome'] == 'lost'])
    shadow_push = len(shadow[shadow['shadow_outcome'] == 'push'])
    shadow_wr = round((shadow_won / total_shadow) * 100, 1) if total_shadow > 0 else 0
    shadow_pl_flat = shadow_won - shadow_lost
    shadow_pl_conservative = round((shadow_won - shadow_lost) * 0.5, 1)

    print(f"  Total shadow bets tracked: {total_shadow}")
    print(f"  Shadow won: {shadow_won} | Shadow lost: {shadow_lost} "
          f"| Shadow win rate: {shadow_wr}%")
    print(f"  Shadow P&L (at 1 unit flat):          "
          f"{'+' if shadow_pl_flat >= 0 else ''}{shadow_pl_flat:.1f} units")
    print(f"  Shadow P&L (at 0.5 unit conservative): "
          f"{'+' if shadow_pl_conservative >= 0 else ''}{shadow_pl_conservative} units")

    print(f"\n  Directional breakdown:")
    for direction in ['over', 'under']:
        dir_shadow = shadow[shadow['skip_lean'] == direction]
        if len(dir_shadow) > 0:
            d_won = len(dir_shadow[dir_shadow['shadow_outcome'] == 'won'])
            d_wr = round((d_won / len(dir_shadow)) * 100, 1)
            d_avg_corners = round(dir_shadow['total_corners'].mean(), 1)
            d_avg_line = round(dir_shadow['line_offered'].mean(), 1)
            print(f"  Lean={direction:<6} {len(dir_shadow)} bets — "
                  f"{d_won} won — {d_wr}% — "
                  f"avg corners {d_avg_corners} vs avg line {d_avg_line}")

    print()
    if total_shadow >= 10:
        if shadow_wr >= 70:
            dominant_dir = 'over' if len(shadow[
                (shadow['skip_lean'] == 'over') &
                (shadow['shadow_outcome'] == 'won')
            ]) > len(shadow[
                (shadow['skip_lean'] == 'under') &
                (shadow['shadow_outcome'] == 'won')
            ]) else 'under'
            print(f"  Recommendation: Consider lowering skip threshold from "
                  f"1.5 to 1.2 for {dominant_dir} leans")
        elif shadow_wr < 60:
            print("  Recommendation: Current skip threshold is correct — "
                  "maintain 1.5 edge requirement")
    else:
        print(f"  Recommendation: Insufficient data ({total_shadow} shadow bets) "
              "— continue tracking before adjusting threshold")

    print(f"\n  SECTION 8B — TIERED STAKING ANALYSIS")
    print(thin)

    for tier_name, stake_size in [('tier_1', 2.0), ('tier_2', 1.0)]:
        tier_bets = merged_preds[merged_preds['tier'] == tier_name]
        if len(tier_bets) > 0:
            t_won = len(tier_bets[tier_bets['outcome_bet'] == 'won'])
            t_pl = round(tier_bets['profit_loss'].sum(), 3)
            t_staked = round(len(tier_bets) * stake_size, 2)
            t_roi = round((t_pl / t_staked) * 100, 1) if t_staked > 0 else 0
            print(f"  {tier_name} ({stake_size:.0f} units): "
                  f"{len(tier_bets)} bets — {t_won} won — "
                  f"P&L: {'+' if t_pl >= 0 else ''}{t_pl} units — "
                  f"ROI: {'+' if t_roi >= 0 else ''}{t_roi}%")

    total_weighted_staked = bets['stake'].sum()
    total_weighted_pl = round(bets['profit_loss'].sum(), 3)
    weighted_roi = round((total_weighted_pl / total_weighted_staked) * 100, 1) if total_weighted_staked > 0 else 0
    print(f"  Total weighted:   {total_weighted_staked:.2f} units staked — "
          f"P&L: {'+' if total_weighted_pl >= 0 else ''}{total_weighted_pl} units — "
          f"ROI: {'+' if weighted_roi >= 0 else ''}{weighted_roi}%")

    flat_pl = round(sum(
        (row['odds'] - 1) if row['outcome'] == 'won' else -1.0
        for _, row in bets.iterrows()
    ), 3)
    flat_staked = len(bets)
    flat_roi = round((flat_pl / flat_staked) * 100, 1) if flat_staked > 0 else 0

    print(f"\n  vs Flat staking comparison:")
    print(f"  Flat (1 unit each): P&L would be "
          f"{'+' if flat_pl >= 0 else ''}{flat_pl} units")
    print(f"  Tiered staking:     P&L is "
          f"{'+' if total_weighted_pl >= 0 else ''}{total_weighted_pl} units")
    diff_pl = round(total_weighted_pl - flat_pl, 3)
    print(f"  Difference:         "
          f"{'+' if diff_pl >= 0 else ''}{diff_pl} units "
          f"{'gained' if diff_pl >= 0 else 'lost'} from tiered staking")

    t1_bets = merged_preds[merged_preds['tier'] == 'tier_1']
    t2_bets = merged_preds[merged_preds['tier'] == 'tier_2']
    t1_wr_val = (len(t1_bets[t1_bets['outcome_bet'] == 'won']) / len(t1_bets) * 100) if len(t1_bets) > 0 else 0
    t2_wr_val = (len(t2_bets[t2_bets['outcome_bet'] == 'won']) / len(t2_bets) * 100) if len(t2_bets) > 0 else 0

    print()
    if t1_wr_val > t2_wr_val:
        print("  Recommendation: Tiered staking is correct — "
              "keep 2 unit Tier 1 stake")
    elif t1_wr_val < t2_wr_val and len(t1_bets) > 0:
        print("  Recommendation: Review Tier 1 classification criteria")
    else:
        print("  Recommendation: Insufficient tier comparison data")

    # Actionable recommendations
    print(f"\n  ACTIONABLE RECOMMENDATIONS")
    print(thin)

    if total_matches < 10:
        print(f"  ⚠️  SAMPLE SIZE WARNING: Only {total_matches} matches logged.")
        print("     All recommendations are provisional — revisit after 10+ matches.")
        print()

    # Tier threshold recommendation
    tier1_preds = merged_preds[merged_preds['tier'] == 'tier_1']
    tier2_preds = merged_preds[merged_preds['tier'] == 'tier_2']
    if len(tier1_preds) > 0:
        t1_wr = round((len(tier1_preds[tier1_preds['outcome_bet'] == 'won']) /
                       len(tier1_preds)) * 100, 1)
        if t1_wr >= 75:
            print(f"  1. Tier 1 win rate {t1_wr}% — threshold is working, keep current rules")
        else:
            print(f"  1. Tier 1 win rate {t1_wr}% — consider raising threshold")

    if len(tier2_preds) > 0:
        t2_wr = round((len(tier2_preds[tier2_preds['outcome_bet'] == 'won']) /
                       len(tier2_preds)) * 100, 1)
        if t2_wr >= 50:
            print(f"  2. Tier 2 win rate {t2_wr}% — profitable, keep betting selectively")
        else:
            print(f"  2. Tier 2 win rate {t2_wr}% — consider tightening tier 2 criteria")

    # Market recommendation
    if len(market_stats) > 0:
        best_mkt = market_stats.loc[market_stats['pl'].idxmax()]
        worst_mkt = market_stats.loc[market_stats['pl'].idxmin()]
        if worst_mkt['pl'] < 0:
            print(f"  3. Avoid {worst_mkt['market']} — negative P&L "
                  f"({worst_mkt['pl']})")
        print(f"  4. Prioritise {best_mkt['market']} — best performing "
              f"({'+' if best_mkt['pl'] >= 0 else ''}{best_mkt['pl']})")

    # Attack type recommendation
    if len(combo_stats) > 0:
        top_combo = combo_stats.iloc[0]
        print(f"  5. Most reliable combo: {top_combo['combo']} "
              f"(avg {top_combo['avg_corners']} corners)")

    print(f"\n{divider}\n")


if __name__ == '__main__':
    analyse_model()
