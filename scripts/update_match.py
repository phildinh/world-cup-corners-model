import pandas as pd
from datetime import date
import argparse
import os
import subprocess

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

ALTITUDE_VENUES = {
    'estadio azteca': 2250,
    'azteca': 2250,
}

ODDS_FLOORS = {
    ('tier_1', 'total_over'): 1.750,
    ('tier_1', 'total_under'): 1.750,
    ('tier_2', 'total_over'): 1.850,
    ('tier_2', 'total_under'): 1.850,
    ('tier_1', 'ah_corners'): 1.900,
    ('tier_2', 'ah_corners'): 1.900,
    ('tier_1', '1h_over'): 1.800,
    ('tier_2', '1h_over'): 1.800,
    ('tier_1', '1h_under'): 1.800,
    ('tier_2', '1h_under'): 1.800,
}

def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    return pd.read_csv(path)

ID_COLUMNS = {
    'matches.csv': 'match_id',
    'bets.csv': ['bet_id', 'match_id'],
    'predictions.csv': ['prediction_id', 'match_id'],
    'lessons.csv': ['lesson_id', 'match_id'],
    'model_versions.csv': None,
}

def save_csv(df, filename):
    path = os.path.join(DATA_DIR, filename)
    id_cols = ID_COLUMNS.get(filename)
    if id_cols:
        if isinstance(id_cols, str):
            id_cols = [id_cols]
        for col in id_cols:
            if col in df.columns:
                df[col] = df[col].astype(int).astype(str).str.zfill(3)
    df.to_csv(path, index=False)
    print(f"  {filename} updated")

def next_id(df, id_col):
    return str(df[id_col].max() + 1).zfill(3)

def detect_altitude(venue):
    if not venue:
        return False
    for name in ALTITUDE_VENUES:
        if name in venue.lower():
            return True
    return False

def derive_counter_threat(away_team, teams, counter_threat_flag, counter_scorer):
    if counter_threat_flag == 'yes':
        return 'yes'
    if counter_threat_flag == 'no':
        return 'no'
    if counter_scorer:
        return 'yes'
    if away_team in teams['team_name'].values:
        away_row = teams[teams['team_name'] == away_team].iloc[0]
        if away_row['attack_type'] == 'counter_attacking':
            return 'yes'
    return 'no'

def derive_match_type(home_team, away_team, teams, match_type_flag):
    if match_type_flag:
        return match_type_flag
    home_in = home_team in teams['team_name'].values
    away_in = away_team in teams['team_name'].values
    if not home_in or not away_in:
        return 'mixed'
    home = teams[teams['team_name'] == home_team].iloc[0]
    away = teams[teams['team_name'] == away_team].iloc[0]
    h_atk, a_atk = home['attack_type'], away['attack_type']
    a_def, h_def = away['defensive_type'], home['defensive_type']

    if h_atk == 'direct_physical' and a_atk == 'direct_physical':
        return 'direct_vs_direct'

    rank = {'wide_possession': 5, 'central_possession': 3,
            'set_piece_specialist': 2, 'counter_attacking': 1,
            'direct_physical': 1}
    if rank.get(h_atk, 0) >= rank.get(a_atk, 0):
        dom_atk, opp_def, opp_atk = h_atk, a_def, a_atk
    else:
        dom_atk, opp_def, opp_atk = a_atk, h_def, h_atk

    if dom_atk == 'wide_possession' and opp_def == 'pure_deep_block':
        return 'wide_vs_deep'
    if dom_atk == 'wide_possession' and opp_atk == 'counter_attacking':
        return 'wide_vs_counter'
    if dom_atk == 'wide_possession' and opp_def == 'open_attack_minded':
        return 'wide_vs_open'
    if dom_atk == 'central_possession' and opp_def == 'pure_deep_block':
        return 'central_vs_deep'
    return 'mixed'

def check_odds_floor(tier, market, odds):
    if not tier or not market or not odds:
        return
    floor = ODDS_FLOORS.get((tier, market))
    if not floor and 'under' in (market or ''):
        floor = 1.850
    if floor and odds < floor:
        print(f"  ODDS BELOW FLOOR — minimum for {tier} {market} is {floor}. "
              f"Consider skipping or reducing stake.")

def calculate_confidence_score(baseline, line, data_confidence,
                               home_attack_type, counter_threat,
                               tier, odds=None):
    score = 50
    edge = abs(baseline - line) if line else 0
    if edge >= 1.5:
        score += 20
    elif edge >= 1.0:
        score += 10
    elif edge >= 0.5:
        pass
    else:
        score -= 10

    if data_confidence == 'high':
        score += 10
    elif data_confidence == 'low':
        score -= 15

    if home_attack_type == 'wide_possession':
        score += 15
    elif home_attack_type in ('central_possession', 'set_piece_specialist'):
        score += 5
    elif home_attack_type in ('direct_physical', 'counter_attacking'):
        score -= 5

    if counter_threat == 'yes':
        score -= 15

    if tier == 'tier_1':
        score += 10
    elif tier == 'tier_2':
        score += 5
    elif tier == 'tier_3':
        score -= 10

    if odds:
        if odds >= 1.950:
            score += 5
        elif odds >= 1.850:
            pass
        else:
            score -= 5

    return max(0, min(100, score))

def apply_counter_threat_rules(ct, dc, market, edge, tier):
    effective_tier = tier
    if ct != 'yes':
        return effective_tier

    if market == 'ah_corners':
        print("  AH CORNERS FORBIDDEN — counter-threat present")
        return effective_tier

    if dc == 'low':
        print("  SKIP SIGNAL — counter-threat + low confidence")
        if effective_tier == 'tier_1':
            effective_tier = 'tier_2'
        elif effective_tier == 'tier_2':
            effective_tier = 'tier_3'
    else:
        if edge < 1.0:
            print(f"  COUNTER-THREAT WARNING — edge {edge:.1f} < 1.0, tier demoted")
            if effective_tier == 'tier_1':
                effective_tier = 'tier_2'
            elif effective_tier == 'tier_2':
                effective_tier = 'tier_3'
        else:
            print(f"  COUNTER-THREAT WARNING — edge {edge:.1f} >= 1.0, tier maintained")

    return effective_tier


def update_match(home, away, home_score, away_score,
                 total_corners, home_corners, away_corners,
                 group, game_state, notes,
                 market=None, selection=None, odds=None,
                 stake=None, bet_outcome=None,
                 tier=None, confidence=None, line=None,
                 home_avg=None, away_avg=None,
                 lesson=None, lesson_category=None, rule=None,
                 skip_lean=None, data_confidence=None,
                 counter_threat=None, counter_scorer=False,
                 transition_xg=None, altitude=None, venue=None,
                 debut_opponent=False, match_type=None,
                 match_notes=None):

    today = date.today().isoformat()
    teams = load_csv('teams.csv')

    if altitude is None or altitude == 'no':
        altitude_active = detect_altitude(venue) if venue else False
    else:
        altitude_active = (altitude == 'yes')

    ct = derive_counter_threat(
        away, teams, counter_threat or 'auto', counter_scorer)
    if transition_xg and float(transition_xg) > 0.3:
        ct = 'yes'

    mt = derive_match_type(home, away, teams, match_type)
    dc = data_confidence or 'high'

    effective_away_avg = away_avg
    if debut_opponent and away_avg:
        effective_away_avg = round(float(away_avg) * 0.9, 2)
        print(f"  DEBUT OPPONENT — {away} corners taken adjusted "
              f"{away_avg} -> {effective_away_avg} (-10%)")

    altitude_adjustment = 0
    if altitude_active:
        altitude_adjustment = -1.0
        print(f"  ALTITUDE VENUE — baseline adjusted -1.0")

    if market and odds and tier:
        check_odds_floor(tier, market, odds)

    # --- matches.csv ---
    matches = load_csv('matches.csv')
    match_id = next_id(matches, 'match_id')
    new_match = {
        'match_id': match_id,
        'date': today,
        'group': group,
        'home_team': home,
        'away_team': away,
        'home_score': home_score,
        'away_score': away_score,
        'total_corners': total_corners,
        'home_corners': home_corners,
        'away_corners': away_corners,
        'game_state': game_state,
        'match_type': mt,
        'notes': notes,
        'match_notes': match_notes or ''
    }
    matches = pd.concat([matches, pd.DataFrame([new_match])], ignore_index=True)
    save_csv(matches, 'matches.csv')

    # --- teams.csv ---
    for team, corners_taken, corners_conceded in [
        (home, home_corners, away_corners),
        (away, away_corners, home_corners)
    ]:
        if team in teams['team_name'].values:
            idx = teams[teams['team_name'] == team].index[0]
            played = teams.at[idx, 'matches_played']
            old_taken = teams.at[idx, 'avg_corners_taken']
            old_conceded = teams.at[idx, 'avg_corners_conceded']
            teams.at[idx, 'avg_corners_taken'] = round(
                ((old_taken * played) + corners_taken) / (played + 1), 2)
            teams.at[idx, 'avg_corners_conceded'] = round(
                ((old_conceded * played) + corners_conceded) / (played + 1), 2)
            teams.at[idx, 'matches_played'] = played + 1
            teams.at[idx, 'last_updated'] = today
    save_csv(teams, 'teams.csv')

    # --- bets.csv ---
    if market and selection and odds and stake and bet_outcome:
        bets = load_csv('bets.csv')
        bet_id = next_id(bets, 'bet_id')
        profit_loss = round(
            (float(odds) - 1) * float(stake) if bet_outcome == 'won'
            else -float(stake), 3
        )
        new_bet = {
            'bet_id': bet_id, 'match_id': match_id, 'date': today,
            'home_team': home, 'away_team': away, 'market': market,
            'selection': selection, 'odds': odds, 'stake': stake,
            'outcome': bet_outcome, 'profit_loss': profit_loss,
            'notes': notes
        }
        bets = pd.concat([bets, pd.DataFrame([new_bet])], ignore_index=True)
        save_csv(bets, 'bets.csv')

    # --- predictions.csv ---
    if tier:
        predictions = load_csv('predictions.csv')
        pred_id = next_id(predictions, 'prediction_id')
        combined_baseline = round(
            float(home_avg or 0) + float(effective_away_avg or away_avg or 0), 2)
        combined_baseline = round(combined_baseline + altitude_adjustment, 2)

        # Data confidence tier demotion
        effective_tier = tier
        if dc == 'low':
            if tier == 'tier_1':
                effective_tier = 'tier_2'
                print(f"  LOW DATA CONFIDENCE — tier demoted: tier_1 -> tier_2")
            elif tier == 'tier_2':
                effective_tier = 'tier_3'
                print(f"  LOW DATA CONFIDENCE — tier demoted: tier_2 -> tier_3 (skip)")

        # v4.1 refined counter-threat rules
        edge = abs(combined_baseline - (line or 0))
        effective_tier = apply_counter_threat_rules(
            ct, dc, market, edge, effective_tier)

        bet_placed = True if market else False
        lean = skip_lean if not market else ''
        shadow_bet = (not market) and lean in ('over', 'under')
        shadow_outcome = ''
        if shadow_bet and line and total_corners is not None:
            if lean == 'over':
                if total_corners > line:
                    shadow_outcome = 'won'
                elif total_corners < line:
                    shadow_outcome = 'lost'
                else:
                    shadow_outcome = 'push'
            elif lean == 'under':
                if total_corners < line:
                    shadow_outcome = 'won'
                elif total_corners > line:
                    shadow_outcome = 'lost'
                else:
                    shadow_outcome = 'push'

        home_atk = ''
        if home in teams['team_name'].values:
            home_atk = teams[teams['team_name'] == home].iloc[0]['attack_type']

        conf_score = calculate_confidence_score(
            combined_baseline, line or 0, dc, home_atk, ct,
            effective_tier, odds)

        new_pred = {
            'prediction_id': pred_id, 'match_id': match_id, 'date': today,
            'home_team': home, 'away_team': away,
            'home_avg_corners': home_avg, 'away_avg_corners': away_avg,
            'combined_baseline': combined_baseline,
            'original_tier': tier,
            'tier': effective_tier,
            'recommended_market': market or 'skip',
            'recommended_direction': selection or 'skip',
            'confidence': confidence or 'skip',
            'line_offered': line or 0,
            'bet_placed': bet_placed, 'skip_lean': lean,
            'shadow_bet': shadow_bet, 'shadow_outcome': shadow_outcome,
            'data_confidence': dc, 'counter_threat': ct,
            'match_type': mt, 'confidence_score': conf_score,
            'outcome': bet_outcome or 'skip', 'notes': notes
        }
        predictions = pd.concat(
            [predictions, pd.DataFrame([new_pred])], ignore_index=True)
        save_csv(predictions, 'predictions.csv')

    # --- lessons.csv ---
    if lesson and lesson_category:
        lessons = load_csv('lessons.csv')
        lesson_id = next_id(lessons, 'lesson_id')
        new_lesson = {
            'lesson_id': lesson_id, 'match_id': match_id, 'date': today,
            'category': lesson_category, 'lesson': lesson,
            'rule_added': rule or '', 'model_version': 'v4.1'
        }
        lessons = pd.concat(
            [lessons, pd.DataFrame([new_lesson])], ignore_index=True)
        save_csv(lessons, 'lessons.csv')

    print(f"\n  All data updated for {home} vs {away}")
    print(f"   Match ID: {match_id}")
    print(f"   Score: {home_score}-{away_score}")
    print(f"   Corners: {total_corners} ({home_corners} / {away_corners})")
    print(f"   Match type: {mt} | Data confidence: {dc} | Counter-threat: {ct}")
    if altitude_active:
        print(f"   Altitude: YES (baseline -1.0)")
    if debut_opponent:
        print(f"   Debut opponent: YES (away corners -10%)")
    if match_notes:
        print(f"   Research notes: {match_notes}")

    git_commit(home, away, total_corners)


def git_commit(home, away, total_corners):
    try:
        repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        subprocess.run(['git', 'add', 'data/'],
                       check=True, cwd=repo_dir)
        subprocess.run(['git', 'commit', '-m',
                        f'data: {home} vs {away} — {total_corners} corners'],
                       check=True, cwd=repo_dir)
        subprocess.run(['git', 'push'],
                       check=True, cwd=repo_dir)
        print(f"\n  Git committed and pushed successfully")
    except subprocess.CalledProcessError as e:
        print(f"\n  Git operation failed — push manually: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Update match result across all CSVs')
    parser.add_argument('--home', required=True)
    parser.add_argument('--away', required=True)
    parser.add_argument('--home-score', type=int, required=True)
    parser.add_argument('--away-score', type=int, required=True)
    parser.add_argument('--total-corners', type=int, required=True)
    parser.add_argument('--home-corners', type=int, required=True)
    parser.add_argument('--away-corners', type=int, required=True)
    parser.add_argument('--group', required=True)
    parser.add_argument('--game-state', default='normal')
    parser.add_argument('--notes', default='')
    parser.add_argument('--match-notes', default='',
        help='Post-match research findings')
    parser.add_argument('--market', default=None)
    parser.add_argument('--selection', default=None)
    parser.add_argument('--odds', type=float, default=None)
    parser.add_argument('--stake', type=float, default=None)
    parser.add_argument('--bet-outcome', default=None)
    parser.add_argument('--tier', default=None)
    parser.add_argument('--confidence', default=None)
    parser.add_argument('--line', type=float, default=None)
    parser.add_argument('--home-avg', type=float, default=None)
    parser.add_argument('--away-avg', type=float, default=None)
    parser.add_argument('--lesson', default=None)
    parser.add_argument('--lesson-category', default=None)
    parser.add_argument('--rule', default=None)
    parser.add_argument('--skip-lean', default='',
        help='Direction leaning when skipping: over / under / none')
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
        help='Match type override')
    args = parser.parse_args()

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
