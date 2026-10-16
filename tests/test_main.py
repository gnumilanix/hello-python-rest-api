"""Tests for the main module."""

from necktie.main import main


def test_main_runs(capsys) -> None:
    main()
    captured = capsys.readouterr()
    assert "necktie" in captured.out
