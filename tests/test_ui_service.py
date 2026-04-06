import pytest

pd = pytest.importorskip("pandas")

from diamond_rca.ui import service


def test_build_collapse_analysis_with_mock(monkeypatch):
    sample_games = pd.DataFrame(
        {
            "game_date": pd.to_datetime(["2025-04-01", "2025-04-02", "2025-04-03"]),
            "is_win": [1, 0, 0],
            "opponent": ["MIA", "ATL", "PHI"],
            "result": ["W", "L", "L"],
            "runs_for": [5, 2, 1],
            "runs_against": [3, 4, 6],
        }
    )
    monkeypatch.setattr(service, "fetch_team_game_results", lambda season, team: sample_games)

    result = service.build_collapse_analysis(team="NYM", season=2025, window=2, threshold=0.4)

    assert result.total_games == 3
    assert result.collapse_games >= 1
    assert "rolling_win_pct" in result.games.columns
    assert "is_collapse_window" in result.games.columns


def test_build_collapse_analysis_empty(monkeypatch):
    monkeypatch.setattr(service, "fetch_team_game_results", lambda season, team: pd.DataFrame())

    result = service.build_collapse_analysis(team="NYM", season=2025)

    assert result.total_games == 0
    assert result.collapse_games == 0
    assert result.collapse_rate == 0.0
    assert result.games.empty
