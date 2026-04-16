import os
import sys
import types


if "streamlit" not in sys.modules:
    sys.modules["streamlit"] = types.SimpleNamespace(session_state={})

from user_manager import UserManager


def test_user_manager_initializes_users_file_in_clean_directory(tmp_path):
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        manager = UserManager()
        assert os.path.exists(os.path.join("users", "users.json"))
        assert manager.users_file == os.path.join("users", "users.json")
    finally:
        os.chdir(cwd)
