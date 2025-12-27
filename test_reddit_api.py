"""Test script to verify Reddit API credentials"""

from src.config import get_settings

def test_reddit_credentials():
    """Test if Reddit API credentials are properly configured"""

    settings = get_settings()

    print("\n" + "="*60)
    print("Reddit API Configuration Test")
    print("="*60 + "\n")

    # Check if credentials are set
    print("1. Checking credentials in .env file...")

    if not settings.REDDIT_CLIENT_ID or settings.REDDIT_CLIENT_ID == "your_reddit_client_id_here":
        print("   ❌ REDDIT_CLIENT_ID is not set")
        print("   → Please add your client ID to the .env file")
        return False
    else:
        print(f"   ✓ REDDIT_CLIENT_ID found: {settings.REDDIT_CLIENT_ID[:10]}...")

    if not settings.REDDIT_CLIENT_SECRET or settings.REDDIT_CLIENT_SECRET == "your_reddit_client_secret_here":
        print("   ❌ REDDIT_CLIENT_SECRET is not set")
        print("   → Please add your client secret to the .env file")
        return False
    else:
        print(f"   ✓ REDDIT_CLIENT_SECRET found: {settings.REDDIT_CLIENT_SECRET[:10]}...")

    print(f"   ✓ REDDIT_USER_AGENT: {settings.REDDIT_USER_AGENT}")

    # Try to authenticate
    print("\n2. Testing authentication with Reddit API...")

    try:
        import praw

        reddit = praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent=settings.REDDIT_USER_AGENT,
            check_for_async=False
        )

        # This will throw an exception if authentication fails
        user = reddit.user.me()

        print("   ✓ Authentication successful!")
        print(f"   ✓ Connected as: Read-only (script app)")

    except Exception as e:
        print(f"   ❌ Authentication failed: {e}")
        print("\n   Common issues:")
        print("   - Client ID or secret is incorrect")
        print("   - App type is not 'script' on Reddit")
        print("   - Network connection issues")
        return False

    # Test basic API call
    print("\n3. Testing API access...")

    try:
        # Try to get a subreddit
        subreddit = reddit.subreddit("wallstreetbets")
        print(f"   ✓ Can access r/wallstreetbets")
        print(f"   ✓ Subscribers: {subreddit.subscribers:,}")

    except Exception as e:
        print(f"   ❌ API call failed: {e}")
        return False

    print("\n" + "="*60)
    print("✓ All tests passed! Reddit API is ready to use.")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    success = test_reddit_credentials()

    if not success:
        print("\nPlease fix the issues above and run this test again.")
        print("Visit https://www.reddit.com/prefs/apps to create or check your app.\n")
        exit(1)
    else:
        print("You can now run the Reddit collector to gather sentiment data.\n")
        exit(0)
