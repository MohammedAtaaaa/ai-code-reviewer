"""Detect security vulnerabilities and risky patterns in Python code."""

import ast
import re
from dataclasses import dataclass

HARDCODED_SECRET_PATTERNS = [
    re.compile(r"(?i)(password|passwd|pwd|secret|token|api_key|apikey)\s*=\s*['\"][^'\"]+['\"]"),
    re.compile(r"(?i)(aws_access_key|aws_secret)\s*=\s*['\"][^'\"]+['\"]"),
    re.compile(r"['\"](?:sk|pk)[-_](?:live|test)[-_][a-zA-Z0-9]{20,}['\"]"),
]

DANGEROUS_FUNCTIONS = {
    "eval": "eval() executes arbitrary code and is a major security risk.",
    "exec": "exec() executes arbitrary code and can lead to code injection.",
    "compile": "compile() with exec/eval can execute arbitrary code.",
    "__import__": "Dynamic imports can be used for code injection.",
}

DANGEROUS_MODULES = {
    "pickle": "pickle.loads() can execute arbitrary code during deserialization.",
    "subprocess": "subprocess calls can be vulnerable to command injection.",
    "os.system": "os.system() is vulnerable to command injection. Use subprocess with shell=False.",
}

SQL_INJECTION_PATTERNS = [
    re.compile(r'(?:execute|cursor\.execute)\s*\(\s*["\'].*%s'),
    re.compile(r'(?:execute|cursor\.execute)\s*\(\s*f["\']'),
    re.compile(r'(?:execute|cursor\.execute)\s*\(\s*["\'].*\+'),
]


@dataclass
class SecurityIssue:
    rule: str
    severity: str
    line: int | None
    message: str
    recommendation: str


class SecurityChecker:
    """Detects security vulnerabilities in Python source code."""

    def check(self, source: str) -> list[SecurityIssue]:
        issues: list[SecurityIssue] = []
        issues.extend(self._check_dangerous_calls(source))
        issues.extend(self._check_hardcoded_secrets(source))
        issues.extend(self._check_sql_injection(source))
        issues.extend(self._check_dangerous_imports(source))
        issues.extend(self._check_assert_in_production(source))
        return issues

    def _check_dangerous_calls(self, source: str) -> list[SecurityIssue]:
        issues: list[SecurityIssue] = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return issues

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                if func_name in DANGEROUS_FUNCTIONS:
                    issues.append(
                        SecurityIssue(
                            rule=f"dangerous-call-{func_name}",
                            severity="critical",
                            line=node.lineno,
                            message=DANGEROUS_FUNCTIONS[func_name],
                            recommendation=f"Avoid using {func_name}(). "
                            "Use safer alternatives or validate all inputs rigorously.",
                        )
                    )

                if func_name in ("subprocess.Popen", "subprocess.call"):
                    for kw in node.keywords:
                        if (
                            kw.arg == "shell"
                            and isinstance(kw.value, ast.Constant)
                            and kw.value.value is True
                        ):
                            issues.append(
                                SecurityIssue(
                                    rule="shell-injection",
                                    severity="critical",
                                    line=node.lineno,
                                    message="subprocess with shell=True is vulnerable "
                                    "to shell injection attacks.",
                                    recommendation="Use shell=False and pass arguments "
                                    "as a list.",
                                )
                            )
        return issues

    def _check_hardcoded_secrets(self, source: str) -> list[SecurityIssue]:
        issues: list[SecurityIssue] = []
        for line_num, line in enumerate(source.splitlines(), 1):
            for pattern in HARDCODED_SECRET_PATTERNS:
                if pattern.search(line):
                    issues.append(
                        SecurityIssue(
                            rule="hardcoded-secret",
                            severity="critical",
                            line=line_num,
                            message="Possible hardcoded secret detected. "
                            "Secrets should never be committed to source code.",
                            recommendation="Use environment variables or a secrets manager "
                            "(e.g., AWS Secrets Manager, HashiCorp Vault).",
                        )
                    )
                    break  # one flag per line
        return issues

    def _check_sql_injection(self, source: str) -> list[SecurityIssue]:
        issues: list[SecurityIssue] = []
        for line_num, line in enumerate(source.splitlines(), 1):
            for pattern in SQL_INJECTION_PATTERNS:
                if pattern.search(line):
                    issues.append(
                        SecurityIssue(
                            rule="sql-injection",
                            severity="critical",
                            line=line_num,
                            message="Potential SQL injection vulnerability. "
                            "User input appears to be directly interpolated into a SQL query.",
                            recommendation="Use parameterized queries or an ORM.",
                        )
                    )
                    break
        return issues

    def _check_dangerous_imports(self, source: str) -> list[SecurityIssue]:
        issues: list[SecurityIssue] = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return issues

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in DANGEROUS_MODULES:
                        issues.append(
                            SecurityIssue(
                                rule=f"risky-import-{alias.name}",
                                severity="warning",
                                line=node.lineno,
                                message=DANGEROUS_MODULES[alias.name],
                                recommendation="Ensure proper input validation "
                                "when using this module.",
                            )
                        )
            elif (
                isinstance(node, ast.ImportFrom)
                and node.module
                and node.module in DANGEROUS_MODULES
            ):
                issues.append(
                    SecurityIssue(
                        rule=f"risky-import-{node.module}",
                        severity="warning",
                        line=node.lineno,
                        message=DANGEROUS_MODULES[node.module],
                        recommendation="Ensure proper input validation "
                        "when using this module.",
                    )
                )
        return issues

    def _check_assert_in_production(self, source: str) -> list[SecurityIssue]:
        issues: list[SecurityIssue] = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return issues

        assert_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Assert))
        if assert_count > 3:
            issues.append(
                SecurityIssue(
                    rule="excessive-asserts",
                    severity="info",
                    line=None,
                    message=f"Found {assert_count} assert statements. "
                    "Asserts are stripped in optimized mode (-O) and should not "
                    "be used for input validation in production code.",
                    recommendation="Use explicit if/raise for input validation.",
                )
            )
        return issues

    def _get_call_name(self, node: ast.Call) -> str:
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return ""
