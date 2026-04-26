"""
Reusable UI components for BJJ Mat IQ Streamlit app
Extracted from app.py to reduce code duplication
"""

import streamlit as st
import os
import json

# Export functions are expected to be imported from review_engine in app.py

def render_match_card(match, athlete_name=None, index=0, export_pdf=None, export_word=None, on_edit=None, on_delete=None, context_prefix=""):
    """
    Render a match review card with export, edit, and delete options.
    - match: dict with match data
    - athlete_name: optional, for display
    - index: unique index for Streamlit keys
    - export_pdf/export_word: functions to generate export bytes
    - on_edit: callback for edit action
    - on_delete: callback for delete action
    - context_prefix: string to prefix Streamlit keys for uniqueness
    """
    match_info = match.get("match_info", {})
    scores = match.get("scores", {})
    metadata = match.get("metadata", {})
    review_id = metadata.get("review_id", "")
    result = match_info.get("result", "")
    fighter_a = match_info.get("fighter_a", "")
    opponent = match_info.get("fighter_b", "Unknown Opponent")
    match_title = f"vs {opponent}" if opponent else "Assessment"
    
    # Result icon logic
    if (fighter_a and "wins" in result.lower() and fighter_a.lower() in result.lower()) or "Fighter A wins" in result or (athlete_name and athlete_name in result and "wins" in result):
        result_icon = "🟢"
    elif "Fighter B wins" in result or (fighter_a and ("loses" in result.lower() or "lost" in result.lower()) and fighter_a.lower() in result.lower()):
        result_icon = "🔴"
    else:
        result_icon = "🟡"

    with st.container():
        match_col, action_col = st.columns([3, 1])
        with match_col:
            display_title = f"**🎥 {result_icon} {athlete_name + ' ' if athlete_name else ''}{match_title}**"
            st.markdown(display_title)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.caption(f"📅 {metadata.get('reviewed_at', '')[:10]}")
            with col2:
                st.caption(f"🏆 {result}")
            with col3:
                st.caption(f"🎯 {scores.get('fighter_a', 0)}-{scores.get('fighter_b', 0)}")
            with col4:
                event = match_info.get("event", "")
                if event:
                    st.caption(f"🏟️ {event}")
        with action_col:
            if st.button("👁️ View & Export", key=f"{context_prefix}view_{review_id}_{index}", help="View details and export options", use_container_width=True):
                with st.expander(f"📄 Export {match_title}", expanded=True):
                    st.markdown("**📄 Export Options:**")
                    export_col1, export_col2 = st.columns(2)
                    with export_col1:
                        if export_pdf:
                            try:
                                pdf_bytes = export_pdf(match)
                                if pdf_bytes:
                                    st.download_button(
                                        label="📄 Download PDF",
                                        data=pdf_bytes,
                                        file_name=f"{match_title.replace(' ', '_')}_analysis.pdf",
                                        mime="application/pdf",
                                        key=f"{context_prefix}dl_pdf_{review_id}_{index}"
                                    )
                                else:
                                    st.error("❌ Failed to generate PDF - missing dependencies")
                            except Exception as e:
                                st.error(f"❌ PDF export error: {str(e)}")
                    with export_col2:
                        if export_word:
                            try:
                                word_bytes = export_word(match)
                                if word_bytes:
                                    st.download_button(
                                        label="📝 Download Word Doc",
                                        data=word_bytes,
                                        file_name=f"{match_title.replace(' ', '_')}_analysis.docx",
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                        key=f"{context_prefix}dl_word_{review_id}_{index}"
                                    )
                                else:
                                    st.error("❌ Failed to generate Word document - missing dependencies")
                            except Exception as e:
                                st.error(f"❌ Word export error: {str(e)}")
            if on_edit and st.button("✏️ Edit", key=f"{context_prefix}edit_{review_id}_{index}", help="Edit this match", use_container_width=True):
                on_edit(review_id)
            if on_delete and st.button("🗑️ Delete", key=f"{context_prefix}delete_{review_id}_{index}", help="Delete this match", use_container_width=True, type="secondary"):
                on_delete(review_id)


def render_assessment_card(assessment, athlete_name=None, index=0, export_pdf=None, export_word=None, on_edit=None, on_delete=None, context_prefix=""):
    """
    Render an assessment card with export, edit, and delete options.
    - assessment: dict with assessment data
    - athlete_name: optional, for display
    - index: unique index for Streamlit keys
    - export_pdf/export_word: functions to generate export bytes
    - on_edit: callback for edit action
    - on_delete: callback for delete action
    - context_prefix: string to prefix Streamlit keys for uniqueness
    """
    assessment_id = assessment.get("report_id", "")
    match_context = assessment.get("match_context", {})
    overall_score = assessment.get("overall_score", 0)
    result_text = match_context.get("result", "Assessment")
    belt = match_context.get("belt_level", "")
    date = assessment.get("date", "")
    file_path = assessment.get("file_path", "")
    
    if "wins" in result_text.lower():
        assess_icon = "🟢"
    elif "loses" in result_text.lower():
        assess_icon = "🔴"
    else:
        assess_icon = "📊"
    
    with st.container():
        assess_col, action_col = st.columns([3, 1])
        with assess_col:
            display_title = f"**📊 {assess_icon} {athlete_name + ' - ' if athlete_name else ''}Assessment**"
            st.markdown(display_title)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.caption(f"📅 {date[:10]}")
            with col2:
                st.caption(f"🏆 {result_text}")
            with col3:
                st.caption(f"⭐ Score: {overall_score:.1f}/5.0")
            with col4:
                if belt:
                    st.caption(f"🥋 {belt}")
        with action_col:
            if st.button("👁️ View & Export", key=f"{context_prefix}view_assess_{assessment_id}_{index}", help="View details and export options", use_container_width=True):
                if file_path and os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            assessment_data = json.load(f)
                        with st.expander(f"📊 Assessment Details - {assessment_id}", expanded=True):
                            assessments_dict = assessment_data.get("assessments", {})
                            st.markdown("**🎯 Skill Breakdown:**")
                            for area, data in assessments_dict.items():
                                if data.get("demonstrated", True):
                                    rating = data.get("rating", 0)
                                    label = data.get("label", "")
                                    stars = "⭐" * rating + "☆" * (5 - rating)
                                    st.write(f"• **{area}**: {stars} ({label})")
                            st.markdown("**📄 Export Options:**")
                            export_col1, export_col2 = st.columns(2)
                            with export_col1:
                                if export_pdf:
                                    try:
                                        # Map assessment to match-like structure for export
                                        export_data = assessment_data
                                        pdf_bytes = export_pdf(export_data)
                                        if pdf_bytes:
                                            st.download_button(
                                                label="📄 Download PDF",
                                                data=pdf_bytes,
                                                file_name=f"Assessment_{assessment_id}.pdf",
                                                mime="application/pdf",
                                                key=f"{context_prefix}dl_pdf_assess_{assessment_id}_{index}"
                                            )
                                        else:
                                            st.error("❌ Failed to generate PDF - missing dependencies")
                                    except Exception as e:
                                        st.error(f"❌ PDF export error: {str(e)}")
                            with export_col2:
                                if export_word:
                                    try:
                                        export_data = assessment_data
                                        word_bytes = export_word(export_data)
                                        if word_bytes:
                                            st.download_button(
                                                label="📝 Download Word Doc",
                                                data=word_bytes,
                                                file_name=f"Assessment_{assessment_id}.docx",
                                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                                key=f"{context_prefix}dl_word_assess_{assessment_id}_{index}"
                                            )
                                        else:
                                            st.error("❌ Failed to generate Word document - missing dependencies")
                                    except Exception as e:
                                        st.error(f"❌ Word export error: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Error loading assessment: {str(e)}")
                else:
                    st.error("❌ Assessment file not found")
            if on_edit and st.button("✏️ Edit", key=f"{context_prefix}edit_assess_{assessment_id}_{index}", help="Edit this assessment", use_container_width=True):
                on_edit(assessment_id)
            if on_delete and st.button("🗑️ Delete", key=f"{context_prefix}delete_assess_{assessment_id}_{index}", help="Delete this assessment", use_container_width=True, type="secondary"):
                on_delete(assessment_id)
