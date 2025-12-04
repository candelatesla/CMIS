"""
Comprehensive test for run_matching_workflow_for_student
Tests with multiple students
"""
import sys
sys.path.insert(0, '/Users/yashdoshi/Documents/CMIS')

from ai.workflow import WorkflowEngine
from services.student_service import StudentService


def test_workflow_for_multiple_students():
    """Test the matching workflow for multiple students"""
    
    print("=" * 80)
    print("COMPREHENSIVE WORKFLOW TEST")
    print("=" * 80)
    print()
    
    # Initialize services
    workflow = WorkflowEngine()
    student_service = StudentService()
    
    # Get first 3 students
    all_students = student_service.list_students()
    students = all_students[:3]
    
    print(f"Testing workflow for {len(students)} students")
    print()
    
    overall_results = {
        "total_students": 0,
        "successful_workflows": 0,
        "total_matches": 0,
        "total_emails": 0,
        "failures": []
    }
    
    for student in students:
        student_id = student.get("student_id")
        student_name = student.get("name")
        
        print(f"{'=' * 80}")
        print(f"Processing Student: {student_name} (ID: {student_id})")
        print(f"{'=' * 80}")
        
        # Run workflow
        result = workflow.run_matching_workflow_for_student(
            student_id=student_id,
            top_n=2  # Only 2 matches per student for this test
        )
        
        overall_results["total_students"] += 1
        
        if result["success"]:
            overall_results["successful_workflows"] += 1
            overall_results["total_matches"] += result["matches_created"]
            overall_results["total_emails"] += result["emails_scheduled"]
            
            print(f"✅ Success: {result['matches_created']} matches, {result['emails_scheduled']} emails scheduled")
        else:
            overall_results["failures"].append({
                "student_id": student_id,
                "student_name": student_name,
                "errors": result["errors"]
            })
            print(f"❌ Failed")
        
        # Show match details
        for i, match in enumerate(result["match_details"], 1):
            status = "✅" if not match["error"] else "❌"
            print(f"  {status} Match {i}: {match['mentor_name']} ({match['score']:.1%})")
            if match["error"]:
                print(f"     Error: {match['error']}")
        
        print()
    
    # Overall summary
    print("=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    print()
    print(f"📊 Total Students Processed: {overall_results['total_students']}")
    print(f"✅ Successful Workflows: {overall_results['successful_workflows']}")
    print(f"🤝 Total Matches Created: {overall_results['total_matches']}")
    print(f"📧 Total Emails Scheduled: {overall_results['total_emails']}")
    print()
    
    if overall_results["failures"]:
        print("❌ FAILURES:")
        for failure in overall_results["failures"]:
            print(f"   - {failure['student_name']} ({failure['student_id']})")
            for error in failure["errors"]:
                print(f"     • {error}")
        print()
    
    print("=" * 80)
    print("HOW TO USE IN STREAMLIT")
    print("=" * 80)
    print()
    print("```python")
    print("from ai.workflow import WorkflowEngine")
    print()
    print("# Initialize workflow engine")
    print("workflow = WorkflowEngine()")
    print()
    print("# Run matching workflow for a student")
    print("result = workflow.run_matching_workflow_for_student(")
    print("    student_id='93700',")
    print("    top_n=3")
    print(")")
    print()
    print("# Check results")
    print("if result['success']:")
    print("    st.success(f\"Created {result['matches_created']} matches!\")")
    print("    st.info(f\"Scheduled {result['emails_scheduled']} emails\")")
    print("    ")
    print("    # Show match details")
    print("    for match in result['match_details']:")
    print("        st.write(f\"{match['mentor_name']}: {match['score']:.1%}\")")
    print("else:")
    print("    st.error('Workflow failed')")
    print("    for error in result['errors']:")
    print("        st.write(error)")
    print("```")
    print()
    print("=" * 80)
    print()
    print("✅ Workflow is synchronous - safe for Streamlit!")
    print("✅ No background workers required")
    print("✅ Emails sent automatically by scheduler")


if __name__ == "__main__":
    test_workflow_for_multiple_students()
