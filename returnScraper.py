

import asyncio
import re
from playwright.async_api import Playwright, async_playwright, expect

class TrainReturnScrapeTicketBot:
    async def run(self, playwright: Playwright, origin: str,originCode: str, destination: str,destinationCode: str,leavingDate: str, leavingHour: str, leavingMinute: str,arrivalDate: str, arrivalHour: str, arrivalMinute: str) -> None:
    
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.nationalrail.co.uk/plan-a-journey/")
        await page.click("#onetrust-accept-btn-handler")
        await page.get_by_label("Plan a Journey").click()
        
        await page.locator("#jp-origin").click()
        await page.locator("#jp-origin").fill(origin)
        await page.get_by_role("option", name=f"{origin} ({originCode})").locator("b").click()
        await page.locator("#jp-destination").click()
        await page.locator("#jp-destination").fill(destination)
        await page.get_by_role("option", name=f"{destination} ({destinationCode})").locator("b").click()
        await page.get_by_text("Return").click()

        await page.get_by_label("Choose leaving date").click()
        await page.get_by_label("month 2024-06").get_by_label(f"Choose {leavingDate}").click()
        await page.get_by_label("Choose leaving hour").select_option({leavingHour})
        await page.get_by_label("Choose leaving minutes").select_option({leavingMinute})
        await page.get_by_label("Choose return date").click()
        await page.get_by_label(f"Choose {arrivalDate}").click()
        await page.get_by_label("Choose return departure option").select_option("arriving")
        await page.get_by_label("Choose return hour").select_option({arrivalHour})
        await page.get_by_label("Choose return minutes").select_option({arrivalMinute})


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
    bot = TrainReturnScrapeTicketBot()
    async with async_playwright() as playwright:
        await bot.run(playwright, "oxford","OXF", "norwich","NRW", "Saturday, 15 june", "17", "00","Sunday, 30 june", "17", "00")
if __name__ == "__main__":
    asyncio.run(main())

