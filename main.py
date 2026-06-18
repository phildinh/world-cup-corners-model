import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from baseline_calculator import calculate_baseline
from model_stats import model_stats
from update_match import update_match
from briefing import generate_briefing
from analyse_model import analyse_model
from log_version import log_version

def main():
    parser = argparse.ArgumentParser(
        description='World Cup 2026 — Corners Betting Model',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('command', choices=[
        'update', 'stats', 'baseline', 'report', 'briefing',
        'analyse', 'log-version'
    ], help='''
Commands:
  update      → Log match result and update all CSVs
  stats       → Show full model stats and P&L
  baseline    → Calculate corners baseline for a matchup
  report      → Generate full model report
  analyse     → Run full model analysis
  log-version → Log model version change
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
    parser.add_argument('--match-notes', default='',
                        help='Post-match research findings')

    # ── BET ARGS ─────────────────────────────────────
    parser.add_argument('--market', default=None,
                        help='total_over / total_under / ah_corners / 1h_over / 1h_under')
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

    # ── V4.0 FLAGS ───────────────────────────────────
    parser.add_argument('--data-confidence', default='high',
                        help='Data source confidence: high / medium / low')
    parser.add_argument('--counter-threat', default='auto',
                        help='Counter-threat present: yes / no / auto')
    parser.add_argument('--counter-scorer', action='store_true',
                        help='Opponent scored on counter in last 3 matches')
    parser.add_argument('--transition-xg', type=float, default=None,
                        help='Opponent xG in transition per game')
    parser.add_argument('--altitude', default='no',
                        help='Altitude venue: yes / no')
    parser.add_argument('--venue', default=None,
                        help='Stadium name — auto-detects altitude')
    parser.add_argument('--debut-opponent', action='store_true',
                        help='Opponent at first World Cup')
    parser.add_argument('--match-type', default=None,
                        help='wide_vs_deep / wide_vs_counter / central_vs_deep / '
                             'direct_vs_direct / wide_vs_open / mixed')

    # ── LESSON ARGS ──────────────────────────────────
    parser.add_argument('--lesson', default=None,
                        help='Lesson learned from match')
    parser.add_argument('--lesson-category', default=None,
                        help='baseline_accuracy / market_selection / '
                             'style_classification / game_state / skip_accuracy')
    parser.add_argument('--rule', default=None,
                        help='New rule added to model')

    # ── LOG-VERSION ARGS ─────────────────────────────
    parser.add_argument('--version', default=None,
                        help='Model version e.g. v3.1')
    parser.add_argument('--change', default=None,
                        help='What rule changed')
    parser.add_argument('--trigger', default=None,
                        help='Why the change was made')

    args = parser.parse_args()

    # ── COMMAND ROUTER ───────────────────────────────
    if args.command == 'stats':
        model_stats()

    elif args.command == 'baseline':
        if not args.home or not args.away:
            print("baseline requires --home and --away")
            print("   Example: python main.py baseline "
                  "--home France --away Morocco --line 9.5")
            sys.exit(1)
        calculate_baseline(args.home, args.away, args.line)

    elif args.command == 'update':
        required = ['home', 'away', 'home_score', 'away_score',
                    'total_corners', 'home_corners', 'away_corners', 'group']
        missing = [r for r in required if getattr(args, r, None) is None]
        if missing:
            print(f"update missing required args: {', '.join(missing)}")
            sys.exit(1)

        update_match(
            home=args.home, away=args.away,
            home_score=args.home_score, away_score=args.away_score,
            total_corners=args.total_corners,
            home_corners=args.home_corners, away_corners=args.away_corners,
            group=args.group, game_state=args.game_state, notes=args.notes,
            market=args.market, selection=args.selection,
            odds=args.odds, stake=args.stake, bet_outcome=args.bet_outcome,
            tier=args.tier, confidence=args.confidence, line=args.line,
            home_avg=args.home_avg, away_avg=args.away_avg,
            lesson=args.lesson, lesson_category=args.lesson_category,
            rule=args.rule, skip_lean=args.skip_lean,
            data_confidence=args.data_confidence,
            counter_threat=args.counter_threat,
            counter_scorer=args.counter_scorer,
            transition_xg=args.transition_xg,
            altitude=args.altitude, venue=args.venue,
            debut_opponent=args.debut_opponent,
            match_type=args.match_type,
            match_notes=args.match_notes
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

    elif args.command == 'log-version':
        if not args.version or not args.change or not args.trigger:
            print("log-version requires --version, --change, --trigger")
            sys.exit(1)
        log_version(args.version, args.change, args.trigger)

if __name__ == '__main__':
    main()
