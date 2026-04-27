"""
BJJ Mat IQ - Phase 1 Streamlit App
5-step review workflow: Match Info -> Timeline -> Assessment -> Export -> Progress
with user authentication and role-based access control
"""

import streamlit as st
import json
import os
from supabase_client import create_match_supabase, create_review_supabase
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ui_components import render_match_card, render_assessment_card
from datetime import datetime
try:
    from config import (
        POSITIONS, ACTIONS, SUBMISSIONS, TACTICAL_TAGS,
        ASSESSMENT_AREAS, RATING_LABELS, RULESETS,
        BELT_LEVELS, WEIGHT_CLASSES, AGE_DIVISIONS, GI_NOGI,
        BJJ_REASONS, MOMENT_RESULTS, MISSED_OPPORTUNITIES
    )
except ImportError as e:
    import sys
    import os
    # ...existing code...
    # Fallback - define minimal constants if config.py is missing
    POSITIONS = {}
    ACTIONS = {}
    SUBMISSIONS = {}
    TACTICAL_TAGS = {}
    ASSESSMENT_AREAS = {}
    RATING_LABELS = {1: "Poor", 2: "Fair", 3: "Good", 4: "Very Good", 5: "Excellent"}
    RULESETS = {}
    BELT_LEVELS = ["White", "Blue", "Purple", "Brown", "Black"]
    WEIGHT_CLASSES = ["Light", "Medium", "Heavy"]
    AGE_DIVISIONS = ["Adult"]
    GI_NOGI = ["Gi", "No-Gi"]
    BJJ_REASONS = {}
    MOMENT_RESULTS = []
    MISSED_OPPORTUNITIES = []
from review_engine import (
    calculate_score, build_review_data,
    export_json, export_markdown, export_pdf, export_word, analyze_timeline_for_assessment,
    generate_ai_summary_report
)
from user_manager import UserManager
from athlete_manager import AthleteManager

st.set_page_config(
    page_title="BJJ Mat IQ - Match Review Tool",
    page_icon="🥋",
    layout="wide"
)

# Initialize user manager
user_manager = UserManager()

# Debug: Check if users file exists
users_file_path = os.path.join("users", "users.json")
if not os.path.exists(users_file_path):
    st.stop()

# Authentication check
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# Authentication interface
if not st.session_state.authenticated:
    st.title("🥋 BJJ Mat IQ - Login")
    st.markdown("**The complete BJJ match analysis and progress tracking system**")
    # ...existing code...

    auth_tab1, auth_tab2, auth_tab3 = st.tabs(["Login", "Create Account", "Reset Password"])

    with auth_tab1:
        with st.form("login_form"):
            st.subheader("Login to Your Account")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button("Login", type="primary")

            if login_submitted:
                if username and password:
                    success, user_info = user_manager.authenticate_user(username, password)
                    if success and user_info:
                        st.session_state.authenticated = True
                        st.session_state.current_user = username
                        st.session_state.user_role = user_info["role"]
                        st.success(f"Welcome back, {user_info.get('username', username)}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")
        
        # Show forgot password link
        # ...existing code...

    with auth_tab2:
        with st.form("register_form"):
            st.subheader("Create New Account")
                 # ...existing code...

            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            full_name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            team_affiliation = st.text_input("Team/Academy (optional)")
            role = st.selectbox("Account Type", 
                               ["individual", "team_owner", "admin"],
                               format_func=lambda x: {
                                   "individual": "Individual Athlete",
                                   "team_owner": "Team Owner/Coach",
                                   "admin": "Administrator"
                               }[x])
            register_submitted = st.form_submit_button("Create Account", type="primary")

            if register_submitted:
                if not all([new_username, new_password, confirm_password, full_name, email]):
                    st.warning("Please fill in all required fields")
                elif new_password != confirm_password:
                    st.error("Passwords don't match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    success, message = user_manager.create_user(
                        username=new_username,
                        email=email,
                        password=new_password,
                        role=role,
                        team=team_affiliation
                    )
                    if success:
                        st.success("Account created successfully! Please login with your new credentials.")
                    else:
                        st.error(message)

    with auth_tab3:
        with st.form("reset_password_form"):
            st.subheader("🔑 Reset Your Password")
            st.info("🔄 **Self-Service Password Reset**\n"
                   "Enter your username and choose a new password.")
            
            reset_username = st.text_input("Username*", help="Enter your existing username")
            reset_email = st.text_input("Email (for verification)*", help="Enter your email address for verification")
            new_reset_password = st.text_input("New Password*", type="password", help="Choose a new password (minimum 6 characters)")
            confirm_reset_password = st.text_input("Confirm New Password*", type="password", help="Re-enter your new password")
            
            reset_submitted = st.form_submit_button("🔑 Reset Password", type="primary")
            
            if reset_submitted:
                if not all([reset_username, reset_email, new_reset_password, confirm_reset_password]):
                    st.error("❌ Please fill in all fields")
                elif new_reset_password != confirm_reset_password:
                    st.error("❌ New passwords don't match")
                elif len(new_reset_password) < 6:
                    st.error("❌ Password must be at least 6 characters long")
                else:
                    # Verify user exists and email matches
                    success, message = user_manager.self_reset_password(
                        username=reset_username,
                        email=reset_email,
                        new_password=new_reset_password
                    )
                    if success:
                        st.success("✅ Password reset successfully! You can now login with your new password.")
                        # ...existing code...
                    else:
                        st.error(f"❌ {message}")

    st.stop()  # Stop execution until user is authenticated

# If we get here, user is authenticated
# Header with user info and logout
col_logo, col_title, col_user = st.columns([1, 3, 1])

with col_logo:
    try:
        st.image("logo.png", width=100)
    except:
        st.markdown("# 🥋")

with col_title:
    st.title("BJJ Mat IQ - Match Review Tool")
    st.caption("Phase 1: Expert-Assisted Review with Progress Tracking")

with col_user:
    user_info = user_manager.get_user_info(st.session_state.current_user)
    if user_info:
        st.write(f"👤 {user_info.get('username', st.session_state.current_user)}")
        st.caption(f"Role: {user_info['role'].replace('_', ' ').title()}")
        
        # Admin navigation
        if user_info['role'] == 'admin':
            col_admin, col_logout = st.columns(2)
            
            with col_admin:
                if st.button("👥 User Management", key="nav_user_mgmt", help="Manage user accounts"):
                    st.session_state.page_mode = "user_management"
                    st.rerun()
            
            with col_logout:
                if st.button("Logout", key="logout_btn"):
                    st.session_state.authenticated = False
                    st.session_state.current_user = None
                    st.session_state.user_role = None
                    st.rerun()
        else:
            if st.button("Logout", key="logout_btn"):
                st.session_state.authenticated = False
                st.session_state.current_user = None
                st.session_state.user_role = None
                st.rerun()

# Initialize session state
if "events" not in st.session_state:
    st.session_state.events = []
if "assessments" not in st.session_state:
    st.session_state.assessments = {}
if "tactical_tags" not in st.session_state:
    st.session_state.tactical_tags = {}

def get_athlete_manager():
    """Get athlete manager with current user context."""
    return AthleteManager(
        current_user=st.session_state.get('current_user'),
        user_role=st.session_state.get('user_role', 'individual')
    )

# Initialize global athlete manager for backward compatibility 
athlete_manager = get_athlete_manager()

# Update athlete manager if user context has changed
if (athlete_manager.current_user != st.session_state.get('current_user') or 
    athlete_manager.user_role != st.session_state.get('user_role')):
    athlete_manager = get_athlete_manager()
    st.session_state.tactical_tags = []
if "editing_event" not in st.session_state:
    st.session_state.editing_event = None
if "current_athlete_id" not in st.session_state:
    st.session_state.current_athlete_id = None
if "athlete_linked" not in st.session_state:
    st.session_state.athlete_linked = False
if "page_mode" not in st.session_state:
    st.session_state.page_mode = "landing"  # landing, match_review, progress_tracking, member_info

def flatten_dict(d):
    items = []
    for category, entries in d.items():
        items.extend(entries)
    return items

# Flatten nested dictionaries for dropdowns
ALL_POSITIONS = flatten_dict(POSITIONS)
ALL_ACTIONS = flatten_dict(ACTIONS)
ALL_SUBMISSIONS = flatten_dict(SUBMISSIONS)
ALL_TACTICAL_TAGS = flatten_dict(TACTICAL_TAGS)
ALL_BJJ_REASONS = flatten_dict(BJJ_REASONS)

# Navigation and Page Mode Handling
if st.session_state.page_mode == "landing":
    # LANDING PAGE
    # ...existing code...

    col_athlete1, col_athlete2 = st.columns([2, 1])

    with col_athlete1:
        # Fetch athletes (implement as needed)
        athlete_manager = get_athlete_manager()
        existing_athletes = athlete_manager.list_all_athletes()
        # Only include athletes with a 'name' key
        # Only show athletes whose file exists and matches their athlete_id
        valid_athletes = []
        for a in existing_athletes:
            if 'name' in a and a['name'] and 'athlete_id' in a:
                for athlete_dir in athlete_manager._get_athlete_dirs():
                    profile_path = os.path.join(athlete_dir, f"{a['athlete_id']}.json")
                    if os.path.exists(profile_path):
                        valid_athletes.append(a)
                        break
        # ...existing code...
        # Use both name and athlete_id for unique selection
        athlete_options = ["Select Athlete", "Create New Athlete"] + [f"{a['name']} [{a['athlete_id']}]" for a in valid_athletes]
        selected_option = st.selectbox("Choose an athlete", athlete_options, index=0)
        # Removed warning about missing athlete names

        if selected_option == "Select Athlete":
            st.session_state.current_athlete_id = None
            st.session_state.registered_athlete_name = ""
            st.session_state.registered_athlete_team = ""
            st.session_state.registered_athlete_belt = ""
            st.session_state.registered_athlete_age_division = ""
            st.session_state.registered_athlete_weight_class = ""
        elif selected_option == "Create New Athlete":
            st.session_state.current_athlete_id = None
            # Clear registered athlete info
            if 'registered_athlete_name' in st.session_state:
                del st.session_state.registered_athlete_name
            if 'registered_athlete_team' in st.session_state:
                del st.session_state.registered_athlete_team

            # Show athlete creation form
            st.markdown("#### 👤 Create New Athlete Profile")
            st.info("🏷️ **Athlete Profile Benefits:**\n"
                    "• Automatically populates as 'Fighter A' in match reviews\n"
                    "• Tracks progress across multiple matches\n"
                    "• Generates personalized training recommendations\n"
                    "• Links all your match data to one athlete profile")

            with st.form("create_athlete_form"):
                new_name = st.text_input("Athlete Name*", placeholder="Enter athlete's full name")
                new_team = st.text_input("Team/Academy", placeholder="Enter team or academy name (optional)")
                new_belt = st.selectbox("Belt Level*", BELT_LEVELS)
                new_age_division = st.selectbox("Age Division", AGE_DIVISIONS)
                new_weight = st.selectbox("Weight Class", WEIGHT_CLASSES)

                create_submitted = st.form_submit_button("🆕 Create Athlete Profile", type="primary")

                if create_submitted:
                    if new_name.strip():
                        # ...existing code...
                        # Create the athlete profile
                        athlete_id = athlete_manager.create_or_update_athlete(
                            name=new_name.strip(),
                            team=new_team.strip() if new_team.strip() else None,
                            belt=new_belt,
                            age_division=new_age_division,
                            weight_class=new_weight
                        )
                        st.success(f"✅ Created athlete profile: **{new_name}**")
                        st.info("🏷️ This athlete is now registered for match reviews")
                        st.rerun()

                    else:
                        st.warning("⚠️ Please enter an athlete name")
        else:
            # Extract athlete from selection using athlete_id
            selected_athlete = None
            if selected_option not in ["Select Athlete", "Create New Athlete"]:
                # Parse athlete_id from option string
                if selected_option.endswith("]") and "[" in selected_option:
                    athlete_id_lookup = selected_option.split("[")[-1][:-1]
                    for athlete in valid_athletes:
                        if athlete.get("athlete_id") == athlete_id_lookup:
                            selected_athlete = athlete
                            break

            if selected_athlete:
                # Always fetch the latest athlete profile from disk for all info and session state
                athlete_id_debug = selected_athlete["athlete_id"]
                latest_profile = athlete_manager.get_athlete_profile(athlete_id_debug)
                if latest_profile:
                    st.session_state.current_athlete_id = latest_profile["athlete_id"]
                    st.session_state.registered_athlete_name = latest_profile['name']
                    st.session_state.registered_athlete_team = latest_profile.get('team', '')
                    st.session_state.registered_athlete_belt = latest_profile.get('current_belt', '')
                    st.session_state.registered_athlete_age_division = latest_profile.get('current_age_division', '')
                    st.session_state.registered_athlete_weight_class = latest_profile.get('current_weight_class', '')
                else:
                    pass

    with col_athlete2:
        if st.session_state.get('current_athlete_id'):
            profile = athlete_manager.get_athlete_profile(st.session_state.current_athlete_id)
            if profile:
                st.markdown("**Selected Profile:**")
                st.write(f"**Name:** {profile['name']}")
                st.write(f"**Team:** {profile.get('team', 'N/A')}")
                st.write(f"**Current Belt:** {profile.get('current_belt', 'N/A')}")
                st.write(f"**Age Division:** {profile.get('current_age_division', 'N/A')}")
                st.write(f"**Weight Class:** {profile.get('current_weight_class', 'N/A')}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                st.write(f"**Total Score:** {profile.get('total_score', 0)}")
                st.write(f"**Total Matches:** {len(profile.get('match_history', []))}")
                st.write(f"**Total Reviews:** {len(profile.get('reviews', []))}")
                st.write(f"**Total Assessments:** {len(profile.get('assessment_reports', []))}")
                st.write(f"**Total Points:** {profile.get('total_points', 0)}")
                # ...existing code...
                # The following block is removed due to undefined variables (review_id, i, assessments)
                # If you want to enable match editing/deleting, ensure these variables are defined in the correct scope.
                # ...existing code...
    # End of match data block


if 'analysis_mode' not in locals() and 'analysis_mode' not in globals():
    analysis_mode = None
# Top-level analysis mode selection
if 'analysis_mode' in locals() or 'analysis_mode' in globals():
    if analysis_mode == "📋 All Reviews Management":
        # ALL REVIEWS MANAGEMENT SECTION
        st.subheader("📋 All Reviews Management")
        all_reviews = athlete_manager.list_all_reviews()
        if not all_reviews:
            st.warning("⚠️ No match reviews found.")
            st.info("💡 Complete and save at least one match review to see it here.")
        else:
            st.caption(f"Total reviews: {len(all_reviews)}")
            for i, review in enumerate(all_reviews[:20]):
                def on_edit_match(review_id):
                    st.session_state.page_mode = "match_review"
                    st.session_state.editing_existing_match = True
                    st.session_state.editing_review_id = review_id
                    st.success("Loading for edit...")
                    st.rerun()
                render_match_card(
                    review,
                    athlete_name=review.get("match_info", {}).get("fighter_a", None),
                    index=i,
                    export_pdf=export_pdf,
                    export_word=export_word,
                    on_edit=on_edit_match,
                    on_delete=None,
                    context_prefix="all_"
                )

    elif analysis_mode == "🏆 Team Analysis":
        st.subheader("🏆 Team Analysis")
        st.info("👥 **Team Analysis:** Compare performance across multiple athletes and identify team strengths/weaknesses")
        
        all_athletes = athlete_manager.list_all_athletes()
        if all_athletes:
            # Group athletes by team
            teams = {}
            for athlete in all_athletes:
                team = athlete.get('team', 'No Team')
                if team not in teams:
                    teams[team] = []
                teams[team].append(athlete)
            
            team_options = list(teams.keys())
            if team_options:
                selected_team = st.selectbox("Select Team for Analysis", team_options)
                
                team_athletes = teams[selected_team]
                
                # Team Overview
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Team Size", len(team_athletes))
                with col2:
                    total_matches = sum(len(athlete.get('match_history', [])) for athlete in team_athletes)
                    st.metric("Total Matches", total_matches)
                with col3:
                    active_athletes = len([a for a in team_athletes if len(a.get('match_history', [])) > 0])
                    st.metric("Active Athletes", active_athletes)
                with col4:
                    avg_matches = total_matches / len(team_athletes) if team_athletes else 0
                    st.metric("Avg Matches/Athlete", f"{avg_matches:.1f}")
                
                st.divider()
                
                # Team Performance Analysis
                if total_matches > 0:
                    st.subheader("📊 Team Performance Breakdown")
                    
                    # Aggregate all match data from team
                    all_assessments = []
                    all_match_results = []
                    belt_distribution = {}
                    weight_distribution = {}
                    
                    for athlete in team_athletes:
                        matches = athlete.get('match_history', [])
                        for match in matches:
                            # Collect assessments
                            assessments = match.get('assessments', {})
                            if assessments:
                                all_assessments.append(assessments)
                            
                            # Collect match results
                            match_info = match.get('match_info', {})
                            result = match_info.get('result', '')
                            if result:
                                all_match_results.append(result)
                            
                            # Belt distribution
                            belt = match_info.get('belt', 'Unknown')
                            belt_distribution[belt] = belt_distribution.get(belt, 0) + 1
                            
                            # Weight distribution
                            weight = match_info.get('weight_class', 'Unknown')
                            weight_distribution[weight] = weight_distribution.get(weight, 0) + 1
                    
                    if all_assessments:
                        # Calculate team averages for each skill area
                        st.markdown("**🎯 Team Skill Averages:**")
                        skill_totals = {}
                        skill_counts = {}
                        
                        for assessment in all_assessments:
                            for skill, data in assessment.items():
                                rating = data.get('rating', 0)
                                if rating > 0:
                                    skill_totals[skill] = skill_totals.get(skill, 0) + rating
                                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
                        
                        # Display skill averages in columns
                        skills = list(skill_totals.keys())
                        if skills:
                            skill_chunks = [skills[i:i+3] for i in range(0, len(skills), 3)]
                            for chunk in skill_chunks:
                                cols = st.columns(len(chunk))
                                for i, skill in enumerate(chunk):
                                    with cols[i]:
                                        avg_rating = skill_totals[skill] / skill_counts[skill]
                                        
                                        # Color based on rating
                                        if avg_rating >= 4:
                                            color = "🟢"
                                        elif avg_rating >= 3:
                                            color = "🟡"
                                        else:
                                            color = "🔴"
                                        
                                        st.metric(
                                            f"{color} {skill}",
                                            f"{avg_rating:.1f}/5",
                                            f"{skill_counts[skill]} matches"
                                        )
                    
                    # Match Results Analysis
                    if all_match_results:
                        st.markdown("**🏆 Team Results Overview:**")
                        result_col1, result_col2 = st.columns(2)
                        
                        with result_col1:
                            wins = len([r for r in all_match_results if 'wins' in r.lower()])
                            losses = len([r for r in all_match_results if 'loses' in r.lower() or 'lost' in r.lower()])
                            total_decided = wins + losses
                            win_rate = (wins / total_decided * 100) if total_decided > 0 else 0
                            
                            st.metric("Win Rate", f"{win_rate:.1f}%", f"{wins}W-{losses}L")
                        
                        with result_col2:
                            submissions = len([r for r in all_match_results if 'submission' in r.lower()])
                            points_wins = len([r for r in all_match_results if 'points' in r.lower() and 'wins' in r.lower()])
                            st.metric("Submissions", submissions, f"{points_wins} by points")
                    
                    # Belt and Weight Distribution
                    dist_col1, dist_col2 = st.columns(2)
                    
                    with dist_col1:
                        if belt_distribution:
                            st.markdown("**🥋 Belt Distribution:**")
                            for belt, count in sorted(belt_distribution.items()):
                                st.write(f"• {belt}: {count} matches")
                    
                    with dist_col2:
                        if weight_distribution:
                            st.markdown("**⚖️ Weight Class Distribution:**")
                            for weight, count in sorted(weight_distribution.items()):
                                st.write(f"• {weight}: {count} matches")
                
                st.divider()
                
                # Individual Athlete Summary
                st.subheader("👤 Team Roster")
                for athlete in team_athletes:
                    matches = len(athlete.get('match_history', []))
                    if matches > 0:
                        # Calculate athlete's win rate
                        match_results = [m.get('match_info', {}).get('result', '') for m in athlete.get('match_history', [])]
                        wins = len([r for r in match_results if 'wins' in r.lower()])
                        total = len([r for r in match_results if r])
                        win_rate = (wins / total * 100) if total > 0 else 0
                        
                        st.write(f"👤 **{athlete['name']}** - {matches} matches - {win_rate:.0f}% win rate")
                    else:
                        st.write(f"👤 **{athlete['name']}** - No matches recorded")
        else:
            st.warning("No athletes found for team analysis.")

elif st.session_state.page_mode == "user_management":
    # USER MANAGEMENT PAGE (Admin Only)
    if st.button("← Back to Home", type="secondary", key="back_user_mgmt"):
        st.session_state.page_mode = "landing"
        st.rerun()
        
    st.subheader("👥 User Management")
    st.info("🔧 **Admin Panel:** Manage user accounts, passwords, and permissions")
    
    # Create tabs for different user management functions
    mgmt_tab1, mgmt_tab2, mgmt_tab3 = st.tabs(["👥 View Users", "🔑 Reset Password", "🆕 Create User"])
    
    with mgmt_tab1:
        # List all users
        all_users = user_manager.get_all_users()
        
        if all_users:
            st.markdown(f"**Total Users:** {len(all_users)}")
            st.markdown("---")
            
            for user in all_users:
                col_user, col_info, col_actions = st.columns([2, 2, 1])
                
                with col_user:
                    status_icon = "🟢" if user.get("active", True) else "🔴"
                    st.markdown(f"**{status_icon} {user['username']}**")
                    st.caption(f"📧 {user.get('email', 'No email')}")
                
                with col_info:
                    role = user.get('role', 'individual').replace('_', ' ').title()
                    team = user.get('team', 'No team')
                    created_date = user.get('created_at', '')[:10]
                    last_login = user.get('last_login', '')[:10] if user.get('last_login') else 'Never'
                    
                    st.write(f"🎭 **Role:** {role}")
                    st.caption(f"🏆 Team: {team}")
                    st.caption(f"📅 Created: {created_date}")
                    st.caption(f"🕒 Last Login: {last_login}")
                
                with col_actions:
                    if user['username'] != st.session_state.current_user:  # Don't allow admin to disable themselves
                        if user.get("active", True):
                            if st.button("🚫 Deactivate", key=f"deactivate_{user['username']}", help="Deactivate user account"):
                                success, message = user_manager.deactivate_user(
                                    username=user['username'],
                                    deactivated_by=st.session_state.current_user
                                )
                                if success:
                                    st.success(f"✅ {message}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                
                st.markdown("---")
        else:
            st.warning("⚠️ No users found in the system.")
    
    with mgmt_tab2:
        # Reset user password
        st.markdown("🔑 **Reset User Password**")
        st.caption("Select a user and set a new password for their account")
        
        # Get list of users for password reset
        all_users = user_manager.get_all_users()
        
        if all_users:
            user_options = [u['username'] for u in all_users]  # Show all users, not just active ones
            selected_reset_user = st.selectbox("Select User to Reset Password", ["Select User"] + user_options, key="password_reset_user_select")
            
            if selected_reset_user != "Select User":
                # Find the selected user to check if they're active
                selected_user_info = next((u for u in all_users if u['username'] == selected_reset_user), None)
                if selected_user_info and not selected_user_info.get("active", True):
                    st.warning(f"⚠️ Note: {selected_reset_user} is currently deactivated. Resetting password will not automatically reactivate the account.")
                
                with st.form("password_reset_form"):
                    st.markdown(f"**Resetting password for:** {selected_reset_user}")
                    
                    new_password = st.text_input("New Password", type="password", help="Enter the new password")
                    confirm_password = st.text_input("Confirm New Password", type="password", help="Re-enter the password to confirm")
                    
                    reset_submitted = st.form_submit_button("🔑 Reset Password", type="primary")
                    
                    if reset_submitted:
                        if not new_password:
                            st.error("❌ Password cannot be empty")
                        elif new_password != confirm_password:
                            st.error("❌ Passwords don't match")
                        elif len(new_password) < 6:
                            st.error("❌ Password must be at least 6 characters long")
                        else:
                            success, message = user_manager.reset_user_password(
                                username=selected_reset_user,
                                new_password=new_password,
                                reset_by=st.session_state.current_user
                            )
                            if success:
                                st.success(f"✅ {message}")
                                st.info(f"🔐 User '{selected_reset_user}' can now login with the new password.")
                            else:
                                st.error(f"❌ {message}")
        else:
            st.warning("⚠️ No users found in the system.")
    
    with mgmt_tab3:
        # Create new user
        st.markdown("🆕 **Create New User Account**")
        st.caption("Add a new user to the system")
        
        with st.form("admin_create_user_form"):
            new_username = st.text_input("Username*", help="Unique username for the new account")
            new_email = st.text_input("Email Address*", help="User's email address")
            new_password = st.text_input("Password*", type="password", help="Initial password (user can change later)")
            confirm_new_password = st.text_input("Confirm Password*", type="password", help="Re-enter the password")
            new_role = st.selectbox("Role*", ["individual", "team_owner", "admin"], 
                                  format_func=lambda x: {
                                      "individual": "Individual Athlete",
                                      "team_owner": "Team Owner/Coach", 
                                      "admin": "Administrator"
                                  }[x])
            new_team = st.text_input("Team/Academy", help="Optional team or academy affiliation")
            
            create_user_submitted = st.form_submit_button("🆕 Create User", type="primary")
            
            if create_user_submitted:
                if not all([new_username, new_email, new_password, confirm_new_password]):
                    st.error("❌ Please fill in all required fields")
                elif new_password != confirm_new_password:
                    st.error("❌ Passwords don't match")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters long")
                else:
                    success, message = user_manager.create_user(
                        username=new_username,
                        email=new_email,
                        password=new_password,
                        role=new_role,
                        team=new_team,
                        created_by=st.session_state.current_user
                    )
                    if success:
                        st.success(f"✅ {message}")
                        st.info(f"🎉 User '{new_username}' created successfully! They can now login with their credentials.")
                    else:
                        st.error(f"❌ {message}")

elif st.session_state.page_mode == "member_info":
    # Show back to home button
    if st.button("← Back to Home", type="secondary", key="back_member"):
        st.session_state.page_mode = "landing"
        st.rerun()

    # Member Info Page
    st.header("👤 Member Information")

    user_info = user_manager.get_user_info(st.session_state.current_user)
    current_user = st.session_state.current_user

    if user_info:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Account Details")
            st.write(f"**Username:** {user_info.get('username', 'N/A')}")
            st.write(f"**Email:** {user_info.get('email', 'N/A')}")
            st.write(f"**Role:** {user_info.get('role', 'athlete').replace('_', ' ').title()}")
            st.write(f"**Team:** {user_info.get('team', 'N/A')}")

        with col2:
            st.subheader("Account Statistics")
            try:
                # Get review stats
                user_reviews_dir = f"data/users/{current_user}/reviews"
                import os
                if os.path.exists(user_reviews_dir):
                    review_files = [f for f in os.listdir(user_reviews_dir) if f.endswith('.json')]
                    total_reviews = len(review_files)

                    # Calculate some basic stats from reviews
                    wins = 0
                    losses = 0
                    for review_file in review_files:
                        try:
                            import json
                            with open(os.path.join(user_reviews_dir, review_file), 'r', encoding='utf-8') as f:
                                review = json.load(f)
                                result = review.get('match_info', {}).get('result', '') if 'match_info' in review else review.get('result', '')
                                fighter_a = review.get('match_info', {}).get('fighter_a', '') if 'match_info' in review else ''
                                
                                # Check if current user's fighter wins
                                if fighter_a and 'wins' in result.lower() and fighter_a.lower() in result.lower():
                                    wins += 1
                                elif 'Fighter A wins' in result:  # Fallback for older format
                                    wins += 1
                                elif 'Fighter B wins' in result:  # Current user loses
                                    losses += 1
                                elif result and ('loses' in result.lower() or 'lost' in result.lower()) and fighter_a and fighter_a.lower() in result.lower():
                                    losses += 1
                                # If no clear win/loss, don't count it
                        except:
                            continue

                    st.metric("Total Reviews", total_reviews)
                    st.metric("Wins", wins)
                    st.metric("Losses", losses)
                    if total_reviews > 0:
                        win_rate = round((wins / total_reviews) * 100, 1)
                        st.metric("Win Rate", f"{win_rate}%")
                else:
                    st.info("No reviews found yet. Start your first match review!")

            except Exception as e:
                st.error(f"Error loading stats: {str(e)}")

        st.divider()

        # Logout option
        if st.button("🚪 Logout", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # --- List Registered Athletes ---
    st.subheader("Your Registered Athletes")
    athlete_manager = AthleteManager(base_dir="data", current_user=current_user, user_role=user_info.get('role', 'individual'))
    user_athletes = athlete_manager.list_all_athletes()
    if user_athletes:
        for athlete in user_athletes:
            # Skip malformed athlete profiles without athlete_id
            athlete_id = athlete.get("athlete_id")
            if not athlete_id or athlete.get("owner") != current_user:
                continue  # Only show user's own athletes with valid ID
            col_a1, col_a2, col_a3 = st.columns([3,1,1])
            with col_a1:
                st.write(f"**{athlete.get('name','')}**  ")
                st.write(f"Team: {athlete.get('team','N/A')}")
            with col_a2:
                if st.button(f"✏️ Edit", key=f"edit_{athlete_id}_memberinfo", type="secondary"):
                    st.session_state[f'edit_athlete_{athlete_id}'] = True
            with col_a3:
                if st.button(f"❌ Delete", key=f"delete_{athlete_id}_memberinfo", type="secondary"):
                    athlete_dir = athlete_manager._get_user_athlete_dir()
                    profile_path = os.path.join(athlete_dir, f"{athlete_id}.json")
                    try:
                        if os.path.exists(profile_path):
                            os.remove(profile_path)
                            st.success(f"Athlete '{athlete.get('name','')}' removed.")
                            st.session_state.pop(f'edit_athlete_{athlete_id}', None)
                            st.rerun()
                        else:
                            st.error("Athlete profile file not found.")
                    except Exception as e:
                        st.error(f"Error removing athlete: {str(e)}")
            # Inline edit form
            if st.session_state.get(f'edit_athlete_{athlete_id}', False):
                st.markdown("---")
                st.markdown(f"#### ✏️ Edit Athlete: {athlete.get('name','')}")
                with st.form(f"edit_athlete_form_{athlete_id}"):
                    edit_name = st.text_input("Athlete Name*", value=athlete['name'])
                    edit_team = st.text_input("Team/Academy", value=athlete.get('team', ''))
                    current_belt = athlete.get('current_belt', BELT_LEVELS[0])
                    belt_index = BELT_LEVELS.index(current_belt) if current_belt in BELT_LEVELS else 0
                    edit_belt = st.selectbox("Belt Level*", BELT_LEVELS, index=belt_index)
                    current_age = athlete.get('current_age_division', AGE_DIVISIONS[0])
                    age_index = AGE_DIVISIONS.index(current_age) if current_age in AGE_DIVISIONS else 0
                    edit_age_division = st.selectbox("Age Division", AGE_DIVISIONS, index=age_index)
                    current_weight = athlete.get('current_weight_class', WEIGHT_CLASSES[0])
                    weight_index = WEIGHT_CLASSES.index(current_weight) if current_weight in WEIGHT_CLASSES else 0
                    edit_weight = st.selectbox("Weight Class", WEIGHT_CLASSES, index=weight_index)
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        save_submitted = st.form_submit_button("💾 Save Changes", type="primary")
                    with col_cancel:
                        cancel_submitted = st.form_submit_button("❌ Cancel", type="secondary")
                    if save_submitted:
                        if edit_name.strip():
                            try:
                                new_athlete_id = athlete_manager.create_or_update_athlete(
                                    name=edit_name.strip(),
                                    team=edit_team.strip() if edit_team.strip() else "",
                                    belt=edit_belt,
                                    age_division=edit_age_division,
                                    weight_class=edit_weight
                                )
                                st.success(f"✅ Updated athlete profile: **{edit_name}**")
                                st.session_state.pop(f'edit_athlete_{athlete_id}', None)
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error updating profile: {str(e)}")
                        else:
                            st.error("❌ Athlete name is required")
                    if cancel_submitted:
                        st.session_state.pop(f'edit_athlete_{athlete_id}', None)
                        st.rerun()
    else:
        st.info("No athletes registered yet. Register athletes from the Home page.")

    st.stop()  # Stop here for member info page

# If we reach here, we're in match_review mode
# Show back to home button
if st.button("← Back to Home", type="secondary", key="back_match"):
    st.session_state.page_mode = "landing"
    st.rerun()

# Main interface tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 1. Match Info",
    "� 2. Video Review", 
    "📊 3. Assessment",
    "📄 4. Export",
    "📈 5. Progress Tracking"
])

# TAB 1: Match Information
with tab1:
    # Instructions for Match Info tab
    st.info("📄 **Match Info Instructions:**\n"
           "1. ✅ Register an athlete on the Home page (or create new one here)\n"
           "2. 📝 Fill in match details: opponent, event, ruleset, result\n"
           "3. 🎥 Add video URL if you have match footage\n"
           "4. 💾 Save match info, then proceed to Video Review tab")
    st.markdown("---")

    # Check if we're editing an existing match
    is_editing = st.session_state.get("editing_existing_match", False)
    editing_review_id = st.session_state.get("editing_review_id", "")

    # Show current review being edited
    if is_editing and editing_review_id:
        st.info(f"🔄 **Currently Editing:** {editing_review_id}")

    if is_editing:
        st.warning(f"📝 **EDITING MODE**: You are currently editing match `{editing_review_id}`")
        if st.button("🆕 Start New Match (Clear Form)", type="secondary"):
            # Clear editing state and athlete profile data
            keys_to_clear = [
                "editing_existing_match", "editing_review_id", "match_number", "fighter_a", 
                "team_a", "fighter_b", "team_b", "event_name", "match_video_url", "belt", 
                "weight_class", "age_division", "gi_nogi", "ruleset", "result", "sub_type",
                "events", "assessments", "tactical_tags", "current_athlete_id", "athlete_linked",
                "registered_athlete_name", "registered_athlete_team", "registered_athlete_belt",
                "registered_athlete_age_division", "registered_athlete_weight_class"
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        st.divider()

    # Check for pending edit data and load match info safely
    if "pending_edit_data" in st.session_state:
        review_data = st.session_state.pending_edit_data
        match_info = review_data.get("match_info", {})
        analysis = review_data.get("analysis", {})

        # Load only match info data safely into session state (overwrite existing values)
        for key, value in [
            ("match_number", match_info.get("match_number", "")),
            ("fighter_a", match_info.get("fighter_a", "")),
            ("fighter_b", match_info.get("fighter_b", "")),
            ("team_a", match_info.get("team_a", "")),
            ("team_b", match_info.get("team_b", "")),
            ("event_name", match_info.get("event", "")),
            ("match_date", match_info.get("match_date", "")),
            ("belt", match_info.get("belt", "")),
            ("weight_class", match_info.get("weight_class", "")),
            ("age_division", match_info.get("age_division", "")),
            ("gi_nogi", match_info.get("gi_nogi", "Gi")),
            ("ruleset", match_info.get("ruleset", "IBJJF")),
            ("match_video_url", match_info.get("video_url", "")),
            ("result", match_info.get("result", "")),
            ("submission_type", match_info.get("submission_type", "")),
            ("custom_strengths", analysis.get("custom_strengths", "")),
            ("custom_improvements", analysis.get("custom_improvements", ""))
        ]:
            st.session_state[key] = value

        # Note: Timeline and assessments are loaded in Video Review tab, not here
        st.success(f"✅ Loaded match information from review **{editing_review_id}**!")
        st.info(f"🔄 Go to **Video Review** tab to load timeline events and watch your match.")
        # Don't clear pending_edit_data here - let Video Review tab handle it
        # Don't call st.rerun() here to avoid infinite loops

    # Match Number - auto-generated review ID
    if editing_review_id:
        # Show current review ID when editing
        st.text_input(
            "🔢 Review ID (Auto-Generated)",
            value=editing_review_id,
            disabled=True,
            key="display_review_id",
            help="Unique review identifier - automatically assigned"
        )
        # Keep match_number for compatibility but make it descriptive
        match_number = st.text_input(
            "📝 Match Description (Optional)",
            key="match_number",
            placeholder="e.g., Tournament Semifinal, Assessment vs John",
            help="Optional description to help identify this match"
        )
    else:
        # For new reviews, show that ID will be auto-generated
        from review_engine import get_next_review_id
        next_id = get_next_review_id()
        st.text_input(
            "🔢 Review ID (Auto-Generated)",
            value=f"{next_id} (will be assigned on save)",
            disabled=True,
            help="Unique review identifier - automatically assigned when you save"
        )
        # Make match number optional description
        match_number = st.text_input(
            "📝 Match Description (Optional)",
            key="match_number",
            placeholder="e.g., Tournament Semifinal, Assessment vs John",
            help="Optional description to help identify this match"
        )

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        # Fighter A - automatically populated from registered athlete
        registered_athlete_name = st.session_state.get("registered_athlete_name", "")
        registered_athlete_team = st.session_state.get("registered_athlete_team", "")

        if registered_athlete_name:
            # Show registered athlete with option to override
            st.markdown("**🏷️ Registered Athlete (Fighter A):**")
            
            # Check if profile details are available for auto-population
            has_profile_details = (st.session_state.get("registered_athlete_belt") or 
                                 st.session_state.get("registered_athlete_age_division") or 
                                 st.session_state.get("registered_athlete_weight_class"))
            
            if has_profile_details:
                st.success("✅ Athlete profile details will be auto-populated below")
            
            fighter_a = st.text_input(
                "Fighter A Name", 
                value=registered_athlete_name,
                key="fighter_a",
                help="This is your registered athlete. You can modify if needed."
            )
            team_a = st.text_input(
                "Fighter A Team/Academy", 
                value=registered_athlete_team,
                key="team_a"
            )
            if fighter_a != registered_athlete_name:
                st.warning("⚠️ You've modified the athlete name. Consider updating your athlete profile on the Home page.")
        else:
            # No registered athlete - manual input
            st.markdown("**⚠️ No Registered Athlete Selected**")
            st.caption("Go to Home page to register your athlete profile for automatic population")
            current_user = st.session_state.get("current_user", "Username") 
            fighter_a = st.text_input(f"Fighter A ({current_user})", key="fighter_a")
            team_a = st.text_input(f"Fighter A Team/Academy", key="team_a")

        fighter_b = st.text_input("Fighter B (Opponent)", key="fighter_b")
        team_b = st.text_input("Fighter B Team/Academy", key="team_b")
        event_name = st.text_input("Event / Tournament Name", key="event_name")
        video_url = st.text_input("Video URL (YouTube, Google Drive, etc.)", key="match_video_url")

    with col2:
        # Auto-populate athlete details if registered athlete is selected
        registered_belt = st.session_state.get("registered_athlete_belt", "")
        registered_age = st.session_state.get("registered_athlete_age_division", "")
        registered_weight = st.session_state.get("registered_athlete_weight_class", "")
        
        # Set default indices for selectboxes
        belt_index = BELT_LEVELS.index(registered_belt) if registered_belt and registered_belt in BELT_LEVELS else 0
        age_index = AGE_DIVISIONS.index(registered_age) if registered_age and registered_age in AGE_DIVISIONS else 0  
        weight_index = WEIGHT_CLASSES.index(registered_weight) if registered_weight and registered_weight in WEIGHT_CLASSES else 0
        
        belt = st.selectbox("Belt Level", BELT_LEVELS, index=belt_index, key="belt", 
                           help="Auto-populated from athlete profile" if registered_belt else None)
        weight_class = st.selectbox("Weight Class", WEIGHT_CLASSES, index=weight_index, key="weight_class",
                                   help="Auto-populated from athlete profile" if registered_weight else None)
        age_division = st.selectbox("Age Division", AGE_DIVISIONS, index=age_index, key="age_division",
                                   help="Auto-populated from athlete profile" if registered_age else None)
        gi_nogi = st.selectbox("Gi / No-Gi", GI_NOGI, key="gi_nogi")
        ruleset = st.selectbox("Ruleset", list(RULESETS.keys()), key="ruleset")

    # Use registered athlete name or fallback  
    fighter_a_name = st.session_state.get("registered_athlete_name") or st.session_state.get("fighter_a", "")
    current_user = st.session_state.get("current_user", "Username")
    result = st.selectbox("Match Result", [
        f"{fighter_a_name or current_user} wins by Points",
        f"{fighter_a_name or current_user} wins by Submission", 
        f"{fighter_a_name or current_user} wins by Advantage",
        f"{fighter_a_name or current_user} wins by Referee Decision",
        f"{fighter_a_name or current_user} wins by DQ",
        "Fighter B wins by Points",
        "Fighter B wins by Submission",
        "Fighter B wins by Advantage", 
        "Fighter B wins by Referee Decision",
        "Fighter B wins by DQ",
        "Draw"
    ], key="result")

    if result and "Submission" in result:
        submission_type = st.selectbox("Submission Used", ALL_SUBMISSIONS, key="sub_type")
    else:
        submission_type = None

    # Athlete profile is now managed on home page
    if st.session_state.get('current_athlete_id'):
        profile = athlete_manager.get_athlete_profile(st.session_state.current_athlete_id)
        if profile:
            st.info(f"🏷️ **Linked to athlete:** {profile['name']} ({profile.get('team', 'No Team')})")
        else:
            st.warning("⚠️ Selected athlete profile not found")
    else:
        st.info("ℹ️ No athlete profile selected. Select one on the Home page for tracking.")

    # Save Match Info Button
    if st.button("💾 Save Match Info", type="secondary"):
        # Save match to Supabase
        match_result = create_match_supabase(
            athlete_id=st.session_state.get('current_athlete_id'),
            coach_id=st.session_state.get('current_user'),
            event_name=st.session_state.get('event_name'),
            video_url=st.session_state.get('match_video_url')
        )
        st.success("✅ Match information saved to Supabase!")
        # Optionally, get the new match_id: match_result.data[0]['id']

    st.success("✅ Fill in the match details above, then proceed to the Video Review tab.")

# TAB 3: Assessment
with tab3:
    # Instructions for Assessment tab
    st.info("📊 **Assessment Instructions:**\n"
           "1. 🤖 Assessments auto-generate from timeline events in Video Review\n"
           "2. ⚙️ Use Manual Override to adjust scores if needed\n"
           "3. 🏷️ Add tactical tags to categorize performance patterns\n"
           "4. 📝 Include coach notes for personalized feedback")
    st.markdown("---")

    st.header("Assessment")
    # Show current review being edited
    editing_review_id = st.session_state.get("editing_review_id", "")
    editing_assessment = st.session_state.get("editing_assessment", False)
    editing_assessment_id = st.session_state.get("editing_assessment_id", "")
    
    if editing_assessment and editing_assessment_id:
        st.info(f"🔄 **Currently Editing Assessment:** {editing_assessment_id}")
        
        # Load assessment data into session state if not already loaded
        if "editing_assessment_data" in st.session_state and not st.session_state.get("assessment_data_loaded", False):
            assessment_data = st.session_state.editing_assessment_data
            
            # Load assessment ratings
            assessments_dict = assessment_data.get("assessments", {})
            loaded_assessments = {}
            for area, data in assessments_dict.items():
                if data.get("demonstrated", False):
                    loaded_assessments[area] = data.get("rating", 0)
            
            st.session_state.assessments = loaded_assessments
            st.session_state.assessment_data_loaded = True
            
            # Load match context into session state 
            match_context = assessment_data.get("match_context", {})
            for key, value in [
                ("match_number", match_context.get("match_number", "")),
                ("fighter_a", assessment_data.get("metadata", {}).get("athlete_id", "").replace("_", " ").title()),
                ("belt", match_context.get("belt_level", "")),
                ("weight_class", match_context.get("weight_class", "")),
                ("ruleset", match_context.get("ruleset", "IBJJF")),
                ("result", match_context.get("result", "")),
            ]:
                if key not in st.session_state:
                    st.session_state[key] = value
                    
            st.success(f"✅ Loaded assessment data from **{editing_assessment_id}**!")
    
    elif st.session_state.get("editing_existing_match", False) and editing_review_id:
        st.info(f"🔄 **Currently Editing:** {editing_review_id}")

    # Check if we have existing assessments (from loaded review) or should auto-calculate
    if not hasattr(st.session_state, 'assessments_calculated') and (not st.session_state.assessments or all(v == 0 for v in st.session_state.assessments.values())):
        # No assessments yet, calculate from timeline (but only once)
        st.caption("Assessment automatically generated from key moments timeline. Only areas demonstrated in the match are evaluated.")
        auto_assessments = analyze_timeline_for_assessment(st.session_state.events)
        st.session_state.assessments = auto_assessments
        st.session_state.assessments_calculated = True  # Prevent recalculation
    elif st.session_state.assessments:
        # We have existing assessments (likely loaded from review)
        if editing_review_id:
            st.caption("Assessments loaded from saved review. Edit ratings below or use 'Recalculate' to update from current timeline.")
            if st.button("🔄 Recalculate from Timeline", help="Replace current ratings with auto-calculated values from timeline"):
                auto_assessments = analyze_timeline_for_assessment(st.session_state.events)
                st.session_state.assessments = auto_assessments
                st.success("✅ Assessments recalculated from timeline events!")
                st.rerun()
        else:
            st.caption("Assessment automatically generated from key moments timeline. Only areas demonstrated in the match are evaluated.")
    else:
        st.caption("Add timeline events to generate assessments automatically.")

    if st.session_state.assessments:
        for area, rating in st.session_state.assessments.items():
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"**{area}**")
                st.caption(ASSESSMENT_AREAS[area])
            with col2:
                # Display star rating
                stars = "★" * rating + "☆" * (5 - rating)
                st.write(f"{stars} {rating}/5")
            with col3:
                label = RATING_LABELS.get(rating, "")
                if rating <= 2:
                    st.error(f"⚠️ {label}")
                elif rating >= 4:
                    st.success(f"✅ {label}")
                else:
                    st.info(f"ℹ️ {label}")

        st.divider()

        # Show areas not demonstrated
        demonstrated_areas = set(st.session_state.assessments.keys())
        all_areas = set(ASSESSMENT_AREAS.keys())
        not_demonstrated = all_areas - demonstrated_areas

        if not_demonstrated:
            st.subheader("Areas Not Demonstrated")
            st.caption("These areas were not observed in the key moments timeline for this match:")
            for area in sorted(not_demonstrated):
                st.write(f"• {area}")
    else:
        st.info("🎬 No assessments yet. Add key moments in the Video Review tab to generate automatic assessment.")

    st.divider()
    st.subheader("Manual Override")
    st.caption("Optionally adjust any auto-generated scores or add scores for non-demonstrated areas:")

    # Manual adjustment sliders for all areas
    manual_assessments = {}
    for area in ASSESSMENT_AREAS.keys():
        current_score = st.session_state.assessments.get(area, 0) if st.session_state.assessments else 0
        col1, col2 = st.columns([3, 2])
        with col1:
            if current_score > 0:
                manual_score = st.slider(
                    f"{area} (Auto: {current_score})",
                    min_value=0, max_value=5,
                    value=current_score,
                    help=f"Auto-generated: {current_score}/5 - {RATING_LABELS.get(current_score, '')}",
                    key=f"manual_{area}"
                )
            else:
                manual_score = st.slider(
                    f"{area}",
                    min_value=0, max_value=5,
                    value=0,
                    help="Not demonstrated in timeline - set manually if needed",
                    key=f"manual_{area}"
                )
            manual_assessments[area] = manual_score
        with col2:
            if manual_score > 0:
                label = RATING_LABELS.get(manual_score, "")
                if manual_score <= 2:
                    st.warning(f"⚠️ {label}")
                elif manual_score >= 4:
                    st.success(f"✅ {label}")
                else:
                    st.info(f"ℹ️ {label}")

    # Update session state with manual overrides
    st.session_state.assessments = {area: score for area, score in manual_assessments.items() if score > 0}

    st.divider()
    st.subheader("Tactical Tags")
    st.caption("Select all that apply to the reviewed athlete's performance.")

    for category, tags in TACTICAL_TAGS.items():
        with st.expander(f"🏷️ {category}"):
            for tag in tags:
                if st.checkbox(tag, key=f"tag_{tag}"):
                    if tag not in st.session_state.tactical_tags:
                        st.session_state.tactical_tags.append(tag)
                else:
                    if tag in st.session_state.tactical_tags:
                        st.session_state.tactical_tags.remove(tag)

    st.divider()
    st.subheader("Coach Notes")
    coach_notes = st.text_area(
        "Additional observations, game plan suggestions, or notes for the athlete:",
        height=150,
        key="coach_notes"
    )

    # Save Assessment Button
    editing_assessment = st.session_state.get("editing_assessment", False)
    editing_assessment_id = st.session_state.get("editing_assessment_id", "")
    
    button_label = "💾 Update Assessment" if editing_assessment else "💾 Save Assessment"
    if st.button(button_label, type="secondary"):
        # Generate assessment report
        current_user = st.session_state.get("current_user", "Username")
        athlete_id = st.session_state.get("current_athlete_id")

        if st.session_state.assessments and any(score > 0 for score in st.session_state.assessments.values()):
            # Use existing report ID if editing, otherwise generate new one
            if editing_assessment and editing_assessment_id:
                report_id = editing_assessment_id
                created_date = st.session_state.get("editing_assessment_data", {}).get("metadata", {}).get("created_date", datetime.now().isoformat())
            else:
                report_id = f"ASSESS-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                created_date = datetime.now().isoformat()
            
            # Create assessment report data
            assessment_report = {
                "metadata": {
                    "report_id": report_id,
                    "athlete_id": athlete_id,
                    "generated_by": current_user,
                    "created_date": created_date,
                    "last_updated": datetime.now().isoformat(),
                    "report_type": "assessment"
                },
                "match_context": {
                    "match_number": st.session_state.get("match_number", ""),
                    "opponent": st.session_state.get("fighter_b", ""),
                    "event": st.session_state.get("event_name", ""),
                    "belt_level": st.session_state.get("belt", ""),
                    "weight_class": st.session_state.get("weight_class", ""),
                    "ruleset": st.session_state.get("ruleset", "IBJJF"),
                    "result": st.session_state.get("result", "")
                },
                "assessments": {
                    area: {
                        "rating": rating,
                        "label": RATING_LABELS.get(rating, ""),
                        "demonstrated": rating > 0
                    }
                    for area, rating in st.session_state.assessments.items()
                },
                "tactical_tags": st.session_state.get("tactical_tags", []),
                "coach_notes": st.session_state.get("coach_notes", ""),
                "timeline_events": len(st.session_state.get("events", [])),
                "timeline": st.session_state.get("events", []),  # Include actual timeline events
                "strengths": [area for area, rating in st.session_state.assessments.items() if rating >= 4],
                "improvement_areas": [area for area, rating in st.session_state.assessments.items() if rating <= 2],
                "overall_score": round(sum(st.session_state.assessments.values()) / len(st.session_state.assessments), 1) if st.session_state.assessments else 0
            }

            # Save assessment report to user's directory
            user_dir = os.path.join("data", "users", current_user, "assessments")
            os.makedirs(user_dir, exist_ok=True)

            report_filename = f"{assessment_report['metadata']['report_id']}.json"
            report_path = os.path.join(user_dir, report_filename)

            try:
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(assessment_report, f, indent=2, ensure_ascii=False)

                # If athlete is linked, update their assessment history
                if athlete_id:
                    try:
                        athlete_manager = AthleteManager("data", current_user, st.session_state.get("user_role", "individual"))

                        # Get current athlete profile
                        athlete_profile = athlete_manager.get_athlete_profile(athlete_id)
                        if athlete_profile:
                            # Add or update assessment report in athlete's history
                            if "assessment_reports" not in athlete_profile:
                                athlete_profile["assessment_reports"] = []

                            # If editing, update existing entry; otherwise add new one
                            if editing_assessment and editing_assessment_id:
                                # Update existing assessment entry
                                for i, ar in enumerate(athlete_profile["assessment_reports"]):
                                    if ar.get("report_id") == editing_assessment_id:
                                        athlete_profile["assessment_reports"][i] = {
                                            "report_id": assessment_report['metadata']['report_id'],
                                            "date": assessment_report['metadata']['created_date'],
                                            "overall_score": assessment_report['overall_score'],
                                            "match_context": assessment_report['match_context'],
                                            "file_path": report_path
                                        }
                                        break
                                else:
                                    # Entry not found, add as new
                                    athlete_profile["assessment_reports"].append({
                                        "report_id": assessment_report['metadata']['report_id'],
                                        "date": assessment_report['metadata']['created_date'],
                                        "overall_score": assessment_report['overall_score'],
                                        "match_context": assessment_report['match_context'],
                                        "file_path": report_path
                                    })
                            else:
                                # Add new assessment entry
                                athlete_profile["assessment_reports"].append({
                                    "report_id": assessment_report['metadata']['report_id'],
                                    "date": assessment_report['metadata']['created_date'],
                                    "overall_score": assessment_report['overall_score'],
                                    "match_context": assessment_report['match_context'],
                                    "file_path": report_path
                                })

                            # Update athlete profile
                            athlete_manager._save_athlete_profile(athlete_profile)

                            # Clear editing state if we were editing
                            if editing_assessment:
                                for key in ["editing_assessment", "editing_assessment_id", "editing_assessment_data", "assessment_data_loaded"]:
                                    if key in st.session_state:
                                        del st.session_state[key]

                            success_msg = f"✅ Assessment {'updated' if editing_assessment else 'saved'} successfully!\n📄 Report: {assessment_report['metadata']['report_id']}\n👤 Linked to athlete profile"
                            st.success(success_msg)
                        else:
                            st.success(f"✅ Assessment {'updated' if editing_assessment else 'saved'} successfully!\n📄 Report: {assessment_report['metadata']['report_id']}")
                    except Exception as e:
                        st.success(f"✅ Assessment saved successfully!\n📄 Report: {assessment_report['metadata']['report_id']}\n⚠️ Note: Could not link to athlete profile")
                else:
                    st.success(f"✅ Assessment saved successfully!\n📄 Report: {assessment_report['metadata']['report_id']}\nℹ️ No athlete linked - report saved independently")

            except Exception as e:
                st.error(f"❌ Error saving assessment: {str(e)}")
        else:
            st.warning("⚠️ No assessments to save. Complete some assessments first.")

# TAB 4: Export
with tab4:
    # Instructions for Export tab
    st.info("📄 **Export Instructions:**\n"
           "1. 📝 Add custom analysis notes for personalized insights\n"
           "2. 📋 Generate PDF reports or download JSON data\n"
           "3. 🤖 Get AI-powered summary with training recommendations\n"
           "4. 💾 Save to progress tracking for historical analysis")
    st.markdown("---")

    st.header("Export Review")
    # Show current review being edited
    editing_review_id = st.session_state.get("editing_review_id", "")
    if st.session_state.get("editing_existing_match", False) and editing_review_id:
        st.info(f"🔄 **Currently Editing:** {editing_review_id}")

    # Additional Analysis Section
    st.subheader("Additional Analysis")
    col1, col2 = st.columns(2)

    with col1:
        custom_strengths = st.text_area(
            "Custom Strengths (beyond assessment scores):",
            height=120,
            placeholder="Add any additional strengths, tactical insights, or positive observations...",
            key="custom_strengths"
        )

    with col2:
        custom_improvements = st.text_area(
            "Custom Areas for Improvement (beyond assessment scores):",
            height=120,
            placeholder="Add any additional areas for improvement, specific technique notes, or development priorities...",
            key="custom_improvements"
        )

    st.divider()

    # Get submission type from session state if it exists
    submission_type = st.session_state.get("sub_type", None) if st.session_state.get("result", "").find("Submission") != -1 else None

    # Gather all data
    match_info = {
        "match_number": st.session_state.get("match_number", ""),
        "fighter_a": st.session_state.get("fighter_a", ""),
        "team_a": st.session_state.get("team_a", ""),
        "fighter_b": st.session_state.get("fighter_b", ""),
        "team_b": st.session_state.get("team_b", ""),
        "belt": st.session_state.get("belt", ""),
        "weight_class": st.session_state.get("weight_class", ""),
        "age_division": st.session_state.get("age_division", ""),
        "gi_nogi": st.session_state.get("gi_nogi", ""),
        "ruleset": st.session_state.get("ruleset", "IBJJF"),
        "event": st.session_state.get("event_name", ""),
        "video_url": st.session_state.get("match_video_url", ""),
        "result": st.session_state.get("result", ""),
        "submission_type": submission_type
    }

    # Map display result back to internal format for storage
    current_user = st.session_state.get("current_user", "Username")
    if f"{current_user} wins" in match_info["result"]:
        match_info["result"] = match_info["result"].replace(f"{current_user} wins", "Fighter A wins")

    review_data = build_review_data(
        match_info=match_info,
        events=st.session_state.events,
        assessments=st.session_state.assessments,
        tactical_tags=st.session_state.tactical_tags,
        notes=st.session_state.get("coach_notes", ""),
        custom_strengths=st.session_state.get("custom_strengths", ""),
        custom_improvements=st.session_state.get("custom_improvements", ""),
        existing_review_id=editing_review_id if st.session_state.get("editing_existing_match", False) else None
    )

    # If editing, preserve the original review ID and creation date
    if st.session_state.get("editing_existing_match", False):
        editing_review_id = st.session_state.get("editing_review_id", "")
        if editing_review_id:
            # Keep the original review ID but update the timestamp
            original_metadata = review_data["metadata"].copy()
            review_data["metadata"]["review_id"] = editing_review_id
            review_data["metadata"]["last_updated"] = datetime.now().isoformat()

    # Preview section
    st.subheader("Preview")

    # Generate AI Summary
    ai_summary = generate_ai_summary_report(review_data)

    # Add AI summary to review data
    review_data["analysis"]["ai_summary"] = ai_summary

    with st.expander("🤖 AI Summary & Training Recommendations", expanded=True):
        st.info("AI-generated analysis based on your timeline data, assessment scores, and tactical observations")
        st.markdown(ai_summary)

    with st.expander("📄 View Markdown Report"):
        markdown_report = export_markdown(review_data)
        st.markdown(markdown_report)

    with st.expander("🔧 View JSON Data"):
        st.json(review_data)

    # Export buttons
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        # Check if we're editing an existing match
        is_editing = st.session_state.get("editing_existing_match", False)
        editing_review_id = st.session_state.get("editing_review_id", "")

        button_text = "📝 Update Match" if is_editing else "💾 Save JSON (Training Data)"

        if st.button(button_text, type="primary"):
            if is_editing and editing_review_id:
                # Update existing match (optional: implement Supabase update logic if needed)
                st.warning("Update for existing reviews in Supabase is not yet implemented.")
                st.session_state.editing_existing_match = False
                st.session_state.editing_review_id = ""
            else:
                # Create new review in Supabase
                review_id = review_data["metadata"]["review_id"]
                result = create_review_supabase(review_data)
                if result and getattr(result, 'status_code', 200) in (200, 201):
                    st.success(f"✅ Review saved to Supabase with ID: **{review_id}**")
                else:
                    st.error("❌ Failed to save review to Supabase.")
            st.balloons()

    with col2:
        # Create filename with match number if available
        match_number = review_data.get("match_info", {}).get("match_number", "")
        if match_number:
            filename = f"{match_number.replace(' ', '_')}_{review_data['metadata']['review_id']}_complete_report.md"
        else:
            filename = f"{review_data['metadata']['review_id']}_complete_report.md"

        st.download_button(
            label="📥 Download Complete Report (with AI Summary)",
            data=markdown_report,
            file_name=filename,
            mime="text/markdown"
        )

    # Summary metrics
    st.divider()
    st.subheader("Review Summary")
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("Key Moments", len(st.session_state.events))
    with col_b:
        strengths_count = sum(1 for score in st.session_state.assessments.values() if isinstance(score, (int, float)) and score >= 4)
        st.metric("Strengths", strengths_count)
    with col_c:
        weakness_count = sum(1 for score in st.session_state.assessments.values() if isinstance(score, (int, float)) and score <= 2)
        st.metric("Areas to Improve", weakness_count)
    with col_d:
        st.metric("Tactical Tags", len(st.session_state.tactical_tags))

    st.divider()
    if st.button("🔄 Start New Review"):
        st.session_state.events = []
        st.session_state.assessments = {}
        st.session_state.tactical_tags = []
        st.session_state.editing_event = None
        # Clear custom analysis fields
        if "custom_strengths" in st.session_state:
            del st.session_state.custom_strengths
        if "custom_improvements" in st.session_state:
            del st.session_state.custom_improvements
        # Reset assessment calculation flag
        if 'assessments_calculated' in st.session_state:
            del st.session_state.assessments_calculated
        st.rerun()

# TAB 2: Video Viewer with Timeline
with tab2:
        # Instructions for Video Review tab
        st.info("🎥 **Video Review Instructions:**\n"
               "1. 🔗 Paste your video URL (YouTube, Vimeo, Google Drive, etc.)\n"
               "2. ⏱️ Log key moments while watching using the form below\n"
               "3. 🏆 Track live scoring in the sidebar\n"
               "4. 📊 Auto-generated assessments will appear in Assessment tab")
        st.markdown("---")

        editing_review_id = st.session_state.get("editing_review_id", "")
        if st.session_state.get("editing_existing_match", False) and editing_review_id:
            st.info(f"🔄 **Currently Editing:** {editing_review_id}")

        st.caption("Watch your match while logging key moments - no need to switch tabs!")

        # Get video URL from current session or allow manual entry (avoid key conflicts)
        match_info_video_url = ""
        try:
            # Safely get video URL from match info without causing widget conflicts
            match_info_video_url = st.session_state.get("match_video_url", "")
        except:
            pass  # If there's any conflict, just use empty string

        # Top section: Video player and current score
        col_video, col_score = st.columns([3, 1])

        with col_video:
            st.subheader("🎥 Video Player")

            # Video URL input (independent from Match Info tab to avoid conflicts)
            video_url_input = st.text_input(
                "Video URL",
                value=match_info_video_url,
                placeholder="Enter YouTube, Vimeo, or direct video URL",
                help="Paste your video URL here. YouTube, Vimeo, and direct video links are supported.",
                key="video_viewer_url"
            )

            # Timeline input section - moved here for easy access while watching
            st.markdown("---")
            st.subheader("⏱️ Add Key Moment While Watching")
            st.caption("🎥 Keep the video playing and quickly log moments as they happen")

            # Check if editing an existing event
            editing_mode = st.session_state.editing_event is not None
            if editing_mode:
                st.info(f"📝 Editing event #{st.session_state.editing_event + 1} - Make changes and click Update")
                edit_event = st.session_state.events[st.session_state.editing_event]

            # Row 1: Time & Fighter & Position
            col_time, col_fighter, col_pos = st.columns([1, 1, 2])

            with col_time:
                st.markdown("**⏱️ Time**")
                event_time = st.text_input("Timestamp", 
                                           value=edit_event.get('timestamp', '') if editing_mode else '',
                                           placeholder="2:35",
                                           key="video_event_time")

            current_user = st.session_state.get("current_user", "Username")
            with col_fighter:
                st.markdown("**🤼 Fighter**")
                # Map internal identifier to display name for editing
                display_fighter = edit_event.get('fighter', 'Fighter A') if editing_mode else current_user
                if display_fighter == 'Fighter A':
                    display_fighter = current_user

                event_fighter = st.selectbox("Fighter", [current_user, "Fighter B"], 
                                           index=0 if not editing_mode else ([current_user, "Fighter B"].index(display_fighter)),
                                           key="video_event_fighter")

            with col_pos:
                st.markdown("**🥋 Position Details**")
                position_category = st.selectbox("Position Category", list(POSITIONS.keys()), 
                                               index=0 if not editing_mode else list(POSITIONS.keys()).index(next((k for k, v in POSITIONS.items() if edit_event.get('position', '') in v), list(POSITIONS.keys())[0])),
                                               key="video_pos_cat")
                event_position = st.selectbox("Specific Position", POSITIONS[position_category], 
                                            index=0 if not editing_mode else POSITIONS[position_category].index(edit_event.get('position', POSITIONS[position_category][0])),
                                            key="video_event_position")

            # Row 2: Action & Result
            col_act, col_result = st.columns(2)

            with col_act:
                st.markdown("**⚡ Action Details**")
                action_category = st.selectbox("Action Category", list(ACTIONS.keys()), 
                                             index=0 if not editing_mode else list(ACTIONS.keys()).index(next((k for k, v in ACTIONS.items() if edit_event.get('action', '') in v), list(ACTIONS.keys())[0])),
                                             key="video_act_cat")
                event_action = st.selectbox("Specific Action", ACTIONS[action_category], 
                                          index=0 if not editing_mode else ACTIONS[action_category].index(edit_event.get('action', ACTIONS[action_category][0])),
                                          key="video_event_action")
                
                # Missed Opportunities under Specific Action
                st.markdown("**🎯 Missed Opportunity**")
                # Safely get the index for missed opportunity, defaulting to 0 if not found
                missed_opportunity_value = edit_event.get('missed_opportunity', MISSED_OPPORTUNITIES[0]) if editing_mode else MISSED_OPPORTUNITIES[0]
                try:
                    missed_opportunity_index = MISSED_OPPORTUNITIES.index(missed_opportunity_value) if editing_mode else 0
                except ValueError:
                    missed_opportunity_index = 0  # Default to first item if value not found in list
                
                event_missed = st.selectbox("What Could Have Been Better?", MISSED_OPPORTUNITIES,
                                          index=missed_opportunity_index,
                                          key="video_event_missed")

            with col_result:
                st.markdown("**🏆 Result & Points**")
                event_result = st.selectbox("Outcome", MOMENT_RESULTS,
                                          index=0 if not editing_mode else MOMENT_RESULTS.index(edit_event.get('result', MOMENT_RESULTS[0])),
                                          key="video_event_result")

                # Calculate points
                ruleset_key = st.session_state.get("ruleset", "IBJJF")
                ruleset = RULESETS.get(ruleset_key, {})
                scoring = ruleset.get("scoring", {})
                calculated_points = 0

                if "Attempt (Advantage)" in event_result and "Advantage" in scoring:
                    calculated_points = scoring["Advantage"]
                elif event_result in scoring:
                    calculated_points = scoring[event_result]

                st.metric("Points", f"{calculated_points} pts")

            # Row 3: Analysis & Context
            st.markdown("**🎯 Analysis & Context**")
            col_reason, col_positioning = st.columns(2)

            with col_reason:
                st.markdown("**🤔 Why & Motivation**") 
                reason_category = st.selectbox("Why? Category", list(BJJ_REASONS.keys()), 
                                             index=0 if not editing_mode else list(BJJ_REASONS.keys()).index(next((k for k, v in BJJ_REASONS.items() if edit_event.get('why', '') in v), list(BJJ_REASONS.keys())[0])),
                                             key="video_reason_cat")
                event_why = st.selectbox("Specific Reason", BJJ_REASONS[reason_category], 
                                       index=0 if not editing_mode else BJJ_REASONS[reason_category].index(edit_event.get('why', BJJ_REASONS[reason_category][0])),
                                       key="video_event_why")

            with col_positioning:
                st.markdown("**📐 Base & Position**")
                event_positioning = st.selectbox("Positioning & Base", ["None"] + TACTICAL_TAGS["Positioning and Base"], 
                                               index=0 if not editing_mode else (["None"] + TACTICAL_TAGS["Positioning and Base"]).index(edit_event.get('positioning', 'None') or 'None'),
                                               key="video_event_positioning")

            # Row 4: Notes
            st.markdown("**📝 Additional Notes**")
            event_notes = st.text_area("Observations, tactical details, or other context:", 
                                      value=edit_event.get('notes', '') if editing_mode else '',
                                      height=80, 
                                      placeholder="e.g., 'Good setup but rushed finish', 'Opponent was tired', 'Perfect timing'...",
                                      key="video_event_notes")

            # Action buttons for timeline
            col_add, col_update, col_cancel = st.columns(3)

            with col_add:
                if not editing_mode:
                    if st.button("➕ Add Key Moment", type="primary", key="video_add_moment"):
                        # Map display selection to internal identifier
                        internal_fighter = "Fighter A" if event_fighter == current_user else event_fighter

                        new_event = {
                            "timestamp": event_time,
                            "fighter": internal_fighter,
                            "position": event_position,
                            "action": event_action,
                            "result": event_result,
                            "points": calculated_points,
                            "notes": event_notes,
                            "why": event_why,
                            "positioning": event_positioning if event_positioning != "None" else "",
                            "missed_opportunity": event_missed if event_missed != "None" else ""
                        }
                        st.session_state.events.append(new_event)

                        # Reset assessment calculation flag when adding new events
                        if 'assessments_calculated' in st.session_state:
                            del st.session_state.assessments_calculated

                        st.success(f"✅ Added: {event_time} - {event_fighter} - {event_action}")
                        st.rerun()

            with col_update:
                if editing_mode:
                    if st.button("💾 Update Key Moment", type="primary", key="video_update_moment"):
                        # Map display selection to internal identifier
                        internal_fighter = "Fighter A" if event_fighter == current_user else event_fighter

                        updated_event = {
                            "timestamp": event_time,
                            "fighter": internal_fighter,
                            "position": event_position,
                            "action": event_action,
                            "result": event_result,
                            "points": calculated_points,
                            "notes": event_notes,
                            "why": event_why,
                            "positioning": event_positioning if event_positioning != "None" else "",
                            "missed_opportunity": event_missed if event_missed != "None" else ""
                        }
                        st.session_state.events[st.session_state.editing_event] = updated_event
                        st.session_state.editing_event = None
                        st.success(f"✅ Updated: {event_time} - {event_fighter} - {event_action}")
                        st.rerun()

            with col_cancel:
                if editing_mode:
                    if st.button("❌ Cancel Edit", key="video_cancel_edit"):
                        st.session_state.editing_event = None
                        st.rerun()

            st.markdown("---")

            # Use the input directly - prioritize manual input over match info
            display_url = video_url_input if video_url_input else match_info_video_url

            if display_url:
                try:
                    # Handle different video types with better embedding
                    if "youtube.com" in display_url or "youtu.be" in display_url:
                        # Convert YouTube URL to embed format
                        video_id = None

                        if "youtu.be/" in display_url:
                            video_id = display_url.split("youtu.be/")[1].split("?")[0]
                        elif "watch?v=" in display_url:
                            video_id = display_url.split("watch?v=")[1].split("&")[0]

                        if video_id:
                            # Try Streamlit video first
                            try:
                                st.video(display_url)
                                st.success("✅ YouTube video loaded!")
                            except:
                                # Fallback to iframe embed
                                embed_url = f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
                                st.markdown(
                                    f"""
                                    <iframe width="100%" height="400" 
                                    src="{embed_url}" 
                                    frameborder="0" 
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                                    allowfullscreen>
                                    </iframe>
                                    """,
                                    unsafe_allow_html=True
                                )
                                st.info("🎥 Video embedded via iframe")
                        else:
                            st.error("❌ Could not extract YouTube video ID")

                    elif "vimeo.com" in display_url:
                        # Handle Vimeo videos
                        try:
                            st.video(display_url)
                            st.success("✅ Vimeo video loaded!")
                        except:
                            # Extract Vimeo ID for embed
                            vimeo_id = display_url.split("/")[-1].split("?")[0]
                            embed_url = f"https://player.vimeo.com/video/{vimeo_id}"

                            st.markdown(
                                f"""
                                <iframe width="100%" height="400" 
                                src="{embed_url}" 
                                frameborder="0" 
                                allow="autoplay; fullscreen; picture-in-picture" 
                                allowfullscreen>
                                </iframe>
                                """,
                                unsafe_allow_html=True
                            )
                            st.info("🎥 Vimeo video embedded via iframe")

                    elif display_url.endswith(('.mp4', '.webm', '.ogg', '.mov', '.avi')):
                        # Direct video files
                        try:
                            st.video(display_url)
                            st.success("✅ Video file loaded!")
                        except Exception as e:
                            st.markdown(
                                f"""
                                <video width="100%" height="400" controls>
                                    <source src="{display_url}" type="video/mp4">
                                    Your browser does not support the video tag.
                                </video>
                                """,
                                unsafe_allow_html=True
                            )
                            st.info("🎥 HTML5 video player")

                    elif "drive.google.com" in display_url:
                        # Google Drive videos
                        st.info("📁 Google Drive Video")

                        if "/file/d/" in display_url:
                            file_id = display_url.split("/file/d/")[1].split("/")[0]
                            embed_url = f"https://drive.google.com/file/d/{file_id}/preview"

                            st.markdown(
                                f"""
                                <iframe width="100%" height="400" 
                                src="{embed_url}" 
                                frameborder="0">
                                </iframe>
                                """,
                                unsafe_allow_html=True
                            )
                            st.caption("⚠️ Make sure the file is shared publicly")
                        else:
                            st.warning("❌ Invalid Google Drive URL format")

                    else:
                        # Try generic video embedding
                        try:
                            st.video(display_url)
                            st.success("✅ Video loaded!")
                        except Exception as e:
                            st.warning(f"⚠️ Could not embed video: {str(e)}")
                            st.markdown(f"**Direct Link:** [Open Video]({display_url})")

                except Exception as e:
                    st.error(f"❌ Error processing video: {str(e)}")
                    st.markdown(f"**Fallback Link:** [Open Video]({display_url})")

            else:
                # Show enhanced placeholder
                st.markdown(
                    """
                    <div style="
                        border: 2px dashed #ccc;
                        border-radius: 10px;
                        padding: 30px;
                        text-align: center;
                        color: #666;
                        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                        margin: 20px 0;
                    ">
                        <h3 style="margin-bottom: 15px;">🎬 Video Player Ready</h3>
                        <p>Enter a video URL above or in Match Info tab</p>
                        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin-top: 15px;">
                            <div>📺 YouTube</div>
                            <div>🎥 Vimeo</div>
                            <div>📁 Google Drive</div>
                            <div>📼 MP4/WebM</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col_score:
            st.subheader("🏆 Live Score")

            # Get ruleset for scoring
            ruleset_key = st.session_state.get("ruleset", "IBJJF")

            # Show match info - use registered athlete name
            registered_athlete_name = st.session_state.get("registered_athlete_name", "")
            fighter_a = st.session_state.get("fighter_a") or registered_athlete_name or st.session_state.get("current_user", "Username")
            fighter_b = st.session_state.get("fighter_b", "Fighter B")
            match_number = st.session_state.get("match_number", "")

            if match_number:
                st.caption(f"🏷️ {match_number}")
            st.caption(f"🤼 {fighter_a} vs {fighter_b}")

            # Calculate and display current score
            if st.session_state.events:
                final_scores = calculate_score(st.session_state.events, ruleset_key)
                st.metric(f"🎯 {fighter_a}", f"{final_scores['fighter_a']} pts")
                st.metric("🎯 Fighter B", f"{final_scores['fighter_b']} pts")
                st.metric("Events Logged", len(st.session_state.events))
            else:
                st.metric(f"🎯 {fighter_a}", "0 pts")
                st.metric("🎯 Fighter B", "0 pts")
                st.info("🏁 Log events below to see scoring")

            # Quick scoring reference
            if ruleset_key in RULESETS:
                with st.expander("📊 Scoring Rules"):
                    scoring = RULESETS[ruleset_key]["scoring"]
                    for action, points in scoring.items():
                        st.caption(f"{action}: **{points} pts**")

        # Display current timeline (compact view)
        if st.session_state.events:
            st.subheader(f"📋 Timeline ({len(st.session_state.events)} events)")

            # Show last 5 events for quick reference
            recent_events = st.session_state.events[-5:] if len(st.session_state.events) > 5 else st.session_state.events

            for i, event in enumerate(recent_events):
                actual_index = len(st.session_state.events) - len(recent_events) + i

                col_event, col_score, col_actions = st.columns([4, 1, 1])

                with col_event:
                    points_text = f" ({event.get('points', 0)} pts)" if event.get('points', 0) != 0 else ""
                    # Map internal Fighter A to display name
                    display_fighter_name = current_user if event['fighter'] == 'Fighter A' else event['fighter']
                    st.write(f"⏱️ **{event['timestamp']}** | {display_fighter_name} | {event['action']}{points_text}")
                    if event.get('notes'):
                        st.caption(f"📝 {event['notes']}")

                with col_score:
                    # Calculate score up to this point
                    events_up_to_here = st.session_state.events[:actual_index + 1]
                    scores = calculate_score(events_up_to_here, ruleset_key)
                    st.caption(f"A:{scores['fighter_a']} B:{scores['fighter_b']}")

                with col_actions:
                    col_edit, col_del = st.columns(2)
                with col_edit:
                    if st.button("✏️", key=f"video_edit_{actual_index}", help="Edit event"):
                        st.session_state.editing_event = actual_index
                        st.rerun()
                with col_del:
                    if st.button("🗑️", key=f"video_del_{actual_index}", help="Delete event"):
                        st.session_state.events.pop(actual_index)
                        if st.session_state.editing_event == actual_index:
                            st.session_state.editing_event = None
                        elif st.session_state.editing_event is not None and st.session_state.editing_event > actual_index:
                            pass
                        st.success("✅ Event deleted")
                        st.rerun()

        if len(st.session_state.events) > 5:
            st.caption(f"👆 Showing last 5 events. See Video Review tab for complete history.")

        else:
            st.info("🎬 No events logged yet. Watch the video and add key moments above!")