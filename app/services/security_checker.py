"""Detect security vulnerabilities and risky patterns in Python code."""

import ast
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

HARDCODED_SECRET_PATTERNS = [
    re.compile(
        r"(?i)(password|passwd|pwd|secret|token|api_key|apikey)\s*=\s*['\"][^'\"]+['\"]"
    ),
    re.compile(r"(?i)(aws_access_key|aws_secret)\s*=\s*['\"][^'\"]+['\"]"),
    re.compile(r"['\"](?:sk|pk)[-_](?:live|test)[-_][a-zA-Z0-9]{20,}['\"]"),
    re.compile(r"(?i)(database_url|db_password|db_pass)\s*=\s*['\"][^'\"]+['\"]"),
    re.compile(r"(?i)(private_key|ssh_key)\s*=\s*['\"][^'\"]+['\"]"),
    re.compile(r"(?i)bearer\s+[a-zA-Z0-9\-_.]{20,}"),
]

DANGEROUS_FUNCTIONS = {
    "eval": "eval() executes arbitrary code and is a major security risk.",
    "exec": "exec() executes arbitrary code and can lead to code injection.",
    "compile": "compile() with exec/eval can execute arbitrary code.",
    "__import__": "Dynamic imports can be used for code injection.",
    "globals": "globals() exposes the global symbol table — avoid dynamic access.",
    "setattr": "setattr() can modify any attribute — validate inputs carefully.",
    "getattr": "getattr() with user input can access unexpected attributes.",
}

DANGEROUS_MODULES = {
    "pickle": "pickle.loads() can execute arbitrary code during deserialization.",
    "subprocess": "subprocess calls can be vulnerable to command injection.",
    "os.system": "os.system() is vulnerable to command injection. "
    "Use subprocess with shell=False.",
    "marshal": "marshal can execute arbitrary code on load.",
    "shelve": "shelve uses pickle internally — same deserialization risks.",
    "tempfile": "Ensure tempfile usage is secure — avoid predictable names.",
}

SQL_INJECTION_PATTERNS = [
    re.compile(r'(?:execute|cursor\.execute)\s*\(\s*["\'].*%s'),
    re.compile(r'(?:execute|cursor\.execute)\s*\(\s*f["\']'),
    re.compile(r'(?:execute|cursor\.execute)\s*\(\s*["\'].*\+'),
    re.compile(r'(?:execute|cursor\.execute)\s*\(\s*["\'].*\.format\('),
]

INSECURE_CRYPTO_PATTERNS = [
    re.compile(r"(?i)\b(?:md5|sha1)\s*\("),
    re.compile(r"(?i)hashlib\.\s*(?:md5|sha1)\s*\("),
]

INSECURE_NETWORK_PATTERNS = [
    re.compile(r"verify\s*=\s*False"),
    re.compile(r"http://(?!localhost|127\.0\.0\.1)"),
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
        issues.extend(self._check_insecure_crypto(source))
        issues.extend(self._check_insecure_network(source))
        issues.extend(self._check_broad_exception(source))
        logger.debug("Security check: %d issues found", len(issues))
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

                if func_name in ("subprocess.Popen", "subprocess.call", "subprocess.run"):
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

                # open() without explicit mode
                if func_name == "open":
                    has_mode = any(
                        kw.arg == "mode" for kw in node.keywords
                    ) or len(node.args) >= 2
                    if not has_mode:
                        issues.append(
                            SecurityIssue(
                                rule="open-no-mode",
                                severity="info",
                                line=node.lineno,
                                message="open() called without explicit mode — "
                                "defaults to read, but explicit is clearer.",
                                recommendation="Specify the mode parameter explicitly.",
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
                            "User input appears to be directly interpolated "
                            "into a SQL query.",
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

    def _check_insecure_crypto(self, source: str) -> list[SecurityIssue]:
        issues: list[SecurityIssue] = []
        for line_num, line in enumerate(source.splitlines(), 1):
            for pattern in INSECURE_CRYPTO_PATTERNS:
                if pattern.search(line):
                    issues.append(
                        SecurityIssue(
                            rule="insecure-hash",
                            severity="warning",
                            line=line_num,
                            message="Use of weak hashing algorithm (MD5/SHA1). "
                            "These are cryptographically broken.",
                            recommendation="Use SHA-256 or stronger. "
                            "For passwords, use bcrypt/scrypt/argon2.",
                        )
                    )
                    break
        return issues

    def _check_insecure_network(self, source: str) -> list[SecurityIssue]:
        issues: list[SecurityIssue] = []
        for line_num, line in enumerate(source.splitlines(), 1):
            if re.search(r"verify\s*=\s*False", line):
                issues.append(
                    SecurityIssue(
                        rule="ssl-verify-disabled",
                        severity="critical",
                        line=line_num,
                        message="SSL verification is disabled (verify=False). "
                        "This makes the connection vulnerable to MITM attacks.",
                        recommendation="Enable SSL verification or use a trusted CA bundle.",
                    )
                )
            if re.search(r"http://(?!localhost|127\.0\.0\.1)", line):
                issues.append(
                    SecurityIssue(
                        rule="insecure-http",
                        severity="warning",
                        line=line_num,
                        message="Non-localhost HTTP URL detected. "
                        "Use HTTPS for secure communication.",
                        recommendation="Replace http:// with https:// for external URLs.",
                    )
                )
        return issues

    def _check_broad_exception(self, source: str) -> list[SecurityIssue]:
        issues: list[SecurityIssue] = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return issues

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(
                    SecurityIssue(
                        rule="broad-exception",
                        severity="info",
                        line=node.lineno,
                        message="Bare 'except:' catches all exceptions including "
                        "SystemExit and KeyboardInterrupt.",
                        recommendation="Catch specific exceptions, "
                        "e.g., 'except ValueError:'.",
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
