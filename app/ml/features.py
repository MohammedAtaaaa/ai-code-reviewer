"""Extract numerical features from source code for ML classification."""

import ast
import math
import re


def extract_features(source: str) -> dict[str, float]:
    """Extract a feature vector from Python source code."""
    lines = source.splitlines()
    loc = len(lines)
    sloc = sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return _default_features(loc, sloc, blank_lines, comment_lines)

    func_types = (ast.FunctionDef, ast.AsyncFunctionDef)
    functions = [n for n in ast.walk(tree) if isinstance(n, func_types)]
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]

    avg_line_length = sum(len(line) for line in lines) / max(loc, 1)
    max_line_length = max((len(line) for line in lines), default=0)

    cyclomatic = _cyclomatic_complexity(tree)
    max_nesting = _max_nesting(tree)

    func_lengths = [_func_length(f) for f in functions]
    avg_func_length = sum(func_lengths) / max(len(func_lengths), 1)
    max_func_length = max(func_lengths, default=0)

    arg_counts = [_arg_count(f) for f in functions]
    avg_args = sum(arg_counts) / max(len(arg_counts), 1)
    max_args = max(arg_counts, default=0)

    docstring_ratio = sum(1 for f in functions if _has_docstring(f)) / max(len(functions), 1)

    name_violations = _count_name_violations(tree)

    return {
        "loc": loc,
        "sloc": sloc,
        "blank_ratio": blank_lines / max(loc, 1),
        "comment_ratio": comment_lines / max(loc, 1),
        "avg_line_length": avg_line_length,
        "max_line_length": max_line_length,
        "function_count": len(functions),
        "class_count": len(classes),
        "import_count": len(imports),
        "cyclomatic_complexity": cyclomatic,
        "max_nesting_depth": max_nesting,
        "avg_function_length": avg_func_length,
        "max_function_length": max_func_length,
        "avg_args_per_function": avg_args,
        "max_args": max_args,
        "docstring_ratio": docstring_ratio,
        "name_violation_ratio": name_violations / max(len(functions) + len(classes), 1),
        "halstead_volume": sloc * math.log2(max(sloc, 2)),
    }


def feature_names() -> list[str]:
    """Return ordered feature names for the ML model."""
    return [
        "loc",
        "sloc",
        "blank_ratio",
        "comment_ratio",
        "avg_line_length",
        "max_line_length",
        "function_count",
        "class_count",
        "import_count",
        "cyclomatic_complexity",
        "max_nesting_depth",
        "avg_function_length",
        "max_function_length",
        "avg_args_per_function",
        "max_args",
        "docstring_ratio",
        "name_violation_ratio",
        "halstead_volume",
    ]


def _default_features(
    loc: int, sloc: int, blank_lines: int, comment_lines: int
) -> dict[str, float]:
    return {name: 0.0 for name in feature_names()} | {
        "loc": loc,
        "sloc": sloc,
        "blank_ratio": blank_lines / max(loc, 1),
        "comment_ratio": comment_lines / max(loc, 1),
    }


def _cyclomatic_complexity(node: ast.AST) -> int:
    cc = 1
    branch_types = (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler)
    for child in ast.walk(node):
        if isinstance(child, branch_types):
            cc += 1
        elif isinstance(child, ast.BoolOp):
            cc += len(child.values) - 1
    return cc


def _max_nesting(node: ast.AST, depth: int = 0) -> int:
    max_d = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            max_d = max(max_d, _max_nesting(child, depth + 1))
        else:
            max_d = max(max_d, _max_nesting(child, depth))
    return max_d


def _func_length(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    if hasattr(node, "end_lineno") and node.end_lineno:
        return node.end_lineno - node.lineno + 1
    return 0


def _arg_count(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    args = node.args
    count = len(args.args) + len(args.posonlyargs) + len(args.kwonlyargs)
    if args.args and args.args[0].arg in ("self", "cls"):
        count -= 1
    return count


def _has_docstring(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return bool(
        node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
    )


SNAKE = re.compile(r"^[a-z_][a-z0-9_]*$")
PASCAL = re.compile(r"^[A-Z][a-zA-Z0-9]*$")


def _count_name_violations(tree: ast.AST) -> int:
    violations = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_") and not SNAKE.match(node.name):
                violations += 1
        elif isinstance(node, ast.ClassDef) and not PASCAL.match(node.name):
            violations += 1
    return violations
