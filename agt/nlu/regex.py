import re


class RegexIntent:
    def __init__(self, *patterns):
        self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns]

    def __call__(self, user_input):
        for p in self.patterns:
            if p.match(user_input):
                return True
        return False


class RegexExtractor:
    def __init__(self, pattern, target_group) -> None:
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.target_group = target_group

    def __call__(self, user_input):
        m = self.pattern.match(user_input)
        if m:
            return m.group(self.target_group)
