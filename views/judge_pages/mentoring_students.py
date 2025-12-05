"""
Mentoring Students Page for Judge/Mentor Dashboard
"""
import streamlit as st
from services.mentoring_service import MentoringService
from services.student_service import StudentService


def render_mentoring_students(mentor):
    """Render the mentoring students page showing assigned students"""
    
    mentor_id = str(mentor.get("_id"))
    
    # Get services
    mentoring_service = MentoringService()
    student_service = StudentService()
    
    # ============ STUDENTS YOU MENTOR ============
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🎓 Students You Mentor")
    st.markdown("View profiles of students matched with you for mentorship.")
    
    # Fetch pending and accepted students from mentoring service (DB-only, instant visibility)
    pending_requests = mentoring_service.get_pending_requests_for_mentor(mentor_id)
    accepted_students = mentoring_service.get_students_mentored_by(mentor_id)
    
    # Combine for unified display
    all_students = []
    
    # Add pending with status
    for request in pending_requests:
        student = request.get("student", {})
        student["mentorship_status"] = "pending"
        student["match_reason"] = request.get("match_reason", "")
        all_students.append(student)
    
    # Add accepted with status
    for student in accepted_students:
        student["mentorship_status"] = "accepted"
        all_students.append(student)
    
    if all_students:
        total_count = len(all_students)
        pending_count = len(pending_requests)
        accepted_count = len(accepted_students)
        
        st.markdown(f"**You have {total_count} student(s): {accepted_count} accepted, {pending_count} pending approval**")
        st.markdown("")
        
        for idx, student in enumerate(all_students):
            mentorship_status = student.get('mentorship_status', 'unknown')
            match_reason = student.get('match_reason', '')
            
            # Student card
            st.markdown("<div class='card' style='background-color: #f8f9fa; padding: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
            
            # Status badge
            if mentorship_status == 'accepted':
                st.markdown("<div style='background-color: #d4edda; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>", unsafe_allow_html=True)
                st.markdown("### ✅ Accepted Mentee")
                st.markdown("</div>", unsafe_allow_html=True)
            elif mentorship_status == 'pending':
                st.markdown("<div style='background-color: #fff3cd; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>", unsafe_allow_html=True)
                st.markdown("### ⏳ Pending Approval")
                st.caption("Visit 'Mentor Requests' page to accept or decline this mentorship")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning(f"Status: {mentorship_status}")
            
            st.markdown(f"### 🎓 {student.get('name', 'Unknown Student')}")
            st.markdown("")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Student Information**")
                st.write(f"**Email:** {student.get('email', 'N/A')}")
                st.write(f"**Major:** {student.get('major', 'N/A')}")
                st.write(f"**Graduation Year:** {student.get('grad_year', 'N/A')}")
                st.write(f"**GPA:** {student.get('gpa', 'N/A')}")
                
                if student.get('contact_number'):
                    st.write(f"**Phone:** {student.get('contact_number')}")
                
                if student.get('tagline'):
                    st.write(f"**Tagline:** _{student.get('tagline')}_")
            
            with col2:
                st.markdown("**Skills & Interests**")
                
                skills = student.get('skills', [])
                if skills:
                    st.markdown("**Skills:**")
                    st.write(", ".join(skills[:5]))  # Show first 5
                    if len(skills) > 5:
                        st.caption(f"+ {len(skills) - 5} more")
                else:
                    st.write("**Skills:** _Not specified_")
                
                st.markdown("")
                
                interests = student.get('interests', [])
                if interests:
                    st.markdown("**Interests:**")
                    st.write(", ".join(interests[:5]))  # Show first 5
                    if len(interests) > 5:
                        st.caption(f"+ {len(interests) - 5} more")
                else:
                    st.write("**Interests:** _Not specified_")
            
            st.markdown("---")
            
            # Match reason
            if match_reason:
                with st.expander("💡 Why you were matched"):
                    st.markdown(match_reason)
            
            # Student resume
            resume_text = student.get('resume_text', '')
            if resume_text:
                with st.expander("📄 Student Resume"):
                    st.text_area(
                        "Resume Text",
                        value=resume_text,
                        height=300,
                        disabled=True,
                        key=f"student_resume_{idx}",
                        label_visibility="collapsed"
                    )
            
            # Contact button
            st.markdown("---")
            col_contact1, col_contact2, col_contact3 = st.columns([1, 2, 1])
            with col_contact2:
                student_email = student.get('email', '')
                if student_email:
                    st.markdown(f"📧 **[Email {student.get('name', 'Student')}](mailto:{student_email})**")
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("")
        
        st.markdown("---")
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Students", total_count)
        with col2:
            st.metric("Accepted", accepted_count)
        with col3:
            st.metric("Pending Approval", pending_count)
    
    else:
        st.info("🔍 No students are currently matched with you for mentorship.")
        st.markdown("")
        st.markdown("**What this means:**")
        st.write("• The matching algorithm hasn't assigned any students to you yet")
        st.write("• Check back later as new matches are created")
        st.write("• Contact your program administrator if you have questions")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Future features
    st.markdown("")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🚀 Coming Soon")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📅 Schedule Meetings**")
        st.caption("Book one-on-one sessions with students")
        st.caption("🚧 Feature in development")
    
    with col2:
        st.markdown("**📊 Track Progress**")
        st.caption("Monitor student development and goals")
        st.caption("🚧 Feature in development")
    
    st.markdown("</div>", unsafe_allow_html=True)
