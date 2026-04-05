# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.19.10",
#     "playwright>=1.50.0",
#     "playwright-stealth>=2.0.0",  # <--- Update this to get the new class-based API
#     "pyzmq>=27.1.0",
# ]
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    **Note:**

    - To create a new marimo notebook in Codespaces / VS Code, use the command palette (`Ctrl + Shift + P` or `Cmd + Shift + P`) and select `Create: New marimo notebook`.
        - This will open a new marimo notebook where you can start writing and executing your code.
    - To execute a code cell in a marimo notebook, a kernel must have been selected first.
        - Select a kernel by clicking on the `Select Kernel` button in the top right corner of the marimo notebook and choose `marimo sandbox` from the dropdown list.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    # **Accepting & Storing Website Cookies**

    - This notebook visits a target website using a **headless browser** (a browser that runs invisibly in the background, without opening a window on your screen),
    - handles any **cookie consent banners** that appear (the pop-ups asking you to accept or reject cookies), and
    - saves the resulting **cookies and local storage** to files so that later scripts can reuse them — making the browser session look like that of a returning, consenting user.
    - It also collects and saves the **raw list of URLs** found on the page, as well as a **filtered list** containing only URLs related to topics of interest (e.g., sustainability, ESG).
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Notebook Flow — Outline Pseudocode**

    _Read this section first to understand the overall logic of the notebook before diving into the code._


    - STEP 1 — SET UP
        - Define settings: website to visit, topics to filter URLs by
        - Load required tools (libraries)

    - STEP 2 — PREPARE HELPER FUNCTIONS
        - `check_banner()`         → check whether the cookie consent banner is visible on the page
        - `click_accept_cookies()` → find and click the "Accept All" button in the banner

    - STEP 3 — MAIN FUNCTION: `acceptNstoreCookies()`
        - Launch a headless browser (Playwright / Chromium)
        - CONTEXT 1 — bare context (no evasion):
            - Open a page with no user agent or JS patches → gets blocked by the website
            - Take screenshot → `screenshot_BotDetected.png` &emsp; (confirms the block is real)
            - Close context 1
        - CONTEXT 2 — evasion context:
            - Set a realistic user agent string
            - Use some tricks to hide automation flags as though the browser was used by a human
            - Open a fresh page → website now loads correctly
            - Take screenshot → `screenshot_CookiesPopup.png` &emsp; (cookie banner visible)
            - Click the "Accept All" button on the cookie banner
            - Take screenshot → `screenshot_CookiesAccepted.png` &emsp; (banner gone)
            - Extract all URLs from the page → save to `urls_raw.csv`
            - Filter URLs by topic keywords &emsp; → save to `urls_filtered.csv`
            - Save browser cookies &emsp; &emsp; &emsp; &emsp; → `cookies.json`
            - Save browser local storage &emsp; &emsp; → `localStorage.json`
            - Close browser

    - STEP 4 — RUN
        - Call `acceptNstoreCookies()` using `await` (async execution)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### What does `async`/`await` mean?

    - Normally, Python runs your code **one line at a time**, waiting for each line to finish before moving on. This works fine for most tasks — but browsing the web involves a lot of **waiting** (for pages to load, for buttons to appear, for the server to respond). If Python just sat still during that waiting time, the whole notebook would freeze.

    - **`async`** and **`await`** are Python's way of handling this gracefully:
      - When you define a function with **`async def`**, you are telling Python: *"This function may need to pause and wait at certain points."*
      - When you write **`await`** before a call, you are saying: *"Start this task, and while it is waiting, feel free to do other things — but come back here when it is done."*

    - Think of it like placing a coffee order at a café. Instead of standing frozen at the counter until your coffee is ready, you step aside and do something else — and return when your name is called. **`await`** is the "step aside and come back" instruction.

    - In practice, you do not need to understand every detail of `async`/`await` to use this notebook. The key thing to remember is: **if a function is defined with `async def`, you must call it with `await`** — otherwise Python will not actually run it.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **User-configurable Parameters**

    _**Note:**_

    - Think of this cell as the **control panel** of the notebook — it is the only place you need to edit to aim the script at a different website or topic.
    - `topLevelURL` is the website you want to visit. The script will load this page, accept its cookie banner, and collect links from it.
    - `topics` are the words the script uses to filter URLs. A URL is kept in the filtered list only if it contains at least one of these words.
        - For example, a URL like `.../sustainability/reports/` would be kept because it contains the word `sustainability`.
    """)
    return


@app.cell
def _(os):
    # The website to visit
    #topLevelURL = 'https://group.mercedes-benz.com'
    topLevelURL = 'https://www.siemens.com/global/en/company/'

    # Keywords used to filter URLs found on the page
    topics = [
        'sustainability', 'ESG', 'environment', 'water', 'social',
        'governance', 'corporate responsibility', 'transparency'
    ]

    # Create the directory if it does not exist
    os.makedirs('public/crawl', exist_ok=True)  # In marimo, you can use os before it is imported in the next code cell
    return topLevelURL, topics


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Imports**

    _**Note:**_

    - This cell loads the **external tools (libraries)** that the rest of the notebook depends on.
    - Here is a plain-English summary of what each one does:
        - **`marimo`** — the notebook framework itself.
        - **`playwright`** — controls a real web browser from Python, so the script can visit pages just like a human would. We use the **async** version, which lets the browser run without freezing the notebook.
        - **`asyncio`** — Python's built-in tool for running code **asynchronously** (i.e., doing multiple things at once without waiting). Required for async Playwright.
        - **`re`** — short for *regular expressions*; lets us search text for patterns, such as finding a keyword inside a URL.
        - **`csv`, `json`** — for writing results to comma-separated and JSON data files.
        - **`time`** — for measuring how long operations take.
    """)
    return


@app.cell
def _():
    # Load necessary libraries

    import marimo as mo
    from playwright.async_api import async_playwright
    import asyncio
    import os
    import re
    import csv
    import json
    import time

    return async_playwright, asyncio, csv, json, mo, os, re, time


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Helper Function: `check_banner()`**

    ### Check whether the **cookie consent banner** is visible

    _**Note:**_

    - Many websites use a **shadow DOM** to embed their cookie banner. The shadow DOM is a hidden, self-contained section of the page's HTML that is isolated from the main page — like a secret compartment inside the webpage.
    - Standard tools that search the page's HTML (like `document.querySelector`) cannot see inside the shadow DOM without special access.
    - This function first uses `document.querySelector('#usercentrics-root')` to find the container that holds the banner, then uses `.shadowRoot` to peek inside it, and finally searches for a button whose text contains "Accept All".
    - If that button is found, the function returns `True` (banner is present); otherwise it returns `False`.
    - **In plain English:** *"Is the cookie pop-up currently visible on this page?"*
    """)
    return


@app.cell
def _():
    # JavaScript code (as a Python string) that will be executed inside the browser
    # to check whether the cookie consent banner is currently visible.
    #
    # Note: The banner lives inside a "shadow DOM" — a hidden, self-contained section
    # of the page's HTML that standard selectors cannot reach directly.
    # We access it via `.shadowRoot` and then search for the "Accept All" button.

    script_check_banner = """
    () => {
        const shadowRoot = document.querySelector('#usercentrics-root')?.shadowRoot;
        if (shadowRoot) {
            const shadowButtons = Array.from(shadowRoot.querySelectorAll('button'));
            const shadowAcceptButton = shadowButtons.find(button =>
                button.textContent.includes('Accept All') ||
                button.textContent.includes('Accept all') ||
                button.innerText.includes('Accept All') ||
                button.innerText.includes('Accept all')
            );
            return shadowAcceptButton ? true : false;
        }
        return false;
    }
    """
    return (script_check_banner,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Helper Function: `click_accept_cookies()`**

    ### Find and **click** the "Accept All" cookie button

    _**Note:**_

    - This function does the actual work of dismissing the cookie banner.
    - It runs a small piece of code inside the browser that:
        1. Searches the **main page** for any button labelled "Accept All" or "Accept all" and clicks it.
        2. Searches inside the **shadow DOM** (the hidden compartment) for the same button and clicks it too.
        - Both searches are done because different websites place the button in different locations.
    - After clicking, the function waits a moment and then checks whether the banner has disappeared using `check_banner()`.
    - It returns `True` if the banner is gone (success) and `False` if something went wrong.
    - **In plain English:** *"Click the 'Accept All' button, then confirm the cookie pop-up has closed."*
    """)
    return


@app.cell
def _(asyncio, script_check_banner):
    async def click_accept_cookies(page):
        try:
            # First take note if cookie banner exists
            initial_banner_present = await page.evaluate(script_check_banner)
            print(f"Cookie banner present: {initial_banner_present}")

            # JavaScript that searches for and clicks the Accept All button —
            # both in the main page and inside the shadow DOM.
            script_click = """
            () => {
                let result = '';

                // Search the main page for an Accept All button
                const buttons = Array.from(document.querySelectorAll('button'));
                const acceptButton = buttons.find(button =>
                    button.textContent.includes('Accept All') ||
                    button.textContent.includes('Accept all') ||
                    button.innerText.includes('Accept All') ||
                    button.innerText.includes('Accept all')
                );
                if (acceptButton) {
                    acceptButton.click();
                    result += '  acceptButton clicked ';
                }

                // Search inside the shadow DOM for the same button
                const shadowRoot = document.querySelector('#usercentrics-root')?.shadowRoot;
                if (shadowRoot) {
                    const shadowButtons = Array.from(shadowRoot.querySelectorAll('button'));
                    const shadowAcceptButton = shadowButtons.find(button =>
                        button.textContent.includes('Accept All') ||
                        button.textContent.includes('Accept all') ||
                        button.innerText.includes('Accept All') ||
                        button.innerText.includes('Accept all')
                    );
                    if (shadowAcceptButton) {
                        shadowAcceptButton.click();
                        result += '  shadowAcceptButton clicked ';
                    }
                }

                return result || 'no button clicked';
            }
            """

            # Execute the click script inside the browser
            click_result = await page.evaluate(script_click)
            print(f"Click result: {click_result}")

            if 'clicked' not in click_result:
                print("Could not find cookie accept button")
                return False

            # Wait briefly — the page needs a moment to react to the click
            await asyncio.sleep(1)

            # Confirm the banner is gone
            banner_still_present = await page.evaluate(script_check_banner)
            if not banner_still_present:
                print("Verified: Cookie banner is gone")
                return True
            else:
                print("Warning: Cookie banner still present after click")
                return False

        except Exception as e:
            print(f"Error in click_accept_cookies: {str(e)}")
            return False

    return (click_accept_cookies,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Main Function: `acceptNstoreCookies()`**

    ### The **core workflow** — visit the site, accept cookies, save everything

    _**Note:**_

    - This is the main function that orchestrates all the steps.
    - It is defined as `async def` because it uses `await` — a Python keyword that pauses execution while waiting for the browser to finish a task (like loading a page), then resumes. This is called **asynchronous programming** and prevents the notebook from freezing while waiting.
    - Key steps inside this function:

    **1. Bot-detection evasion** — Websites often try to detect and block automated browsers. We counter this with two techniques:
      - Setting a realistic **User Agent** string (the label a browser sends to identify itself — we pretend to be a normal Chrome browser on Windows).
      - Hiding the **`navigator.webdriver`** flag, a property that is automatically set to `true` in automated browsers. We set it to `undefined` so the site cannot tell the difference.

    **2. Screenshots** — The function takes screenshots at two moments:
      - *Before* accepting cookies → `screenshot_CookiesPopup.png`
      - *After* accepting cookies → `screenshot_CookiesAccepted.png`
      - These are useful for **debugging**: you can open the image files to verify that the cookie banner appeared and was dismissed correctly.

    **3. URL collection and filtering** — After the banner is dismissed, the function extracts all links (`<a href="...">`) from the page, saves the full list to `urls_raw.csv`, and saves a filtered subset (only URLs containing a topic keyword) to `urls_filtered.csv`.

    **4. Saving session data** — Finally, it saves the browser's **cookies** and **local storage** to `cookies.json` and `localStorage.json`. These files allow later scripts (like the crawler) to inherit this session and bypass the cookie banner automatically.
    """)
    return


@app.cell
def _(
    async_playwright,
    asyncio,
    click_accept_cookies,
    csv,
    json,
    re,
    time,
    topLevelURL,
    topics,
):
    async def acceptNstoreCookies(): 
        async with async_playwright() as p:

            # ----------------------------------------------------------------
            # LAUNCH CONFIGURATION (CRITICAL FOR EVASION)
            # 1. headless=False: We disable Playwright's default headless flag.
            # 2. --headless=new: We pass the Chrome argument for "New Headless",
            #    which is much harder to detect than the old standard.
            # ----------------------------------------------------------------
            browser = await p.chromium.launch(
                headless=False,  # <--- Set to False so we can control it via args
                args=[
                    '--headless=new', # <--- The modern way to run headless
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--window-position=0,0',
                ]
            )

            # ================================================================
            # CONTEXT 1 — Bare (Expected Block)
            # ================================================================
            context_bare = await browser.new_context()
            page_bare = await context_bare.new_page()
            try:
                await page_bare.goto(topLevelURL, wait_until='domcontentloaded', timeout=15000)
            except:
                pass
            await page_bare.screenshot(path='img/screenshot_BotDetected.png', full_page=True)
            print("\nScreenshot saved: screenshot_BotDetected.png")
            await context_bare.close()

            # ================================================================
            # CONTEXT 2: Evasion (Manual Patching)
            # ================================================================
            context_evasion = await browser.new_context(
                # Chrome 133 on Windows 10
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='Europe/Berlin',
                device_scale_factor=1,
            )

            # ----------------------------------------------------------------
            # MANUAL EVASION SCRIPT
            # This runs on every page load before any other JS.
            # ----------------------------------------------------------------
            await context_evasion.add_init_script("""
                // 1. Hide the Automation flag (navigator.webdriver)
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // 2. Fix Platform Mismatch (Codespaces is Linux, UA is Windows)
                // If we don't do this, the site sees "Linux x86_64" vs "Windows" in UA -> BLOCK.
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32'
                });

                // 3. Mock Plugins (Headless has 0, Real Chrome has some)
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });

                // 4. Ensure window.chrome exists
                window.chrome = { runtime: {} };
            """)

            page = await context_evasion.new_page()

            try:
                print(f"Navigating to {topLevelURL}...")
                start_time = time.time()

                # Use domcontentloaded, then wait for content
                await page.goto(topLevelURL, wait_until='domcontentloaded', timeout=60000)

                # Wait longer for the specific cookie container to appear
                # This ensures we don't screenshot a blank loading screen
                try:
                    await page.wait_for_selector('body', timeout=10000)
                    # Try waiting for the shadow root container if possible, but don't crash
                    await asyncio.sleep(5) 
                except:
                    print("Warning: Body selector timeout, page might be blocked.")

                load_time = time.time() - start_time
                print(f"Time taken to fully load page: {load_time:.2f} seconds")

                await page.screenshot(path='img/screenshot_CookiesPopup.png', full_page=True)
                print("\nScreenshot saved: screenshot_CookiesPopup.png")

                # Accept cookies
                await click_accept_cookies(page)
                await asyncio.sleep(3)

                await page.screenshot(path='img/screenshot_CookiesAccepted.png', full_page=True)
                print("\nScreenshot saved: screenshot_CookiesAccepted.png")

                # Extract URLs
                urls = await page.evaluate(
                    "() => Array.from(document.querySelectorAll('a')).map(a => a.href)"
                )

                # Filter URLs
                filtered_urls = [
                    url for url in urls
                    if any(re.search(keyword.replace('_', '[_-]'), url, re.IGNORECASE) for keyword in topics)
                ]


                # Save Data
                with open('public/crawl/urls_raw.csv', 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['URL'])
                    writer.writerows([[url] for url in urls])
                print(f"Saved {len(urls)} raw URLs")

                with open('public/urls_filtered.csv', 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['URL'])
                    writer.writerows([[url] for url in filtered_urls])
                print(f"Saved {len(filtered_urls)} filtered URLs")

            except Exception as error:
                print(f"Error during page interaction: {error}")

            finally:
                cookies = await context_evasion.cookies()
                with open('cookies.json', 'w', encoding='utf-8') as f:
                    json.dump(cookies, f, indent=2)

                try:
                    local_storage = await page.evaluate("() => JSON.stringify(localStorage)")
                    with open('localStorage.json', 'w', encoding='utf-8') as f:
                        f.write(local_storage)
                except:
                    pass

                await browser.close()
                print("Browser closed.")

    return (acceptNstoreCookies,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Run the Script**

    _**Note:**_

    - This cell **calls** (executes) the `acceptNstoreCookies()` function defined above.
    - Because the function is `async`, we cannot call it with a plain `acceptNstoreCookies()`.
      Instead, we use `await` — which tells Python: *"start this task and wait for it to finish before moving on"*.
    - In a marimo notebook, `await` works directly inside a cell — there is no need to wrap it in `asyncio.run()`.
    - After running this cell, check the file panel for the output files:
        - `screenshot_BotDetected.png` — the page as seen by a bare browser with no evasion (blocked = expected)
        - `screenshot_CookiesPopup.png` — the page as seen by the evasion browser before accepting cookies
        - `screenshot_CookiesAccepted.png` — the page after the cookie banner was dismissed
        - `urls_raw.csv` — every link found on the page
        - `urls_filtered.csv` — only the links related to your chosen topics
        - `cookies.json` — the browser session cookies (used by the next notebook)
        - `localStorage.json` — the browser local storage (used by the next notebook)
    """)
    return


@app.cell
async def _(acceptNstoreCookies):
    # Run the main function.
    # `await` is used here because acceptNstoreCookies() is an async function.
    # Marimo notebooks support `await` directly in cells — no asyncio.run() needed.
    await acceptNstoreCookies()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ---
    """)
    return


if __name__ == "__main__":
    app.run()
