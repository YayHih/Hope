"""Test Playwright to see Food Bank NYC page structure."""
import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            print("Loading Food Bank NYC page...")
            await page.goto("https://www.foodbanknyc.org/find-food/", wait_until='domcontentloaded', timeout=30000)

            # Wait a bit for JavaScript
            await asyncio.sleep(3)

            # Look for iframe
            iframes = await page.query_selector_all('iframe')
            print(f"\nFound {len(iframes)} iframes")

            for i, iframe in enumerate(iframes):
                src = await iframe.get_attribute('src')
                print(f"  iframe {i+1}: {src}")

            # Look for map elements
            map_divs = await page.query_selector_all('[id*="map"], [class*="map"]')
            print(f"\nFound {len(map_divs)} map-related elements")

            # Get page title
            title = await page.title()
            print(f"\nPage title: {title}")

            # Take screenshot
            await page.screenshot(path='/tmp/foodbank_test.png')
            print(f"\nScreenshot saved to /tmp/foodbank_test.png")

            await browser.close()
            print("\n✓ Playwright test complete!")

        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
