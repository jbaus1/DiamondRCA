import pytest

pd = pytest.importorskip("pandas")

from diamond_rca.data import extract


def test_fetch_team_batting_data_with_mock(monkeypatch):
    sample = pd.DataFrame({"Team": ["NYM", "ATL"], "OPS": [0.700, 0.750]})
    monkeypatch.setattr(extract, "batting_stats", lambda season, qual=0: sample)

    result = extract.fetch_team_batting_data(2025, "NYM")

    assert not result.empty
    assert (result["Team"] == "NYM").all()


def test_fetch_team_pitching_data_with_mock(monkeypatch):
    sample = pd.DataFrame({"Team": ["NYM", "ATL"], "ERA": [3.8, 3.5]})
    monkeypatch.setattr(extract, "pitching_stats", lambda season, qual=0: sample)

    result = extract.fetch_team_pitching_data(2025, "NYM")

    assert not result.empty
    assert (result["Team"] == "NYM").all()


def test_fetch_statcast_data_with_mock(monkeypatch):
    sample = pd.DataFrame({"game_date": ["2025-06-01"], "events": ["single"]})
    monkeypatch.setattr(extract, "statcast", lambda start_dt, end_dt: sample)

    result = extract.fetch_statcast_data("2025-06-01", "2025-06-02")

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1


def test_fetch_team_game_results_with_mock(monkeypatch):
    sample = pd.DataFrame(
        {
            "Date": ["Apr 01", "Apr 02"],
            "Opp": ["MIA", "ATL"],
            "W/L": ["W", "L"],
            "R": [5, 2],
            "RA": [3, 4],
        }
    )
    monkeypatch.setattr(extract, "schedule_and_record", lambda season, team: sample)

    result = extract.fetch_team_game_results(2025, "NYM")

    expected_columns = {
        "game_date",
        "opponent",
        "result",
        "is_win",
        "is_loss",
        "runs_for",
        "runs_against",
    }
    assert expected_columns.issubset(result.columns)
    assert list(result["is_win"]) == [1, 0]
    assert list(result["is_loss"]) == [0, 1]
