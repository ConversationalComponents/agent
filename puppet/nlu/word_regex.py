"""
    Compile simple word patterns to regex

    Examples:
    intent = Intent(
        Pattern("the", "boy", "ate", "an", "apple")
    )
    intent("the boy ate an apple") -> True
    intent("the boy ate an orange") -> False

    intent = Intent(
        Pattern("the", "boy", "ate", "an", AnyWords(min=1, max=1))
    )
    intent("the boy ate an apple") -> True
    intent("the boy ate an orange") -> True

    intent = Intent(
        Pattern("the", Words("boy", "girl"), "ate", "an", AnyWords(min=1, max=1))
    )
    intent("the boy ate an apple") -> True
    intent("the boy ate an orange") -> True
    intent("the girl ate an orange") -> True
    intent("the girl ate a banana") -> False

    intent = Intent(
        Pattern("the", ("boy", "girl"), "ate", WordsRegex(r"an?"), AnyWords(min=1, max=1))
    )
    intent("the boy ate an apple") -> True
    intent("the boy ate an orange") -> True
    intent("the girl ate an orange") -> True
    intent("the girl ate a banana") -> True
    intent("a nice boy ate an apple") -> False

    intent = Intent(
        Pattern(WILDCARD, Words("boy", "girl"), "ate", WordsRegex(r"an?"), AnyWords(min=1, max=1))
    )
    intent("a nice boy ate an apple") -> True

"""
import typing as ta
import abc
import re


class PatternElement(abc.ABC):
    """
        Base class for element in pattern
    """
    @abc.abstractmethod
    def regex_transformation(self):
        raise NotImplementedError


class RegexElement(PatternElement):
    """
        element for any regex in a word position
    """
    def __init__(self, pattern):
        self.pattern = pattern

    def regex_transformation(self):
        return self.pattern


class WordsRegex(PatternElement):
    """
        List of word regex patterns to match against a single word position
    """
    def __init__(self, *patterns):
        self.word_list_tran = f"\\b({'|'.join(patterns)})\\b"

    def regex_transformation(self):
        return self.word_list_tran


class Words(WordsRegex):
    """
        List of words to match against a single word position
    """
    def __init__(self, *words):
        self.word_list_tran = f"\\b({'|'.join(re.escape(w) for w in words)})\\b"


class AnyWords(PatternElement):
    """
        Any word configurable with min, max
    """
    def __init__(self, min="", max=""):
        self.pattern = "(\\s?\\b\\w+\\b\\s?){" + f"{str(min)},{str(max)}" + "}"

    def regex_transformation(self):
        return self.pattern


WILDCARD = RegexElement(r"(.*)")


class Pattern:
    """
    A class representing a single pattern for a Sentence/Utterance
    pattern is built out of elements that match a single word in an utterance

    """
    def __init__(self, *elements: ta.Union[PatternElement, str, tuple]):
        elements_normalized = []
        for e in elements:
            if isinstance(e, PatternElement):
                elements_normalized.append(e)
            elif isinstance(e, str):
                elements_normalized.append(Words(e))
            elif isinstance(e, tuple):
                elements_normalized.append(Words(*e))

        self.pattern = re.compile(
            r"\s*".join(e.regex_transformation() for e in elements_normalized),
            re.IGNORECASE,
        )

    def __call__(self, user_input):
        return bool(self.pattern.fullmatch(user_input))


class Intent:
    """
    Intent reposesents a group of patterns to match against an utterance
    """
    def __init__(
        self, *patterns: Pattern, preprocess_func: ta.Callable[[str], str] = None
    ) -> None:
        self.patterns: ta.Tuple[Pattern, ...] = patterns
        if preprocess_func:
            self.preprocess_func = preprocess_func
        else:
            self.preprocess_func = lambda s: s

    def __call__(self, user_input) -> bool:
        prepro_user_input = self.preprocess_func(user_input)
        for s in self.patterns:
            if s(prepro_user_input):
                return True
        return False
