"""Tests for static analysis modules."""

import textwrap

from app.analysis.duplicates import DuplicateDetector
from app.analysis.functions import FunctionAnalyzer
from app.analysis.naming import NamingConventionChecker
from app.analysis.unused_vars import UnusedVarDetector


class TestUnusedVarDetector:
    def test_detects_unused_variable(self) -> None:
        code = textwrap.dedent("""\
            x = 1
            y = 2
            print(x)
        """)
        items = UnusedVarDetector().detect(code)
        names = [i.name for i in items]
        assert "y" in names
        assert "x" not in names

    def test_detects_unused_import(self) -> None:
        code = textwrap.dedent("""\
            import os
            import sys
            print(sys.argv)
        """)
        items = UnusedVarDetector().detect(code)
        names = [i.name for i in items]
        assert "os" in names

    def test_ignores_underscore_prefix(self) -> None:
        code = "_unused = 42\n"
        items = UnusedVarDetector().detect(code)
        assert len(items) == 0

    def test_handles_syntax_error(self) -> None:
        items = UnusedVarDetector().detect("def broken(:\n")
        assert items == []


class TestNamingConventionChecker:
    def test_detects_bad_function_name(self) -> None:
        code = "def MyFunction():\n    pass\n"
        issues = NamingConventionChecker().check(code)
        assert len(issues) == 1
        assert issues[0].expected_convention == "snake_case"

    def test_detects_bad_class_name(self) -> None:
        code = "class my_class:\n    pass\n"
        issues = NamingConventionChecker().check(code)
        assert len(issues) == 1
        assert issues[0].expected_convention == "PascalCase"

    def test_accepts_good_naming(self) -> None:
        code = textwrap.dedent("""\
            class UserService:
                def get_user(self):
                    pass
        """)
        issues = NamingConventionChecker().check(code)
        assert len(issues) == 0


class TestFunctionAnalyzer:
    def test_detects_too_many_args(self) -> None:
        code = "def func(a, b, c, d, e, f, g):\n    pass\n"
        issues = FunctionAnalyzer().analyze(code)
        arg_issues = [i for i in issues if i.metric == "arguments"]
        assert len(arg_issues) == 1

    def test_detects_deep_nesting(self) -> None:
        code = textwrap.dedent("""\
            def deep():
                if True:
                    if True:
                        if True:
                            if True:
                                if True:
                                    pass
        """)
        issues = FunctionAnalyzer().analyze(code)
        nesting_issues = [i for i in issues if i.metric == "nesting_depth"]
        assert len(nesting_issues) == 1

    def test_accepts_simple_function(self) -> None:
        code = textwrap.dedent("""\
            def add(a, b):
                return a + b
        """)
        issues = FunctionAnalyzer().analyze(code)
        assert len(issues) == 0


class TestDuplicateDetector:
    def test_detects_similar_functions(self) -> None:
        code = textwrap.dedent("""\
            def process_a(items):
                result = []
                for item in items:
                    if item > 0:
                        result.append(item * 2)
                return result

            def process_b(data):
                output = []
                for d in data:
                    if d > 0:
                        output.append(d * 2)
                return output
        """)
        dups = DuplicateDetector().detect(code)
        assert len(dups) >= 1

    def test_no_false_positive_on_different_functions(self) -> None:
        code = textwrap.dedent("""\
            def add(a, b):
                return a + b

            def multiply(a, b, c, d):
                result = a * b
                result = result * c
                result = result * d
                return result
        """)
        dups = DuplicateDetector().detect(code)
        assert len(dups) == 0
