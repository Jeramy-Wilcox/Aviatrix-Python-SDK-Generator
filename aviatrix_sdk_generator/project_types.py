from typing import Any, List, TypedDict


class ARGS(TypedDict):
    name: str
    type: str
    description: str
    required: bool
    example: str
    default: str


class API(TypedDict):
    name: str
    method: str
    description: List[str]
    action: str
    args: List[ARGS]


class SUB_CLASS(TypedDict):
    name: str
    filename: str
    path: List[str]
    sub_classes: List[Any]
    api_calls: List[API]


class PARSED_POSTMAN(TypedDict):
    sub_classes: List[SUB_CLASS]
    api_calls: List[API]
