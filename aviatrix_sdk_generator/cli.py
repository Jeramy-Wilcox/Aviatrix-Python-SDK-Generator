import argparse
import json
from logging import getLogger
from os import getenv
from typing import Optional, Sequence

from aviatrix_sdk_generator.groups import Groups
from aviatrix_sdk_generator.template import Templates

logger = getLogger(__name__)


def main(
    api_file_path: Optional[str] = None,
    output_dir: Optional[str] = None,
    debug_file: bool = False,
    debug_file_name: Optional[str] = None,
) -> int:
    if api_file_path is None:
        api_file_path = "./postman-api.json"

    if output_dir is None:
        output_dir = "."

    logger.info(f"Using API file: {api_file_path}")
    with open(api_file_path) as file:
        pm = json.load(file)

    data = Groups(pm).get_template_vars()
    if debug_file:
        if debug_file_name is None:
            debug_file_name = "./debug_parsed_api_values.json"
        with open(debug_file_name, "w") as json_file:
            json.dump(data, json_file, indent=4)

    templates = Templates(data, output_dir)  # type: ignore
    templates.render_list(["__init__", "client", "exceptions", "api_base", "response"])
    templates.render_generated_classes(data)  # type: ignore
    return 0


def cli(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the Aviatrix Python SDK from the Aviatrix API documentation."
        ),
        usage="%(prog)s [options]",
    )
    parser.add_argument(
        "-f",
        "--api-file-path",
        default=getenv("AVIATRIX_API_FILEPATH") or "./postman-api.json",
        help="provide file path to API documentation file (default `%(default)s`).",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=".",
        help="the location of the generated sdk (default `local directory`).",
    )

    parser.add_argument(
        "-d",
        "--debug_file",
        type=bool,
        default=False,
        help="Output the parsed API file to a file for debugging purposes.",
    )

    parser.add_argument(
        "--debug_file_name",
        default="./debug_parsed_api_values.json",
        help="Output location for the parsed API file for debugging purposes.",
    )

    args = parser.parse_args(argv)
    main(
        api_file_path=args.api_file_path,
        output_dir=args.output_dir,
        debug_file=args.debug_file,
        debug_file_name=args.debug_file_name,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
