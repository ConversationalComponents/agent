import re

class RegexIntent:
    def __init__(self, pattern):
        self.pattern = re.compile(pattern)

    def __call__(self, user_input):
        if self.pattern.match(user_input):
            return True
        return False
