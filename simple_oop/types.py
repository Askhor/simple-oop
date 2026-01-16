import logging

from .terminal_formatting import parse_color

log = logging.getLogger("simple-oop")


class Type:
    def __init__(self, name):
        if name is None:
            raise ValueError("Name cannot be None")
        self.name = name
        self.parent = None
        self.indirect_children = set()
        self.children = set()
        self.has_instances = False
        self.gen_table = False

    def add_indirect_child(self, child):
        self.indirect_children.add(child)

        if self.parent is not None:
            self.parent.add_indirect_child(child)

    def add_child(self, child, ):
        self.children.add(child)
        self.add_indirect_child(child)

        if child.parent is not None:
            log.error(f"{child} already has the parent {child.parent} and cannot also have {self} as parent")
            sys.exit(1)
        child.parent = self

    def print_tree(self, indent):
        name = self.name
        if self.parent is None:
            name = parse_color(f"ℂ1.{name}ℂ.")

        print(" " * 2 * indent + name
              + (parse_color(" ℂ3.has instancesℂ.") if self.has_instances else "")
              + (parse_color(" ℂ4.generate tableℂ.") if self.gen_table else ""))
        for t in self.children:
            t.print_tree(indent + 1)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name
