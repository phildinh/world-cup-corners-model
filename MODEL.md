# World Cup 2026 — Corners Betting Model v3.0

## Overview
A data-driven corners prediction model for FIFA World Cup 2026.
Built and validated across live matches — updated after every game.

Last updated: June 17, 2026
Current record: 2W 1L | Correct skips: 3/4

---

## STEP 1 — DATA COLLECTION

For every match collect before analysis:

| Data Point | Source |
|---|---|
| Team A avg corners taken (last 6 matches) | Sofascore / web search |
| Team A avg corners conceded (last 6 matches) | Sofascore / web search |
| Team B avg corners taken (last 6 matches) | Sofascore / web search |
| Team B avg corners conceded (last 6 matches) | Sofascore / web search |
| Combined baseline | Team A taken + Team B taken |
| Line comparison | Combined baseline vs Bet365 line |

**Edge exists when baseline differs from line by 1.5+**

---

## STEP 2 — ATTACK STYLE CLASSIFICATION

### The Most Important Question
> Does this team generate corners through wide sustained crossing
> or through central individual quality?

### Attack Type Reference

| Attack Type | Corner Output | Examples |
|---|---|---|
| wide_possession | High 7+ per game | Spain, France, Belgium |
| central_possession | Medium 4-6 per game | Argentina, Norway |
| direct_physical | Low 3-5 per game | Uruguay, Iran, Saudi Arabia |
| counter_attacking | Low winning, high chasing | Egypt, Senegal, Algeria |
| set_piece_specialist | Adds 1-2 regardless of style | Norway, Iraq, New Zealand |

---

## STEP 3 — OPPONENT CLASSIFICATION

| Defensive Style | Effect on Corners |
|---|---|
| pure_deep_block | Maximum corners — dominant team probes wide all game |
| compact_mid_block | Moderate corners — tight game, occasional counter |
| open_attack_minded | End-to-end — both teams contribute corners |
| high_press | Fewer corners — transitions-based, less wide play |

---

## STEP 4 — SITUATION LAYER

| Situation | Effect on Corners |
|---|---|
| Underdog scores early | Favourite chases wide → corners spike (Saudi-Uruguay = 18) |
| Favourite scores 2+ early central | May ease off wide → corners drop |
| 0-0 deep into second half | Both teams push wide late → corners build |
| Must-win urgency both teams | Raises tempo but only if style supports wide play |
| Blowout via central scorer | Corners drop — no need for wide probing |
| Tournament opener mentality | Cautious first half — tight early, opens later |

---

## STEP 5 — TIER CLASSIFICATION

### TIER 1 — Bet (High Confidence)
All three must be true:
- Wide possession team with wide-specific threats
- Opponent is pure deep low block with zero attacking threat
- Combined baseline exceeds line by 1.5+

**Real example: Spain vs Cape Verde — 13 corners — WON ✅**

### TIER 2 — Consider (Medium Confidence)
- Possession team but opponent has defensive quality or counter-threat
- Combined baseline above line by 1.0-1.5
- Attack type must be wide not central
- Odds must offer genuine value (1.850+)

**Real example: France vs Senegal — 10 corners — WON ✅**

### TIER 3 — Skip
Any one of these present:
- Both teams direct and central
- Line at or above combined baseline
- Opponent has genuine counter-threat
- Favourite scores through central individual brilliance
- Odds don't reflect edge (Under 1.750 or Over 1.700)

---

## STEP 6 — MARKET SELECTION

| Market | When To Use |
|---|---|
| Asian Total Corners Over | Default first choice — robust to game state |
| Asian Total Corners Under | Both teams direct AND line 1.5+ above baseline |
| AH Corners (team -X) | ONLY pure deep block opponent, zero counter-threat |
| 1st Half Corners Over | One team aggressively starts + wide attack style |
| Team Corners Over/Under | One team clearly dominates corners battle |

### AH Corners Warning
Never use when opponent has a counter-threat.
One early goal flips the corners battle completely.
Belgium vs Egypt: Belgium 2 — Egypt 7. Lost. ❌

---

## STEP 7 — LINE VALUE RULES

| Scenario | Decision |
|---|---|
| Baseline 1.5+ above line | Strong Over — bet |
| Baseline 1.0-1.5 above line | Consider Over — check odds |
| Baseline within 0.5 of line | Skip — no edge |
| Baseline 1.5+ below line | Strong Under — bet |
| Line perfectly priced at baseline | Skip — bookmaker has it right |

---

## STEP 8 — DECISION CHECKLIST

Before every bet ask:
1. What is the combined baseline vs the line?
2. Does the favourite score through wide play or central individual quality?
3. What is the opponent defensive style?
4. Is there an early goal risk that could flip game state?
5. Does the line offer 1.5+ edge over baseline?
6. Which market is most robust to game state changes?
7. Are the odds offering genuine value (1.850+)?

---

## STAKING RULES
- Unit stake: split evenly across all bets
- Maximum 1 bet per match
- Maximum 2 bets only if two genuinely independent strong edges exist
- No multis — single bets only
- Only play Tier 1 or strong Tier 2
- Skip if no clean edge — never force a bet

---

## LESSONS LEARNED LOG

| Match | Corners | Lesson |
|---|---|---|
| Spain vs Cape Verde ✅ | 13 | Wide possession vs pure deep block = reliable Over |
| Belgium vs Egypt ❌ | 9 (Bel 2, Egy 7) | AH corners fragile — early goal flips battle. Never use AH when counter-threat exists |
| Saudi vs Uruguay ⚠️ | 18 | Underdog scores early → favourite chases wide → corners explode |
| Iran vs New Zealand ✅ | 4-5 | Two direct teams = low corners regardless of urgency. Style beats urgency |
| France vs Senegal ✅ | 10 | Wide possession vs compact mid-block — tight first half, corners build across 90 mins |
| Iraq vs Norway ✅ | 7 | Central scorer (Haaland) dominates through middle — low corners confirmed |

---

## MODEL EVOLUTION LOG

| Version | Date | Change |
|---|---|---|
| v1.0 | Jun 15 | Initial framework — Over/Under focus |
| v2.0 | Jun 15 | Added AH corners, 1H markets, blowout rule |
| v3.0 | Jun 16 | Added attack style classification, HOW team scores rule, line value thresholds |

---

## CORNER VOLUME REFERENCE

| Total Corners | Match Profile |
|---|---|
| 13+ | Wide possession machine vs pure deep block |
| 10-12 | Wide possession vs compact mid-block, tight game |
| 7-9 | Central/direct team dominates, scores through middle |
| 4-6 | Two direct teams, both defensive, low tempo |
| 18+ | Outlier — underdog scores early, favourite chases wide desperately |

## BATCH ANALYSIS RULES

When multiple matches are given at once:
1. Research all matches before making any decision
2. Rank all matches by edge strength before dropping lines
3. See full day picture before committing to any bet
4. Natural filter — only strongest edges survive when you see all matches together
5. Maximum 2 bets per day unless 3+ genuinely independent strong edges exist
6. Drop all lines at once — not one by one

### Daily Edge Ranking Format
STRONG EDGE:   [Match] — Tier 1 — [market] — [direction]
MODERATE EDGE: [Match] — Tier 2 — [market] — [direction]
NO EDGE:       [Match] — Tier 3 — Skip