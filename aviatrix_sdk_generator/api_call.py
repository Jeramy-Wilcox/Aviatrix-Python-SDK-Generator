from __future__ import annotations

import re
from typing import Any, Dict, List

from aviatrix_sdk_generator.args import _Args
from aviatrix_sdk_generator.exceptions import MissingAction, NoOptionsFound


class Call:
    def __init__(self, call: Dict[str, Any]):
        self.call = call
        self.args = _Args(self._req_args)

        try:
            self.action
        except MissingAction:
            raise MissingAction(f"Action not found for {self.name}") from None

    @property
    def name(self) -> str:
        return self.action.replace(".", "_")

    @property
    def method(self) -> str:
        return self.call["request"]["method"]

    @property
    def action(self) -> str:
        return self.args.action.value

    @property
    def _req_args(self) -> List[Dict[str, str]]:
        if self.method == "GET":
            return self.call["request"]["url"]["query"]
        if self.method == "POST":
            _type = self.call["request"]["body"]["mode"]
            return self.call["request"]["body"][_type]
        raise NoOptionsFound("No options found")

    @property
    def description(self) -> List[str]:
        pattern = r"Description\n-*[\n]*\+?"
        _des = re.sub(pattern, "", self.call["request"].get("description", ""))
        return [x.strip() for x in _des.split("+ ")]

    @property
    def types(self) -> List[str]:
        resp = []
        for arg in self.args.args:
            resp.extend(arg.import_types)
        return resp

    def __str__(self) -> str:
        try:
            return f"Call: {self.name}"
        except MissingAction:
            return f"Call: {self.call.get('name')} (Missing action)"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.call})"

    def get_template_vars(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "method": self.method,
            "description": self.description,
            "action": self.action,
            "args": [x.get_template_vars() for x in self.args.args],
        }
