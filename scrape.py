

import asyncio
import re
from playwright.async_api import Playwright, async_playwright, expect

class TrainScrapeTicketBot:
    async def run(self, playwright: Playwright) -> None:
    
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.nationalrail.co.uk/plan-a-journey/")
        await page.click("#onetrust-accept-btn-handler")
        await page.get_by_label("Plan a Journey").click()
        
        await page.locator("#jp-origin").click()
        await page.locator("#jp-origin").fill("oxford")
        await page.get_by_role("option", name="oxford (OXF)").locator("b").click()
        await page.locator("#jp-destination").click()
        await page.locator("#jp-destination").fill("norwich")
        await page.get_by_role("option", name="norwich (NRW)").locator("b").click()
        
        await page.get_by_label("Choose leaving date").click()
        await page.get_by_label("Choose Saturday, 18 may").click()
        await page.get_by_label("Choose leaving hour").select_option("17")
        await page.get_by_label("Choose leaving minutes").select_option("00")
        await page.click("#button-jp")
        # value = await page.locator('#jp-class-jp-results-standard').input_value()
        # print(value)   
        price = await page.locator('#jp-class-jp-results-standard').get_attribute('aria-label')
        print(price) 
        current_url = page.url
        print(current_url)
        # ---------------------
        await context.close()
        await browser.close()


async def main() -> None:
    bot = TrainScrapeTicketBot()
    async with async_playwright() as playwright:
        await bot.run(playwright)

asyncio.run(main())


