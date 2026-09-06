#!/usr/bin/env python3
"""
Gym slot auto-booker.
Runs Mon/Tue/Thu/Fri at 07:00 Morocco time (06:00 UTC) via cron inside Docker.
Books the 18:00 - 19:30 slot exactly 7 days ahead.
"""

import sys
import os
from datetime import date, timedelta
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

ALLOWED_DAYS = [0, 1, 3, 4]          # Mon Tue Thu Fri
BASE_URL     = "https://better-campus.vercel.app/services/1370/8"
TARGET_SLOT  = "18:00 - 19:30"
PROFILE_DIR  = "/app/browser_profile"

# Read from environment variables (set in Railway dashboard)
EMAIL    = os.environ["GYM_EMAIL"]
PASSWORD = os.environ["GYM_PASSWORD"]


def login_if_needed(page) -> None:
    page.goto("https://better-campus.vercel.app/", wait_until="networkidle", timeout=30_000)
    page.wait_for_timeout(2_000)
    if page.locator("input[placeholder*='um6p']").count() == 0:
        print("[ok] Already logged in.")
        return
    print("[info] Logging in...")
    page.fill("input[placeholder*='um6p']", EMAIL)
    page.fill("input[type='password']", PASSWORD)
    page.click("button:has-text('login')")
    page.wait_for_load_state("networkidle", timeout=15_000)
    print("[ok] Logged in.")


def main() -> None:
    today = date.today()
    if today.weekday() not in ALLOWED_DAYS:
        print(f"[skip] Today is {today.strftime('%A')} — not a booking day.")
        sys.exit(0)

    target = today + timedelta(days=14)
    url = f"{BASE_URL}?date={target.isoformat()}"
    print(f"[info] Today: {today.strftime('%A %d %b')} → booking {target.strftime('%A %d %b')} slot {TARGET_SLOT}")

    with sync_playwright() as pw:
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = browser.new_page()

        try:
            login_if_needed(page)

            page.goto(url, wait_until="networkidle", timeout=30_000)
            page.wait_for_timeout(3_000)

            slot = page.get_by_text(TARGET_SLOT, exact=False).first
            slot.wait_for(state="visible", timeout=15_000)
            slot.click()
            print(f"[ok] Clicked '{TARGET_SLOT}' slot.")

            confirm_btn = page.get_by_role("button", name="Confirm").or_(
                          page.get_by_role("button", name="Confirmer"))
            confirm_btn.wait_for(state="visible", timeout=10_000)
            confirm_btn.click()
            print("[ok] Confirmed booking.")

            page.wait_for_timeout(2_000)
            print(f"[done] Booked {TARGET_SLOT} on {target}.")

        except PWTimeout as exc:
            print(f"[error] Timed out: {exc}", file=sys.stderr)
            sys.exit(1)

        finally:
            browser.close()


if __name__ == "__main__":
    main()
