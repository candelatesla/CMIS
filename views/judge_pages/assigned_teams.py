"""
Assigned Teams Page for Judge/Mentor Dashboard
"""
import streamlit as st
from services.team_service import TeamService
import pandas as pd


def render_assigned_teams(mentor):
    """Render the assigned teams page for judges"""
    
    mentor_id = str(mentor.get("_id"))
    team_service = TeamService()
    
    # ============ ASSIGNED TEAMS ============
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🏆 Teams Assigned to You")
    st.markdown("View all teams you are judging for competitions and events.")
    
    # Fetch teams assigned to this judge
    teams = team_service.get_teams_assigned_to_judge(mentor_id)
    
    if teams:
        # Create DataFrame for display
        teams_data = []
        
        for team in teams:
            event_name = team.get('event_name', 'N/A')
            team_name = team.get('team_name', 'N/A')
            
            # Get member names
            members = team.get('members', [])
            member_names = [m.get('name', 'Unknown') for m in members]
            members_str = ", ".join(member_names) if member_names else "N/A"
            member_count = len(members)
            
            # Get scoring status
            judge_scores = team.get('judge_scores', {})
            has_scored = mentor_id in judge_scores
            
            if has_scored:
                your_score = judge_scores[mentor_id].get('score', 'N/A')
                status = "✅ Scored"
            else:
                your_score = "⏳ Pending"
                status = "📝 Not Scored"
            
            # Final score
            final_score = team.get('final_score')
            if final_score is not None:
                final_str = f"{final_score:.2f}"
            else:
                final_str = "Pending"
            
            teams_data.append({
                "Event": event_name,
                "Team Name": team_name,
                "Members": f"{member_count} members",
                "Your Score": your_score,
                "Final Score": final_str,
                "Status": status,
                "Team ID": team.get('_id')
            })
        
        # Display as DataFrame
        df = pd.DataFrame(teams_data)
        display_df = df.drop(columns=['Team ID'])
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Team details - expandable cards
        st.markdown("#### 📋 Team Details")
        
        for idx, team in enumerate(teams):
            team_name = team.get('team_name', 'Unknown Team')
            event_name = team.get('event_name', 'Unknown Event')
            
            with st.expander(f"🏅 {team_name} – {event_name}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Team Information**")
                    st.write(f"**Team Name:** {team_name}")
                    st.write(f"**Event:** {event_name}")
                    
                    # Members list
                    st.markdown("**Team Members:**")
                    members = team.get('members', [])
                    for member in members:
                        name = member.get('name', 'Unknown')
                        email = member.get('email', 'N/A')
                        st.write(f"• {name} ({email})")
                
                with col2:
                    st.markdown("**Scoring Information**")
                    
                    # Check if judge has scored
                    judge_scores = team.get('judge_scores', {})
                    if mentor_id in judge_scores:
                        your_score_data = judge_scores[mentor_id]
                        st.success(f"✅ You scored: **{your_score_data.get('score', 'N/A')}**/100")
                        
                        if your_score_data.get('comments'):
                            st.write(f"**Your Comments:** {your_score_data.get('comments')}")
                        
                        submitted_at = your_score_data.get('submitted_at', 'N/A')
                        st.caption(f"Submitted: {submitted_at[:19] if isinstance(submitted_at, str) else submitted_at}")
                    else:
                        st.warning("⏳ You haven't scored this team yet")
                        st.write("Go to 'Score Teams' to submit your score")
                    
                    # Final score if available
                    final_score = team.get('final_score')
                    if final_score is not None:
                        st.info(f"🏆 **Final Score:** {final_score:.2f}/100")
                    else:
                        st.info("🏆 **Final Score:** Pending (all judges must score)")
                
                # Submission field (if exists)
                submission = team.get('submission', '')
                if submission:
                    st.markdown("---")
                    st.markdown("**📎 Team Submission**")
                    st.text_area("", value=submission, height=100, disabled=True, key=f"submission_{idx}", label_visibility="collapsed")
        
        st.markdown("---")
        
        # Statistics
        total_teams = len(teams)
        scored_teams = sum(1 for team in teams if mentor_id in team.get('judge_scores', {}))
        pending_teams = total_teams - scored_teams
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Teams Assigned", total_teams)
        with col2:
            st.metric("Teams You've Scored", scored_teams)
        with col3:
            st.metric("Pending", pending_teams)
        
    else:
        st.info("📭 No teams have been assigned to you yet. Check back later or contact the event administrator.")
    
    st.markdown("</div>", unsafe_allow_html=True)
