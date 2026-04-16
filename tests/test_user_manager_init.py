import os

from user_manager import UserManager


def test_user_manager_initializes_users_file_in_clean_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    users_dir = tmp_path / "users"
    user_data_dir = tmp_path / "user_data"
    manager = UserManager(users_dir=str(users_dir), user_data_dir=str(user_data_dir))
    expected_users_file = os.path.join(str(users_dir), "users.json")
    assert os.path.exists(expected_users_file)
    assert manager.users_file == expected_users_file
