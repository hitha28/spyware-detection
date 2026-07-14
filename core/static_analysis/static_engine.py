from pathlib import Path

from core.static_analysis.apk_analyzer import APKAnalyzer
from core.static_analysis.hash_matcher import check_hash
from core.static_analysis.yara_scanner import YaraScanner

try:
    from core.static_analysis.pe_analyzer import PEAnalyzer
except ImportError:
    class PEAnalyzer:
        """Placeholder for the future PE analyzer implementation."""
        def analyze(self, file_path: str) -> dict:
            """Raise a clear error until the PE analyzer module exists."""
            raise NotImplementedError("PEAnalyzer is not implemented yet")


class HashMatcher:
    """Adapter for the existing function-based hash matcher."""
    def analyze(self, file_path: str) -> dict:
        """Return the hash matching result for the provided file."""
        return check_hash(file_path)


class StaticAnalysisEngine:
    """Coordinate hash, YARA, and file-specific static analyzers."""
    def __init__(self, hash_matcher=None, yara_scanner=None, apk_analyzer=None, pe_analyzer=None):
        """Instantiate reusable analyzer instances for repeated scans."""
        self.hash_matcher = hash_matcher or HashMatcher()
        self.yara_scanner = yara_scanner or YaraScanner()
        self.apk_analyzer = apk_analyzer or APKAnalyzer()
        self.pe_analyzer = pe_analyzer or PEAnalyzer()

    def analyze(self, file_path: str) -> dict:
        """Run static analysis for a file and return one structured result."""
        target_path = self._validate_file_path(file_path)
        file_type = self._detect_file_type(target_path)
        return {
            "file": str(target_path),
            "file_type": file_type,
            "hash_matcher": self.hash_matcher.analyze(str(target_path)),
            "yara": self.yara_scanner.scan(str(target_path)),
            "analysis": self._run_file_type_analysis(target_path, file_type),
        }

    def _validate_file_path(self, file_path: str) -> Path:
        """Validate that a scan target exists and is a regular file."""
        target_path = Path(file_path)
        if not target_path.exists():
            raise FileNotFoundError(f"File does not exist: {target_path}")
        if not target_path.is_file():
            raise ValueError(f"Path is not a file: {target_path}")
        return target_path

    def _detect_file_type(self, file_path: Path) -> str:
        """Detect apk, pe, or unknown from the file extension."""
        extension = file_path.suffix.lower()
        if extension == ".apk":
            return "apk"
        if extension in {".exe", ".dll"}:
            return "pe"
        return "unknown"

    def _run_file_type_analysis(self, file_path: Path, file_type: str) -> dict:
        """Run the analyzer selected by file type."""
        if file_type == "apk":
            return self.apk_analyzer.analyze(str(file_path))
        if file_type == "pe":
            return self.pe_analyzer.analyze(str(file_path))
        return {"status": "unsupported", "reason": "No file-specific analyzer is available for this extension"}
