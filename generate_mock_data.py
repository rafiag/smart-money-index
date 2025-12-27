"""Script to generate mock Reddit data only for testing"""

from src.database import init_db
from src.utils.mock_data_generator import MockDataGenerator

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Smart Money Divergence Index - Mock Reddit Data Generator")
    print("=" * 70)
    print("\nThis will generate mock Reddit data for all 12 tickers:")
    print("  - Reddit sentiment and mentions")
    print("\nDate range: 2024-01-01 to present")
    print("\nNote: For other data sources, use collect_data.py")
    print("=" * 70 + "\n")

    # Ensure database is initialized
    print("Initializing database...")
    init_db()
    print("[OK] Database ready\n")

    # Generate mock Reddit data only
    generator = MockDataGenerator()
    generator.generate_reddit_only()

    print("\n" + "=" * 70)
    print("[SUCCESS] Mock Reddit data generation complete!")
    print("=" * 70)
    print("\nNext Steps:")
    print("  1. Run: python collect_data.py (to collect real data for other sources)")
    print("  2. Run: streamlit run src/dashboard/app.py")
    print("  3. Open browser to: http://localhost:8501")
    print("\nNote: Reddit data is MOCK for testing purposes")
    print("      Use collect_data.py for real data from other sources")
    print("=" * 70 + "\n")
