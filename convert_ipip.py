import csv
import json
from statistics import mean

SRC = "ipip/IPIP-FFM-data-8Nov2018/data-final.csv"
CODEBOOK = "ipip/IPIP-FFM-data-8Nov2018/codebook.txt"
OUT = "knowledge_base.json"

TRAITS = {
    "EXT": {"pos": [1, 3, 5, 7, 9], "neg": [2, 4, 6, 8, 10]},
    "EST": {"pos": [1, 3, 5, 6, 7, 8, 9, 10], "neg": [2, 4]},
    "AGR": {"pos": [2, 4, 6, 8, 9, 10], "neg": [1, 3, 5, 7]},
    "CSN": {"pos": [1, 3, 5, 7, 9, 10], "neg": [2, 4, 6, 8]},
    "OPN": {"pos": [1, 3, 5, 7, 8, 9, 10], "neg": [2, 4, 6]},
}

QUESTION_CODES = [f"{t}{i}" for t in TRAITS for i in range(1, 11)]

ARCHETYPES = {
    "EXT": "The Connector",
    "EST": "The Sentinel",
    "AGR": "The Empath",
    "CSN": "The Guardian",
    "OPN": "The Explorer",
}
BALANCED = "The Balanced"
DOMINANCE_MARGIN = 0.5  # min gap in z-score units between top trait and the rest to avoid "Balanced"

ARCHETYPE_DESCRIPTIONS = {
    "The Connector": (
        "Scores highest on Extraversion. Tends to be energized by people, seeks out "
        "social situations, and speaks up readily in groups. Likely to be seen as "
        "outgoing and assertive, though may find solitude or quiet environments draining."
    ),
    "The Sentinel": (
        "Scores highest on Neuroticism (emotional reactivity). Tends to feel emotions "
        "intensely and notice stress or risk quickly. This isn't a flaw — it often maps "
        "to strong empathy and vigilance — but it can mean more time spent worrying or "
        "feeling on edge compared to others."
    ),
    "The Empath": (
        "Scores highest on Agreeableness. Tends to prioritize cooperation, trust, and "
        "others' wellbeing over personal advantage. Likely to be seen as warm and "
        "easygoing, though may sometimes struggle with confrontation or saying no."
    ),
    "The Guardian": (
        "Scores highest on Conscientiousness. Tends to be organized, dependable, and "
        "goal-directed, preferring plans over spontaneity. Likely to follow through on "
        "commitments, though may be less comfortable with ambiguity or last-minute change."
    ),
    "The Explorer": (
        "Scores highest on Openness. Tends to be curious, drawn to novelty, ideas, and "
        "abstract thinking. Likely to enjoy creative or intellectual pursuits, though may "
        "get bored with routine or highly structured environments."
    ),
    "The Balanced": (
        "No single trait stands out strongly above the others. This means responses were "
        "moderate across all five dimensions rather than extreme in any one direction — "
        "often reflecting genuine flexibility, or simply that personality here doesn't "
        "reduce neatly to one dominant label."
    ),
}


def trait_score(row, trait):
    total = 0
    for i in TRAITS[trait]["pos"]:
        total += int(row[f"{trait}{i}"])
    for i in TRAITS[trait]["neg"]:
        total += 6 - int(row[f"{trait}{i}"])
    return total


def classify(z_scores):
    ordered = sorted(z_scores.items(), key=lambda x: x[1], reverse=True)
    top_trait, top_z = ordered[0]
    second_z = ordered[1][1]
    if top_z - second_z < DOMINANCE_MARGIN:
        return BALANCED
    return ARCHETYPES[top_trait]


def load_question_text():
    text = {}
    with open(CODEBOOK, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if "\t" not in line:
                continue
            code, question = line.split("\t", 1)
            if code in QUESTION_CODES:
                text[code] = question.strip()
    return text


def main():
    valid_rows = []
    with open(SRC, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row.get("IPC") != "1":
                continue
            try:
                answers = {code: int(row[code]) for code in QUESTION_CODES}
            except (ValueError, KeyError):
                continue
            if any(v == 0 for v in answers.values()):
                continue
            valid_rows.append(answers)

    print(f"Valid rows after filtering: {len(valid_rows)}")

    # Pass 1: population mean/stdev per trait so traits are compared fairly
    all_scores = {t: [trait_score(r, t) for r in valid_rows] for t in TRAITS}
    stats = {}
    for t, scores in all_scores.items():
        mu = mean(scores)
        var = sum((s - mu) ** 2 for s in scores) / len(scores)
        stats[t] = (mu, var ** 0.5)
        print(f"{t}: mean={mu:.2f} stdev={stats[t][1]:.2f}")

    # Pass 2: classify each respondent by which trait is most z-score-dominant
    buckets = {name: [] for name in list(ARCHETYPES.values()) + [BALANCED]}
    for idx, answers in enumerate(valid_rows):
        z_scores = {t: (all_scores[t][idx] - stats[t][0]) / stats[t][1] for t in TRAITS}
        archetype = classify(z_scores)
        buckets[archetype].append(answers)

    characters = {}
    for name, rows in buckets.items():
        if not rows:
            continue
        profile = {}
        for code in QUESTION_CODES:
            avg = mean(r[code] for r in rows)
            if avg >= 3.5:
                profile[code] = 1
            elif avg <= 2.5:
                profile[code] = -1
            else:
                profile[code] = 0
        characters[name] = profile
        print(f"{name}: {len(rows)} respondents")

    question_text = load_question_text()
    kb = {
        "attributes": QUESTION_CODES,
        "characters": characters,
        "question_text": question_text,
        "archetype_description": ARCHETYPE_DESCRIPTIONS,
    }
    with open(OUT, "w") as f:
        json.dump(kb, f, indent=2)
    print(f"\nWrote {OUT} with {len(characters)} archetypes and {len(QUESTION_CODES)} attributes.")


if __name__ == "__main__":
    main()
