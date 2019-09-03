import abc
import typing as ta

class Interepreter(abc.ABC):

    @abc.abstractmethod
    def interpret(self, text: str, hypotheses: ta.List[str]) -> ta.Dict[str, float]:
        pass

    @abc.abstractmethod
    def load(self):
        pass
