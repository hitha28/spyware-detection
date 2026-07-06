from pathlib import Path

import yara


RULES_DIR = Path(__file__).resolve().parent / "yara_rules"


class YaraScanner:
    """Compile and reuse YARA rules for static file scanning."""

    def __init__(self):
        """Discover and compile all YARA rule files once for reuse."""

        self.rule_files = self._discover_rule_files()
        self.compiled_rules = self._compile_rules(self.rule_files)

    def scan(self, file_path: str) -> dict:
        """
        Scan a file using the compiled YARA rules.

        Args:
            file_path: Path to the file that should be scanned.

        Returns:
            A structured dictionary containing scan status, match count,
            and formatted match details.

        Raises:
            FileNotFoundError: If the scan target does not exist.
            ValueError: If the scan target is not a file.
            RuntimeError: If YARA fails while scanning the file.
        """

        target_path = Path(file_path)

        if not target_path.exists():
            raise FileNotFoundError(f"Scan target does not exist: {target_path}")

        if not target_path.is_file():
            raise ValueError(f"Scan target is not a file: {target_path}")

        try:
            matches = self.compiled_rules.match(str(target_path))
        except yara.Error as exc:
            raise RuntimeError(f"Failed to scan file with YARA: {target_path}") from exc

        return self._format_results(matches)

    def _format_results(self, matches) -> dict:
        """
        Convert YARA match objects into an API-friendly dictionary.

        Args:
            matches: Iterable of YARA Match objects returned by yara-python.

        Returns:
            A dictionary containing the normalized scan result.
        """

        formatted_matches = [
            {
                "rule": match.rule,
                "tags": list(match.tags),
                "meta": dict(match.meta),
            }
            for match in matches
        ]

        return {
            "status": "matched" if formatted_matches else "clean",
            "match_count": len(formatted_matches),
            "matches": formatted_matches,
        }

    def _discover_rule_files(self) -> dict:
        """
        Discover all .yar files in the static analysis rules directory.

        Returns:
            A dictionary mapping rule namespaces to rule file paths.

        Raises:
            FileNotFoundError: If the rules directory or rule files are missing.
        """

        if not RULES_DIR.exists():
            raise FileNotFoundError(f"YARA rules directory not found: {RULES_DIR}")

        rule_files = {
            rule_file.stem: str(rule_file)
            for rule_file in sorted(RULES_DIR.glob("*.yar"))
        }

        if not rule_files:
            raise FileNotFoundError(f"No YARA rule files found in {RULES_DIR}")

        return rule_files

    def _compile_rules(self, rule_files: dict):
        """
        Compile discovered YARA rule files.

        Args:
            rule_files: Dictionary of rule namespaces and file paths.

        Returns:
            A compiled yara.Rules object.

        Raises:
            RuntimeError: If YARA cannot compile the discovered rules.
        """

        try:
            return yara.compile(filepaths=rule_files)
        except yara.Error as exc:
            raise RuntimeError("Failed to compile YARA rules") from exc
