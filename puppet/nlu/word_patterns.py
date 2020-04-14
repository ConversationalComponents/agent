"""
    Compile simple word patterns to regex

    Examples:
    intent = IntentBuilder(
        S("the", "boy", "ate", "an", "apple")
    )
    intent("the boy ate an apple") -> True
    intent("the boy ate an orange") -> False

    intent = IntentBuilder(
        S("the", "boy", "ate", "an", NWords(min=1, max=1))
    )
    intent("the boy ate an apple") -> True
    intent("the boy ate an orange") -> True

    intent = IntentBuilder(
        S("the", Word("boy", "girl"), "ate", "an", NWords(min=1, max=1))
    )
    intent("the boy ate an apple") -> True
    intent("the boy ate an orange") -> True
    intent("the girl ate an orange") -> True
    intent("the girl ate a banana") -> False

    intent = IntentBuilder(
        S("the", Word("boy", "girl"), "ate", WordP(r"an?"), NWords(min=1, max=1))
    )
    intent("the boy ate an apple") -> True
    intent("the boy ate an orange") -> True
    intent("the girl ate an orange") -> True
    intent("the girl ate a banana") -> True
    intent("a nice boy ate an apple") -> False

    intent = IntentBuilder(
        S(WC, Word("boy", "girl"), "ate", WordP(r"an?"), NWords(min=1, max=1))
    )
    intent("a nice boy ate an apple") -> True

"""
import typing as ta
import abc
import re


class SentenceElement(abc.ABC):
    @abc.abstractmethod
    def regex_transformation(self):
        raise NotImplementedError


class RegexPattern(SentenceElement):
    def __init__(self, pattern):
        self.pattern = pattern

    def regex_transformation(self):
        return self.pattern


class WordP(SentenceElement):
    def __init__(self, *patterns):
        self.word_list_tran = f"\\b({'|'.join(patterns)})\\b"

    def regex_transformation(self):
        return self.word_list_tran


class Word(WordP):
    def __init__(self, *words):
        self.word_list_tran = f"\\b({'|'.join(re.escape(w) for w in words)})\\b"


class NWords(SentenceElement):
    def __init__(self, min="", max=""):
        self.pattern = "(\\s?\\b\\w+\\b\\s?){" + f"{str(min)},{str(max)}" + "}"

    def regex_transformation(self):
        return self.pattern


WC = RegexPattern(r"(.*)")


class S:
    def __init__(self, *elements: ta.Union[SentenceElement, str]):
        elements_normalized = (
            e if isinstance(e, SentenceElement) else Word(e) for e in elements
        )
        self.pattern = re.compile(
            r"\s*".join(e.regex_transformation() for e in elements_normalized),
            re.IGNORECASE,
        )

    def __call__(self, user_input):
        return bool(self.pattern.fullmatch(user_input))


class IntentBuilder:
    def __init__(
        self, *sentence_patterns: S, preprocess_func: ta.Callable[[str], str] = None
    ) -> None:
        self.sentence_patterns: ta.Tuple[S, ...] = sentence_patterns
        if preprocess_func:
            self.preprocess_func = preprocess_func
        else:
            self.preprocess_func = lambda s: s

    def __call__(self, user_input) -> bool:
        prepro_user_input = self.preprocess_func(user_input)
        for s in self.sentence_patterns:
            if s(prepro_user_input):
                return True
        return False
