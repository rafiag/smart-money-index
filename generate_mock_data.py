"""Script to generate and populate database with mock data for testing"""

from src.database import init_db
from src.utils.mock_data_generator import MockDataGenerator

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Smart Money Divergence Index - Mock Data Generator")
    print("=" * 70)
    print("\nThis will generate realistic mock data for all 12 tickers:")
    print("  - Price data (OHLCV)")
    print("  - Institutional holdings (13F)")
    print("  - Form 4 insider transactions")
    print("  - Google Trends search volume")
    print("  - Reddit sentiment and mentions")
    print("\nDate range: 2024-01-01 to present")
    print("=" * 70 + "\n")

    # Ensure database is initialized
    print("Initializing database...")
    init_db()
    print("[OK] Database ready\n")

    # Generate mock data
    generator = MockDataGenerator()
    generator.generate_all_mock_data()

    print("\n" + "=" * 70)
    print("[SUCCESS] Mock data generation complete!")
    print("=" * 70)
    print("\nNext Steps:")
    print("  1. Run: streamlit run src/dashboard/app.py")
    print("  2. Open browser to: http://localhost:8501")
    print("  3. Start building and testing the dashboard!")
    print("\nNote: This is mock data for development only")
    print("   Real data collection will begin once APIs are configured")
    print("=" * 70 + "\n")
