"""
Test CoinGecko API integration
"""

from api.data_providers.coingecko_provider import CoinGeckoProvider
from services.data_service import DataService


def test_coingecko_single():
    """Test fetching single token price (uses bulk method to avoid rate limits)"""
    print("=" * 60)
    print("Testing CoinGecko - Single Token Prices")
    print("=" * 60)

    provider = CoinGeckoProvider()

    test_tokens = ["ETH", "WBTC", "USDC", "LINK", "UNI"]

    print(f"\nFetching {len(test_tokens)} tokens using bulk method...")
    results = provider.get_multiple_prices(test_tokens)

    if results:
        print(f"[OK] Fetched {len(results)} prices\n")
        for symbol in test_tokens:
            if symbol in results:
                data = results[symbol]
                print(f"--- {symbol} ---")
                print(f"  Price: ${data['price_usd']:,.2f}")
                print(f"  Volume 24h: ${data['volume_24h']:,.0f}")
                print(f"  Change 24h: {data['price_change_24h']:.2f}%")
                print(f"  Market Cap: ${data['market_cap']:,.0f}")
            else:
                print(f"--- {symbol} ---")
                print(f"  [ERROR] Failed to fetch price")
    else:
        print("[ERROR] No results returned")


def test_coingecko_bulk():
    """Test fetching multiple tokens at once"""
    print("\n" + "=" * 60)
    print("Testing CoinGecko - Bulk Fetch")
    print("=" * 60)

    provider = CoinGeckoProvider()

    symbols = ["ETH", "WBTC", "USDC", "USDT", "LINK", "UNI", "AAVE", "MKR"]
    print(f"\nFetching {len(symbols)} tokens...")

    results = provider.get_multiple_prices(symbols)

    print(f"\n[OK] Fetched {len(results)} prices")

    for symbol, data in results.items():
        print(f"  {symbol:6s} ${data['price_usd']:>12,.2f}")



def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CoinGecko API Integration Test")
    print("=" * 60)

    try:
        # Test 1: Single token
        test_coingecko_single()

        # Test 2: Bulk fetch
        test_coingecko_bulk()

        print("\n" + "=" * 60)
        print("[SUCCESS] All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
