# Big Five Personality Guesser

A terminal-based guessing game that identifies which Big Five personality archetype best fits you, using a Naive Bayes probabilistic engine and real-world survey data.

## Overview

The game asks a sequence of yes/no/unsure questions drawn from the IPIP-50 personality inventory, updating its belief about which archetype you belong to after each answer. Questions are selected using an information-gain heuristic, so the game asks the most discriminating question at each step rather than going in a fixed order.

## Data

Built on the [IPIP-FFM dataset](https://openpsychometrics.org/tests/IPIP-BFFM/) — just over 1 million responses to the 50-item IPIP Big Five questionnaire, collected by Open Psychometrics.

Preprocessing (`convert_ipip.py`):
1. Filter to one response per IP address (`IPC == 1`) and drop incomplete rows, leaving ~603k respondents.
2. Compute each respondent's five trait scores (Extraversion, Neuroticism, Agreeableness, Conscientiousness, Openness), applying the standard IPIP reverse-scoring key for negatively-worded items.
3. Z-normalize each trait score against the population mean/stdev, so traits with different baseline distributions (e.g. Openness scores tend to run higher than Neuroticism) are compared fairly.
4. Assign each respondent to an archetype based on their most z-score-dominant trait, or to "The Balanced" archetype if no trait stands out clearly.
5. Aggregate the modal response to each of the 50 questions within each archetype, producing a `1` (agree), `-1` (disagree), or `0` (neutral) profile per archetype.

The result is `knowledge_base.json`: 50 boolean-ish attributes, 6 character profiles (archetypes), and the original question text for each attribute.

## Archetypes

| Archetype | Dominant Trait |
|---|---|
| The Connector | Extraversion |
| The Sentinel | Neuroticism |
| The Empath | Agreeableness |
| The Guardian | Conscientiousness |
| The Explorer | Openness |
| The Balanced | No single dominant trait |

## Engine

`engine.py` implements the core probabilistic logic:

- **Prior**: all archetypes start equally likely (`1/N`).
- **Bayesian update**: each answer shifts probability toward archetypes whose known profile agrees with the answer, and away from those that disagree, using a fixed likelihood ratio.
- **Question selection**: at each step, the engine picks the unasked question that splits the remaining probability mass as close to 50/50 as possible (maximizing information gain).
- **Stopping condition**: the game stops and guesses once one archetype's probability exceeds 85%, or when no more questions remain.

## Learning

If the guess is wrong, the game asks which archetype actually fits better, then reinforces that archetype's profile using `reinforce_archetype()`: for each question the user answered, if their answer disagrees with the existing profile, that attribute is pulled toward neutral rather than being overwritten outright, since each archetype represents an aggregate over tens of thousands of respondents.

## Project Structure

```
main.py              CLI game loop
engine.py             Naive Bayes engine (priors, updates, question selection)
data_manager.py       Load/save knowledge_base.json, add attributes/characters, reinforce archetypes
convert_ipip.py       One-time script: raw IPIP CSV -> knowledge_base.json
knowledge_base.json    Generated data file (attributes, archetypes, question text, descriptions)
```

## Running It

Requires Python 3 standard library only — no external dependencies.

```
python3 main.py
```

Answer each question with `y`, `n`, or `i` (not sure). At the end, the game shows its guess, a confidence score, and a short description of the archetype.

To regenerate `knowledge_base.json` from the raw dataset (e.g. after changing the archetype logic or dominance threshold):

```
python3 convert_ipip.py
```

This expects the raw data at `ipip/IPIP-FFM-data-8Nov2018/data-final.csv` and its accompanying `codebook.txt`, available from the [IPIP-FFM dataset on Kaggle](https://www.kaggle.com/datasets/tunguz/big-five-personality-test).

## Design Notes

- The dominance threshold for assigning archetypes (`DOMINANCE_MARGIN` in `convert_ipip.py`) is a tunable parameter — lowering it produces fewer "Balanced" results and more decisive archetype assignments, at the cost of calling closer trait scores decisively rather than acknowledging genuine ambiguity.
- All scoring uses the standard IPIP-50 reverse-coding key, cross-checked against item wording (e.g. "I don't talk a lot" is reverse-scored relative to "I am the life of the party").
