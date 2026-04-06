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


def test_fetch_team_game_results_with_mock(monkeypatch, recwarn):
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
    assert len(recwarn) == 0


def test_lookup_team_id():
    assert extract._lookup_team_id("NYM") == 121


def test_fetch_schedule_fallback_uses_mlb_stats_api(monkeypatch):
    payload = {
        "dates": [
            {
                "date": "2025-04-01",
                "games": [
                    {
                        "status": {"abstractGameCode": "F"},
                        "teams": {
                            "home": {"team": {"id": 121, "abbreviation": "NYM"}, "score": 5},
                            "away": {"team": {"id": 146, "abbreviation": "MIA"}, "score": 3},
                        },
                    }
                ],
            }
        ]
    }

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return payload

    monkeypatch.setattr(extract.requests, "get", lambda *args, **kwargs: FakeResponse())

    result = extract._fetch_schedule_fallback(2025, "NYM")

    assert not result.empty
    assert result.iloc[0]["Date"] == "2025-04-01"
    assert result.iloc[0]["Opp"] == "MIA"
    assert result.iloc[0]["W/L"] == "W"


def test_fetch_team_game_results_falls_back_when_pybaseball_breaks(monkeypatch):
    sample = pd.DataFrame(
        {
            "Gm#": [1, 2],
            "Date": ["Apr 01", "Apr 02"],
            "Opp": ["MIA", "ATL"],
            "W/L": ["W", "L"],
            "R": [5, 2],
            "RA": [3, 4],
        }
    )

    def _raise(_season, _team):
        raise ValueError("Data cannot be retrieved for this team/year combo.")

    monkeypatch.setattr(extract, "schedule_and_record", _raise)
    monkeypatch.setattr(extract, "_fetch_schedule_fallback", lambda season, team: sample)

    result = extract.fetch_team_game_results(2025, "NYM")

    assert not result.empty
    assert list(result["is_win"]) == [1, 0]
    assert list(result["opponent"]) == ["MIA", "ATL"]
