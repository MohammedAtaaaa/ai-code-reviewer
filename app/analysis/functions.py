"""Detect overly long or complex functions."""

import ast
from dataclasses import dataclass


@dataclass
class FunctionIssue:
    name: str
    line: int
    metric: str
    value: int
    threshold: int
    message: str


MAX_FUNCTION_LINES = 50
MAX_FUNCTION_ARGS = 5
MAX_NESTING_DEPTH = 4
MAX_RETURN_STATEMENTS = 5


class FunctionAnalyzer(ast.NodeVisitor):
    """Analyzes functions for length, argument count, nesting depth, and return count."""

    def __init__(self) -> None:
        self.issues: list[FunctionIssue] = []

    def analyze(self, source: str) -> list[FunctionIssue]:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []
        self.visit(tree)
        return self.issues

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def _check_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        func_lines = self._count_lines(node)
        if func_lines > MAX_FUNCTION_LINES:
            self.issues.append(
                FunctionIssue(
                    name=node.name,
                    line=node.lineno,
                    metric="lines",
                    value=func_lines,
                    threshold=MAX_FUNCTION_LINES,
                    message=(
                        f"Function '{node.name}' is {func_lines} lines long "
                        f"(max recommended: {MAX_FUNCTION_LINES}). "
                        "Consider breaking it into smaller functions."
                    ),
                )
            )

        arg_count = self._count_args(node)
        if arg_count > MAX_FUNCTION_ARGS:
            self.issues.append(
                FunctionIssue(
                    name=node.name,
                    line=node.lineno,
                    metric="arguments",
                    value=arg_count,
                    threshold=MAX_FUNCTION_ARGS,
                    message=(
                        f"Function '{node.name}' has {arg_count} parameters "
                        f"(max recommended: {MAX_FUNCTION_ARGS}). "
                        "Consider using a configuration object or splitting the function."
                    ),
                )
            )

        nesting = self._max_nesting_depth(node)
        if nesting > MAX_NESTING_DEPTH:
            self.issues.append(
                FunctionIssue(
                    name=node.name,
                    line=node.lineno,
                    metric="nesting_depth",
                    value=nesting,
                    threshold=MAX_NESTING_DEPTH,
                    message=(
                        f"Function '{node.name}' has a nesting depth of {nesting} "
                        f"(max recommended: {MAX_NESTING_DEPTH}). "
                        "Consider extracting nested logic into helper functions."
                    ),
                )
            )

        returns = self._count_returns(node)
        if returns > MAX_RETURN_STATEMENTS:
            self.issues.append(
                FunctionIssue(
                    name=node.name,
                    line=node.lineno,
                    metric="return_statements",
                    value=returns,
                    threshold=MAX_RETURN_STATEMENTS,
                    message=(
                        f"Function '{node.name}' has {returns} return statements "
                        f"(max recommended: {MAX_RETURN_STATEMENTS}). "
                        "Consider simplifying the control flow."
                    ),
                )
            )

    def _count_lines(self, node: ast.AST) -> int:
        if hasattr(node, "end_lineno") and node.end_lineno and hasattr(node, "lineno"):
            return node.end_lineno - node.lineno + 1
        return 0

    def _count_args(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
        args = node.args
        count = len(args.args) + len(args.posonlyargs) + len(args.kwonlyargs)
        if args.vararg:
            count += 1
        if args.kwarg:
            count += 1
        # Don't count 'self' or 'cls'
        if args.args and args.args[0].arg in ("self", "cls"):
            count -= 1
        return count

    def _max_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._max_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._max_nesting_depth(child, depth)
                max_depth = max(max_depth, child_depth)
        return max_depth

    def _count_returns(self, node: ast.AST) -> int:
        count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                count += 1
        return count
