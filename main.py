import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from baseline_calculator import calculate_baseline
from model_stats import model_stats
from update_match import update_match
from briefing import generate_briefing
from analyse_model import analyse_model

def main():
    parser = argparse.ArgumentParser(
        description='World Cup 2026 — Corners Betting Model',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('command', choices=[
        'update', 'stats', 'baseline', 'report', 'briefing', 'analyse'
    ], help='''
Commands:
  update    → Log match result and update all CSVs
  stats     → Show full model stats and P&L
  baseline  → Calculate corners baseline for a matchup
  report    → Generate full model report
  analyse   → Run full model analysis
    ''')

    # ── BASELINE ARGS ────────────────────────────────
    parser.add_argument('--home', help='Home team name')
    parser.add_argument('--away', help='Away team name')
    parser.add_argument('--line', type=float,
                        help='Bet365 corners line')

    # ── UPDATE ARGS ──────────────────────────────────
    parser.add_argument('--home-score', type=int,
                        help='Home team score')
    parser.add_argument('--away-score', type=int,
                        help='Away team score')
    parser.add_argument('--total-corners', type=int,
                        help='Total corners in match')
    parser.add_argument('--home-corners', type=int,
                        help='Home team corners')
    parser.add_argument('--away-corners', type=int,
                        help='Away team corners')
    parser.add_argument('--group',
                        help='World Cup group — e.g. A, B, I')
    parser.add_argument('--game-state', default='normal',
                        help='normal / underdog_scored_early / blowout')
    parser.add_argument('--notes', default='',
                        help='Match notes')

    # ── BET ARGS ─────────────────────────────────────
    parser.add_argument('--market', default=None,
                        help='total_over / total_under / ah_corners / 1h_over')
    parser.add_argument('--selection', default=None,
                        help='e.g. Over 9.5 / Belgium -3.0')
    parser.add_argument('--odds', type=float, default=None,
                        help='Decimal odds — e.g. 1.850')
    parser.add_argument('--stake', type=float, default=None,
                        help='Unit stake — e.g. 1.00')
    parser.add_argument('--bet-outcome', default=None,
                        help='won / lost / void')

    # ── PREDICTION ARGS ──────────────────────────────
    parser.add_argument('--tier', default=None,
                        help='tier_1 / tier_2 / tier_3')
    parser.add_argument('--confidence', default=None,
                        help='high / medium / low / skip')
    parser.add_argument('--home-avg', type=float, default=None,
                        help='Home team avg corners taken')
    parser.add_argument('--away-avg', type=float, default=None,
                        help='Away team avg corners taken')

    # ── SKIP LEAN ARG ────────────────────────────────
    parser.add_argument('--skip-lean', default='',
                        help='Direction leaning when skipping: over / under / none')

    # ── LESSON ARGS ──────────────────────────────────
    parser.add_argument('--lesson', default=None,
                        help='Lesson learned from match')
    parser.add_argument('--lesson-category', default=None,
                        help='baseline_accuracy / market_selection / '
                             'style_classification / game_state / skip_accuracy')
    parser.add_argument('--rule', default=None,
                        help='New rule added to model')

    args = parser.parse_args()

    # ── COMMAND ROUTER ───────────────────────────────
    if args.command == 'stats':
        model_stats()

    elif args.command == 'baseline':
        if not args.home or not args.away:
            print("❌ baseline requires --home and --away")
            print("   Example: python main.py baseline "
                  "--home France --away Morocco --line 9.5")
            sys.exit(1)
        calculate_baseline(args.home, args.away, args.line)

    elif args.command == 'update':
        required = ['home', 'away', 'home_score', 'away_score',
                    'total_corners', 'home_corners', 'away_corners', 'group']
        missing = [r for r in required if getattr(args, r, None) is None]
        if missing:
            print(f"❌ update missing required args: {', '.join(missing)}")
            print("\n  Minimum example:")
            print("  python main.py update \\")
            print("    --home France --away Morocco \\")
            print("    --home-score 2 --away-score 0 \\")
            print("    --total-corners 11 --home-corners 8 "
                  "--away-corners 3 \\")
            print("    --group I --game-state normal \\")
            print("    --notes 'France dominant Mbappe scored'")
            sys.exit(1)

        update_match(
            home=args.home,
            away=args.away,
            home_score=args.home_score,
            away_score=args.away_score,
            total_corners=args.total_corners,
            home_corners=args.home_corners,
            away_corners=args.away_corners,
            group=args.group,
            game_state=args.game_state,
            notes=args.notes,
            market=args.market,
            selection=args.selection,
            odds=args.odds,
            stake=args.stake,
            bet_outcome=args.bet_outcome,
            tier=args.tier,
            confidence=args.confidence,
            line=args.line,
            home_avg=args.home_avg,
            away_avg=args.away_avg,
            lesson=args.lesson,
            lesson_category=args.lesson_category,
            rule=args.rule,
            skip_lean=args.skip_lean
        )

    elif args.command == 'report':
        print("\n")
        print("=" * 50)
        print("  WORLD CUP 2026 — FULL MODEL REPORT")
        print("=" * 50)
        model_stats()
        print("\n  See MODEL.md for full framework and rules.")
        print("  See data/lessons.csv for full lessons log.")
        print("=" * 50 + "\n")

    elif args.command == 'briefing':
        generate_briefing()

    elif args.command == 'analyse':
        analyse_model()

if __name__ == '__main__':
    main()