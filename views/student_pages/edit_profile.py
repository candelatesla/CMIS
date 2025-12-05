"""
Edit Profile Page for Student Dashboard
"""
import streamlit as st
from services.student_service import StudentService
from utils.pdf_utils import extract_text_from_pdf
from datetime import datetime
import pandas as pd


def render_edit_profile(student):
    """Render the edit profile page with resume versioning"""
    
    student_service = StudentService()
    student_id = str(student.get("_id"))
    
    # ============ PROFILE EDITING ============
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📝 Edit Your Profile")
    st.markdown("Update your information to help mentors find and connect with you.")
    
    with st.form("student_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", value=student.get('name', ''))
            email_display = st.text_input("Email", value=student.get('email', ''), disabled=True)
            contact_number = st.text_input("Contact Number", value=student.get('contact_number', ''))
            uin = st.text_input("Student ID / UIN *", value=student.get('student_id', ''))
            
            # One-line tagline
            tagline = st.text_input(
                "Interest / Tagline",
                value=student.get('tagline', ''),
                help="e.g., 'Interested in AI + product management'",
                placeholder="Brief description of your interests"
            )
            
            # Major dropdown
            major_list = [
                "Computer Science", "Information Systems", "Data Science",
                "Engineering", "Business", "Finance", "Accounting",
                "Management Information Systems", "Statistics", "Mathematics",
                "Cybersecurity", "MIS", "Other"
            ]
            current_major = student.get('major', 'Computer Science')
            major_index = major_list.index(current_major) if current_major in major_list else 0
            major = st.selectbox("Major *", major_list, index=major_index)
        
        with col2:
            # Graduation year
            grad_year_list = [2024, 2025, 2026, 2027, 2028, 2029, 2030]
            current_grad_year = student.get('grad_year', 2025)
            grad_year_index = grad_year_list.index(current_grad_year) if current_grad_year in grad_year_list else 1
            grad_year = st.selectbox("Graduation Year *", grad_year_list, index=grad_year_index)
            
            # GPA
            gpa = st.number_input("GPA", min_value=0.0, max_value=4.0, value=float(student.get('gpa', 3.5)), step=0.01)
        
        # Skills multi-select
        skills_list = [
            "Python", "Java", "C++", "JavaScript", "React", "SQL",
            "Machine Learning", "Data Analysis", "Web Development",
            "Cloud Computing", "Project Management", "Communication",
            "Leadership", "Problem Solving", "Teamwork", "Kali Linux",
            "Wireshark", "Nmap", "Splunk", "Penetration Testing", "R",
            "MATLAB", "Arena", "Tableau", "Six Sigma", "Power BI",
            "SAP", "Salesforce", "Excel", "Data Visualization", "Statistics",
            "Node.js", "MongoDB", "Git", "Docker", "Kubernetes"
        ]
        current_skills = student.get('skills', [])
        valid_skills = [s for s in current_skills if s in skills_list]
        skills = st.multiselect("Skills *", skills_list, default=valid_skills)
        
        # Interests multi-select
        interests_list = [
            "Software Development", "Data Science", "AI/ML", "Cybersecurity",
            "Consulting", "Finance", "Entrepreneurship", "Research",
            "Product Management", "Business Analytics", "Ethical Hacking",
            "Network Security", "Malware Analysis", "Supply Chain Optimization",
            "Process Improvement", "Business Intelligence", "Data Analytics",
            "Enterprise Systems", "Cloud Computing", "Digital Transformation",
            "Project Management", "FinTech", "Marketing"
        ]
        current_interests = student.get('interests', [])
        valid_interests = [i for i in current_interests if i in interests_list]
        interests = st.multiselect("Interests *", interests_list, default=valid_interests)
        
        # Form buttons
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
        with col_btn2:
            save_button = st.form_submit_button("💾 Save Profile", use_container_width=True, type="primary")
        
        if save_button:
            # Validation
            if not name or not uin:
                st.error("❌ Please fill in all required fields (Name and UIN).")
            elif not skills or not interests:
                st.error("❌ Please select at least one skill and one interest.")
            else:
                # Prepare update data
                updated_data = {
                    "name": name,
                    "student_id": uin,
                    "contact_number": contact_number,
                    "tagline": tagline,
                    "major": major,
                    "grad_year": grad_year,
                    "gpa": gpa,
                    "skills": skills,
                    "interests": interests,
                    "updated_at": datetime.utcnow()
                }
                
                # Update student profile
                result = student_service.update_student(student_id, updated_data)
                
                if "error" in result:
                    st.error(f"❌ Error updating profile: {result['error']}")
                else:
                    st.toast("✅ Profile updated successfully!", icon="✅")
                    import time
                    time.sleep(1)
                    st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("")
    
    # ============ RESUME UPLOAD & VERSIONING ============
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📄 Resume Upload & History")
    st.markdown("Upload new resume versions and view your upload history.")
    
    # Resume upload section
    col_upload1, col_upload2 = st.columns([2, 1])
    
    with col_upload1:
        uploaded_new_resume = st.file_uploader(
            "Upload a new resume (PDF)",
            type=["pdf"],
            help="Upload a PDF version of your resume. It will be saved with version tracking.",
            key="new_resume_upload"
        )
    
    if uploaded_new_resume is not None:
        # Process the uploaded resume
        try:
            # Extract text from PDF
            parsed_text = extract_text_from_pdf(uploaded_new_resume)
            
            if parsed_text:
                # Get existing resumes or initialize empty list
                existing_resumes = student.get('resumes', [])
                
                # Determine next version number
                if existing_resumes:
                    existing_versions = [r.get("version", 0) for r in existing_resumes]
                    next_version = max(existing_versions) + 1
                else:
                    next_version = 1
                
                # Create new resume entry
                new_resume = {
                    "version": next_version,
                    "filename": uploaded_new_resume.name,
                    "uploaded_at": datetime.utcnow(),
                    "parsed_text": parsed_text
                }
                
                # Append to resumes list
                existing_resumes.append(new_resume)
                
                # Update student with new resume
                update_result = student_service.update_student(
                    student_id,
                    {
                        "resumes": existing_resumes,
                        "resume_text": parsed_text,
                        "updated_at": datetime.utcnow()
                    }
                )
                
                if "error" not in update_result:
                    st.toast(f"✅ Resume uploaded successfully! (Version {next_version})", icon="✅")
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Error saving resume: {update_result['error']}")
            else:
                st.warning("⚠️ Could not extract text from PDF. Please try a different file.")
        
        except Exception as e:
            st.error(f"❌ Error processing resume: {str(e)}")
    
    st.markdown("---")
    
    # Resume version history
    resumes = student.get('resumes', [])
    
    if resumes:
        st.markdown("#### 📋 Resume Version History")
        
        # Sort by version (most recent first)
        sorted_resumes = sorted(resumes, key=lambda r: r.get('version', 0), reverse=True)
        
        # Create DataFrame for display
        history_data = []
        for resume in sorted_resumes:
            version = resume.get('version', 'N/A')
            filename = resume.get('filename', 'N/A')
            uploaded_at = resume.get('uploaded_at')
            parsed_text = resume.get('parsed_text', '')
            
            # Format date
            if uploaded_at:
                if isinstance(uploaded_at, datetime):
                    date_str = uploaded_at.strftime("%Y-%m-%d %H:%M")
                else:
                    date_str = str(uploaded_at)
            else:
                date_str = 'N/A'
            
            # Preview text (first 150 chars)
            preview = parsed_text[:150] + "..." if len(parsed_text) > 150 else parsed_text
            
            history_data.append({
                "Version": f"v{version}",
                "Filename": filename,
                "Uploaded": date_str,
                "Preview": preview
            })
        
        # Display as table
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Show latest resume in expandable section
        latest_resume = sorted_resumes[0]
        with st.expander(f"📖 View Latest Resume (Version {latest_resume.get('version')})"):
            st.text_area(
                "Resume Text",
                value=latest_resume.get('parsed_text', ''),
                height=400,
                disabled=True,
                label_visibility="collapsed"
            )
    else:
        st.info("📭 No resumes uploaded yet. Upload your first resume above!")
    
    st.markdown("</div>", unsafe_allow_html=True)
