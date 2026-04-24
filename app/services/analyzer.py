"""Orchestrates all static analysis checks into a unified result."""

from dataclasses import dataclass, field

from app.analysis.duplicates import DuplicateBlock, DuplicateDetector
from app.analysis.functions import FunctionAnalyzer, FunctionIssue
from app.analysis.naming import NamingConventionChecker, NamingIssue
from app.analysis.unused_vars import UnusedItem, UnusedVarDetector
from app.services.complexity import ComplexityAnalyzer, ComplexityResult
from app.services.security_checker import SecurityChecker, SecurityIssue


@dataclass
class AnalysisResult:
    unused_items: list[UnusedItem] = field(default_factory=list)
    naming_issues: list[NamingIssue] = field(default_factory=list)
    function_issues: list[FunctionIssue] = field(default_factory=list)
    duplicates: list[DuplicateBlock] = field(default_factory=list)
    security_issues: list[SecurityIssue] = field(default_factory=list)
    complexity: ComplexityResult | None = None

    @property
    def total_issues(self) -> int:
        return (
            len(self.unused_items)
            + len(self.naming_issues)
            + len(self.function_issues)
            + len(self.duplicates)
            + len(self.security_issues)
        )


class CodeAnalyzer:
    """Runs all analysis passes on submitted code."""

    def __init__(self) -> None:
        self._unused_detector = UnusedVarDetector()
        self._naming_checker = NamingConventionChecker()
        self._function_analyzer = FunctionAnalyzer()
        self._duplicate_detector = DuplicateDetector()
        self._security_checker = SecurityChecker()
        self._complexity_analyzer = ComplexityAnalyzer()

    def analyze(self, source: str, language: str = "python") -> AnalysisResult:
        if language != "python":
            return AnalysisResult(
                complexity=self._complexity_analyzer.analyze(source),
            )

        return AnalysisResult(
            unused_items=UnusedVarDetector().detect(source),
            naming_issues=NamingConventionChecker().check(source),
            function_issues=FunctionAnalyzer().analyze(source),
            duplicates=self._duplicate_detector.detect(source),
            security_issues=self._security_checker.check(source),
            complexity=self._complexity_analyzer.analyze(source),
        )
