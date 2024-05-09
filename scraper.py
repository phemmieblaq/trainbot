

import asyncio
import re
from playwright.async_api import Playwright, async_playwright, expect


async def run(playwright: Playwright) -> None:
    user_responses = {
    'singlejourney': {'service': None,'fromCity': None, 'toCity': None, 'fullDate': None, 'time': None},
    'returnJourney': {'fromCity': None, 'toCity': None, 'fullDate': None, 'time': None}
} 
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://www.nationalrail.co.uk/plan-a-journey/")
    await page.click("#onetrust-accept-btn-handler")
    await page.get_by_label("Plan a Journey").click()
    
    await page.locator("#jp-origin").click()

    #change this value to the origin value 
    await page.locator("#jp-origin").fill("oxford")
    #change this value to the origin value and the code 
    await page.get_by_role("option", name="oxford (OXF)").locator("b").click()

    await page.locator("#jp-destination").click()

     #change this value to the destination value
    await page.locator("#jp-destination").fill("norwich")
     #change this value to the destination value and the code 
    await page.get_by_role("option", name="norwich (NRW)").locator("b").click()


    
    await page.get_by_label("Choose leaving date").click()
    await page.get_by_label("Choose friday, 10 may").click()
    await page.get_by_label("Choose leaving hour").select_option("17")
    await page.get_by_label("Choose leaving minutes").select_option("00")

    if user_responses['returnJourney']['fromCity'] is not None:
        await page.get_by_text("Return").click()
        await page.get_by_label("Choose return date").click()
        await page.get_by_label("Choose Sunday, 12 May").click()
        await page.get_by_label("Choose return departure option").select_option("arriving")
        await page.get_by_label("Choose return hour").select_option("05")
        await page.get_by_label("Choose return minutes").select_option("30")
    

    


    


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
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())
