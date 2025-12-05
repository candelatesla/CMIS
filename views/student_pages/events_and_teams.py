"""
Event Registration & Teams Page for Student Dashboard
"""
import streamlit as st
from services.event_service import EventService
from services.team_service import TeamService
from services.email_service import EmailService
from services.student_service import StudentService
from datetime import datetime
import re


def render_events_and_teams(student):
    """Render the event registration and teams page"""
    
    student_id = str(student.get("_id"))
    
    # Get services
    event_service = EventService()
    team_service = TeamService()
    email_service = EmailService()
    student_service = StudentService()
    
    # ============ EVENTS & TEAM REGISTRATION ============
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🏆 Active Events & Team Registration")
    st.markdown("Register your team for upcoming competitions and events.")
    
    # Fetch all events
    all_events = event_service.list_events()
    
    # Filter for active events (either by status or by date)
    from datetime import datetime as dt
    today = dt.now().date()
    
    active_events = []
    for event in all_events:
        # Check if event has explicit status field
        if event.get("status", "").lower() == "active":
            active_events.append(event)
        # Otherwise use date-based filtering
        elif event.get("start_datetime"):
            try:
                # Parse start_datetime (format: "2025-12-05T15:00:00")
                event_date_str = event.get("start_datetime", "")
                if "T" in event_date_str:
                    event_date = dt.fromisoformat(event_date_str).date()
                else:
                    event_date = dt.strptime(event_date_str[:10], "%Y-%m-%d").date()
                
                # Include if event is today or in the future
                if event_date >= today:
                    active_events.append(event)
            except:
                pass
    
    if active_events:
        st.markdown("#### 📅 Select an Event")
        
        # Create event display names
        event_options = {}
        for event in active_events:
            # Format: "Event Name – YYYY-MM-DD"
            date_str = event.get('start_datetime', '')[:10] if event.get('start_datetime') else 'TBD'
            display_name = f"{event.get('name', 'Unnamed Event')} – {date_str}"
            event_options[display_name] = event
        
        selected_event_label = st.selectbox(
            "Choose an event to register for:",
            options=list(event_options.keys()),
            key="event_selector"
        )
        
        selected_event = event_options[selected_event_label]
        
        # Show event details
        with st.expander("📋 Event Details", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Name:** {selected_event.get('name', 'N/A')}")
                st.write(f"**Type:** {selected_event.get('event_type', 'N/A')}")
                st.write(f"**Date:** {selected_event.get('start_datetime', '')[:10] if selected_event.get('start_datetime') else 'TBD'}")
            with col2:
                st.write(f"**Location:** {selected_event.get('location', 'N/A')}")
                st.write(f"**Capacity:** {selected_event.get('capacity', 'N/A')}")
            
            if selected_event.get('description'):
                st.write(f"**Description:** {selected_event.get('description')}")
        
        st.markdown("---")
        st.markdown(f"#### 👥 Register a Team for {selected_event.get('name')}")
        
        with st.form("team_registration_form"):
            team_name = st.text_input("Team Name *", placeholder="e.g., CMIS Champions")
            
            num_members = st.number_input(
                "Number of Team Members *",
                min_value=1,
                max_value=10,
                value=3,
                step=1
            )
            
            st.markdown("**Team Members**")
            st.markdown("_Enter details for each team member:_")
            
            members = []
            
            # Pre-fill first member with current student's info
            col1, col2, col3 = st.columns(3)
            with col1:
                member1_name = st.text_input(
                    f"Member 1 Name *",
                    value=student.get('name', ''),
                    key="member_1_name"
                )
            with col2:
                member1_email = st.text_input(
                    f"Member 1 Email *",
                    value=student.get('email', ''),
                    key="member_1_email"
                )
            with col3:
                member1_phone = st.text_input(
                    f"Member 1 Phone",
                    value=student.get('contact_number', ''),
                    key="member_1_phone"
                )
            
            members.append({
                "name": member1_name,
                "email": member1_email,
                "phone": member1_phone
            })
            
            # Additional members
            for i in range(2, int(num_members) + 1):
                st.markdown(f"**Member {i}**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    name = st.text_input(
                        f"Name *",
                        key=f"member_{i}_name",
                        label_visibility="collapsed"
                    )
                with col2:
                    email_input = st.text_input(
                        f"Email *",
                        key=f"member_{i}_email",
                        label_visibility="collapsed"
                    )
                with col3:
                    phone = st.text_input(
                        f"Phone",
                        key=f"member_{i}_phone",
                        label_visibility="collapsed"
                    )
                
                members.append({
                    "name": name,
                    "email": email_input,
                    "phone": phone
                })
            
            st.markdown("---")
            submit_button = st.form_submit_button("🚀 Register Team", type="primary", use_container_width=True)
            
            if submit_button:
                # Validation
                errors = []
                
                if not team_name or team_name.strip() == "":
                    errors.append("Team name is required")
                
                # Validate members
                valid_members = []
                for idx, member in enumerate(members, 1):
                    if not member["name"] or member["name"].strip() == "":
                        errors.append(f"Member {idx} name is required")
                    elif not member["email"] or member["email"].strip() == "":
                        errors.append(f"Member {idx} email is required")
                    elif not re.match(r"[^@]+@[^@]+\.[^@]+", member["email"]):
                        errors.append(f"Member {idx} email is invalid")
                    else:
                        valid_members.append(member)
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                elif len(valid_members) == 0:
                    st.error("❌ At least one valid team member is required")
                else:
                    # Link members to existing students
                    linked_members = team_service.link_members_to_students(valid_members, student_service)
                    
                    # Create team object
                    event_id_str = str(selected_event.get('_id'))
                    team_data = {
                        "event_id": event_id_str,
                        "event_name": selected_event.get('name'),
                        "team_name": team_name.strip(),
                        "created_by_student_id": student_id,
                        "members": linked_members,
                        "scores": None,
                        "final_score": None
                    }
                    
                    # Insert team
                    result = team_service.create_team(team_data)
                    
                    if "error" in result:
                        st.error(f"❌ Error creating team: {result['error']}")
                    else:
                        st.toast(f"✅ Team '{team_name}' registered successfully!", icon="✅")
                        
                        # Send confirmation emails
                        event_date = selected_event.get('start_datetime', '')[:10] if selected_event.get('start_datetime') else 'TBD'
                        member_names = [m['name'] for m in linked_members]
                        
                        email_success_count = 0
                        for member in linked_members:
                            success = email_service.send_team_registration_email(
                                member_email=member['email'],
                                member_name=member['name'],
                                event_name=selected_event.get('name'),
                                event_date=event_date,
                                team_name=team_name,
                                all_members=member_names
                            )
                            if success:
                                email_success_count += 1
                        
                        if email_success_count == len(linked_members):
                            st.toast(f"📧 Confirmation emails sent to all {email_success_count} team members!", icon="📧")
                        elif email_success_count > 0:
                            st.warning(f"⚠️ Confirmation emails sent to {email_success_count}/{len(linked_members)} members")
                        else:
                            st.warning("⚠️ Team registered but emails could not be sent")
                        
                        import time
                        time.sleep(2)
                        st.rerun()
    
    else:
        st.info("📭 No active events at the moment. Check back later for upcoming competitions!")
    
    st.markdown("</div>", unsafe_allow_html=True)
