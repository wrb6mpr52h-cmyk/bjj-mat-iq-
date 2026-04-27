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
    import streamlit as st

    st.session_state.current_user = None
if "user_role" not in st.session_state:

    try:
        from supabase import create_client
        st.success("Supabase package is installed and importable.")
    except Exception as e:
        st.error(f"Supabase import failed: {e}")
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


st.session_state.events = []
if "assessments" not in st.session_state:
    st.session_state.assessments = {}
if "tactical_tags" not in st.session_state:
    st.session_state.tactical_tags = []

try:
    from supabase import create_client
    st.success("Supabase package is installed and importable.")
except Exception as e:
    st.error(f"Supabase import failed: {e}")