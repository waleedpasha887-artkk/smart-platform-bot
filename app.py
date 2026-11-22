from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright
from urllib.parse import urlparse

app = FastAPI(title="QUREO Smart Bot")

START_URL = "https://sprixportal.jp/"

@app.get("/")
def home():
    return {
        "status": "running",
        "bot": "QUREO Smart Bot",
        "message": "البوت جاهز لفحص بوابة SPRIX"
    }

@app.get("/inspect")
async def inspect_portal():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox"]
            )

            page = await browser.new_page()
            await page.goto(
                START_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            await page.wait_for_timeout(3000)

            title = await page.title()
            text = await page.locator("body").inner_text()

            links = await page.locator("a").evaluate_all("""
                elements => elements.map(a => ({
                    text: (a.innerText || "").trim(),
                    url: a.href
                })).filter(a => a.url)
            """)

            await browser.close()

            return {
                "status": "success",
                "title": title,
                "page_text": text[:10000],
                "links": links[:100]
            }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
