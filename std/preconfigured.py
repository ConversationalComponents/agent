import json
import importlib.resources

import puppet
from . import data_files

_basic_nlu_patterns = json.loads(
    importlib.resources.read_text(data_files, "basic_nlu.json"))

basic_nlu_interpreter = puppet.nlu.RegexInterpreter(_basic_nlu_patterns)
