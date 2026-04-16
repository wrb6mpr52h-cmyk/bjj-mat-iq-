import json
import os

import pytest

from athlete_manager import AthleteManager


def _write_review(path, review_id, owner, rating=3, notes="Initial notes"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {
        "metadata": {
            "review_id": review_id,
            "reviewed_at": "2026-04-10T12:00:00",
            "reviewer": "Test Reviewer",
            "owner": owner,
        },
        "match_info": {
            "fighter_a": "Athlete A",
            "fighter_b": "Athlete B",
        },
        "assessments": {
            "Guard Passing": {
                "rating": rating,
                "label": "Competent",
            }
        },
        "coach_notes": notes,
    }
    with open(path, "w") as f:
        json.dump(payload, f)


def test_admin_can_list_update_and_delete_reviews(tmp_path):
    base_dir = tmp_path / "data"
    global_review_path = base_dir / "reviews" / "REV-0001.json"
    user_review_path = base_dir / "users" / "other_user" / "reviews" / "REV-0002.json"

    _write_review(global_review_path, "REV-0001", "owner_a", rating=3)
    _write_review(user_review_path, "REV-0002", "owner_b", rating=4)

    manager = AthleteManager(base_dir=str(base_dir), current_user="admin_user", user_role="admin")

    listed = manager.admin_list_reviews(page=1, page_size=10)
    listed_ids = {item["id"] for item in listed["items"]}

    assert listed["total"] == 2
    assert listed_ids == {"REV-0001", "REV-0002"}

    selected = manager.admin_get_review("REV-0001")
    assert selected is not None
    assert selected["coach_notes"] == "Initial notes"

    updated = manager.admin_update_review(
        "REV-0001",
        {
            "coach_notes": "Updated by admin",
            "assessments": {"Guard Passing": 5},
        },
    )
    assert updated is True

    with open(global_review_path, "r") as f:
        review_data = json.load(f)

    assert review_data["coach_notes"] == "Updated by admin"
    assert review_data["assessments"]["Guard Passing"]["rating"] == 5
    assert review_data["metadata"]["last_updated_by"] == "admin_user"
    assert "last_updated" in review_data["metadata"]

    deleted = manager.admin_delete_review("REV-0002")
    assert deleted is True
    assert not os.path.exists(user_review_path)

    listed_after_delete = manager.admin_list_reviews(page=1, page_size=10)
    assert listed_after_delete["total"] == 1
    assert listed_after_delete["items"][0]["id"] == "REV-0001"


def test_non_admin_cannot_access_admin_review_methods(tmp_path):
    base_dir = tmp_path / "data"
    review_path = base_dir / "reviews" / "REV-0001.json"
    _write_review(review_path, "REV-0001", "owner_a")

    manager = AthleteManager(base_dir=str(base_dir), current_user="regular_user", user_role="individual")

    with pytest.raises(PermissionError):
        manager.admin_list_reviews()

    with pytest.raises(PermissionError):
        manager.admin_get_review("REV-0001")

    with pytest.raises(PermissionError):
        manager.admin_update_review("REV-0001", {"coach_notes": "x"})

    with pytest.raises(PermissionError):
        manager.admin_delete_review("REV-0001")
