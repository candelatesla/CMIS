#!/usr/bin/env python3
"""
Test script for team registration
Tests creating a team and sending confirmation emails via n8n webhook
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.event_service import EventService
from services.student_service import StudentService
from services.team_service import TeamService
from services.email_service import EmailService
from datetime import datetime


def main():
    """Test team registration and email sending"""
    
    print("=" * 60)
    print("CMIS Team Registration Test Script")
    print("=" * 60)
    
    # Initialize services
    event_service = EventService()
    student_service = StudentService()
    team_service = TeamService()
    email_service = EmailService()
    
    # Step 1: Find CMIS Case Competition event
    print("\n[Step 1] Finding CMIS Case Competition event...")
    all_events = event_service.list_events()
    
    print(f"Found {len(all_events)} total events in database")
    
    cmis_event = None
    for event in all_events:
        event_name = event.get('name', '').lower()
        print(f"  Checking: {event.get('name')}")
        
        # Look for CMIS Case Competition
        if ("cmis" in event_name and "case" in event_name) or ("cmis" in event_name and "competition" in event_name):
            cmis_event = event
            break
    
    if not cmis_event:
        print("❌ CMIS Case Competition event not found")
        print("\nAvailable events:")
        for event in all_events:
            print(f"  - {event.get('name')} (Type: {event.get('event_type', 'N/A')})")
        
        # Use first available event as fallback
        if all_events:
            cmis_event = all_events[0]
            print(f"\n⚠️  Using fallback event: {cmis_event.get('name')}")
        else:
            print("❌ No events found in database. Please create an event first.")
            return
    
    print(f"✅ Found event: {cmis_event.get('name')}")
    print(f"   Event ID: {cmis_event.get('_id')}")
    print(f"   Date: {cmis_event.get('start_datetime', 'N/A')}")
    
    # Step 2: Find test students
    print("\n[Step 2] Finding test students...")
    all_students = student_service.list_students()
    
    test_emails = [
        "yash.doshi@tamu.edu",
        "khushi.shah@tamu.edu",
        "ujjawal.patel@tamu.edu"
    ]
    
    found_students = {}
    for email in test_emails:
        student = None
        for s in all_students:
            if s.get('email', '').lower() == email.lower():
                student = s
                break
        
        if student:
            found_students[email] = student
            print(f"✅ Found student: {student.get('name')} ({email})")
        else:
            print(f"⚠️  Student not found: {email} - will use generic info")
            # Create generic member info
            name = email.split('@')[0].replace('.', ' ').title()
            found_students[email] = {
                'name': name,
                'email': email,
                'student_id': None
            }
    
    # Step 3: Create team members list
    print("\n[Step 3] Preparing team members...")
    members = []
    
    for email, student_data in found_students.items():
        member = {
            "name": student_data.get('name', email.split('@')[0]),
            "email": email,
            "phone": "123-456-7890"
        }
        members.append(member)
        print(f"  • {member['name']} - {member['email']}")
    
    # Step 4: Link members to students
    print("\n[Step 4] Linking members to existing student records...")
    linked_members = team_service.link_members_to_students(members, student_service)
    
    for member in linked_members:
        linked_id = member.get('linked_student_id')
        if linked_id:
            print(f"  ✅ {member['name']}: Linked to student ID {linked_id}")
        else:
            print(f"  ⚠️  {member['name']}: No matching student record")
    
    # Step 5: Create team
    print("\n[Step 5] Creating team...")
    team_name = "Test CMIS Demo Team"
    
    # Use first student as creator (or None if no students found)
    creator_student_id = None
    for student_data in found_students.values():
        if student_data.get('student_id'):
            creator_student_id = student_data.get('student_id')
            break
    
    if not creator_student_id:
        print("⚠️  No student ID found, using placeholder")
        creator_student_id = "TEST_STUDENT_ID"
    
    team_data = {
        "event_id": str(cmis_event.get('_id')),
        "event_name": cmis_event.get('name'),
        "team_name": team_name,
        "created_by_student_id": creator_student_id,
        "members": linked_members,
        "scores": None,
        "final_score": None
    }
    
    result = team_service.create_team(team_data)
    
    if "error" in result:
        print(f"❌ Error creating team: {result['error']}")
        return
    
    print(f"✅ Team created successfully!")
    print(f"   Team ID: {result.get('_id')}")
    print(f"   Team Name: {result.get('team_name')}")
    print(f"   Event: {result.get('event_name')}")
    print(f"   Members: {len(result.get('members', []))}")
    
    # Step 6: Send confirmation emails
    print("\n[Step 6] Sending confirmation emails via n8n webhook...")
    
    event_date = cmis_event.get('start_datetime', '')[:10] if cmis_event.get('start_datetime') else 'TBD'
    member_names = [m['name'] for m in linked_members]
    
    email_results = []
    for member in linked_members:
        print(f"\n  Sending email to {member['email']}...")
        
        success = email_service.send_team_registration_email(
            member_email=member['email'],
            member_name=member['name'],
            event_name=cmis_event.get('name'),
            event_date=event_date,
            team_name=team_name,
            all_members=member_names
        )
        
        email_results.append({
            'email': member['email'],
            'name': member['name'],
            'success': success
        })
    
    # Step 7: Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    print(f"\n✅ Team Created:")
    print(f"   ID: {result.get('_id')}")
    print(f"   Name: {team_name}")
    print(f"   Event: {cmis_event.get('name')}")
    print(f"   Members: {len(linked_members)}")
    
    print(f"\n📧 Email Status:")
    success_count = sum(1 for r in email_results if r['success'])
    print(f"   Sent: {success_count}/{len(email_results)}")
    
    for result in email_results:
        status = "✅ Sent" if result['success'] else "❌ Failed"
        print(f"   {status}: {result['name']} ({result['email']})")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    
    if success_count == len(email_results):
        print("\n🎉 All emails sent successfully! Check the inboxes.")
    elif success_count > 0:
        print(f"\n⚠️  Partial success: {success_count}/{len(email_results)} emails sent")
    else:
        print("\n❌ No emails were sent. Check n8n webhook configuration.")


if __name__ == "__main__":
    main()
