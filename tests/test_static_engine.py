import pytest

from core.static_analysis.static_engine import StaticAnalysisEngine


class FakeHashMatcher:
    def analyze(self, file_path):
        return {"status": "clean", "sha256": "a" * 64, "family": None, "source": None}


class FakeYaraScanner:
    def scan(self, file_path):
        return {"status": "clean", "match_count": 0, "matches": []}


class FakeAPKAnalyzer:
    def analyze(self, file_path):
        return {"status": "analyzed", "package_name": "com.example.app"}


class FakePEAnalyzer:
    def analyze(self, file_path):
        return {"status": "analyzed", "format": "pe"}


def build_engine():
    return StaticAnalysisEngine(FakeHashMatcher(), FakeYaraScanner(), FakeAPKAnalyzer(), FakePEAnalyzer())


def test_static_engine_analyzes_apk_file(tmp_path):
    test_file = tmp_path / "sample.apk"
    test_file.write_text("apk content")
    result = build_engine().analyze(str(test_file))
    assert result["file"] == str(test_file)
    assert result["file_type"] == "apk"
    assert result["hash_matcher"]["status"] == "clean"
    assert result["yara"]["match_count"] == 0
    assert result["analysis"] == {"status": "analyzed", "package_name": "com.example.app"}


@pytest.mark.parametrize("extension", [".exe", ".dll"])
def test_static_engine_analyzes_pe_file(tmp_path, extension):
    test_file = tmp_path / f"sample{extension}"
    test_file.write_text("pe content")
    result = build_engine().analyze(str(test_file))
    assert result["file_type"] == "pe"
    assert result["hash_matcher"]["status"] == "clean"
    assert result["yara"]["status"] == "clean"
    assert result["analysis"] == {"status": "analyzed", "format": "pe"}


def test_static_engine_handles_unknown_file_type(tmp_path):
    test_file = tmp_path / "sample.txt"
    test_file.write_text("plain text")
    result = build_engine().analyze(str(test_file))
    assert result["file_type"] == "unknown"
    assert result["hash_matcher"]["status"] == "clean"
    assert result["yara"]["status"] == "clean"
    assert result["analysis"] == {"status": "unsupported", "reason": "No file-specific analyzer is available for this extension"}


def test_static_engine_raises_for_missing_file():
    with pytest.raises(FileNotFoundError):
        build_engine().analyze("missing.apk")
