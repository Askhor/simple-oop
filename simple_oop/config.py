import json
import logging
import sys
import re
from pathlib import Path

log = logging.getLogger("simple-oop")


class Config:
    def __init__(self, path, data):
        def field(name):
            if name not in data:
                log.error(f"Config missing field {name}")
                sys.exit(1)
            return data[name]

        def check_path(p, must_exist=True, must_be_dir=True):
            p = path / p
            if must_exist and not p.exists():
                log.error(f"Path \"{p}\" does not exist")
                sys.exit(1)
            if must_be_dir and not p.is_dir():
                log.error(f"Path \"{p}\" is not a directory")
                sys.exit(1)
            return p

        def get_regex(name):
            value = field(name)
            if isinstance(value, list):
                value = "".join(value)
                log.debug(f"Joining regex to {value}")
            return re.compile(value, re.ASCII)


        self.regex = get_regex("regex")
        self.file_regex = get_regex("file_regex")
        self.input_directories = [check_path(p) for p in field("input_directories")]
        self.output_directory = check_path(field("output_directory"))

    @classmethod
    def parse(cls, path: Path):
        if not path.exists():
            log.error(f"File \"{path}\" does not exist")
            sys.exit(1)
        with open(path) as f:
            data = json.load(f)
        return cls(path.parent, data)
