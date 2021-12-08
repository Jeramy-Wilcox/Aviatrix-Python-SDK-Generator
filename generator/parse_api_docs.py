import json
import re
from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Union

from jinja2 import FileSystemLoader, StrictUndefined
from jinja2.environment import Environment
from project_types import API, ARGS, PARSED_POSTMAN, SUB_CLASS

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


def parse_items(items: List[Dict[str, Any]]) -> PARSED_POSTMAN:
    api_calls: List[API] = []
    sub_classes: List[SUB_CLASS] = []
    for item in items:
        if item["name"] == "DEPRECATED":
            continue
        try:

            sub_classes.append(
                {
                    "name": sanitize_class_name(item["name"]),
                    "filename": snake_case_name(item["name"]),
                    **parse_items(item["item"]),
                }
            )
        except KeyError:
            api_calls.append(get_params(item))
    return {
        "sub_classes": sub_classes,
        "api_calls": api_calls,
    }


def get_params(api_call: Dict[str, Any]) -> API:
    request = api_call["request"]
    details = {
        "name": snake_case_name(api_call["name"]),
        "method": request["method"],
        "description": parse_description(request["description"]),
    }

    if request["method"] == "POST":
        params = request["body"]["formdata"]
    elif request["method"] == "GET":
        params = request["url"]["query"]
    else:
        params = []

    args = []
    for p in params:
        if p["key"] == "action":
            details["action"] = p["value"]
        elif p["key"] == "CID":
            continue
        else:
            args.append(p)

    if not details["action"]:
        raise KeyError

    details["args"] = get_args(args)
    return details  # type: ignore


def sanitize_class_name(name: str) -> str:
    """ remove all non-alphanumeric characters from the name """
    return re.sub(r"[^\w]", "", name)


def snake_case_name(name: str) -> str:
    """ replace all non-alphanumeric characters with underscores """
    characters_removed = re.sub(r"[^\w]", "_", name)
    duplicate_underscores_removed = re.sub(r"_+", "_", characters_removed)
    trailing_underscores_removed = re.sub(r"_$", "", duplicate_underscores_removed)
    return trailing_underscores_removed.lower()


def parse_description(description: str) -> List[str]:
    pattern = r"Description\n-*[\n]*\+?"
    _des = re.sub(pattern, "", description)
    return [x.strip() for x in _des.split("+ ")]


def parse_arg_name(arg: str) -> str:
    descriptors_removed = arg.split(" ")[0]
    list_notation_removed = descriptors_removed.split("[")[0]
    return list_notation_removed


def parse_examples(example: str) -> str:
    return example.replace('"', "")


def get_args(args: List[Dict[str, str]]) -> List[ARGS]:
    return_args: List[ARGS] = []
    arg_list: List[str] = []
    for arg in args:
        if not arg["key"]:
            continue
        arg_name = parse_arg_name(arg["key"])
        if arg_name in arg_list:
            continue
        arg_list.append(arg_name)
        try:
            des = arg["description"]
        except KeyError:
            return_args.append(
                {
                    "name": arg_name,
                    "type": "Any",
                    "description": "",
                    "required": False,
                    "example": "",
                    "default": "",
                }
            )
        else:
            return_args.append(
                {
                    "name": arg_name,
                    "type": ARG_TYPES.get(get_value("type", des), "Any"),
                    "description": get_value("description", des),
                    "required": get_value("required", des).lower() == "yes",
                    "example": parse_examples(get_value("example", des)),
                    "default": get_value("default", des),
                }
            )
    return return_args


def get_value(pattern: str, description: str) -> str:
    _patterns = {
        "required": r"Required\n(\w*)\n",
        "description": r"Description\n(.*)\n",
        "type": r"Type\n(\w*)\n",
        "example": r"Example\(s\)\n(\S*)\n",
        "default": r"Default Value\n(\W*)\n",
    }
    match = re.search(_patterns[pattern], description, re.MULTILINE)
    if match:
        return match.group(1)
    else:
        return ""


class Templates:
    def __init__(self, template_variables: List[SUB_CLASS]):
        self.data = template_variables
        self.j2_env = Environment(
            autoescape=False,
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
            loader=FileSystemLoader("templates"),
        )

    def render_generated_classes(self, template_variables: List[SUB_CLASS], path: Union[str, PathLike] = ""):
        for x in template_variables:
            _path = Path(path) / x["filename"]
            if x["sub_classes"]:
                # _path = _path / x['filename']
                self.render_template(
                    template_name="class.j2",
                    filename=f"{_path}/__init__.py",
                    template_variables=x,
                )
                self.render_generated_classes(
                    template_variables=x["sub_classes"], path=_path
                )
            else:
                # _path = _path / x["filename"]
                self.render_template(
                    template_name="class.j2",
                    template_variables=x,
                    filename=f"{_path}.py",
                )

    def render_template(
        self,
        template_name: str,
        filename: Union[str, PathLike],
        template_variables: Any = None,
    ):
        if template_variables is None:
            template_variables = {"data": self.data}
        template = self.j2_env.get_template(template_name)
        self.write_to_file(template.render(template_variables), filename)

    def render_list(self, template_list: List[str]):
        for template_name in template_list:
            self.render_template(
                template_name=f"{template_name}.j2", filename=f"{template_name}.py"
            )

    def write_to_file(self, content: str, filename: Union[str, PathLike]):
        filepath = Path(f"../aviatrix/{filename}")
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with filepath.open(mode="w") as f:
            f.write(content)


def main():
    with open("./postman-api.json") as file:
        pm = json.load(file)

    data = parse_items(pm["item"])["sub_classes"]
    with open("parsed_api_values.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

    templates = Templates(data)
    templates.render_list(["__init__", "client", "exceptions", "api_base", "response"])
    templates.render_generated_classes(data)


if __name__ == "__main__":
    main()
