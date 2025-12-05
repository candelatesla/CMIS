"""
Test the refined email scheduling logic
"""
import sys
sys.path.insert(0, '/Users/yashdoshi/Documents/CMIS')

from datetime import datetime, timezone, time, timedelta
from utils.time_utils import get_human_like_schedule_time


def test_scheduling_logic():
    """Test the refined scheduling logic for different times of day"""
    
    print("=" * 80)
    print("REFINED EMAIL SCHEDULING LOGIC TEST")
    print("=" * 80)
    print()
    
    # Test current time
    now = datetime.now(timezone.utc)
    current_hour = now.hour
    current_time_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    print(f"Current Time: {current_time_str}")
    print(f"Current Hour (UTC): {current_hour}")
    print()
    
    # Determine which rule applies
    if current_hour < 8:
        rule = "Rule 1: Before 8 AM → Schedule between 8-10 AM today"
    elif 8 <= current_hour < 17:
        rule = "Rule 2: 8 AM - 5 PM → Schedule after 10-25 minutes"
    else:
        rule = "Rule 3: After 5 PM → Schedule next day between 8-10 AM"
    
    print(f"Active Rule: {rule}")
    print()
    
    # Test 10 times to see the randomization
    print("Testing 10 scheduled times (to verify randomization):")
    print("-" * 80)
    
    for i in range(10):
        scheduled_time = get_human_like_schedule_time()
        
        # Calculate delay
        delay = scheduled_time - now
        delay_minutes = delay.total_seconds() / 60
        
        # Format scheduled time
        scheduled_str = scheduled_time.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Check if next day
        is_next_day = scheduled_time.date() > now.date()
        next_day_marker = " (NEXT DAY)" if is_next_day else ""
        
        print(f"{i+1:2}. {scheduled_str}{next_day_marker}")
        print(f"    Delay: {delay_minutes:.1f} minutes ({delay_minutes/60:.2f} hours)")
    
    print()
    print("=" * 80)
    print("VALIDATION CHECKS")
    print("=" * 80)
    print()
    
    # Run validation
    test_scheduled = get_human_like_schedule_time()
    test_hour = test_scheduled.hour
    test_minute = test_scheduled.minute
    test_second = test_scheduled.second
    
    if current_hour < 8:
        # Should be between 8-10 AM today
        if 8 <= test_hour < 10:
            print("✅ PASS: Scheduled between 8-10 AM")
        else:
            print(f"❌ FAIL: Expected 8-10 AM, got {test_hour}:{test_minute:02d}")
        
        if test_scheduled.date() == now.date():
            print("✅ PASS: Scheduled for today (not next day)")
        else:
            print("❌ FAIL: Should be today, not next day")
    
    elif 8 <= current_hour < 17:
        # Should be after 10-25 minutes
        delay = (test_scheduled - now).total_seconds() / 60
        if 10 <= delay <= 25:
            print(f"✅ PASS: Scheduled after {delay:.1f} minutes (within 10-25 range)")
        else:
            print(f"❌ FAIL: Expected 10-25 minutes, got {delay:.1f} minutes")
        
        # Should not be next day unless time rolls over past midnight
        if test_scheduled.date() == now.date() or (test_scheduled.date() == (now + timedelta(days=1)).date() and test_hour < 1):
            print("✅ PASS: Scheduled for today (or just past midnight)")
        else:
            print("❌ FAIL: Scheduled for wrong day")
    
    else:  # After 5 PM
        # Should be next day between 8-10 AM
        if test_scheduled.date() == (now + timedelta(days=1)).date():
            print("✅ PASS: Scheduled for next day")
        else:
            print("❌ FAIL: Should be next day")
        
        if 8 <= test_hour < 10:
            print("✅ PASS: Scheduled between 8-10 AM")
        else:
            print(f"❌ FAIL: Expected 8-10 AM, got {test_hour}:{test_minute:02d}")
    
    # Check for human-like randomization (seconds should vary)
    print()
    print("Checking randomization of seconds:")
    seconds_set = set()
    for _ in range(5):
        t = get_human_like_schedule_time()
        seconds_set.add(t.second)
    
    if len(seconds_set) > 1:
        print(f"✅ PASS: Seconds vary ({len(seconds_set)} different values: {sorted(seconds_set)})")
    else:
        print(f"⚠️  WARNING: Seconds not varying much (only {len(seconds_set)} unique value)")
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_scheduling_logic()
