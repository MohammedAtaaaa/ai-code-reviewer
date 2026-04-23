"""Detect bad naming conventions using AST analysis."""

import ast
import re
from dataclasses import dataclass

SNAKE_CASE = re.compile(r"^[a-z_][a-z0-9_]*$")
UPPER_SNAKE_CASE = re.compile(r"^[A-Z_][A-Z0-9_]*$")
PASCAL_CASE = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
SINGLE_CHAR = re.compile(r"^[a-zA-Z_]$")

ALLOWED_SHORT_NAMES = {"i", "j", "k", "n", "x", "y", "e", "_", "f", "db"}


@dataclass
class NamingIssue:
    name: str
    line: int
    expected_convention: str
    message: str


class NamingConventionChecker(ast.NodeVisitor):
    """Checks Python naming conventions (PEP 8)."""

    def __init__(self) -> None:
        self.issues: list[NamingIssue] = []

    def check(self, source: str) -> list[NamingIssue]:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []
        self.visit(tree)
        return self.issues

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if not node.name.startswith("_") and not SNAKE_CASE.match(node.name):
            self.issues.append(
                NamingIssue(
                    name=node.name,
                    line=node.lineno,
                    expected_convention="snake_case",
                    message=f"Function '{node.name}' should use snake_case naming.",
                )
            )
        for arg in node.args.args:
            self._check_arg(arg)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if not PASCAL_CASE.match(node.name):
            self.issues.append(
                NamingIssue(
                    name=node.name,
                    line=node.lineno,
                    expected_convention="PascalCase",
                    message=f"Class '{node.name}' should use PascalCase naming.",
                )
            )
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._check_variable(target)
        self.generic_visit(node)

    def _check_variable(self, node: ast.Name) -> None:
        name = node.id
        if name.startswith("_"):
            return
        if UPPER_SNAKE_CASE.match(name) and len(name) > 1:
            return  # constants
        if SNAKE_CASE.match(name):
            return
        if name in ALLOWED_SHORT_NAMES:
            return
        self.issues.append(
            NamingIssue(
                name=name,
                line=node.lineno,
                expected_convention="snake_case",
                message=f"Variable '{name}' should use snake_case naming.",
            )
        )

    def _check_arg(self, arg: ast.arg) -> None:
        name = arg.arg
        if name == "self" or name == "cls" or name.startswith("_"):
            return
        if name in ALLOWED_SHORT_NAMES:
            return
        if not SNAKE_CASE.match(name):
            self.issues.append(
                NamingIssue(
                    name=name,
                    line=arg.lineno,
                    expected_convention="snake_case",
                    message=f"Parameter '{name}' should use snake_case naming.",
                )
            )


def has_descriptive_name(name: str, min_length: int = 3) -> bool:
    """Check if a name is descriptive enough."""
    if name in ALLOWED_SHORT_NAMES or name.startswith("_"):
        return True
    return len(name) >= min_length
