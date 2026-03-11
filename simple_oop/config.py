import logging
import os
import re
from enum import Enum
from pathlib import Path
from typing import Annotated, Any, Tuple, Iterator, Optional

from colorama import Fore
from pydantic import BaseModel, ConfigDict, BeforeValidator, AfterValidator, model_validator

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


def require_is_file(path: Path) -> Path:
    assert path.is_file(), f"Path {path} is not a file"
    return path


EXTENDED_REGEX = Annotated[re.Pattern, BeforeValidator(coerce_list_to_str)]
PATH_EXISTS = Annotated[Path, AfterValidator(require_exists)]
DIRECTORY_EXISTS = Annotated[PATH_EXISTS, AfterValidator(require_is_dir)]


class VariableType(Enum):
    STRING = "string"
    BOOL = "bool"
    NODE = "node"

    def default(self) -> Any:
        match self:
            case self.BOOL:
                return False
            case _:
                return None

    def color(self) -> str:
        match self:
            case self.STRING:
                return Fore.YELLOW
            case self.BOOL:
                return Fore.BLUE
            case self.NODE:
                return Fore.GREEN

    def format(self, name: str, value: Any) -> str:
        match self:
            case self.STRING:
                return f"{self.color()}{value}{Fore.RESET} ({name}) "
            case self.BOOL:
                assert isinstance(value, bool), f"Value {value} is not a bool for field {name}"
                if value:
                    return f"{self.color()}{name}{Fore.RESET} "
                else:
                    return ""
            case self.NODE:
                return f"{self.color()}{name}->{str(value)}{Fore.RESET}"


class TemplateConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    file: Path
    name: str
    foreach: Optional[str]


class Config(BaseModel):
    model_config = ConfigDict(frozen=True)

    # Regexes/Globs
    file_glob: str
    regex: EXTENDED_REGEX

    # The variables allowed in the regex
    variables: dict[str, VariableType]

    # Important directories
    input_directories: list[DIRECTORY_EXISTS]
    output_directory: DIRECTORY_EXISTS
    template_directory: DIRECTORY_EXISTS

    # Templates (either a file path or a more complex dict)
    templates: list[str | TemplateConfig]

    def iter_templates(self) -> Iterator[TemplateConfig]:
        for t in self.templates:
            if isinstance(t, TemplateConfig):
                yield t
            else:
                yield TemplateConfig(file=Path(t), name=t, foreach=None)

    @model_validator(mode="after")
    def check_template_files_exist(self):
        t_dir = self.template_directory

        for t in self.templates:
            try:
                assert (t_dir / t.file).exists(), f"Template file {t_dir / t.file} does not exist"
            except AttributeError:
                assert (t_dir / t).exists(), f"Template file {t_dir / t} does not exist"

        return self
