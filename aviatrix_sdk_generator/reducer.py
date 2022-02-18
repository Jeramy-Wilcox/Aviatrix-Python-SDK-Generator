from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from aviatrix_sdk_generator.api_call import Call
    from aviatrix_sdk_generator.args import _Arg


class ArgReducer:
    def __init__(self, args: Optional[List[_Arg]] = None):
        self.args = args or []
        self.groups = defaultdict(list)

        if args is not None:
            for arg in args:
                self.groups[arg.key].append(arg)

    def __add(self, arg: _Arg) -> ArgReducer:
        if arg in self.args:
            return self
        self.args.append(arg)
        self.groups[arg.key].append(arg)
        return self

    def add(self, arg: Union[_Arg, List[_Arg]]) -> ArgReducer:
        if isinstance(arg, list):
            for a in arg:
                self.__add(a)
        else:
            self.__add(arg)
        return self

    def member_count(self, group: str) -> int:
        return len(self.groups[group])

    def get_reduced_template_vars(self, call_count: int) -> List[Dict[str, Any]]:
        resp = []
        for group in self.groups.values():
            _vars = group[0].get_template_vars()
            if group[0].required and call_count == len(group):
                _vars["required"] = True
            else:
                _vars["required"] = False
            resp.append(_vars)
        return resp


class ReducedCall:
    def __init__(self, calls: List[Call]):
        self.calls = calls

    @property
    def name(self) -> str:
        return self.calls[0].name

    @property
    def method(self) -> str:
        return self.calls[0].method

    @property
    def action(self) -> str:
        return self.calls[0].action

    @property
    def description(self) -> List[str]:
        return self.calls[0].description

    @property
    def args(self) -> ArgReducer:
        resp = ArgReducer()
        for call in self.calls:
            resp.add(call.args.args)
        return resp

    @property
    def types(self) -> List[str]:
        resp = []
        for call in self.calls:
            resp.extend(call.types)
        return list(set(resp))

    def get_template_vars(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "method": self.method,
            "description": self.description,
            "action": self.action,
            "args": self.args.get_reduced_template_vars(len(self.calls)),
        }


class CallReducer:
    def __init__(self, calls: List[Call]):
        self.calls = calls
        self.groups = defaultdict(list)
        self.reduced: List[ReducedCall] = []

        for call in self.calls:
            self.groups[call.action].append(call)

        for group in self.groups.values():
            if len(group) <= 1:
                self.reduced.extend(group)
            else:
                self.reduced.append(ReducedCall(group))
