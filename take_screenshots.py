"""
Take screenshots of all app pages using Playwright.
Run: python take_screenshots.py
"""
import asyncio
import os
from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:8000"
OUT  = os.path.join(os.path.dirname(__file__), "docs", "screenshots")
os.makedirs(OUT, exist_ok=True)

PAGES = [
    ("02_dashboard",        "/"),
    ("03_chatbot",          "/chatbot/"),
    ("04_image_chat",       "/image-chat/"),
    ("05_document_chat",    "/document-chat/"),
    ("06_website_analyzer", "/website-analyzer/"),
    ("07_image_generator",  "/image-generator/"),
    ("08_resume_analyzer",  "/resume-analysis/"),
    ("09_email_manager",    "/email-manager/"),
    ("10_content_writer",   "/content-writer/"),
    ("11_compare_images",   "/compare-images/"),
    ("12_pricing_plans",    "/pricing/"),
    ("13_history",          "/history/"),
    ("14_settings",         "/settings/"),
]

async def login(page):
    await page.goto(f"{BASE}/accounts/login/")
    await page.wait_for_load_state("networkidle")
    # Fill whichever label the form uses
    await page.fill("input[name='username']", "ntsh.vicky")
    await page.fill("input[name='password']", "screenshot123")
    await page.locator("button[type='submit'], input[type='submit']").first.click()
    await page.wait_for_load_state("networkidle")
    print(f"  Logged in, URL: {page.url}")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 860},
            locale="en-US",
        )
        page = await ctx.new_page()

        # ── Login page screenshot (unauthenticated) ─────────────────────
        await page.goto(f"{BASE}/accounts/login/")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(OUT, "01_login.png"), full_page=False)
        print("✓ 01_login")

        # ── Log in ──────────────────────────────────────────────────────
        await login(page)

        # ── Screenshot each authenticated page ──────────────────────────
        for name, path_url in PAGES:
            try:
                print(f"  → {name}  {path_url}")
                await page.goto(f"{BASE}{path_url}", wait_until="networkidle", timeout=20000)
                # If redirected to login, re-auth and retry
                if "login" in page.url:
                    print("    (session lost, re-logging in)")
                    await login(page)
                    await page.goto(f"{BASE}{path_url}", wait_until="networkidle", timeout=20000)
                await page.wait_for_timeout(1500)
                await page.screenshot(path=os.path.join(OUT, f"{name}.png"), full_page=False)
                print(f"  ✓ {name}")
            except Exception as e:
                print(f"  ✗ {name}: {e}")

        await browser.close()
        print(f"\nAll screenshots saved to: {OUT}")

asyncio.run(run())
