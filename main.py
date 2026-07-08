import data_manager
from engine import AkinatorEngine

def phrase(kb, attr):
    text = kb.get("question_text", {}).get(attr, attr)
    return f"Do you agree: \"{text}\""

def main():
    kb = data_manager.load_knowledge_base()
    engine = AkinatorEngine(kb)
    asked = set()
    user_answers = {}

    print("Big Five Personality Guesser")
    print("Answer honestly about yourself: (y)es, (n)o, or (i) not sure.\n")

    while True:
        best_attr = engine.get_best_question(asked)
        if not best_attr:
            break

        print(phrase(kb, best_attr))
        ans = input("> ").strip().lower()

        if ans == 'y':
            val = 1
        elif ans == 'n':
            val = -1
        else:
            val = 0

        engine.update_probabilities(best_attr, val)
        asked.add(best_attr)
        user_answers[best_attr] = val

        top_char, prob = engine.get_top_character()
        if prob > 0.85:
            break

    top_char, prob = engine.get_top_character()
    print(f"\nMy guess is: {top_char} (Confidence: {prob*100:.1f}%)")
    description = kb.get("archetype_description", {}).get(top_char)
    if description:
        print(f"\n{description}")

    print("Does that sound like you? (y/n)")
    if input("> ").strip().lower() != 'y':
        archetypes = list(kb["characters"].keys())
        print("\nNo worries! Which of these feels closer?")
        for i, name in enumerate(archetypes, 1):
            print(f"  {i}. {name}")
        choice = input("> ").strip()

        try:
            idx = int(choice) - 1
            correct = archetypes[idx]
        except (ValueError, IndexError):
            print("Didn't catch that, skipping the update.")
            correct = None

        if correct:
            kb = data_manager.reinforce_archetype(kb, correct, user_answers)
            data_manager.save_knowledge_base(kb)
            print(f"Thanks! I've updated the {correct} profile based on your answers.")
    else:
        print("Awesome! The Bayesian math prevails.")

if __name__ == "__main__":
    main()
