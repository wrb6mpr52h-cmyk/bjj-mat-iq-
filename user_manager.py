"""
BJJ Mat IQ - User Authentication and Role Management System
Handles user accounts, login/logout, and role-based access control
"""

import json
import os
try:
    import bcrypt
except ImportError:
    # bcrypt not available - will use fallback hashing
    bcrypt = None
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import streamlit as st

class UserManager:
    """Manages user authentication, registration, and role-based access control."""
    
    def __init__(self, users_dir="users", user_data_dir="user_data"):
        self.users_dir = users_dir
        self.user_data_dir = user_data_dir
        self.users_file = os.path.join(users_dir, "users.json")
        
        # Create directories
        os.makedirs(users_dir, exist_ok=True)
        os.makedirs(user_data_dir, exist_ok=True)
        
        # Initialize users file if it doesn't exist
        if not os.path.exists(self.users_file):
            self._initialize_users_file()
        
        # Available roles and their permissions
        self.roles = {
            "admin": {
                "name": "Administrator",
                "permissions": ["view_all", "edit_all", "manage_users", "manage_teams"],
                "description": "Full system access - can view and manage all data"
            },
            "team_owner": {
                "name": "Team Owner",
                "permissions": ["view_team", "edit_team", "manage_team_athletes"],
                "description": "Can manage specific teams and their athletes"
            },
            "individual": {
                "name": "Individual User", 
                "permissions": ["view_own", "edit_own"],
                "description": "Can only view and edit own athlete data"
            }
        }
    
    def _initialize_users_file(self):
        """Initialize empty users file with admin account."""
        initial_users = {
            "users": {},
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        with open(self.users_file, 'w') as f:
            json.dump(initial_users, f, indent=2)
    
    def _load_users(self) -> Dict:
        """Load users from file."""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._initialize_users_file()
            return self._load_users()
    
    def _save_users(self, users_data: Dict):
        """Save users to file."""
        with open(self.users_file, 'w') as f:
            json.dump(users_data, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        if bcrypt is None:
            # Fallback for when bcrypt is not available (NOT secure for production)
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest()
        
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        # Check if hash is empty or invalid
        if not hashed or not hashed.strip():
            return False
        
        if bcrypt is None:
            # Fallback for when bcrypt is not available (NOT secure for production)
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest() == hashed
        
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except ValueError:
            # Handle invalid salt/hash format - silently return False
            return False
    
    def create_user(self, username: str, email: str, password: str, role: str, 
                   team: str = "", created_by: str = "") -> Tuple[bool, str]:
        """Create a new user account."""
        users_data = self._load_users()
        
        # Check if username already exists
        if username in users_data["users"]:
            return False, "Username already exists"
        
        # Check if email already exists
        for user_data in users_data["users"].values():
            if user_data.get("email", "").lower() == email.lower():
                return False, "Email already exists"
        
        # Validate role
        if role not in self.roles:
            return False, "Invalid role specified"
        
        # Hash password
        hashed_password = self._hash_password(password)
        
        # Create user data
        user_data = {
            "username": username,
            "email": email,
            "password_hash": hashed_password,
            "role": role,
            "team": team,
            "created_at": datetime.now().isoformat(),
            "created_by": created_by,
            "last_login": None,
            "active": True,
            "owned_teams": [] if role == "team_owner" else [],
            "owned_athletes": [] if role == "individual" else []
        }
        
        # Save user
        users_data["users"][username] = user_data
        self._save_users(users_data)
        
        # Create user data directory
        user_dir = os.path.join(self.user_data_dir, username)
        os.makedirs(user_dir, exist_ok=True)
        os.makedirs(os.path.join(user_dir, "athletes"), exist_ok=True)
        os.makedirs(os.path.join(user_dir, "reviews"), exist_ok=True)
        
        return True, "User created successfully"
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """Authenticate user login."""
        users_data = self._load_users()
        
        if username not in users_data["users"]:
            return False, None
        
        user_data = users_data["users"][username]
        
        if not user_data.get("active", True):
            return False, None
        
        if self._verify_password(password, user_data["password_hash"]):
            # Update last login
            user_data["last_login"] = datetime.now().isoformat()
            users_data["users"][username] = user_data
            self._save_users(users_data)
            
            # Return user info without password
            user_info = user_data.copy()
            del user_info["password_hash"]
            return True, user_info
        
        return False, None
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information without password."""
        users_data = self._load_users()
        
        if username not in users_data["users"]:
            return None
        
        user_info = users_data["users"][username].copy()
        del user_info["password_hash"]
        return user_info
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (admin only)."""
        users_data = self._load_users()
        all_users = []
        
        for username, user_data in users_data["users"].items():
            user_info = user_data.copy()
            del user_info["password_hash"]
            all_users.append(user_info)
        
        return sorted(all_users, key=lambda x: x["created_at"])
    
    def update_user_role(self, username: str, new_role: str, updated_by: str) -> Tuple[bool, str]:
        """Update user role (admin only)."""
        if new_role not in self.roles:
            return False, "Invalid role specified"
        
        users_data = self._load_users()
        
        if username not in users_data["users"]:
            return False, "User not found"
        
        users_data["users"][username]["role"] = new_role
        users_data["users"][username]["updated_by"] = updated_by
        users_data["users"][username]["updated_at"] = datetime.now().isoformat()
        
        self._save_users(users_data)
        return True, "User role updated successfully"
    
    def deactivate_user(self, username: str, deactivated_by: str) -> Tuple[bool, str]:
        """Deactivate user account (admin only)."""
        users_data = self._load_users()
        
        if username not in users_data["users"]:
            return False, "User not found"
        
        users_data["users"][username]["active"] = False
        users_data["users"][username]["deactivated_by"] = deactivated_by
        users_data["users"][username]["deactivated_at"] = datetime.now().isoformat()
        
        self._save_users(users_data)
        return True, "User account deactivated"
    
    def get_user_data_path(self, username: str, subfolder: str = "") -> str:
        """Get path to user's data directory."""
        if subfolder:
            return os.path.join(self.user_data_dir, username, subfolder)
        return os.path.join(self.user_data_dir, username)
    
    def has_permission(self, user_info: Dict, permission: str) -> bool:
        """Check if user has specific permission."""
        user_role = user_info.get("role", "")
        if user_role not in self.roles:
            return False
        
        return permission in self.roles[user_role]["permissions"]
    
    def can_access_team(self, user_info: Dict, team_name: str) -> bool:
        """Check if user can access specific team data."""
        if self.has_permission(user_info, "view_all"):
            return True
        
        if self.has_permission(user_info, "view_team"):
            # Team owner can access their teams
            return team_name in user_info.get("owned_teams", []) or user_info.get("team", "") == team_name
        
        # Individual users can only access their own team
        return user_info.get("team", "") == team_name
    
    def can_access_athlete(self, user_info: Dict, athlete_id: str, athlete_team: str = "") -> bool:
        """Check if user can access specific athlete data."""
        if self.has_permission(user_info, "view_all"):
            return True
        
        if self.has_permission(user_info, "view_team"):
            # Team owner can access athletes from their teams
            return self.can_access_team(user_info, athlete_team)
        
        # Individual users can only access their own athletes
        return athlete_id in user_info.get("owned_athletes", [])
    
    def get_accessible_teams(self, user_info: Dict) -> List[str]:
        """Get list of teams user can access."""
        if self.has_permission(user_info, "view_all"):
            # Admin can see all teams - would need to scan all user data
            from athlete_manager import AthleteManager
            athlete_manager = AthleteManager()
            all_athletes = athlete_manager.list_all_athletes()
            return list(set(a.get('team', '') for a in all_athletes if a.get('team')))
        
        if self.has_permission(user_info, "view_team"):
            # Team owner can see their owned teams plus their own team
            teams = user_info.get("owned_teams", []).copy()
            if user_info.get("team"):
                teams.append(user_info["team"])
            return list(set(teams))
        
        # Individual can only see their own team
        if user_info.get("team"):
            return [user_info["team"]]
        return []
    
    def assign_team_ownership(self, username: str, team_name: str, assigned_by: str) -> Tuple[bool, str]:
        """Assign team ownership to a user (admin only)."""
        users_data = self._load_users()
        
        if username not in users_data["users"]:
            return False, "User not found"
        
        user_data = users_data["users"][username]
        
        # Add team to owned teams if not already there
        if team_name not in user_data.get("owned_teams", []):
            if "owned_teams" not in user_data:
                user_data["owned_teams"] = []
            user_data["owned_teams"].append(team_name)
            user_data["team_assigned_by"] = assigned_by
            user_data["team_assigned_at"] = datetime.now().isoformat()
            
            self._save_users(users_data)
            return True, f"Team '{team_name}' assigned to {username}"
        
        return False, f"User {username} already owns team '{team_name}'"
    
    def assign_athlete_ownership(self, username: str, athlete_id: str, assigned_by: str) -> Tuple[bool, str]:
        """Assign athlete ownership to a user."""
        users_data = self._load_users()
        
        if username not in users_data["users"]:
            return False, "User not found"
        
        user_data = users_data["users"][username]
        
        # Add athlete to owned athletes if not already there
        if athlete_id not in user_data.get("owned_athletes", []):
            if "owned_athletes" not in user_data:
                user_data["owned_athletes"] = []
            user_data["owned_athletes"].append(athlete_id)
            user_data["athlete_assigned_by"] = assigned_by
            user_data["athlete_assigned_at"] = datetime.now().isoformat()
            
            self._save_users(users_data)
            return True, f"Athlete '{athlete_id}' assigned to {username}"
        
        return False, f"User {username} already owns athlete '{athlete_id}'"
    
    def reset_user_password(self, username: str, new_password: str, reset_by: str = "") -> Tuple[bool, str]:
        """Reset a user's password (admin only, or self-reset)."""
        users_data = self._load_users()
        
        if username not in users_data["users"]:
            return False, "User not found"
        
        try:
            # Hash the new password
            new_hash = self._hash_password(new_password)
            
            # Update user data
            users_data["users"][username]["password_hash"] = new_hash
            users_data["users"][username]["password_reset_by"] = reset_by
            users_data["users"][username]["password_reset_at"] = datetime.now().isoformat()
            
            self._save_users(users_data)
            return True, "Password reset successfully"
            
        except Exception as e:
            return False, f"Error resetting password: {str(e)}"
    
    def self_reset_password(self, username: str, email: str, new_password: str) -> Tuple[bool, str]:
        """Self-service password reset with email verification.""" 
        users_data = self._load_users()
        
        if username not in users_data["users"]:
            return False, "Username not found"
        
        user_data = users_data["users"][username]
        
        # Check if user is active
        if not user_data.get("active", True):
            return False, "Account is deactivated. Please contact an administrator."
        
        # Verify email matches
        if user_data.get("email", "").lower() != email.lower():
            return False, "Email address does not match our records"
        
        try:
            # Hash the new password
            new_hash = self._hash_password(new_password)
            
            # Update user data
            users_data["users"][username]["password_hash"] = new_hash
            users_data["users"][username]["password_reset_by"] = "Self-Reset"
            users_data["users"][username]["password_reset_at"] = datetime.now().isoformat()
            users_data["users"][username]["last_updated"] = datetime.now().isoformat()
            
            self._save_users(users_data)
            return True, "Password reset successfully"
            
        except Exception as e:
            return False, f"Error resetting password: {str(e)}"

def init_session_state():
    """Initialize session state for authentication."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'user_manager' not in st.session_state:
        st.session_state.user_manager = UserManager()

def show_login_page():
    """Display login/registration page."""
    user_manager = st.session_state.user_manager
    
    st.title("🥋 BJJ Mat IQ - Authentication")
    
    # Check if any users exist (for first-time setup)
    users_data = user_manager._load_users()
    is_first_user = len(users_data.get("users", {})) == 0
    
    if is_first_user:
        st.warning("🚀 **First Time Setup**: Create your administrator account")
        show_registration_form(user_manager, first_admin=True)
    else:
        tab1, tab2 = st.tabs(["🔑 Login", "👤 Register"])
        
        with tab1:
            show_login_form(user_manager)
        
        with tab2:
            show_registration_form(user_manager)

def show_login_form(user_manager):
    """Display login form."""
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.form_submit_button("🔑 Login", type="primary"):
            if username and password:
                success, user_info = user_manager.authenticate_user(username, password)
                
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_info = user_info
                    st.success(f"Welcome back, {user_info['username']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            else:
                st.error("Please enter both username and password")

def show_registration_form(user_manager, first_admin=False):
    """Display registration form."""
    if first_admin:
        st.subheader("Create Administrator Account")
    else:
        st.subheader("Create New Account")
    
    with st.form("register_form"):
        username = st.text_input("Username", help="Choose a unique username")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password", help="Minimum 6 characters")
        password_confirm = st.text_input("Confirm Password", type="password")
        
        if first_admin:
            role = "admin"
            st.info("🔧 **Admin Account**: You will have full system access")
        else:
            role = st.selectbox("Account Type", 
                               options=["individual", "team_owner"],
                               format_func=lambda x: user_manager.roles[x]["name"],
                               help="Choose your access level")
        
        team = st.text_input("Team/Academy Name (Optional)", 
                           help="Enter your team or academy name")
        
        if st.form_submit_button("👤 Create Account", type="primary"):
            # Validation
            if not all([username, email, password, password_confirm]):
                st.error("Please fill in all required fields")
                return
            
            if len(password) < 6:
                st.error("Password must be at least 6 characters long")
                return
            
            if password != password_confirm:
                st.error("Passwords do not match")
                return
            
            # Create user
            success, message = user_manager.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                team=team,
                created_by="self" if not first_admin else "system"
            )
            
            if success:
                st.success(f"✅ {message}")
                if first_admin:
                    st.info("🎉 Admin account created! You can now log in.")
                else:
                    st.info("🎉 Account created! You can now log in.")
                st.rerun()
            else:
                st.error(f"❌ {message}")

def show_user_info():
    """Display current user information in sidebar."""
    if st.session_state.authenticated and st.session_state.user_info:
        user_info = st.session_state.user_info
        role_info = st.session_state.user_manager.roles.get(user_info['role'], {})
        
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 Current User")
            st.write(f"**{user_info['username']}**")
            st.write(f"📧 {user_info['email']}")
            st.write(f"🎭 {role_info.get('name', user_info['role'])}")
            if user_info.get('team'):
                st.write(f"🏆 {user_info['team']}")
            
            if st.button("🚺 Logout", key="logout_user_manager"):
                st.session_state.authenticated = False
                st.session_state.user_info = None
                st.rerun()

def require_authentication():
    """Decorator/function to require authentication."""
    if not st.session_state.authenticated:
        show_login_page()
        st.stop()

def require_permission(permission: str):
    """Check if current user has required permission."""
    if not st.session_state.authenticated:
        return False
    
    return st.session_state.user_manager.has_permission(
        st.session_state.user_info, permission
    )