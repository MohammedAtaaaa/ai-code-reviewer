"""Tests for security checker."""

import textwrap

from app.services.security_checker import SecurityChecker


class TestSecurityChecker:
    def setup_method(self) -> None:
        self.checker = SecurityChecker()

    def test_detects_eval(self) -> None:
        code = "result = eval(user_input)\n"
        issues = self.checker.check(code)
        rules = [i.rule for i in issues]
        assert "dangerous-call-eval" in rules

    def test_detects_exec(self) -> None:
        code = "exec(code_string)\n"
        issues = self.checker.check(code)
        rules = [i.rule for i in issues]
        assert "dangerous-call-exec" in rules

    def test_detects_hardcoded_password(self) -> None:
        code = 'password = "super_secret_123"\n'
        issues = self.checker.check(code)
        rules = [i.rule for i in issues]
        assert "hardcoded-secret" in rules

    def test_detects_hardcoded_api_key(self) -> None:
        code = 'API_KEY = "sk_live_abcdef1234567890abcd"\n'
        issues = self.checker.check(code)
        rules = [i.rule for i in issues]
        assert "hardcoded-secret" in rules

    def test_detects_sql_injection(self) -> None:
        code = textwrap.dedent("""\
            def query(user_id):
                cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
        """)
        issues = self.checker.check(code)
        rules = [i.rule for i in issues]
        assert "sql-injection" in rules

    def test_clean_code_no_issues(self) -> None:
        code = textwrap.dedent("""\
            import logging

            logger = logging.getLogger(__name__)

            def greet(name: str) -> str:
                return f"Hello, {name}!"
        """)
        issues = self.checker.check(code)
        # Should have no critical/error issues
        critical = [i for i in issues if i.severity == "critical"]
        assert len(critical) == 0

    def test_detects_pickle_import(self) -> None:
        code = "import pickle\ndata = pickle.loads(raw)\n"
        issues = self.checker.check(code)
        rules = [i.rule for i in issues]
        assert "risky-import-pickle" in rules

    def test_detects_insecure_hash(self) -> None:
        code = "import hashlib\nh = hashlib.md5(data)\n"
        issues = self.checker.check(code)
        rules = [i.rule for i in issues]
        assert "insecure-hash" in rules

    def test_detects_ssl_verify_disabled(self) -> None:
        code = 'requests.get(url, verify=False)\n'
        issues = self.checker.check(code)
        rules = [i.rule for i in issues]
        assert "ssl-verify-disabled" in rules

    def test_detects_broad_exception(self) -> None:
        code = textwrap.dedent("""\
            try:
                do_something()
            except:
                pass
        """)
        issues = self.checker.check(code)
        rules = [i.rule for i in issues]
        assert "broad-exception" in rules

    def test_detects_shell_injection(self) -> None:
        code = textwrap.dedent("""\
            import subprocess
            subprocess.run(cmd, shell=True)
        """)
        issues = self.checker.check(code)
        rules = [i.rule for i in issues]
        assert "shell-injection" in rules

    def test_detects_insecure_http(self) -> None:
        code = 'url = "http://external-api.com/data"\n'
        issues = self.checker.check(code)
        rules = [i.rule for i in issues]
        assert "insecure-http" in rules

    def test_localhost_http_not_flagged(self) -> None:
        code = 'url = "http://localhost:8000/api"\n'
        issues = self.checker.check(code)
        rules = [i.rule for i in issues]
        assert "insecure-http" not in rules
