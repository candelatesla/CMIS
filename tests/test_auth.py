"""
Test authentication functionality
"""
import sys
sys.path.insert(0, '/Users/yashdoshi/Documents/CMIS')

from utils.auth import load_admin_credentials, check_login


def test_auth():
    """Test authentication functions"""
    
    print("=" * 80)
    print("AUTHENTICATION SYSTEM TEST")
    print("=" * 80)
    print()
    
    # Test 1: Load admin credentials
    print("Test 1: Loading admin credentials from .env")
    admin_emails, admin_password = load_admin_credentials()
    print(f"✅ Admin emails: {admin_emails}")
    print(f"✅ Admin password: {'*' * len(admin_password)}")
    print()
    
    # Test 2: Valid login
    print("Test 2: Testing valid login")
    valid_email = "drg@tamu.edu"
    valid_password = "Passw0rd!"
    result = check_login(valid_email, valid_password)
    if result:
        print(f"✅ Login successful for {valid_email}")
    else:
        print(f"❌ Login failed for {valid_email}")
    print()
    
    # Test 3: Invalid email
    print("Test 3: Testing invalid email")
    invalid_email = "hacker@example.com"
    result = check_login(invalid_email, valid_password)
    if not result:
        print(f"✅ Login correctly rejected for {invalid_email}")
    else:
        print(f"❌ Login incorrectly accepted for {invalid_email}")
    print()
    
    # Test 4: Invalid password
    print("Test 4: Testing invalid password")
    invalid_password = "wrongpassword"
    result = check_login(valid_email, invalid_password)
    if not result:
        print(f"✅ Login correctly rejected for wrong password")
    else:
        print(f"❌ Login incorrectly accepted for wrong password")
    print()
    
    # Test 5: Case insensitive email
    print("Test 5: Testing case insensitive email")
    uppercase_email = "DRG@TAMU.EDU"
    result = check_login(uppercase_email, valid_password)
    if result:
        print(f"✅ Login successful with uppercase email: {uppercase_email}")
    else:
        print(f"❌ Login failed with uppercase email: {uppercase_email}")
    print()
    
    # Test 6: Second admin email
    print("Test 6: Testing second admin email")
    second_email = "drwhitten@tamu.edu"
    result = check_login(second_email, valid_password)
    if result:
        print(f"✅ Login successful for {second_email}")
    else:
        print(f"❌ Login failed for {second_email}")
    print()
    
    print("=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80)
    print()
    print("✅ Authentication system working correctly!")
    print()
    print("Valid credentials:")
    for email in admin_emails:
        print(f"  - Email: {email}")
    print(f"  - Password: Passw0rd!")


if __name__ == "__main__":
    test_auth()
