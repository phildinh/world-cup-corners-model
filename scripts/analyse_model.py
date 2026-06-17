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

    divider = "=" * 60
    thin = "-" * 60

    print(f"\n{divider}")
    print("  WORLD CUP 2026 — MODEL ANALYSIS")
    print(divider)

    # ── SECTION 7 — MODEL RECOMMENDATIONS ────────────
    print("\n  SECTION 7 — MODEL RECOMMENDATIONS")
    print(thin)

    # Skip lean analysis
    skips = predictions[predictions['bet_placed'] == False].copy()
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
        would_have_won = len(over_leans[over_leans['total_corners'] > over_leans['line_offered']])
        would_have_lost = len(over_leans) - would_have_won
        result = "WON" if would_have_won > would_have_lost else "LOST"
        print(f"  Skipped Over leans:  {len(over_leans)} matches, "
              f"avg corners {avg_corners_over} — "
              f"would have {result} at avg line {avg_line_over}")
        for _, row in over_leans.iterrows():
            actual = row['total_corners']
            line = row['line_offered']
            verdict = "WON" if actual > line else "LOST"
            print(f"    {row['home_team']} vs {row['away_team']}: "
                  f"{int(actual)} corners vs line {line} → {verdict}")
    else:
        print("  Skipped Over leans:  0 matches")

    print()

    if len(under_leans) > 0:
        avg_corners_under = round(under_leans['total_corners'].mean(), 1)
        avg_line_under = round(under_leans['line_offered'].mean(), 1)
        would_have_won = len(under_leans[under_leans['total_corners'] < under_leans['line_offered']])
        would_have_lost = len(under_leans) - would_have_won
        result = "WON" if would_have_won > would_have_lost else "LOST"
        print(f"  Skipped Under leans: {len(under_leans)} matches, "
              f"avg corners {avg_corners_under} — "
              f"would have {result} at avg line {avg_line_under}")
        for _, row in under_leans.iterrows():
            actual = row['total_corners']
            line = row['line_offered']
            verdict = "WON" if actual < line else "LOST"
            print(f"    {row['home_team']} vs {row['away_team']}: "
                  f"{int(actual)} corners vs line {line} → {verdict}")
    else:
        print("  Skipped Under leans: 0 matches")

    print()

    if len(none_leans) > 0:
        print(f"  Skipped No lean:     {len(none_leans)} matches")
    else:
        print("  Skipped No lean:     0 matches")

    # Summary
    total_leans = len(over_leans) + len(under_leans)
    if total_leans > 0:
        correct_over = len(over_leans[over_leans['total_corners'] > over_leans['line_offered']]) if len(over_leans) > 0 else 0
        correct_under = len(under_leans[under_leans['total_corners'] < under_leans['line_offered']]) if len(under_leans) > 0 else 0
        total_correct = correct_over + correct_under
        lean_accuracy = round((total_correct / total_leans) * 100, 1)
        print(f"\n  Skip lean accuracy:  {total_correct}/{total_leans} "
              f"directionally correct ({lean_accuracy}%)")
        if lean_accuracy >= 60:
            print("  → We may be leaving money on the table by skipping "
                  "matches where we have a directional lean.")
        else:
            print("  → Lean accuracy is low — skipping without clean edge "
                  "remains the right call.")

    print(f"\n{divider}\n")


if __name__ == '__main__':
    analyse_model()
