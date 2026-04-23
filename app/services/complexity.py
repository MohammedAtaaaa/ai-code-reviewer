"""Measure code complexity metrics."""

import ast
import math
from dataclasses import dataclass


@dataclass
class ComplexityResult:
    cyclomatic_complexity: float
    avg_function_complexity: float
    max_function_complexity: float
    maintainability_index: float
    loc: int
    sloc: int
    comment_ratio: float
    function_count: int
    class_count: int


class ComplexityAnalyzer:
    """Computes various complexity metrics for Python source code."""

    def analyze(self, source: str) -> ComplexityResult:
        lines = source.splitlines()
        loc = len(lines)
        sloc = sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))
        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        comment_ratio = comment_lines / max(loc, 1)

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return ComplexityResult(
                cyclomatic_complexity=0,
                avg_function_complexity=0,
                max_function_complexity=0,
                maintainability_index=0,
                loc=loc,
                sloc=sloc,
                comment_ratio=comment_ratio,
                function_count=0,
                class_count=0,
            )

        functions = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        func_complexities = [self._cyclomatic_complexity(fn) for fn in functions]
        total_cc = self._cyclomatic_complexity(tree)

        avg_cc = sum(func_complexities) / max(len(func_complexities), 1)
        max_cc = max(func_complexities, default=0)

        mi = self._maintainability_index(sloc, total_cc, comment_ratio)

        return ComplexityResult(
            cyclomatic_complexity=total_cc,
            avg_function_complexity=round(avg_cc, 2),
            max_function_complexity=max_cc,
            maintainability_index=round(mi, 2),
            loc=loc,
            sloc=sloc,
            comment_ratio=round(comment_ratio, 3),
            function_count=len(functions),
            class_count=len(classes),
        )

    def _cyclomatic_complexity(self, node: ast.AST) -> int:
        """Count decision points: if/elif/for/while/except/and/or/assert/with + 1."""
        complexity = 1
        branch_types = (
            ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While,
            ast.ExceptHandler, ast.Assert, ast.With, ast.AsyncWith,
        )
        for child in ast.walk(node):
            if isinstance(child, branch_types):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _maintainability_index(
        self, sloc: int, cc: int, comment_ratio: float
    ) -> float:
        """Simplified Maintainability Index (0–100 scale)."""

        if sloc == 0:
            return 100.0

        halstead_volume = sloc * math.log2(max(sloc, 1))
        mi = (
            171
            - 5.2 * math.log(max(halstead_volume, 1))
            - 0.23 * cc
            - 16.2 * math.log(max(sloc, 1))
        )
        mi = max(0, mi)
        mi = mi * 100 / 171  # normalize to 0–100

        # Bonus for comments
        mi = min(100, mi + comment_ratio * 10)

        return mi
