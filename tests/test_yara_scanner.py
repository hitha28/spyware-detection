from core.static_analysis.yara_scanner import YaraScanner


def test_yara_rules_compile_successfully():
    scanner = YaraScanner()

    assert scanner.compiled_rules is not None
    assert scanner.rule_files


def test_yara_scanner_detects_known_family(tmp_path):
    test_file = tmp_path / "sample.txt"
    test_file.write_text("Pegasus is spyware")

    scanner = YaraScanner()
    result = scanner.scan(str(test_file))

    assert result["status"] == "matched"
    assert result["match_count"] >= 1
    assert any(match["rule"] == "Known_Spyware_Family" for match in result["matches"])


def test_yara_scanner_returns_clean_result(tmp_path):
    test_file = tmp_path / "clean.txt"
    test_file.write_text("This file does not contain any known malware markers.")

    scanner = YaraScanner()
    result = scanner.scan(str(test_file))

    assert result == {
        "status": "clean",
        "match_count": 0,
        "matches": [],
    }
