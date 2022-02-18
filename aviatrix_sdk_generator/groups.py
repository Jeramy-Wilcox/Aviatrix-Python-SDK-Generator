from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from aviatrix_sdk_generator.api_call import Call
from aviatrix_sdk_generator.exceptions import MissingAction
from aviatrix_sdk_generator.reducer import CallReducer


class Groups:
    def __init__(self, data: Dict[str, Any], path: Optional[List[str]] = None):
        self.data = data
        self.children: List[Groups] = []
        self._calls: List[Call] = []

        if self.name == "Root":
            self.path = []
        else:
            self.path = [*path, self.file_name] if path else [self.file_name]

        for item in data["item"]:
            if item.get("item"):
                self.children.append(Groups(data=item, path=self.path))
            if item.get("request"):
                try:
                    self._calls.append(Call(item))
                except MissingAction:
                    print(f"Call {item} has no action")
                    continue

        self.calls = CallReducer(self._calls).reduced

    def __str__(self) -> str:
        return f"Group: {self.name} Children: {len(self.children)} Calls: {len(self.calls)}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.data})"

    @property
    def arg_types(self) -> List[str]:
        resp = []
        for call in self.calls:
            resp.extend(call.types)
        return list(set(resp))

    @property
    def name(self) -> str:
        _name = self.data.get("name", "root")
        return re.sub(r"[^\w]", "", _name.title())

    @property
    def file_name(self) -> str:
        """ replace all non-alphanumeric characters with underscores """
        _name = self.data.get("name", "root")
        characters_removed = re.sub(r"[^\w]", "_", _name)
        duplicate_underscores_removed = re.sub(r"_+", "_", characters_removed)
        trailing_underscores_removed = re.sub(r"_$", "", duplicate_underscores_removed)
        return trailing_underscores_removed.lower()

    def get_template_vars(self):
        if self.name == "Root":
            return [x.get_template_vars() for x in self.children]
        else:
            return {
                "name": self.name,
                "filename": self.file_name,
                "path": self.path,
                "arg_types": self.arg_types,
                "sub_classes": [x.get_template_vars() for x in self.children],
                "api_calls": [x.get_template_vars() for x in self.calls],
            }
