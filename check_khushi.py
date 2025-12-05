#!/usr/bin/env python3
"""Quick check for Khushi's account"""
from services.auth_service import AuthService
from services.student_service import StudentService

auth = AuthService()
student_service = StudentService()

print("=== Checking k@tamu.edu ===")
students = student_service.list_students()
khushi_records = [s for s in students if s.get('email') == 'k@tamu.edu']
print(f"Found {len(khushi_records)} student record(s)")
if khushi_records:
    print(f"Name: {khushi_records[0].get('name')}")
    print(f"Student ID: {khushi_records[0].get('student_id')}")
    print(f"Email: {khushi_records[0].get('email')}")

print("\n=== Checking auth_users ===")
user = auth.get_user_by_email('k@tamu.edu')
if user:
    print(f"Auth entry exists:")
    print(f"  Role: {user.get('role')}")
    print(f"  Linked ID: {user.get('linked_student_id')}")
else:
    print("No auth entry - will be auto-onboarded on first login")

print("\n=== SOLUTION ===")
print("Login credentials for Khushi Shah:")
print("  Email: k@tamu.edu")
print("  Password: Passw0rd!")
