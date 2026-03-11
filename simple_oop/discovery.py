import logging
import sys
from pathlib import Path

from colorama import Fore

from .config import Config
from .node import NodeContext

log = logging.getLogger("simple-oop")


def check_match_variables(config: Config, g: dict[str, str], file: Path, match_string: str) -> None:
    if "name" not in g:
        print(f"The regex must always fill the \"name\" field, "
              f"this did not happen in {file} for:\n"
              f"{match_string}")
        raise ValueError()

    for name, value in g.items():
        if name not in config.variables:
            print(f"Any variable used in the regex must be declared in the variables list.\n"
                  f"The variable {Fore.RED}{name}{Fore.RESET} was not declared.")
            raise ValueError()


def parse_match(ctx: NodeContext, file: Path, m) -> None:
    g = m.groupdict()
    match_string = m.string[m.start(0):m.end(0)]

    check_match_variables(ctx.config, g, file, match_string)
    node = ctx.node(g["name"])

    node.declare(file, match_string)

    for name, _type in ctx.config.variables.items():
        node.set_variable(name, g.get(name, None), _type)


def discover_file(ctx: NodeContext, path: Path):
    """Calls parse_match on every match of the regex specified in the config"""

    try:
        string = path.read_text("utf-8")
    except UnicodeDecodeError:
        log.error(f"Failed to decode file \"{path}\" using utf-8")
        sys.exit(1)

    for m in ctx.config.regex.finditer(string):
        try:
            parse_match(ctx, path, m)
        except ValueError as e:
            if str(e) != "":
                raise e
            ctx.errors += 1


def discover(ctx: NodeContext, path: Path):
    for file in path.glob(ctx.config.file_glob):
        if file.is_dir(): continue
        discover_file(ctx, file)
