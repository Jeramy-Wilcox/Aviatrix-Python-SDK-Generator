from __future__ import annotations

import re
from typing import Any, Dict, List, Union

from aviatrix_sdk_generator.exceptions import MissingAction

ARG_TYPES = {
    "String": "str",
    "Integer": "int",
    "Boolean": "bool",
    "Float": "float",
    "List": "List[Any]",
    "Array": "List[Any]",
    "Dictionary": "Dict[str, Any]",
    "None": "None",
}

TYPE_IMPORTS = {
    "List": ["List", "Any"],
    "Array": ["List", "Any"],
    "Dictionary": ["Dict", "Any"],
    "Any": ["Any"],
}


class _Arg:
    def __init__(self, arg: Dict[str, str]):
        self._arg = arg
        try:
            self._description = self._arg.get("description", "")
        except Exception:
            self._description = ""

    def __str__(self):
        return f"{self.key}: {self.value}. Description: {self.description}"

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, _Arg):
            return self.key == __o.key
        else:
            return False

    @property
    def key(self):
        return self._arg["key"]

    @property
    def value(self):
        return self._arg["value"]

    @property
    def required(self):
        if self.get_value("required").upper() == "YES" and "[" not in self.key:
            return True
        else:
            return False

    @property
    def description(self):
        return self.get_value("description")

    @property
    def type(self):
        return self.get_value("type")

    @property
    def import_types(self):
        return TYPE_IMPORTS.get(self.type, [])

    @property
    def default_value(self):
        return self.get_value("default")

    @property
    def example(self):
        return self.get_value("example").replace('"', "")

    def get_value(self, pattern: str) -> str:
        _patterns = {
            "required": r"Required\n(\w*)\n",
            "description": r"Description\n(.*)\n",
            "type": r"Type\n(\w*)\n",
            "example": r"Example\(s\)\n(\S*)\n",
            "default": r"Default Value\n(\W*)\n",
        }
        match = re.search(_patterns[pattern], self._description, re.MULTILINE)
        if match:
            return match.group(1)
        else:
            return ""

    def get_template_vars(self) -> Dict[str, Union[str, bool]]:
        return {
            "name": self.key,
            "type": ARG_TYPES.get(self.type, "Any"),
            "description": self.description,
            "default": self.default_value,
            "example": self.example,
            "required": self.required,
        }

    @staticmethod
    def clean_arg_name(name: str) -> str:
        return name.replace("[", "_").replace("]", "").replace(" ", "_")


class _Args:
    def __init__(self, args: List[Dict[str, Any]]):
        self._action = None
        self._args: List[_Arg] = []

        for arg in args:
            opt = _Arg(arg)
            if opt.key == "CID":
                continue
            if opt.key == "action":
                self._action = opt
            else:
                self._args.append(opt)

    @property
    def args(self):
        return self._args

    @property
    def action(self) -> _Arg:
        if self._action is None:
            raise MissingAction("Action not found")
        else:
            return self._action
