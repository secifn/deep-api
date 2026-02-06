#!/usr/bin/env python3
"""
สคริปต์สำหรับทดสอบการเชื่อมต่อกับ Deep Instinct API และ Mattermost Webhook
"""

import os
import sys
import requests
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv('.env1')

def test_deep_instinct():
    """ทดสอบการเชื่อมต่อกับ Deep Instinct API"""
    print("=" * 60)
    print("Testing Deep Instinct API Connection")
    print("=" * 60)
    
    di_url = os.getenv('DEEPINSTINCT_URL')
    di_token = os.getenv('TOKENS_KEY')
    
    if not di_url or not di_token:
        print("❌ Error: Missing Deep Instinct credentials")
        print("   Please check DEEPINSTINCT_URL and TOKENS_KEY in .env1")
        return False
    
    print(f"URL: {di_url}")
    print(f"Token: {di_token[:20]}...")
    print()
    
    # ทดสอบดึง events
    try:
        url = f"{di_url.rstrip('/')}/events/"
        headers = {
            'Authorization': di_token,  # Deep Instinct doesn't use "Bearer " prefix
            'Content-Type': 'application/json'
        }
        
        print("📡 Sending request to /events/...")
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Success! Retrieved {len(events) if isinstance(events, list) else 0} events")
            
            if events and isinstance(events, list) and len(events) > 0:
                print(f"\nSample Event (first event):")
                print("-" * 60)
                sample = events[0]
                for key, value in list(sample.items())[:10]:  # แสดง 10 fields แรก
                    print(f"  {key}: {value}")
                if len(sample) > 10:
                    print(f"  ... และอีก {len(sample) - 10} fields")
            
            return True
        elif response.status_code == 401:
            print("❌ Unauthorized: Token may be invalid or expired")
            return False
        else:
            print(f"⚠️  Warning: Unexpected status code")
            print(f"Response: {response.text[:200]}")
            return False
    
    except requests.exceptions.Timeout:
        print("❌ Error: Request timeout - Server took too long to respond")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Error: Connection failed - Cannot reach server")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_mattermost():
    """ทดสอบการเชื่อมต่อกับ Mattermost Webhook"""
    print("\n" + "=" * 60)
    print("Testing Mattermost Webhook Connection")
    print("=" * 60)
    
    mm_webhook = os.getenv('MATTERMOST_WEBHOOK_URL')
    
    if not mm_webhook:
        print("❌ Error: Missing MATTERMOST_WEBHOOK_URL")
        print("   Please add MATTERMOST_WEBHOOK_URL to .env1")
        return False
    
    if 'your-mattermost-server.com' in mm_webhook or 'xxx-your-hook-id-xxx' in mm_webhook:
        print("⚠️  Warning: MATTERMOST_WEBHOOK_URL appears to be a placeholder")
        print("   Please update with your actual Mattermost webhook URL")
        print(f"\n   Current URL: {mm_webhook}")
        return False
    
    print(f"Webhook URL: {mm_webhook[:50]}...")
    print()
    
    try:
        payload = {
            'text': '✅ **Test Message from Deep Instinct Integration**\n\nThis is a test message to verify the webhook is working correctly.'
        }
        
        print("📡 Sending test message...")
        response = requests.post(
            mm_webhook,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success! Test message sent to Mattermost")
            print("   Check your Mattermost channel for the test message")
            return True
        else:
            print(f"❌ Failed to send message")
            print(f"Response: {response.text[:200]}")
            return False
    
    except requests.exceptions.Timeout:
        print("❌ Error: Request timeout")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Error: Connection failed")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║         Connection Test - Deep Instinct & Mattermost        ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    # ทดสอบ Deep Instinct
    di_success = test_deep_instinct()
    
    # ทดสอบ Mattermost
    mm_success = test_mattermost()
    
    # สรุปผล
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Deep Instinct API: {'✅ PASS' if di_success else '❌ FAIL'}")
    print(f"Mattermost Webhook: {'✅ PASS' if mm_success else '❌ FAIL'}")
    print()
    
    if di_success and mm_success:
        print("🎉 All tests passed! You're ready to run the integration.")
        print("\nNext step:")
        print("  python deepinstinct_to_mattermost.py")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix the issues above before running the integration.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
