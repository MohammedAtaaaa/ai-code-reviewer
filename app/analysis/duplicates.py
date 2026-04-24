"""Detect duplicate code patterns using AST structural comparison."""

import ast
from dataclasses import dataclass


@dataclass
class DuplicateBlock:
    lines_a: tuple[int, int]
    lines_b: tuple[int, int]
    similarity: float
    message: str


MIN_BLOCK_SIZE = 3  # minimum statements to consider


class DuplicateDetector:
    """Detects structurally similar code blocks within a single file."""

    def detect(self, source: str) -> list[DuplicateBlock]:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []

        functions = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(functions) < 2:
            return []

        duplicates: list[DuplicateBlock] = []
        seen_pairs: set[tuple[int, int]] = set()

        for i in range(len(functions)):
            for j in range(i + 1, len(functions)):
                fn_a = functions[i]
                fn_b = functions[j]

                if len(fn_a.body) < MIN_BLOCK_SIZE or len(fn_b.body) < MIN_BLOCK_SIZE:
                    continue

                sim = self._structural_similarity(fn_a, fn_b)
                if sim >= 0.8:
                    pair_key = (fn_a.lineno, fn_b.lineno)
                    if pair_key not in seen_pairs:
                        seen_pairs.add(pair_key)
                        duplicates.append(
                            DuplicateBlock(
                                lines_a=(fn_a.lineno, fn_a.end_lineno or fn_a.lineno),
                                lines_b=(fn_b.lineno, fn_b.end_lineno or fn_b.lineno),
                                similarity=sim,
                                message=(
                                    f"Functions '{fn_a.name}' (line {fn_a.lineno}) and "
                                    f"'{fn_b.name}' (line {fn_b.lineno}) are "
                                    f"{sim:.0%} structurally similar. "
                                    "Consider extracting shared logic into a common function."
                                ),
                            )
                        )
        return duplicates

    def _structural_similarity(self, node_a: ast.AST, node_b: ast.AST) -> float:
        dump_a = self._normalize_dump(node_a)
        dump_b = self._normalize_dump(node_b)

        if not dump_a or not dump_b:
            return 0.0

        tokens_a = set(dump_a.split())
        tokens_b = set(dump_b.split())

        intersection = tokens_a & tokens_b
        union = tokens_a | tokens_b

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def _normalize_dump(self, node: ast.AST) -> str:
        """Dump AST with names normalized to detect structural duplicates."""

        class Normalizer(ast.NodeTransformer):
            def visit_Name(self, node: ast.Name) -> ast.Name:
                node.id = "VAR"
                return node

            def visit_Constant(self, node: ast.Constant) -> ast.Constant:
                node.value = "CONST"
                return node

            def visit_arg(self, node: ast.arg) -> ast.arg:
                node.arg = "ARG"
                return node

        import copy

        normalized = Normalizer().visit(copy.deepcopy(node))
        return ast.dump(normalized)
