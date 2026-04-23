"""Detect unused variables and imports using AST analysis."""

import ast
from dataclasses import dataclass


@dataclass
class UnusedItem:
    name: str
    line: int
    kind: str  # "variable" or "import"


class UnusedVarDetector(ast.NodeVisitor):
    """Walks the AST to find variables/imports that are defined but never used."""

    def __init__(self) -> None:
        self._defined: dict[str, tuple[int, str]] = {}
        self._used: set[str] = set()
        self._scope_stack: list[set[str]] = [set()]

    def detect(self, source: str) -> list[UnusedItem]:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []

        self.visit(tree)
        unused = []
        for name, (line, kind) in self._defined.items():
            if name not in self._used and not name.startswith("_"):
                unused.append(UnusedItem(name=name, line=line, kind=kind))
        return unused

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self._defined[name] = (node.lineno, "import")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.name == "*":
                continue
            name = alias.asname if alias.asname else alias.name
            self._defined[name] = (node.lineno, "import")
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._extract_names(target, "variable")
        self.visit(node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.target:
            self._extract_names(node.target, "variable")
        if node.value:
            self.visit(node.value)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self._used.add(node.id)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._defined[node.name] = (node.lineno, "function")
        for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
            self._used.add(arg.arg)
        if node.args.vararg:
            self._used.add(node.args.vararg.arg)
        if node.args.kwarg:
            self._used.add(node.args.kwarg.arg)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._defined[node.name] = (node.lineno, "class")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self.generic_visit(node)

    def _extract_names(self, target: ast.AST, kind: str) -> None:
        if isinstance(target, ast.Name):
            self._defined[target.id] = (target.lineno, kind)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                self._extract_names(elt, kind)
