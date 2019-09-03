import re

from .interpreter import Interepreter

class RegexInterpreter(Interepreter):
    def __init__(self, patterns):
        self.patterns = patterns

    def interpret(self, text, hypotheses):
        selected_hypotheses = {}
        for hypo in hypotheses:
            for match_group in self.patterns.get(hypo, []):
                neg_matched = False
                for neg_pattern in match_group.get("neg_patterns", []):
                    m = re.match(neg_pattern, text.lower())
                    if m:
                        neg_matched = True
                        break
                if neg_matched:
                    break
                for pattern in match_group.get("patterns", []):
                    m = re.match(pattern, text.lower())
                    if m:
                        selected_hypotheses[hypo] = {
                            slot_name: m.group(slot_group_number)
                            for slot_name, slot_group_number
                            in match_group.get("slots", {}).items()
                        }
                        break
        return selected_hypotheses

    def load():
        pass
