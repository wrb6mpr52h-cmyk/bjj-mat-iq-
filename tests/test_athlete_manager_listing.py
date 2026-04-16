import json
import os

from athlete_manager import AthleteManager


def _write_profile(path, profile):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(profile, f)


def test_individual_lists_user_and_global_athletes_and_normalizes_athlete_id(tmp_path):
    base_dir = tmp_path / "data"
    user_dir = base_dir / "users" / "MSantone" / "athletes"
    global_dir = base_dir / "athletes"

    _write_profile(
        user_dir / "local_athlete.json",
        {"athlete_id": "local_athlete", "name": "Local Athlete", "owner": "MSantone", "team": "Gracie United"},
    )
    _write_profile(
        global_dir / "milo_santone_gracie_uni.json",
        {"athlete_id": "milo_santone", "name": "Milo Santone", "owner": "MSantone", "team": "Gracie United"},
    )
    _write_profile(
        global_dir / "other_user_athlete.json",
        {"athlete_id": "other_user_athlete", "name": "Other User", "owner": "AnotherUser", "team": "Other Team"},
    )

    manager = AthleteManager(base_dir=str(base_dir), current_user="MSantone", user_role="individual")
    athletes = manager.list_all_athletes()

    athlete_ids = {athlete["athlete_id"] for athlete in athletes}
    assert "local_athlete" in athlete_ids
    assert "milo_santone_gracie_uni" in athlete_ids
    assert "other_user_athlete" not in athlete_ids

    milo = next(athlete for athlete in athletes if athlete["name"] == "Milo Santone")
    assert milo["athlete_id"] == "milo_santone_gracie_uni"


def test_team_owner_athlete_dirs_include_user_and_global(tmp_path):
    base_dir = tmp_path / "data"
    user_athlete_dir = base_dir / "users" / "CoachUser" / "athletes"
    global_dir = base_dir / "athletes"
    os.makedirs(user_athlete_dir, exist_ok=True)
    os.makedirs(global_dir, exist_ok=True)

    manager = AthleteManager(base_dir=str(base_dir), current_user="CoachUser", user_role="team_owner")
    athlete_dirs = manager._get_athlete_dirs()

    assert str(user_athlete_dir) in athlete_dirs
    assert str(global_dir) in athlete_dirs
