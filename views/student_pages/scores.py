"""
My Scores Page for Student Dashboard
"""
import streamlit as st
from services.team_service import TeamService
import pandas as pd


def render_scores(student):
    """Render the scores page showing student's teams and scores"""
    
    student_id = str(student.get("_id"))
    
    # Get team service
    team_service = TeamService()
    
    # ============ MY TEAMS & SCORES ============
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📈 My Scores")
    st.markdown("View all teams you're part of and their competition scores.")
    
    # Fetch student's teams
    student_teams = team_service.get_teams_for_student(student_id, student.get('email'))
    
    if student_teams:
        # Additional stats at top
        total_teams = len(student_teams)
        scored_teams = sum(1 for team in student_teams if team.get('final_score') is not None)
        pending_teams = total_teams - scored_teams
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Teams", total_teams)
        with col2:
            st.metric("Scored", scored_teams)
        with col3:
            st.metric("Pending", pending_teams)
        
        st.markdown("---")
        
        # Display each team with detailed score information
        for idx, team in enumerate(student_teams):
            event_name = team.get('event_name', 'Unknown Event')
            team_name = team.get('team_name', 'Unknown Team')
            
            # Team card
            st.markdown(f"<div class='card' style='background-color: #f8f9fa; padding: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
            
            # Team header
            st.markdown(f"### 🏅 {team_name}")
            st.markdown(f"**Event:** {event_name}")
            st.markdown("")
            
            # Team members
            members = team.get('members', [])
            member_names = [m.get('name', 'Unknown') for m in members]
            st.markdown(f"**Team Members:** {', '.join(member_names)}")
            st.markdown("")
            
            # Score information
            final_score = team.get('final_score')
            judge_scores = team.get('judge_scores', {})
            
            if final_score is not None:
                # Final score available
                col_a, col_b = st.columns([1, 3])
                with col_a:
                    st.metric("Final Score", f"{final_score:.2f}/100")
                
                with col_b:
                    st.success(f"✅ All judges have scored this team")
                
                # Show individual judge scores and comments
                if judge_scores:
                    st.markdown("---")
                    st.markdown("**Judge Scores & Feedback:**")
                    
                    for judge_id, score_data in judge_scores.items():
                        score = score_data.get('score', 'N/A')
                        comments = score_data.get('comments', '')
                        submitted_at = score_data.get('submitted_at', '')
                        
                        with st.expander(f"Judge Score: {score}/100", expanded=False):
                            st.write(f"**Score:** {score}/100")
                            if submitted_at:
                                st.caption(f"Submitted: {submitted_at[:19] if isinstance(submitted_at, str) else submitted_at}")
                            
                            if comments:
                                st.markdown("**Comments:**")
                                st.write(comments)
                            else:
                                st.caption("No comments provided.")
            
            elif judge_scores:
                # Partial scores (not all judges scored yet)
                st.warning(f"⏳ Judging in progress ({len(judge_scores)} judge(s) scored)")
                
                # Show available scores
                st.markdown("**Judge Scores Received:**")
                
                for judge_id, score_data in judge_scores.items():
                    score = score_data.get('score', 'N/A')
                    comments = score_data.get('comments', '')
                    submitted_at = score_data.get('submitted_at', '')
                    
                    with st.expander(f"Judge Score: {score}/100", expanded=False):
                        st.write(f"**Score:** {score}/100")
                        if submitted_at:
                            st.caption(f"Submitted: {submitted_at[:19] if isinstance(submitted_at, str) else submitted_at}")
                        
                        if comments:
                            st.markdown("**Comments:**")
                            st.write(comments)
                        else:
                            st.caption("No comments provided.")
            
            else:
                # No scores yet
                st.info("📝 No scores received yet. Judges will score your team soon!")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
    else:
        st.info("📭 You haven't joined any teams yet. Register for an event to get started!")
    
    st.markdown("</div>", unsafe_allow_html=True)
