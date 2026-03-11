# PYTHON_ARGCOMPLETE_OK

import logging
import os
from argparse import ArgumentParser
from pathlib import Path

import argcomplete
import colorama
import mydefaults
from pydantic import ValidationError

from .config import Config, VariableType
from .discovery import discover
from .node import NodeContext
from .version import program_version

colorama.init(autoreset=True)

from .code_gen import TemplateEnvironment  # I put this comment here to stop the line from being moved (professional, I know)

PROGRAM_NAME = "simple-oop"

mydefaults.create_logger(__package__)
log = logging.getLogger(__package__)

colorama.init(autoreset=True)


def command_entry_point():
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Program was interrupted by user")


@mydefaults.sub_command
def generate(parser: ArgumentParser):
    """TODO: add description"""

    parser.add_argument("-w", "--working-directory", type=Path, default=Path(os.getcwd()))
    parser.add_argument("--dump-tree", type=str, default=None)
    parser.add_argument("config", type=Path)

    args = yield

    os.chdir(args.working_directory.resolve())

    assert args.config.exists(), f"File {args.config} does not exist at {os.getcwd()}"
    try:
        c = Config.model_validate_json(args.config.read_text())
    except ValidationError as e:
        print(e)
        return

    if args.verbose:
        log.debug("Using following config:")
        print(c.model_dump_json(indent=4))

    ctx = NodeContext(c)

    discover(ctx, c.input_directories[0])

    if ctx.errors > 0:
        log.error(f"Discovery failed with {ctx.errors} error(s)")
        return

    if args.verbose:
        log.debug("Found the following type structure:")
        ctx.print_types()

    if args.dump_tree is not None:
        assert args.dump_tree in c.variables
        assert c.variables[args.dump_tree] == VariableType.NODE

        roots = [n for n in ctx.nodes.values() if n.variables[args.dump_tree] is None]
        for r in roots:
            r.print_tree(args.dump_tree)

    gen = TemplateEnvironment(ctx)

    for template in c.iter_templates():
        gen.generate(template)


@mydefaults.command(version="2026.3.4")
def main(parser: ArgumentParser):
    """TODO: add description"""

    mydefaults.add_sub_commands(
        parser.add_subparsers(title="Modes", description="Possible modes of operation", required=True))
    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    log.debug("Starting program...")

    mydefaults.run_sub_command(args)
