# World Cup 2026 — Corners Betting Model

A rule-based decision system for betting on football corner markets, built and refined live across the FIFA World Cup 2026 group stage and beyond.

This is **not** a machine learning project. It's a manually-authored expert system — a decision tree of thresholds, classifications, and rules — that gets refined match by match based on real outcomes. A statistical model (logistic regression) is planned as a complementary second opinion once enough data exists, but isn't built yet. See [Roadmap](#roadmap) below.

---

## What problem this solves

Bookmakers offer corner totals (e.g. "Over/Under 9.5 corners") for every match. The model tries to answer one question before each game: **does our estimate of likely corners disagree with the bookmaker's line by enough to be worth betting on?**

The answer depends on more than raw averages — it depends on *how* each team generates corners (sustained wide play vs. central individual quality vs. set pieces), *how* their opponent defends, and situational factors like altitude, game state, and counter-attacking risk. The model encodes all of this as an explicit, auditable rule set rather than a black box.

---

## How it works, end to end

### 1. Collect data
For each matchup, gather both teams' average corners taken/conceded from recent matches. Combine into a baseline estimate and compare against the bookmaker's line.

### 2. Classify attack & defensive style
Every team is labeled by *how* they create or concede corners — e.g. `wide_possession` (high corner output via sustained crossing), `direct_physical` (low output, individual or aerial), `counter_attacking` (dangerous in transition, low corners themselves), `pure_deep_block` (concedes maximum corners to a dominant opponent), and so on. This is the most important classification in the whole model — corner volume is driven far more by *style* than by *quality*.

### 3. Apply situational adjustments
Altitude venues reduce tempo (and corners). Tournament debutants tend to play ultra-cautiously. Game state matters a lot: a team that concedes early often abandons patient build-up and starts crossing aimlessly, **increasing** corners — the opposite of what raw quality difference would predict.

### 4. Classify into a tier
Combining baseline edge, style matchup, and counter-threat risk, every match lands in one of three tiers:
- **Tier 1** — high confidence, clear edge, bet
- **Tier 2** — moderate edge, bet selectively if odds justify it
- **Tier 3** — no clean edge, skip (but the directional lean — over or under — is still recorded for tracking)

Tier 1 and Tier 2 both have symmetric ladders for Over *and* Under bets — an early version of this model only had clear thresholds for Over, which was a real structural bug, since research suggests bookmakers may actually misprice Under more often than Over.

### 5. Pick a market and check the odds floor
Different bet types (Asian Total, Asian Handicap, 1st Half Corners) suit different situations — Handicap bets in particular are forbidden whenever the opponent has any counter-attacking threat, since one early goal can flip a corners battle completely. Every tier/market combination has a minimum acceptable odds floor; bets below it are flagged for manual review rather than placed automatically.

### 6. Bet, track, and log lessons
After every match, the result is logged — including matches the model chose to **skip**, with its directional lean recorded either way. This is deliberate: tracking what the model *would have said* on skipped matches is the only way to tell later whether the skip threshold is too conservative.

---

## Why this design, specifically

**Corners are genuinely hard to predict.** Academic research analyzing thousands of professional matches found even well-fitted statistical models explain very little of the variance in corner counts (R² ≈ 0.01–0.02). This isn't a flaw unique to this model — it's closer to the ceiling of what's knowable. Confidence labels here ("Tier 1 — high confidence") should be read as *best available read given limited information*, not statistical certainty.

**Style beats quality.** Repeatedly, across logged matches, the strongest signal hasn't been which team is "better" but *how* each team scores and defends. A dominant team that scores through individual brilliance up the middle can produce fewer corners than a mediocre team that grinds out width all game.

**Skips are tracked as seriously as bets.** A rule-based system is only as good as its ability to admit when it's wrong. Every skip records a directional lean and gets checked against the actual result, specifically so the model's caution can be audited rather than assumed correct by default.

---

## Project structure

```
world-cup-corners-model/
├── README.md              — this file
├── MODEL.md                — full ruleset, version history, lessons learned
├── CLAUDE.md                — instructions for AI-assisted data entry/automation
├── GUIDE.md                 — step-by-step operating guide for match days
├── main.py                  — single command-line entry point
├── data/
│   ├── matches.csv          — every match result and corner count
│   ├── teams.csv             — team style classifications and rolling averages
│   ├── bets.csv               — betting ledger and profit/loss
│   ├── predictions.csv         — every pre-match call, including skips
│   ├── lessons.csv              — lessons learned, one per notable match
│   └── model_versions.csv        — structured changelog of rule changes
└── scripts/
    ├── update_match.py       — logs a result across all CSVs at once
    ├── baseline_calculator.py — computes a pre-match baseline and tier
    ├── model_stats.py          — win rate, ROI, skip accuracy, readiness tracker
    ├── analyse_model.py         — deeper pattern analysis (tier/market/style performance)
    ├── log_version.py            — appends a structured entry when the ruleset changes
    └── briefing.py                — generates a full-context summary for a new session
```

---

## How a match day actually works

1. **Get the lines.** Bet365 screenshots for each match's corner markets.
2. **Research and classify.** Both teams' style, recent form, and any situational factors (altitude, debutant status, counter-threat) are checked before a tier is assigned.
3. **Decide.** Bet, or skip with a recorded lean — never force a bet without a clean edge.
4. **Log the result.** One command (`python main.py update ...`) appends the outcome across every relevant CSV — match data, the bet (if any), the prediction record, and any new lesson learned.
5. **Review periodically.** Every ~5 matches, `python main.py analyse` is run to check whether tier thresholds, market choices, and style classifications are actually holding up against real outcomes — not just assumed to be working.

---

## A note on data integrity

This system went through a deliberate audit-and-repair process after roughly 15 matches, finding and fixing three real bugs: a duplicate match entry, a gap where skip-leans weren't being recorded in `predictions.csv`, and silent misclassification of any team not in the original starting dataset. All three are now fixed at the code level, not just patched in the data — see the `v4.2` entry in `MODEL.md`'s evolution log for details. Worth remembering: a model is only as trustworthy as the data underneath it, and that's worth auditing directly rather than assuming.

---

## Roadmap

The rule-based system above is intentionally simple and interpretable — appropriate for the small, fast-moving sample size of a single tournament. A complementary statistical model (logistic regression, predicting probability of Over/Under against the line) is planned once roughly 40–50 matches have been logged, which is closer to the volume needed before fitted thresholds become more trustworthy than hand-picked ones. `model_stats.py` tracks progress toward this threshold. Until then, the two-model comparison stays a planned future step, not a current feature.

---

## Limitations, stated plainly

- Small sample size — thresholds (e.g. "1.5 corner edge") are reasoned estimates, not statistically validated cutoffs, until far more matches are logged.
- Built and tuned entirely on World Cup matches — research suggests betting models often don't transfer cleanly between competitions, so don't assume these exact rules would hold in a domestic league.
- Corners have a low ceiling of predictability in general; even a perfect process will lose some bets purely to variance.
