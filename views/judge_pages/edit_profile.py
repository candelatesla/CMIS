"""
Edit Profile Page for Judge/Mentor Dashboard
"""
import streamlit as st
from services.mentor_service import MentorService
from datetime import datetime


def render_judge_edit_profile(mentor):
    """Render the edit profile page for judges/mentors"""
    
    mentor_service = MentorService()
    mentor_id = str(mentor.get("_id"))
    
    # ============ PROFILE EDITING ============
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📝 Edit Your Profile")
    st.markdown("Update your professional information to help students connect with you.")
    
    with st.form("mentor_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", value=mentor.get('name', ''))
            email_display = st.text_input("Email", value=mentor.get('email', ''), disabled=True)
            phone = st.text_input("Phone Number", value=mentor.get('phone', ''))
            company = st.text_input("Company *", value=mentor.get('company', ''))
            job_title = st.text_input("Job Title *", value=mentor.get('job_title', ''))
        
        with col2:
            # Industry dropdown
            industry_list = [
                "Technology", "Finance", "Consulting", "Healthcare",
                "Manufacturing", "Retail", "Energy", "Education",
                "Government", "Non-Profit", "Telecommunications",
                "Real Estate", "Transportation", "Media", "Other"
            ]
            current_industry = mentor.get('industry', 'Technology')
            industry_index = industry_list.index(current_industry) if current_industry in industry_list else 0
            industry = st.selectbox("Industry *", industry_list, index=industry_index)
            
            # Years of experience
            years_exp = st.number_input(
                "Years of Experience",
                min_value=0,
                max_value=50,
                value=int(mentor.get('years_of_experience', 5)),
                step=1
            )
        
        # Expertise areas multi-select
        expertise_list = [
            "Software Development", "Data Science", "AI/ML", "Cybersecurity",
            "Cloud Computing", "DevOps", "Product Management", "Project Management",
            "Business Strategy", "Financial Analysis", "Investment Banking",
            "Consulting", "Supply Chain", "Operations", "Marketing",
            "Sales", "Human Resources", "Legal", "Compliance",
            "Risk Management", "Audit", "Entrepreneurship", "Leadership"
        ]
        current_expertise = mentor.get('expertise_areas', [])
        valid_expertise = [e for e in current_expertise if e in expertise_list]
        expertise_areas = st.multiselect("Expertise Areas *", expertise_list, default=valid_expertise)
        
        # Interests multi-select
        interests_list = [
            "Mentoring Students", "Career Coaching", "Technical Training",
            "Entrepreneurship", "Innovation", "Research", "Teaching",
            "Public Speaking", "Writing", "Community Service",
            "Diversity & Inclusion", "Sustainability", "Case Competitions",
            "Hackathons", "Networking Events"
        ]
        current_interests = mentor.get('interests', [])
        valid_interests = [i for i in current_interests if i in interests_list]
        interests = st.multiselect("Interests *", interests_list, default=valid_interests)
        
        # Resume/Bio text area
        st.markdown("**Professional Bio / Resume**")
        resume_text = st.text_area(
            "Enter your professional background, achievements, and areas of expertise",
            value=mentor.get('resume_text', ''),
            height=200,
            help="This will be shared with students you mentor"
        )
        
        # Form buttons
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
        with col_btn2:
            save_button = st.form_submit_button("💾 Save Profile", use_container_width=True, type="primary")
        
        if save_button:
            # Validation
            if not name or not company or not job_title:
                st.error("❌ Please fill in all required fields (Name, Company, Job Title).")
            elif not expertise_areas or not interests:
                st.error("❌ Please select at least one expertise area and one interest.")
            else:
                # Prepare update data
                updated_data = {
                    "name": name,
                    "phone": phone,
                    "company": company,
                    "job_title": job_title,
                    "industry": industry,
                    "years_of_experience": years_exp,
                    "expertise_areas": expertise_areas,
                    "interests": interests,
                    "resume_text": resume_text,
                    "updated_at": datetime.utcnow()
                }
                
                # Update mentor profile
                result = mentor_service.update_mentor(mentor_id, updated_data)
                
                if "error" in result:
                    st.error(f"❌ Error updating profile: {result['error']}")
                else:
                    st.toast("✅ Profile updated successfully!", icon="✅")
                    import time
                    time.sleep(1)
                    st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("")
    
    # ============ PROFILE SUMMARY ============
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📊 Your Profile Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Company", mentor.get('company', 'N/A'))
    with col2:
        st.metric("Industry", mentor.get('industry', 'N/A'))
    with col3:
        st.metric("Experience", f"{mentor.get('years_of_experience', 0)} years")
    with col4:
        expertise_count = len(mentor.get('expertise_areas', []))
        st.metric("Expertise Areas", expertise_count)
    
    st.markdown("")
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown("**🎯 Expertise Areas**")
        expertise = mentor.get('expertise_areas', [])
        if expertise:
            st.write(", ".join(expertise))
        else:
            st.write("_No expertise areas added yet_")
    
    with col_info2:
        st.markdown("**💡 Interests**")
        interests = mentor.get('interests', [])
        if interests:
            st.write(", ".join(interests))
        else:
            st.write("_No interests added yet_")
    
    st.markdown("</div>", unsafe_allow_html=True)
