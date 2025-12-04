"""
Test the run_matching_workflow_for_student function
"""
import sys
sys.path.insert(0, '/Users/yashdoshi/Documents/CMIS')

from ai.workflow import WorkflowEngine


def test_matching_workflow():
    """Test the matching workflow for a single student"""
    
    print("=" * 80)
    print("TESTING: run_matching_workflow_for_student()")
    print("=" * 80)
    print()
    
    # Initialize workflow engine
    workflow = WorkflowEngine()
    
    # Test with Khushi Shah (existing student)
    student_id = "93700"
    top_n = 3
    
    print(f"Running matching workflow for student: {student_id}")
    print(f"Top N mentors: {top_n}")
    print()
    print("Processing...")
    print()
    
    # Run the workflow
    results = workflow.run_matching_workflow_for_student(
        student_id=student_id,
        top_n=top_n
    )
    
    # Display results
    print("=" * 80)
    print("WORKFLOW RESULTS")
    print("=" * 80)
    print()
    
    print(f"✅ Success: {results['success']}")
    print(f"📚 Student ID: {results['student_id']}")
    print(f"👤 Student Name: {results['student_name']}")
    print(f"🤝 Matches Created: {results['matches_created']}")
    print(f"📧 Emails Scheduled: {results['emails_scheduled']}")
    print()
    
    if results['errors']:
        print("⚠️  ERRORS:")
        for error in results['errors']:
            print(f"   - {error}")
        print()
    
    print("📋 MATCH DETAILS:")
    print()
    for i, match in enumerate(results['match_details'], 1):
        print(f"  Match {i}:")
        print(f"    Mentor: {match['mentor_name']}")
        print(f"    Email: {match['mentor_email']}")
        print(f"    Score: {match['score']:.1%}")
        print(f"    Rank: #{match['rank']}")
        print(f"    Match ID: {match['match_id']}")
        print(f"    Email ID: {match['email_id']}")
        if match['error']:
            print(f"    ❌ Error: {match['error']}")
        else:
            print(f"    ✅ Status: Success")
        print()
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    
    if results['success']:
        print("✅ Workflow executed successfully!")
        print(f"   - Created {results['matches_created']} matches")
        print(f"   - Scheduled {results['emails_scheduled']} emails")
        print()
        print("📧 Emails will be sent automatically by the scheduler")
        print("   (APScheduler runs send_due_emails() every 1 minute)")
    else:
        print("❌ Workflow failed")
        print("   Check errors above for details")


if __name__ == "__main__":
    test_matching_workflow()
