import json
import os

DB_PATH = "knowledge_base.json"

def load_knowledge_base() -> dict:
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"'{DB_PATH}' not found in root directory.")
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_knowledge_base(kb: dict) -> None:
    with open(DB_PATH, "w") as f:
        json.dump(kb, f, indent=2)

def add_attribute(kb: dict, attribute: str) -> dict:
    if attribute not in kb["attributes"]:
        kb["attributes"].append(attribute)
        for name in kb["characters"]:
            kb["characters"][name].setdefault(attribute, 0)
    return kb

def add_character(kb: dict, name: str, traits: dict) -> dict:
    full_traits = {attr: 0 for attr in kb["attributes"]}
    full_traits.update(traits)
    kb["characters"][name] = full_traits
    return kb

def reinforce_archetype(kb: dict, name: str, answers: dict) -> dict:
    profile = kb["characters"][name]
    for attr, answer in answers.items():
        if answer == 0:
            continue
        current = profile.get(attr, 0)
        if current == 0:
            profile[attr] = answer
        elif current != answer:
            profile[attr] = 0
    return kb