class AkinatorEngine:
    def __init__(self, kb_data: dict):
        self.attributes = kb_data["attributes"]
        self.characters = kb_data["characters"]
        self.char_names = list(self.characters.keys())
        n = len(self.char_names)
        self.probabilities = {name: 1.0 / n for name in self.char_names}
        
    def update_probabilities(self, attribute: str, answer: int):
        if answer == 0:
            return

        total_prob = 0.0
        
        for name in self.char_names:
            char_val = self.characters[name].get(attribute, 0)
            
            # P(H|E) = P(E|H) * P(H) / P(E)
            if answer == 1:
                likelihood = 0.85 if char_val == 1 else (0.15 if char_val == -1 else 0.5)
            else: 
                likelihood = 0.85 if char_val == -1 else (0.15 if char_val == 1 else 0.5)
                
            self.probabilities[name] *= likelihood
            total_prob += self.probabilities[name]
            
        for name in self.char_names:
            self.probabilities[name] /= total_prob
            
    def get_best_question(self, asked_attributes: set) -> str:
        best_attr = None
        min_diff = float('inf')
        
        for attr in self.attributes:
            if attr in asked_attributes:
                continue
                
            yes_prob = 0.0
            no_prob = 0.0
            
            for name, prob in self.probabilities.items():
                char_val = self.characters[name].get(attr, 0)
                if char_val == 1:
                    yes_prob += prob
                elif char_val == -1:
                    no_prob += prob
                    
            diff = abs(yes_prob - no_prob)
            
            if diff < min_diff:
                min_diff = diff
                best_attr = attr
                
        return best_attr

    def get_top_character(self) -> tuple:
        return max(self.probabilities.items(), key=lambda x: x[1])