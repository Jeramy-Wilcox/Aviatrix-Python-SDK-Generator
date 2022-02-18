import sys
from logging import getLogger
from os import PathLike
from pathlib import Path
from typing import Any, List, Union

from jinja2 import FileSystemLoader, StrictUndefined
from jinja2.environment import Environment

logger = getLogger(__name__)


class Templates:
    def __init__(self, template_variables: List[dict], output_dir: str):
        self.output_dir = Path(output_dir) / "aviatrix_sdk"
        logger.info(f"Using output directory: {self.output_dir}")
        self.data = template_variables
        self.j2_env = Environment(
            autoescape=False,
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
            loader=FileSystemLoader(
                [
                    Path(sys.path[0]).parent / "aviatrix_sdk_templates",
                    Path(__file__).parent / "aviatrix_sdk_templates",
                ]
            ),
        )

    def render_generated_classes(
        self, template_variables: List[dict], path: Union[str, PathLike] = ""
    ):
        for x in template_variables:
            _path = Path(path) / x["filename"]
            if x["sub_classes"]:
                self.render_template(
                    template_name="class.j2",
                    filename=f"{_path}/__init__.py",
                    template_variables=x,
                )
                self.render_generated_classes(
                    template_variables=x["sub_classes"], path=_path
                )
            else:
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
        filepath = self.output_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with filepath.open(mode="w") as f:
            f.write(content)
