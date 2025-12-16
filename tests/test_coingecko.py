"""
Test CoinGecko API integration
"""

from api.data_providers.coingecko_provider import CoinGeckoProvider
from services.data_service import DataService


def test_coingecko_single():
    """Test fetching single token price"""
    print("=" * 60)
    print("Testing CoinGecko - Single Token")
    print("=" * 60)

    provider = CoinGeckoProvider()

    test_tokens = ["ETH", "WBTC", "USDC", "LINK", "UNI"]

    for symbol in test_tokens:
        print(f"\n--- {symbol} ---")
        result = provider.get_token_price(symbol)

        if result:
            print(f"[OK] Price: ${result['price_usd']:,.2f}")
            print(f"     Volume 24h: ${result['volume_24h']:,.0f}")
            print(f"     Change 24h: {result['price_change_24h']:.2f}%")
            print(f"     Market Cap: ${result['market_cap']:,.0f}")
        else:
            print("[ERROR] Failed to fetch price")


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


def test_data_service():
    """Test DataService with DEX price simulation"""
    print("\n" + "=" * 60)
    print("Testing DataService - DEX Price Simulation")
    print("=" * 60)

    service = DataService()

    token = "ETH"
    print(f"\nFetching {token} prices from all DEXes...")

    prices = service.get_all_dex_prices(token)

    if prices:
        print(f"\n[OK] Got {len(prices)} DEX prices:")

        for dex_key, data in prices.items():
            print(f"  {dex_key:20s} ${data['price_usd']:,.2f}")

        # Calculate spread
        if len(prices) > 1:
            price_values = [d['price_usd'] for d in prices.values()]
            min_price = min(price_values)
            max_price = max(price_values)
            spread = ((max_price - min_price) / min_price) * 100

            print(f"\n  Best Price:  ${max_price:,.2f}")
            print(f"  Worst Price: ${min_price:,.2f}")
            print(f"  Spread:      {spread:.3f}%")
    else:
        print("[ERROR] No prices returned")


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

        # Test 3: Data service
        test_data_service()

        print("\n" + "=" * 60)
        print("[SUCCESS] All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
