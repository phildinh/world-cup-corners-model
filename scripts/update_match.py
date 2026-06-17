import pandas as pd
from datetime import date
import argparse
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    return pd.read_csv(path)

def save_csv(df, filename):
    path = os.path.join(DATA_DIR, filename)
    df.to_csv(path, index=False)
    print(f"✅ {filename} updated")

def next_id(df, id_col):
    return str(df[id_col].max() + 1).zfill(3)

def update_match(home, away, home_score, away_score,
                 total_corners, home_corners, away_corners,
                 group, game_state, notes,
                 market=None, selection=None, odds=None,
                 stake=None, bet_outcome=None,
                 tier=None, confidence=None, line=None,
                 home_avg=None, away_avg=None,
                 lesson=None, lesson_category=None, rule=None):

    today = date.today().isoformat()

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
        'notes': notes
    }
    matches = pd.concat([matches, pd.DataFrame([new_match])], ignore_index=True)
    save_csv(matches, 'matches.csv')

    # --- teams.csv --- update rolling averages
    teams = load_csv('teams.csv')

    for team, corners_taken, corners_conceded in [
        (home, home_corners, away_corners),
        (away, away_corners, home_corners)
    ]:
        if team in teams['team_name'].values:
            idx = teams[teams['team_name'] == team].index[0]
            played = teams.at[idx, 'matches_played']
            old_taken = teams.at[idx, 'avg_corners_taken']
            old_conceded = teams.at[idx, 'avg_corners_conceded']
            # Rolling average recalculation
            teams.at[idx, 'avg_corners_taken'] = round(
                ((old_taken * played) + corners_taken) / (played + 1), 2)
            teams.at[idx, 'avg_corners_conceded'] = round(
                ((old_conceded * played) + corners_conceded) / (played + 1), 2)
            teams.at[idx, 'matches_played'] = played + 1
            teams.at[idx, 'last_updated'] = today

    save_csv(teams, 'teams.csv')

    # --- bets.csv --- only if bet was placed
    if market and selection and odds and stake and bet_outcome:
        bets = load_csv('bets.csv')
        bet_id = next_id(bets, 'bet_id')
        profit_loss = round(
            (float(odds) - 1) * float(stake) if bet_outcome == 'won'
            else -float(stake), 3
        )
        new_bet = {
            'bet_id': bet_id,
            'match_id': match_id,
            'date': today,
            'home_team': home,
            'away_team': away,
            'market': market,
            'selection': selection,
            'odds': odds,
            'stake': stake,
            'outcome': bet_outcome,
            'profit_loss': profit_loss,
            'notes': notes
        }
        bets = pd.concat([bets, pd.DataFrame([new_bet])], ignore_index=True)
        save_csv(bets, 'bets.csv')

    # --- predictions.csv ---
    if tier:
        predictions = load_csv('predictions.csv')
        pred_id = next_id(predictions, 'prediction_id')
        combined_baseline = round(
            float(home_avg or 0) + float(away_avg or 0), 2)
        bet_placed = True if market else False
        new_pred = {
            'prediction_id': pred_id,
            'match_id': match_id,
            'date': today,
            'home_team': home,
            'away_team': away,
            'home_avg_corners': home_avg,
            'away_avg_corners': away_avg,
            'combined_baseline': combined_baseline,
            'tier': tier,
            'recommended_market': market or 'skip',
            'recommended_direction': selection or 'skip',
            'confidence': confidence or 'skip',
            'line_offered': line or 0,
            'bet_placed': bet_placed,
            'outcome': bet_outcome or 'skip',
            'notes': notes
        }
        predictions = pd.concat(
            [predictions, pd.DataFrame([new_pred])], ignore_index=True)
        save_csv(predictions, 'predictions.csv')

    # --- lessons.csv ---
    if lesson and lesson_category:
        lessons = load_csv('lessons.csv')
        lesson_id = next_id(lessons, 'lesson_id')
        new_lesson = {
            'lesson_id': lesson_id,
            'match_id': match_id,
            'date': today,
            'category': lesson_category,
            'lesson': lesson,
            'rule_added': rule or '',
            'model_version': 'v3.0'
        }
        lessons = pd.concat(
            [lessons, pd.DataFrame([new_lesson])], ignore_index=True)
        save_csv(lessons, 'lessons.csv')

    print(f"\n✅ All data updated for {home} vs {away}")
    print(f"   Match ID: {match_id}")
    print(f"   Score: {home_score}-{away_score}")
    print(f"   Corners: {total_corners} ({home_corners} / {away_corners})")


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
    args = parser.parse_args()

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
        rule=args.rule
    )