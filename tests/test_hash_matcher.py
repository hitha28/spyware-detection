from pathlib import Path

from core.static_analysis.hash_matcher import calculate_sha256


def test_sha256_generation():

    test_file = Path("sample.txt")

    test_file.write_text("Hello SpySentinel")

    file_hash = calculate_sha256(str(test_file))

    assert len(file_hash) == 64

    test_file.unlink()
