import argparse
import logging
from pathlib import Path

from .config import Config
from .discovery import discover, DiscoveryContext
from .terminal_formatting import parse_color
from .version import program_version

PROGRAM_NAME = "simple-oop"

log = logging.getLogger(PROGRAM_NAME)
console = logging.StreamHandler()
log.addHandler(console)
log.setLevel(logging.DEBUG)
console.setFormatter(
    logging.Formatter(parse_color("{asctime} [ℂ3.{levelname:>5}ℂ.] ℂ4.{name}ℂ.: {message}"),
                      style="{", datefmt="W%W %a %I:%M"))


def command_entry_point():
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Program was interrupted by user")


def main():
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME,
                                     description="Placeholder description",
                                     allow_abbrev=True, add_help=True, exit_on_error=True)

    parser.add_argument('-v', '--verbose', action='store_true', help="Show more output")
    parser.add_argument("--version", action="store_true", help="Show the current version of the program")
    parser.add_argument("-i", "--input", default=".")
    parser.add_argument("-o", "--output", default="-")

    args = parser.parse_args()

    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    log.debug("Starting program...")

    if args.version:
        log.info(f"{PROGRAM_NAME} version {program_version}")
        return

    c = Config.parse(Path("../../WS24/Bert/soop.json"))
    ctxt = DiscoveryContext(c)

    discover(ctxt, c.input_directories[0])

    if args.verbose:
        log.debug("Found the following type structure:")
        ctxt.print_types()

    
