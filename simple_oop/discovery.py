import logging
import sys
from pathlib import Path

from simple_oop import Config
from simple_oop.types import Type

log = logging.getLogger("simple-oop")


class DiscoveryContext:
    def __init__(self, config: Config):
        self.config = config
        self.types = {}

    def type(self, name) -> Type:
        if name not in self.types:
            self.types[name] = Type(name)

        return self.types[name]

    def print_types(self):
        roots = [t for t in self.types.values() if t.parent is None]
        for r in roots:
            r.print_tree(0)


def require_fields(*requirements: list):
    def impl1(function):
        def impl2(ctxt: DiscoveryContext, match, groups):
            for r in requirements:
                if not (r in groups and groups[r] is not None):
                    return

            function(ctxt, match, groups)

        return impl2

    return impl1


@require_fields("name", "sup")
def subtyping(ctxt: DiscoveryContext, match, groups):
    sub = ctxt.type(groups["name"])
    sup = ctxt.type(groups["sup"])
    sup.add_child(sub)


@require_fields("name", "is_object")
def objecting(ctxt: DiscoveryContext, match, groups):
    t = ctxt.type(groups["name"])
    t.has_instances = True


@require_fields("name", "gen_table")
def tabling(ctxt: DiscoveryContext, match, groups):
    t = ctxt.type(groups["name"])
    t.gen_table = True


def discover_file(ctxt: DiscoveryContext, path: Path):
    if not ctxt.config.file_regex.fullmatch(path.name):
        return
    try:
        string = path.read_text()
    except UnicodeDecodeError:
        log.error(f"Failed to decode file \"{path}\"")
        sys.exit(1)

    possibilities = [subtyping, objecting, tabling]

    for m in ctxt.config.regex.finditer(string):
        groups = m.groupdict()
        for p in possibilities:
            p(ctxt, m, groups)


def discover(ctxt: DiscoveryContext, path: Path):
    if path.is_file():
        discover_file(ctxt, path)
    else:
        for file in path.iterdir():
            discover(ctxt, file)

# def discover_all(string: str) -> list[Superclass]:
#     superclasses = []
#     inheritances = defaultdict(list)
#
#     for m in discovery_re.finditer(string):
#         fields = m.groupdict()
#         if "super_name" in fields and fields["super_name"] is not None:
#             superclasses.append(fields["super_name"])
#         elif "inheritance_name" in fields and fields["inheritance_name"] is not None:
#             sup = fields["inheritance_super"]
#             sub = fields["inheritance_name"]
#             log.debug(f"{sub:5} inherits from {sup}")
#             inheritances[sup].append(sub)
#
#     return [Superclass(s, inheritances[s]) for s in superclasses]
