import logging
import os
import re
from enum import Enum
from pathlib import Path
from typing import Annotated, Any

from colorama import Fore
from pydantic import BaseModel, ConfigDict, BeforeValidator, AfterValidator

log = logging.getLogger("simple-oop")


def coerce_list_to_str(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        value = "".join(value)
        log.debug(f"Joining regex to {value}")
        return value
    raise ValueError(f"Value {value} is not a string or a list of strings")


def require_exists(path: Path) -> Path:
    path = Path(os.curdir) / path
    assert path.exists(), f"Path {path} does not exist"
    return path


def require_is_dir(path: Path) -> Path:
    assert path.is_dir(), f"Path {path} is not a directory"
    return path


EXTENDED_REGEX = Annotated[re.Pattern, BeforeValidator(coerce_list_to_str)]
PATH_EXISTS = Annotated[Path, AfterValidator(require_exists)]
DIRECTORY_EXISTS = Annotated[PATH_EXISTS, AfterValidator(require_is_dir)]


class VariableType(Enum):
    STRING = "string"
    BOOL = "bool"
    NODE = "node"

    def color(self) -> str:
        match self:
            case self.STRING:
                return Fore.YELLOW
            case self.BOOL:
                return Fore.BLUE
            case self.NODE:
                return Fore.GREEN

    def format(self, value: Any) -> str:
        match self:
            case self.STRING:
                return self.color() + f"{value:>20}" + Fore.RESET
            case self.BOOL:
                return self.color() + f"{str(value):>5}" + Fore.RESET
            case self.NODE:
                return self.color() + f"{str(value):>20}" + Fore.RESET


class Config(BaseModel):
    model_config = ConfigDict(frozen=True)
    regex: EXTENDED_REGEX
    file_regex: EXTENDED_REGEX
    variables: dict[str, VariableType]
    input_directories: list[DIRECTORY_EXISTS]
    output_directory: DIRECTORY_EXISTS
    template_directory: DIRECTORY_EXISTS
    # templates: list[str]
