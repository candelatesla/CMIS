"""
Score Teams Page for Judge/Mentor Dashboard
"""
import streamlit as st
from services.team_service import TeamService
from services.email_service import EmailService


def render_score_teams(mentor):
    """Render the score teams page for judges"""
    
    mentor_id = str(mentor.get("_id"))
    team_service = TeamService()
    
    # ============ SCORE TEAMS ============
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📊 Score Teams")
    st.markdown("Submit scores for teams assigned to you.")
    
    # Fetch teams assigned to this judge
    teams = team_service.get_teams_assigned_to_judge(mentor_id)
    
    if teams:
        # Filter teams that haven't been scored yet (or allow re-scoring)
        unscored_teams = [t for t in teams if mentor_id not in t.get('judge_scores', {})]
        scored_teams = [t for t in teams if mentor_id in t.get('judge_scores', {})]
        
        # Tabs for unscored and scored teams
        tab1, tab2 = st.tabs(["⏳ Pending Scores", "✅ Already Scored"])
        
        with tab1:
            if unscored_teams:
                st.markdown(f"**{len(unscored_teams)} team(s) need your score:**")
                st.markdown("")
                
                for idx, team in enumerate(unscored_teams):
                    team_id = team.get('_id')
                    team_name = team.get('team_name', 'Unknown Team')
                    event_name = team.get('event_name', 'Unknown Event')
                    
                    # Team scoring card
                    st.markdown(f"<div class='card' style='background-color: #f8f9fa; padding: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
                    
                    st.markdown(f"### 🏅 {team_name}")
                    st.markdown(f"**Event:** {event_name}")
                    st.markdown("")
                    
                    # Team members
                    st.markdown("**Team Members:**")
                    members = team.get('members', [])
                    member_names = [m.get('name', 'Unknown') for m in members]
                    st.write(", ".join(member_names))
                    st.markdown("")
                    
                    # Submission (if exists)
                    submission = team.get('submission', '')
                    if submission:
                        with st.expander("📎 View Team Submission"):
                            st.text_area("", value=submission, height=150, disabled=True, key=f"view_submission_{idx}", label_visibility="collapsed")
                    
                    st.markdown("---")
                    
                    # Scoring form
                    with st.form(f"score_form_{team_id}"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            score = st.number_input(
                                "Score (0-100) *",
                                min_value=0.0,
                                max_value=100.0,
                                value=75.0,
                                step=0.5,
                                key=f"score_{team_id}"
                            )
                        
                        with col2:
                            st.markdown("")
                            st.markdown("")
                            submit_button = st.form_submit_button("✅ Save Score", type="primary", use_container_width=True)
                        
                        comments = st.text_area(
                            "Comments / Feedback (Optional)",
                            placeholder="Enter feedback for the team...",
                            height=100,
                            key=f"comments_{team_id}"
                        )
                        
                        if submit_button:
                            # Save score
                            result = team_service.save_judge_score(
                                team_id=team_id,
                                judge_id=mentor_id,
                                score=score,
                                comments=comments
                            )
                            
                            if "error" in result:
                                st.error(f"❌ Error saving score: {result['error']}")
                            else:
                                st.toast(f"✅ Score submitted for {team_name}!", icon="✅")
                                
                                # Send email notifications to all team members
                                try:
                                    email_service = EmailService()
                                    sent_count = email_service.send_team_score_notification(
                                        team=team,
                                        mentor=mentor,
                                        score=score,
                                        comments=comments
                                    )
                                    if sent_count > 0:
                                        st.toast(f"📧 Score notifications sent to {sent_count} team member(s)", icon="📧")
                                except Exception as e:
                                    print(f"Error sending score notifications: {str(e)}")
                                    # Don't fail the scoring process if email fails
                                
                                # Check if final score was calculated
                                if result.get('final_score') is not None:
                                    st.info(f"🏆 All judges have scored. Final score: {result['final_score']:.2f}/100")
                                
                                import time
                                time.sleep(2)
                                st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("")
            
            else:
                st.success("🎉 You've scored all assigned teams!")
                st.info("Check the 'Already Scored' tab to review your submissions.")
        
        with tab2:
            if scored_teams:
                st.markdown(f"**{len(scored_teams)} team(s) you've already scored:**")
                st.markdown("")
                
                for idx, team in enumerate(scored_teams):
                    team_id = team.get('_id')
                    team_name = team.get('team_name', 'Unknown Team')
                    event_name = team.get('event_name', 'Unknown Event')
                    
                    judge_scores = team.get('judge_scores', {})
                    your_score_data = judge_scores.get(mentor_id, {})
                    your_score = your_score_data.get('score', 'N/A')
                    your_comments = your_score_data.get('comments', '')
                    submitted_at = your_score_data.get('submitted_at', 'N/A')
                    
                    # Display scored team
                    with st.expander(f"✅ {team_name} – Score: {your_score}/100"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Team Information**")
                            st.write(f"**Event:** {event_name}")
                            st.write(f"**Team:** {team_name}")
                            
                            members = team.get('members', [])
                            member_names = [m.get('name', 'Unknown') for m in members]
                            st.write(f"**Members:** {', '.join(member_names)}")
                        
                        with col2:
                            st.markdown("**Your Score**")
                            st.metric("Score", f"{your_score}/100")
                            st.caption(f"Submitted: {submitted_at[:19] if isinstance(submitted_at, str) else submitted_at}")
                            
                            # Final score if available
                            final_score = team.get('final_score')
                            if final_score is not None:
                                st.info(f"🏆 **Final Score:** {final_score:.2f}/100")
                        
                        if your_comments:
                            st.markdown("---")
                            st.markdown("**Your Comments:**")
                            st.write(your_comments)
                        
                        # Option to re-score
                        st.markdown("---")
                        if st.button(f"🔄 Update Score", key=f"rescore_{team_id}"):
                            st.info("To update your score, please contact the administrator.")
            
            else:
                st.info("You haven't scored any teams yet. Check the 'Pending Scores' tab.")
    
    else:
        st.info("📭 No teams have been assigned to you yet. Check back later or contact the event administrator.")
    
    st.markdown("</div>", unsafe_allow_html=True)
