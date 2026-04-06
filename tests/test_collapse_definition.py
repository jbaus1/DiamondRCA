import pytest

pd = pytest.importorskip("pandas")

from diamond_rca.analysis.collapse_definition import (
    compute_rolling_win_pct,
    detect_threshold_collapse,
    flag_collapse_windows,
)


def test_compute_rolling_win_pct():
    games = pd.DataFrame({"is_win": [1, 0, 1, 0]})
    series = compute_rolling_win_pct(games, window=2)
    assert list(series.round(2)) == [1.0, 0.5, 0.5, 0.5]


def test_flag_collapse_windows():
    games = pd.DataFrame({"is_win": [0, 0, 0, 1, 0, 0]})
    flagged = flag_collapse_windows(games, window=3, threshold=0.34)
    assert "is_collapse_window" in flagged.columns
    assert flagged["is_collapse_window"].any()


def test_detect_threshold_collapse_true():
    games = pd.DataFrame({"is_win": [0] * 10 + [1] * 2})
    result = detect_threshold_collapse(games, window=5, threshold=0.3, min_games_flagged=3)
    assert result is True
