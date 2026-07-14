import math
from collections import Counter
from pathlib import Path

# API imports commonly abused by spyware/stalkerware for keylogging,
# screen capture, credential theft, or code injection. Not exhaustive —
# meant as a fast, explainable first pass, same spirit as the YARA rules.
SUSPICIOUS_IMPORTS = {
    # Keylogging
    "SetWindowsHookExA": "keylogging (global keyboard/mouse hook)",
    "SetWindowsHookExW": "keylogging (global keyboard/mouse hook)",
    "GetAsyncKeyState": "keylogging (polls key state)",
    "GetKeyState": "keylogging (polls key state)",
    "GetKeyboardState": "keylogging (reads full keyboard state)",
    # Screen capture
    "BitBlt": "screen capture",
    "GetDC": "screen capture (device context access)",
    "CreateCompatibleBitmap": "screen capture",
    # Credential / clipboard theft
    "GetClipboardData": "clipboard monitoring",
    "CredEnumerateA": "credential store access",
    "CredEnumerateW": "credential store access",
    # Process injection
    "CreateRemoteThread": "process injection",
    "WriteProcessMemory": "process injection",
    "VirtualAllocEx": "process injection",
    "NtUnmapViewOfSection": "process hollowing",
    # Network exfiltration
    "InternetOpenA": "network exfiltration (WinINet)",
    "InternetOpenW": "network exfiltration (WinINet)",
    "URLDownloadToFileA": "remote payload download",
    "URLDownloadToFileW": "remote payload download",
    # Persistence
    "RegSetValueExA": "registry persistence",
    "RegSetValueExW": "registry persistence",
}

# Section names associated with common packers/obfuscators. A packed file
# hides its real imports, which is itself a spyware-friendly evasion trick.
KNOWN_PACKER_SECTIONS = {
    "upx0", "upx1", "upx2", ".aspack", ".adata", ".petite", ".themida",
}

HIGH_ENTROPY_THRESHOLD = 7.2  # out of 8.0 max; packed/encrypted data runs hot


class PEAnalyzer:
    """Extract static metadata and indicators from Windows PE files (.exe/.dll)."""

    def analyze(self, file_path: str) -> dict:
        """
        Analyze a Windows PE file without executing it.

        Args:
            file_path: Path to the .exe/.dll file.

        Returns:
            A structured dictionary containing imports, sections, and
            packer/suspicious-API indicators.

        Raises:
            FileNotFoundError: If the file path does not exist.
            ValueError: If the path is not a file or is not a valid PE.
            RuntimeError: If pefile is not installed.
        """
        pe_path = self._validate_pe_path(file_path)
        pe = self._load_pe(pe_path)

        try:
            imported_functions = self._extract_imports(pe)
            sections = self._extract_sections(pe)
            suspicious = self._flag_suspicious_imports(imported_functions)
            packer_suspected = self._detect_packer(sections)

            return {
                "status": "analyzed",
                "file_path": str(pe_path),
                "is_dll": pe.is_dll(),
                "entry_point": hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint),
                "imported_dlls": sorted({f["dll"] for f in imported_functions}),
                "suspicious_imports": suspicious,
                "sections": sections,
                "packer_suspected": packer_suspected,
            }
        finally:
            pe.close()

    def _validate_pe_path(self, file_path: str) -> Path:
        """Validate that the provided PE path exists and points to a file."""
        pe_path = Path(file_path)

        if not pe_path.exists():
            raise FileNotFoundError(f"PE file does not exist: {pe_path}")

        if not pe_path.is_file():
            raise ValueError(f"PE path is not a file: {pe_path}")

        return pe_path

    def _load_pe(self, pe_path: Path):
        """Load a PE file with pefile for static analysis."""
        try:
            import pefile
        except ImportError as exc:
            raise RuntimeError("pefile is required for PE analysis") from exc

        try:
            return pefile.PE(str(pe_path))
        except pefile.PEFormatError as exc:
            raise ValueError(f"Invalid PE file: {pe_path}") from exc

    def _extract_imports(self, pe) -> list:
        """
        Extract every imported (dll, function_name) pair.

        Args:
            pe: A loaded pefile.PE object.

        Returns:
            A list of {"dll": str, "function": str} dicts. Empty if the
            file has no import table (unusual, but not itself invalid).
        """
        imports = []
        if not hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
            return imports

        for entry in pe.DIRECTORY_ENTRY_IMPORT:
            dll_name = entry.dll.decode("utf-8", errors="ignore")
            for imp in entry.imports:
                if imp.name:
                    imports.append({
                        "dll": dll_name,
                        "function": imp.name.decode("utf-8", errors="ignore"),
                    })
        return imports

    def _flag_suspicious_imports(self, imported_functions: list) -> list:
        """
        Cross-reference imported functions against the known-suspicious list.

        Args:
            imported_functions: Output of _extract_imports().

        Returns:
            A sorted list of {"function", "dll", "reason"} dicts, one per
            suspicious import actually found (no duplicates).
        """
        seen = set()
        flagged = []
        for imp in imported_functions:
            func = imp["function"]
            if func in SUSPICIOUS_IMPORTS and func not in seen:
                seen.add(func)
                flagged.append({
                    "function": func,
                    "dll": imp["dll"],
                    "reason": SUSPICIOUS_IMPORTS[func],
                })
        return sorted(flagged, key=lambda item: item["function"])

    def _extract_sections(self, pe) -> list:
        """
        Extract per-section metadata, including Shannon entropy.

        Args:
            pe: A loaded pefile.PE object.

        Returns:
            A list of {"name", "entropy", "size", "executable", "writable"}
            dicts, one per PE section.
        """
        sections = []
        for section in pe.sections:
            name = section.Name.decode("utf-8", errors="ignore").strip("\x00")
            data = section.get_data()
            sections.append({
                "name": name,
                "entropy": round(self._shannon_entropy(data), 2),
                "size": len(data),
                "executable": bool(section.Characteristics & 0x20000000),
                "writable": bool(section.Characteristics & 0x80000000),
            })
        return sections

    def _shannon_entropy(self, data: bytes) -> float:
        """
        Compute Shannon entropy (0.0-8.0) of a byte string.

        High entropy (> ~7.2) suggests packed or encrypted content, since
        genuine compiled code/data is rarely that random-looking.

        Args:
            data: Raw section bytes.

        Returns:
            Entropy in bits per byte, 0.0 for empty input.
        """
        if not data:
            return 0.0

        counts = Counter(data)
        length = len(data)
        return -sum(
            (count / length) * math.log2(count / length)
            for count in counts.values()
        )

    def _detect_packer(self, sections: list) -> bool:
        """
        Heuristically flag whether the file looks packed/obfuscated.

        Args:
            sections: Output of _extract_sections().

        Returns:
            True if a known packer section name or high-entropy executable
            section is found, else False.
        """
        for section in sections:
            if section["name"].lower() in KNOWN_PACKER_SECTIONS:
                return True
            if section["executable"] and section["entropy"] >= HIGH_ENTROPY_THRESHOLD:
                return True
        return False
