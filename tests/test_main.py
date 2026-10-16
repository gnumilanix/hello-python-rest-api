"""Tests for the main module."""

from bowtie.main import main


def test_main_runs(capsys) -> None:
    main()
    captured = capsys.readouterr()
    assert "bowtie" in captured.out
