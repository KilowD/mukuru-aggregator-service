from pathlib import Path

import pytest

from mukuru_aggregator.extraction.excel import _validate_file


def test_validate_file_exists(tmp_path: Path) -> None:
    test_file = tmp_path / "test.xlsx"

    test_file.touch()

    _validate_file(test_file)