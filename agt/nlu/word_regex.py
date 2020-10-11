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

from collections import defaultdict
from typing import Optional


class PatternElement(abc.ABC):
    """
    Base class for element in pattern
    """

    def __init__(self, name=None) -> None:
        self.name = name

    @abc.abstractmethod
    def regex_transformation(self):
        raise NotImplementedError


class RegexElement(PatternElement):
    """
    element for any regex in a word position
    """

    def __init__(self, pattern, **kwargs):
        super().__init__(**kwargs)
        self.pattern = pattern

    def regex_transformation(self):
        return self.pattern


class WordsRegex(PatternElement):
    """
    List of word regex patterns to match against a single word position
    """

    def __init__(self, *patterns, **kwargs):
        super().__init__(**kwargs)
        self.word_list_tran = f"\\b({'|'.join(patterns)})\\b"

    def regex_transformation(self):
        return self.word_list_tran


class Words(WordsRegex):
    """
    List of words to match against a single word position
    """

    def __init__(self, *words, **kwargs):
        super().__init__(**kwargs)
        self.word_list_tran = f"\\b({'|'.join(re.escape(w) for w in words)})\\b"


class AnyWords(PatternElement):
    """
    Any word configurable with min, max
    """

    def __init__(self, min="", max="", **kwargs):
        super().__init__(**kwargs)
        self.pattern = "(\\s?\\b\\w+\\b\\s?){" + f"{str(min)},{str(max)}" + "}"

    def regex_transformation(self):
        return self.pattern


class Wildcard(RegexElement):
    def __init__(self, **kwargs) -> None:
        super().__init__(r"(.*)", **kwargs)


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
            elif isinstance(e, (tuple, list, set)):
                elements_normalized.append(Words(*e))

        self.pattern = re.compile(
            r"\s*".join(self.wrap_element_in_group(e) for e in elements_normalized),
            re.IGNORECASE,
        )

    @staticmethod
    def wrap_element_in_group(e):
        e_name_regex = ""
        if e.name:
            e_name_regex = f"?P<{e.name}>"
        return f"({e_name_regex}{e.regex_transformation()})"

    def __call__(self, user_input):
        return bool(self.pattern.fullmatch(user_input))

    def extract(self, user_input):
        m = self.pattern.fullmatch(user_input)
        if m:
            return m.groupdict()
        else:
            return {}


class Extractor(abc.ABC):
    def __init__(
        self, *patterns: Pattern, preprocess_func: ta.Callable[[str], str] = None
    ) -> None:
        self.patterns: ta.Tuple[Pattern, ...] = patterns
        if preprocess_func:
            self.preprocess_func = preprocess_func
        else:
            self.preprocess_func = lambda s: s


class Intent(Extractor):
    """
    Intent reposesents a group of patterns to match against an utterance
    """

    def __call__(self, user_input) -> bool:
        prepro_user_input = self.preprocess_func(user_input)
        for p in self.patterns:
            if p(prepro_user_input):
                return True
        return False


class Slots(Extractor):
    def __call__(self, user_input) -> dict:
        prepro_user_input = self.preprocess_func(user_input)
        slots = defaultdict(lambda: [])
        for p in self.patterns:
            for slot_name, slot_value in p.extract(prepro_user_input).items():
                slots[slot_name].append(slot_value)
        return dict(slots)


def extract_slot(extractor: Slots, user_input: str, slot_name: str) -> Optional[str]:
    slot_values = extractor(user_input).get(slot_name, [])
    if len(slot_values) > 0:
        return slot_values[0]
    return None


def intent_slot(
    *patterns: Pattern, preprocess_func: ta.Callable[[str], str] = None
) -> ta.Tuple[Intent, Slots]:
    """
        convenience wrapper to get intent+slot extractor from a set of patterns and preprocessor

    Keyword Arguments:
        preprocess_func {ta.Callable[[str], str]} -- preprocess function (default: {None})

    Returns:
        ta.Tuple[Intent, SlotsExtractor] -- intent and slot extractor
    """
    return Intent(*patterns, preprocess_func=preprocess_func), Slots(*patterns)
