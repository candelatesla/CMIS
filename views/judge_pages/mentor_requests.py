"""
Mentor Requests Page for Judge/Mentor Dashboard
"""
import streamlit as st
from services.mentoring_service import MentoringService
from services.email_service import EmailService


def render_mentor_requests(mentor):
    """Render the mentor requests page showing pending and accepted mentees"""
    
    mentor_id = str(mentor.get("_id"))
    mentoring_service = MentoringService()
    
    # ============ MENTOR REQUESTS ============
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("👥 Mentorship Requests")
    st.markdown("Manage your pending mentorship requests and view accepted students.")
    st.markdown("")
    
    # Create tabs for pending and accepted
    tab1, tab2 = st.tabs(["⏳ Pending Requests", "✅ Accepted Students"])
    
    # ============ TAB 1: PENDING REQUESTS ============
    with tab1:
        st.markdown("### 📬 Pending Mentorship Requests")
        st.caption("Students who have been matched to you and are awaiting your approval")
        st.markdown("")
        
        pending_requests = mentoring_service.get_pending_requests_for_mentor(mentor_id)
        
        if pending_requests:
            st.markdown(f"**{len(pending_requests)} pending request(s):**")
            st.markdown("")
            
            for idx, request in enumerate(pending_requests):
                student = request.get("student", {})
                match_reason = request.get("match_reason", "No reason provided")
                link_id = request.get("link_id")
                student_id = str(student.get("_id", ""))
                
                # Student card
                st.markdown(f"<div class='card' style='background-color: #fff3cd; padding: 20px; margin-bottom: 20px; border-left: 4px solid #ffc107;'>", unsafe_allow_html=True)
                
                # Student header
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### 👤 {student.get('name', 'Unknown Student')}")
                    st.markdown(f"**Email:** {student.get('email', 'N/A')}")
                with col2:
                    st.markdown("")
                    st.markdown("")
                    st.caption(f"Request #{idx + 1}")
                
                st.markdown("")
                
                # Student details
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("**Student Information:**")
                    major = student.get("major", "N/A")
                    year = student.get("year", "N/A")
                    gpa = student.get("gpa", "N/A")
                    
                    st.write(f"• **Major:** {major}")
                    st.write(f"• **Year:** {year}")
                    st.write(f"• **GPA:** {gpa}")
                
                with col_b:
                    st.markdown("**Skills & Interests:**")
                    skills = student.get("skills", [])
                    interests = student.get("interests", [])
                    
                    if skills:
                        st.write(f"• **Skills:** {', '.join(skills[:5])}")
                    else:
                        st.write("• **Skills:** Not specified")
                    
                    if interests:
                        st.write(f"• **Interests:** {', '.join(interests[:5])}")
                    else:
                        st.write("• **Interests:** Not specified")
                
                # Match reason
                st.markdown("---")
                with st.expander("🎯 Why were you matched?", expanded=True):
                    st.write(match_reason)
                
                # Resume (if available)
                if student.get("resume_text"):
                    with st.expander("📄 View Student Resume"):
                        st.text_area(
                            "",
                            value=student.get("resume_text", ""),
                            height=200,
                            disabled=True,
                            key=f"resume_pending_{student_id}_{idx}",
                            label_visibility="collapsed"
                        )
                
                st.markdown("---")
                
                # Action buttons
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
                
                with col_btn1:
                    if st.button(
                        "✅ Accept Mentorship",
                        key=f"accept_{link_id}_{idx}",
                        type="primary",
                        use_container_width=True
                    ):
                        # Use link_id for reliable lookup instead of mentor_id + student_id
                        result = mentoring_service.accept_request_by_link_id(link_id)
                        
                        if "error" in result:
                            st.error(f"❌ Error accepting request: {result['error']}")
                        else:
                            # Get match reason from request
                            match_reason = request.get('match_reason', 'You were matched based on complementary skills and interests.')
                            
                            # Send acceptance emails using new email service methods
                            try:
                                email_service = EmailService()
                                
                                # Send email to student
                                email_service.send_mentor_acceptance_email(
                                    student=student,
                                    mentor=mentor,
                                    match_reason=match_reason
                                )
                                
                                # Send confirmation email to mentor
                                email_service.send_mentor_accept_confirmation_email(
                                    student=student,
                                    mentor=mentor,
                                    match_reason=match_reason
                                )
                                
                                st.toast("✅ Mentorship accepted! Emails sent.", icon="✅")
                                
                            except Exception as e:
                                print(f"Error sending acceptance emails: {str(e)}")
                                st.toast("✅ Mentorship accepted!", icon="✅")
                            
                            import time
                            time.sleep(1)
                            st.rerun()
                
                with col_btn2:
                    if st.button(
                        "❌ Decline",
                        key=f"decline_{link_id}_{idx}",
                        use_container_width=True
                    ):
                        # Use link_id for reliable lookup
                        result = mentoring_service.decline_request_by_link_id(link_id)
                        
                        if "error" in result:
                            st.error(f"❌ Error declining request: {result['error']}")
                        else:
                            st.toast(f"Request from {student.get('name')} declined", icon="ℹ️")
                            import time
                            time.sleep(1)
                            st.rerun()
                
                with col_btn3:
                    st.markdown("")  # Spacing
                
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("")
        
        else:
            st.info("📭 No pending mentorship requests at this time.")
            st.markdown("")
            st.markdown("When students are matched to you through our matching system, their requests will appear here for your approval.")
    
    # ============ TAB 2: ACCEPTED STUDENTS ============
    with tab2:
        st.markdown("### ✅ Your Accepted Mentees")
        st.caption("Students you are currently mentoring")
        st.markdown("")
        
        accepted_students = mentoring_service.get_students_mentored_by(mentor_id)
        
        if accepted_students:
            st.markdown(f"**You are mentoring {len(accepted_students)} student(s):**")
            st.markdown("")
            
            for idx, student in enumerate(accepted_students):
                student_id = str(student.get("_id", ""))
                match_reason = student.get("match_reason", "No reason provided")
                matched_at = student.get("matched_at")
                
                # Student card
                with st.expander(f"👤 {student.get('name', 'Unknown Student')} – {student.get('email', 'N/A')}", expanded=False):
                    
                    # Student details in columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Student Information:**")
                        st.write(f"**Email:** {student.get('email', 'N/A')}")
                        st.write(f"**Major:** {student.get('major', 'N/A')}")
                        st.write(f"**Year:** {student.get('year', 'N/A')}")
                        st.write(f"**GPA:** {student.get('gpa', 'N/A')}")
                        
                        if matched_at:
                            st.caption(f"Matched: {str(matched_at)[:19]}")
                    
                    with col2:
                        st.markdown("**Skills & Interests:**")
                        skills = student.get("skills", [])
                        interests = student.get("interests", [])
                        
                        if skills:
                            st.write("**Skills:**")
                            st.write(", ".join(skills))
                        
                        if interests:
                            st.write("**Interests:**")
                            st.write(", ".join(interests))
                    
                    # Match reason
                    st.markdown("---")
                    st.markdown("**Why you were matched:**")
                    st.write(match_reason)
                    
                    # Resume
                    if student.get("resume_text"):
                        st.markdown("---")
                        st.markdown("**Student Resume:**")
                        st.text_area(
                            "",
                            value=student.get("resume_text", ""),
                            height=200,
                            disabled=True,
                            key=f"resume_accepted_{student_id}_{idx}",
                            label_visibility="collapsed"
                        )
                    
                    # Contact button
                    st.markdown("---")
                    student_email = student.get("email")
                    if student_email:
                        mailto_link = f"mailto:{student_email}?subject=Mentorship Follow-up"
                        st.markdown(f"[📧 Email {student.get('name', 'Student')}]({mailto_link})", unsafe_allow_html=True)
        
        else:
            st.info("📭 You haven't accepted any mentees yet.")
            st.markdown("")
            st.markdown("Check the 'Pending Requests' tab to review and accept mentorship requests.")
    
    st.markdown("</div>", unsafe_allow_html=True)
