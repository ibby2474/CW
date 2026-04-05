# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.19.10",
#     "pandas>=2.3.3",
#     "playwright>=1.50.0",
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

    - To create a new marimo notebook in Codespaces / VS Code, use the command palette (`Ctrl + Shift + P` or `Cmd + Shift + P`) and select `Create: New marimo notebook`".
        - This will open a new marimo notebook where you can start writing and executing your code.
    - To execute a code cell in a marimo notebook, a kernel must have been selected first.
        - Select a kernel by clicking on the `Select Kernel` button in the top right corner of the marimo notebook and choose `marimo sandbox` from the dropdown list.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    # **Collecting URLs from a Website**

    - This notebook
        - crawls a website starting from a set of **seed URLs** (filtered from a CSV file),
        - follows links up to a configurable **depth**, and
        - collects all URLs matching specified **keywords** (e.g., sustainability, ESG).
    - The results are saved to CSV files for downstream processing.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Notebook Flow — Outline Pseudocode**

    _Read this section first to understand the overall logic of the notebook before diving into the code._


    - STEP 1 — SET UP
        - Define settings: website to crawl, keywords to look for, how deep to follow links
        - Load required tools (libraries)
        - Record the start time; set a maximum run time (timeout)

    - STEP 2 — PREPARE HELPER TOOLS (functions)
        - `commonDomain()`      → check if a URL belongs to the same website
        - `is_excluded()`       → decide whether to skip a URL (wrong site, or non-HTML file)
        - `filter_urls()`       → remove duplicate/redundant URLs from a list
        - `save_urls_to_csv()`  → write a list of URLs to a CSV file
        - `make_timeout_handler()` → set up an emergency stop if the crawl takes too long
        - `clean_url_segment()` → tidy up a piece of a URL so keywords can be matched
        - `matches_keywords()`  → check if any keyword appears in a URL
        - `get_filename()`      → pull out the filename from the end of a URL
        - `preprocess_href()`   → fix messy link text found on web pages
        - `get_all_urls()`      → visit a page and collect all links on it
        - `collect_urls()`      → the main recursive crawler:
            - &emsp; &emsp; &emsp; &emsp; visit a page → collect links → follow relevant links
            - &emsp; &emsp; &emsp; &emsp; &emsp; → repeat up to the allowed depth

    - STEP 3 — LOAD INPUTS
        - Read candidate URLs from a CSV file
        - Keep only URLs that match a topic keyword → these become "seed URLs"
        - Save seed URLs to `seedURLs.csv`
        - Load saved browser cookies and local storage (so the crawler looks like a real user)

    - STEP 4 — CRAWL THE WEBSITE
        - Start a safety timer (timeout)
        - Launch a headless browser (Playwright / Chromium)
        - For each seed URL:
            - Visit the page
            - Collect all links on that page
            - For each link that matches a keyword and is not excluded:
                - Visit that link and repeat (up to the allowed depth)
        - Close the browser; cancel the timer

    - STEP 5 — SAVE RESULTS
        - Post-process collected URLs → add Filename and Extension columns
        - Save all URLs           → `allURLs.csv` / `allURLs_df.csv`
        - Save PDF links only     → `pdfURLs.csv`
        - Save PDFs matching topics → `pdfscreenedURLs.csv`
        - Save pages actually visited → `visitedURLs.csv`
        - Print total run time
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **User-configurable Parameters**

    _**Note:**_

    - Think of this cell as the **control panel** of the notebook — it is the only place you need to edit to aim the crawler at a different website or topic.
    - `topLevelURL` is the website you want to crawl. The crawler will only collect links that belong to this website.
    - `keywords` are the words the crawler looks for inside a URL. A page is only followed if its address contains at least one of these words.
    - `depth` controls how many "hops" away from the seed URLs the crawler will travel.
        - `depth = 1` means: visit the seed pages only.
        - `depth = 2` means: also follow links found on those seed pages — and so on.
        - Larger values find more pages but take longer to run.
    - `excluded_extensions` lists file types (e.g. `.pdf`, `.zip`) that the crawler should **not** try to open as web pages — they are not HTML and cannot be navigated.
    """)
    return


@app.cell
def _(os):
    depth = 2   # Maximum depth of URLs to collect from the topLevelURL
    #topLevelURL = 'https://group.mercedes-benz.com'
    topLevelURL = 'https://www.siemens.com/global/en/company/'

    # Target URL used to verify that the crawler visits it correctly (for debugging)
    #targetURL = 'https://group.mercedes-benz.com/sustainability/sustainability-reports-archive.html'
    targetURL = 'https://www.siemens.com/en-us/company/insights/fuerth-sustainability-lighthouse/'

    #-----------------------------------------------

    # File with URLs to explore from the topLevelURL
    file_name = "public/urls_filtered.csv"
    #file_name = "public/urls_filtered_Backup.csv"
    col_name = 'URL'  # Column name for URLs in the CSV file

    # Keywords to search for in a URL
    topics = ['sustainability', 'ESG', 'environment', 'water', 'social', 'governance', 'corporate responsibility', 'transparency']
    collections = ['report', 'document', 'archive']
    keywords = topics + collections

    # List of file extensions to exclude
    # Note: These are not HTML pages the crawler can navigate
    excluded_extensions = [
        '.pdf', '.ics', '.doc', '.docx', '.xls', '.xlsx',
        '.ppt', '.pptx', '.zip', '.rar', '.7z', '.tar', '.gz',
        '.mp3', '.mp4', '.avi', '.mkv', '.mov', '.exe', '.dmg'
    ]

    # Create the directory if it does not exist
    os.makedirs('public/crawl', exist_ok=True)  # In marimo, you can use os before it is imported in the next code cell
    return (
        col_name,
        depth,
        excluded_extensions,
        file_name,
        keywords,
        targetURL,
        topLevelURL,
        topics,
    )


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Imports**

    _**Note:**_

    - This cell loads the **external tools (libraries)** that the rest of the notebook depends on.
    - You do not need to understand every library in detail — here is a plain-English summary of what each one does:
        - **`marimo`** — the notebook framework itself.
        - **`pandas`** — lets us work with tables of data (like a spreadsheet) in Python.
        - **`playwright`** — controls a real web browser from Python, so the crawler can visit pages just like a human would.
        - **`signal`** — lets the script set a timer and stop itself automatically if it runs too long.
        - **`urljoin` / `urlparse`** — small utilities for building and taking apart web addresses (URLs).
        - **`csv`, `json`** — for reading and writing data files.
        - **`time`, `os`, `re`, `shutil`** — general-purpose Python utilities for timing, file paths, text patterns, and terminal output.
    """)
    return


@app.cell
def _():
    # Load necessary libraries

    import marimo as mo
    import pandas as pd
    from playwright.async_api import async_playwright
    import signal
    from urllib.parse import urljoin, urlparse
    import shutil

    import csv
    import json
    import time
    import re
    import os

    return (
        async_playwright,
        csv,
        json,
        mo,
        os,
        pd,
        re,
        shutil,
        signal,
        time,
        urljoin,
        urlparse,
    )


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Environment Setup**

    _**Note:**_

    - This cell does three small but important things before crawling begins:
        1. **Finds the working folder** — `os.getenv('PWD')` asks the operating system where the notebook is running, so we can build the correct file path to the input CSV.
        2. **Sets a time limit** — `timeout_duration` is the maximum number of seconds the crawler is allowed to run. This prevents the script from running forever on very large websites.
        3. **Starts a stopwatch** — `start_time` records the current time so we can calculate how long the whole process took at the end.
    """)
    return


@app.cell
def _(os, time):
    # Get the working directory based on environment variable PWD
    pwd_dir = os.getenv('PWD')
    print(f"Working directory: {pwd_dir}")

    # Set the timeout duration (in seconds)
    timeout_duration = 240  # 480 # 360 # 30 # 60
    #timeout_duration = float('inf')  # Set to infinity to disable timeout

    # Start the timer
    start_time = time.time()
    return pwd_dir, start_time, timeout_duration


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Helper Function: `commonDomain()`**

    ### Check whether a URL belongs to the **same website**

    _**Note:**_

    - A URL like `https://careers.mercedes-benz.com/jobs` and the benchmark `https://group.mercedes-benz.com` look different at first glance, but both belong to the same website (`mercedes-benz.com`).
    - `commonDomain()` answers the question: *"Does this URL belong to the same website as our target?"*
    - It does this by comparing only the last two parts of the domain name (e.g., `mercedes-benz` and `com`), so sub-sites like `careers.mercedes-benz.com` are correctly recognised as belonging to the same organisation.
    - If the URL shares the same top-level domain, the function returns `True` (keep it); otherwise it returns `False` (skip it).
    """)
    return


@app.cell
def _(urlparse):
    def commonDomain(url, benchmarkURL):
        # Verify it starts with benchmarkURL
        if not url.startswith(benchmarkURL):
            # Extract netlocs (network location, i.e., domain names)
            url_netloc = urlparse(url).netloc
            benchmark_netloc = urlparse(benchmarkURL).netloc

            # Split netlocs into components (e.g., ['group', 'mercedes-benz', 'com'])
            url_parts = url_netloc.split('.')
            benchmark_parts = benchmark_netloc.split('.')

            # Compare the highest two-level domains (e.g., ['mercedes-benz', 'com'])
            if url_parts[-2:] == benchmark_parts[-2:] and len(url_parts) >= 2:
                return True
            return False
        return True

    return (commonDomain,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Helper Function: `is_excluded()`**

    ### Decide whether a URL should be **skipped**

    _**Note:**_

    - Not every link found on a page is worth following. This function acts as a **gatekeeper** that returns `True` when a URL should be skipped, and `False` when it should be kept.
    - A URL is skipped for either of two reasons:
        1. It points to a **downloadable file** (e.g. a PDF or ZIP) rather than a web page — such files cannot be navigated like HTML pages.
        2. It belongs to a **different website** — we only want to stay within the target organisation's domain.
    - If anything goes wrong while checking (e.g. a malformed URL), the function plays it safe and skips the URL.
    """)
    return


@app.cell
def _(commonDomain, excluded_extensions, topLevelURL):
    def is_excluded(url):
        """
        Enhanced URL filtering with multiple checks.
        Returns True if URL should be excluded, False if it should be kept.
        """
        try:
            # Check for None or empty URLs
            if not url:
                return True

            # Basic extension check
            if any(url.lower().endswith(ext) for ext in excluded_extensions):
                return True

            # Check if it does not share the highest two-level domain with topLevelURL
            if not commonDomain(url, topLevelURL):
                return True

            # Additional safety checks can be added here

            return False
        except Exception as e:
            print(f"Error in is_excluded for URL {url}: {str(e)}")
            return True

    return (is_excluded,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Helper Function: `filter_urls()`**

    ### Remove **redundant** URLs from a list

    _**Note:**_

    - After collecting many URLs, some may be **sub-pages of others**. For example, `/sustainability/reports/2023` is a more specific page nested inside `/sustainability/`. If we already plan to visit `/sustainability/`, visiting the deeper sub-path separately is redundant.
    - `filter_urls()` keeps only the **shortest (highest-level) URL** from each such group, so the crawler does not waste time on duplicate paths.
    - The function also removes any URLs flagged by `is_excluded()` and returns a **set** (a collection with no duplicates) of clean seed URLs.
    """)
    return


@app.cell
def _(is_excluded):
    def filter_urls(urls):
        # Step 1: Sort URLs so higher-level (shorter) URLs come first
        urls = sorted(urls)

        # Step 2: Retain only non-lower-level URLs
        result = []
        for url in urls:
            if not is_excluded(url) and not any(
                url.startswith(retained_url) and url != retained_url
                for retained_url in result
            ):
                result.append(url)

        return set(result)  # return only unique URLs

    return (filter_urls,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Helper Function: `save_urls_to_csv()`**

    ### Write a list of URLs to a **CSV file**

    _**Note:**_

    - This is a simple but important utility: it takes any collection of URLs and saves them to a file so results are not lost when the notebook stops running.
    - URLs are **sorted alphabetically** before writing, making the output easier to read and compare across runs.
    - The CSV file always starts with a header row (`URL`) so it can be opened directly as a table in pandas or Excel.
    """)
    return


@app.cell
def _(csv):
    def save_urls_to_csv(filename, urls):
        with open(filename, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['URL'])  # Write the header
            for url in sorted(urls):
                writer.writerow([url])

    return (save_urls_to_csv,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Helper Function: `timeout_handler()`**

    ### Stop the crawler **gracefully** if it runs too long

    _**Note:**_

    - Web crawling can take a very long time on large websites. This function acts as an **emergency stop**: if the crawler is still running after `timeout_duration` seconds, the operating system sends a signal that triggers `timeout_handler()`.
    - When triggered, the handler **saves whatever URLs have been collected so far** to CSV files, prints the elapsed time, and then exits — so no work is lost.
    - The function is wrapped inside a "factory" function (`make_timeout_handler`) simply because of a technical requirement of the marimo notebook: it needs to be able to access the latest values of `all_urls` and `visited_urls` at the moment the timeout fires.
    """)
    return


@app.cell
def _(save_urls_to_csv, start_time, time):
    # Safer alternative using a mutable dict (avoids nonlocal scope issues)
    crawl_status = {'timed_out': False}

    def make_timeout_handler(get_all_urls_ref, get_visited_urls_ref):
        def timeout_handler(signum, frame):

            crawl_status['timed_out'] = True               # ← mutate dict (no nonlocal needed)
            print("\n\n⚠️  TIMEOUT reached — crawl stopped before full exploration was complete.")
            print(f"   Visited {len(get_visited_urls_ref())} pages so far.")

            #print("Timeout reached, saving collected URLs to CSV.")
            save_urls_to_csv('public/crawl/allURLs.csv', get_all_urls_ref())
            save_urls_to_csv('public/crawl/visitedURLs.csv', get_visited_urls_ref())

            end_time = time.time()
            total_processing_time = end_time - start_time
            print(f"Total processing time: {total_processing_time:.2f} seconds")

            exit(0)
        return timeout_handler

    return crawl_status, make_timeout_handler


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Helper Functions: `clean_url_segment()` and `matches_keywords()`**

    ### Check whether a URL contains a relevant **keyword**

    _**Note:**_

    - A URL like `https://group.mercedes-benz.com/sustainability/reports/` is made up of **segments** separated by `/`. The segments here are `sustainability` and `reports`.
    - `clean_url_segment()` strips hyphens, dots, and other punctuation from a segment and converts it to lowercase to facilitate matching against the keyword.
    - `matches_keywords()` splits a URL into its segments, cleans each one, and checks whether any keyword appears inside any segment. If a match is found, the URL is considered relevant and worth following.
    - **In plain English:** *"Does this URL address contain any of our topic words?"*
    """)
    return


@app.cell
def _(re, urlparse):
    def clean_url_segment(segment):
        # Remove all non-alphanumeric characters and convert to lowercase
        return re.sub(r'[^a-zA-Z0-9]', '', segment).lower()

    def matches_keywords(url, keywords):
        # Split the URL path into segments (e.g., ['', 'sustainability', 'reports'])
        segments = urlparse(url).path.split('/')
        for segment in segments:
            cleaned_segment = clean_url_segment(segment)
            for keyword in keywords:
                cleaned_keyword = clean_url_segment(keyword)
                if cleaned_keyword in cleaned_segment:
                    return True
        return False

    return (matches_keywords,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **URL Utility Functions: `get_filename()` and `preprocess_href()`**

    _**Note:**_

    - `get_filename()` extracts the **filename** from the end of a URL. For example, from the URL `.../sustainability-report-2023.pdf` it returns `sustainability-report-2023` (without the `.pdf`). This is used later to screen PDF files by whether their name contains a topic keyword.
    - `preprocess_href()` is a small "cleaning" function. Links found on real web pages are sometimes malformed — they may contain spaces or broken `://` patterns. This function fixes those issues before the URL is used, so the crawler does not choke on bad input.
    """)
    return


@app.cell
def _(urlparse):
    def get_filename(url):
        segments = urlparse(url).path.split('/')
        last_segment = segments[-1]  # retrieves the last segment in the list segments
        if '.' in last_segment:
            return last_segment.split('.')[0]
        return ''

    def preprocess_href(href):
        # Remove all spaces
        href = href.replace(' ', '')

        # Replace the first occurrence of :/ with :// if not already ://
        if '://' not in href:
            href = href.replace(':/', '://', 1)

        # Replace any occurrence of more than one consecutive / with a single /
        parts = href.split('://')
        if len(parts) > 1:
            scheme, rest = parts[0], parts[1]
            rest = rest.replace('//', '/')
            href = f'{scheme}://{rest}'
        else:
            href = href.replace('//', '/')

        return href

    return get_filename, preprocess_href


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Page Scraping Function: `get_all_urls()`**

    ### Visit a single page and **collect all links** on it

    _**Note:**_

    - This function uses the Playwright browser to look at a web page and find every clickable link (`<a href="...">` tag in HTML).
    - Links on web pages often use **relative addresses** like `/sustainability/` instead of a full address like `https://group.mercedes-benz.com/sustainability/`. The function converts all relative links to full addresses using `urljoin`.
    - Links using non-web schemes (e.g. `mailto:` for email, `javascript:` for scripts) are ignored — we only want real web addresses starting with `http` or `https`.
    - The function returns a **set** of all the full URLs found on the page (no duplicates).
    """)
    return


@app.cell
def _(preprocess_href, urljoin, urlparse):
    async def get_all_urls(page, base_url):
        urls = set()
        anchors = await page.query_selector_all('a[href]')
        for anchor in anchors:
            href = await anchor.get_attribute('href')
            if not href:
                continue
            href = preprocess_href(href)

            parsed_href = urlparse(href)

            if not parsed_href.scheme:
                # Relative URL — resolve against the current page URL
                full_url = urljoin(base_url, href)
            elif parsed_href.scheme in ['http', 'https']:
                # Absolute URL — use as-is
                full_url = href
            else:
                # Skip non-http schemes (mailto:, javascript:, etc.)
                continue

            if full_url:
                urls.add(full_url)

        return urls

    return (get_all_urls,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Helper Functions: `collect_urls()` — the heart of the crawler**

    ### Recursively visit pages and **gather URLs** up to the allowed depth

    _**Note:**_

    - This is the most important function in the notebook. Think of it like a **treasure hunt with rules**:
        1. Visit the current page (`base_url`) using the browser.
        2. Collect all links found on that page.
        3. Keep only the links that (a) contain a keyword and (b) are not excluded.
        4. For each of those links, **call this same function again** on the linked page — but only if we haven't been there before and we haven't gone deeper than `max_depth`.
        5. After exploring all children, mark the current page as "visited" so we never visit it again.
    - The word **recursive** means the function calls itself. Each call goes one level deeper, and the process stops automatically when `current_depth > max_depth`.
    - All discovered URLs are added to the shared `all_urls` set, so nothing is lost across recursive calls.
    """)
    return


@app.cell
def _(
    get_all_urls,
    is_excluded,
    keywords,
    matches_keywords,
    shutil,
    targetURL,
):
    async def collect_urls(page, base_url, current_depth, max_depth, all_urls_init, visited_urls):
        if current_depth > max_depth:
            return all_urls_init

        # Print current URL on the same line, overwriting the previous one
        # Get terminal width dynamically, fallback to 200 if not detectable
        term_width = shutil.get_terminal_size(fallback=(200, 24)).columns

        prefix = f"  Visiting (depth {current_depth}): "
        max_url_len = term_width - len(prefix)
        display_url = base_url if len(base_url) <= max_url_len else base_url[:max_url_len]

        print(f"\r\033[K{prefix}{display_url}", end='', flush=True)

        try:
            response = await page.goto(base_url, wait_until="domcontentloaded", timeout=30000)

            if response is None or response.status not in (200, 304):
                visited_urls.append(base_url)
                return all_urls_init

        except Exception as e:
            print(f"\n\033[KError navigating to {base_url}: {e}")
            visited_urls.append(base_url)
            return all_urls_init

        urls = await get_all_urls(page, base_url)

        # Filter to only keyword-matching, non-excluded URLs for further navigation
        filtered_urls = sorted(
            #{url for url in urls if matches_keywords(url, keywords) and not is_excluded(url)}
        # Set exception for url == targetURL
            #{url for url in urls if (matches_keywords(url, keywords) or url == targetURL) and not is_excluded(url)}
        # Set exception for url.startswith(targetURL)
            {url for url in urls if (matches_keywords(url, keywords) or url.startswith(targetURL)) and not is_excluded(url)}
        )


        # Debugging: check whether the targetURL has been found
        if targetURL in urls:
            print(f"\n\033[K  Found link to targetURL on: {base_url}\n", end='', flush=True)
        #if base_url == targetURL:
        if base_url.startswith(targetURL):
            print(f"\n\033[K  Reached targetURL: {base_url}\n", end='', flush=True)

        all_urls_init.update(urls)  # add urls to all_urls_init passed by reference

        # Increment depth for the next recursive call
        next_depth = current_depth + 1

        for url in filtered_urls:
            if url not in visited_urls:
                # Pass visited_urls explicitly — avoids a reactive cycle in Marimo's DAG
                await collect_urls(page, url, next_depth, max_depth, all_urls_init, visited_urls)

        # Mark base_url as visited only after all children have been explored
        visited_urls.append(base_url)

        return all_urls_init

    return (collect_urls,)


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ---

    ## **Read Seed URLs from CSV**

    _**Note:**_

    - Before the crawler can start, it needs a list of **starting pages** — the "seed URLs".
    - This cell reads a CSV file that was prepared in an earlier step. It contains candidate URLs for the website we want to crawl.
    - We keep only the URLs whose address already contains a **topic keyword** (e.g. `sustainability`). These become our seeds — the pages the crawler will visit first.
    - `filter_urls()` then removes any redundant sub-paths, leaving a clean, compact set of starting points.
    - The final seed URLs are saved to `seedURLs.csv` for your reference.
    """)
    return


@app.cell
def _(
    col_name,
    csv,
    file_name,
    filter_urls,
    matches_keywords,
    os,
    pwd_dir,
    save_urls_to_csv,
    topics,
):
    # Read URLs from urls_filtered.csv
    file_path = os.path.join(pwd_dir, file_name)  # full file path of urls_filtered.csv
    print("Reading file: ", file_path)
    with open(file_path, 'r') as infile:
        reader = csv.DictReader(infile)
        urls = [
            row[col_name] for row in reader if matches_keywords(row[col_name], topics)
        ]

    # Filter URLs and keep only unique non-redundant URLs
    seed_urls = filter_urls(urls)

    # Save seed URLs for reference and reproducibility
    save_urls_to_csv('public/crawl/seedURLs.csv', seed_urls)

    print("seed_urls:", seed_urls)
    return (seed_urls,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Load Browser Session State**

    _**Note:**_

    - Some websites show a "cookie consent" banner or require you to be logged in before displaying their full content. A real user clicking "Accept" leaves behind small pieces of data called **cookies** and **localStorage** values in the browser.
    - These were saved to `cookies.json` and `localStorage.json` during a previous manual browsing session.
    - This cell loads that saved data so the crawler can inject it into the browser before it starts visiting pages — making the browser appear to be a returning human visitor rather than a robot.
    - Without this step, some pages might not display their full content or could block access entirely.
    """)
    return


@app.cell
def _(json):
    # Load cookies and local storage saved from a prior browser session
    with open('cookies.json', 'r') as f:
        cookies = json.load(f)

    with open('localStorage.json', 'r') as f:
        local_storage = json.load(f)
    return cookies, local_storage


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Main Crawl Loop**

    ### Launch the browser and **start crawling**

    _**Note:**_

    - This is the cell that actually **runs the crawler**. Everything defined so far has been preparation; this cell sets it all in motion.
    - Here is what happens step by step:
        1. An empty list (`visited_urls`) and a starting set of URLs (`all_urls`) are created.
        2. The **safety timer** is armed — if the crawl exceeds `timeout_duration` seconds, it will save results and stop automatically.
        3. A **headless Chromium browser** is launched (headless means no visible window).
        4. The browser is configured to look like a real human user (realistic browser settings, cookies, localStorage).
        5. For each seed URL, `collect_urls()` is called — which visits the page, collects links, and recursively follows relevant ones up to the allowed depth.
        6. When all seeds have been explored, the browser is closed and the timer is cancelled.
    - The word **`async`** in `async def _(...):` is a technical requirement of the marimo notebook: Playwright needs to run inside an asynchronous context. You can think of it simply as "this cell runs the browser in the background".

    _**Note on Anti-Bot Detection:**_

    - Many websites try to detect and block automated crawlers. This cell applies several techniques to make the browser appear human:
        - Uses a realistic browser identity string (`user_agent`) matching a real Chrome browser on Windows.
        - Sets language and timezone to match a typical user.
        - Hides internal browser flags that would reveal it is being controlled by a script.
    """)
    return


@app.cell
async def _(
    async_playwright,
    collect_urls,
    cookies,
    crawl_status,
    depth,
    local_storage,
    make_timeout_handler,
    seed_urls,
    signal,
    timeout_duration,
    topLevelURL,
):
    # Initialize the list of visited URLs.
    # Defined here (not in a separate cell) and passed explicitly to collect_urls()
    # to avoid a reactive dependency cycle in Marimo's DAG.
    visited_urls = list()

    # Initialize the set of all URLs with a copy of seed URLs
    all_urls = set(seed_urls)  # Must not use all_urls = seed_urls (reference only)

    # Create timeout handler AFTER all_urls and visited_urls are defined
    timeout_handler = make_timeout_handler(lambda: all_urls, lambda: visited_urls)
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_duration)

    # Start the collection process using async_playwright
    # (sync_playwright would conflict with Marimo's existing async event loop)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',  # key: hides webdriver flag
                '--disable-dev-shm-usage',
                '--disable-infobars',
                '--window-size=1920,1080',
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            locale='en-US',
            timezone_id='America/New_York',
            # Mimic a real browser's accepted languages and encoding
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
            }
        )

        # ── Patch navigator.webdriver to undefined (critical for Akamai bypass) ──
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]   // non-empty plugins list
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            window.chrome = { runtime: {} };  // Chrome object present in real browsers
        """)

        # Inject cookies to simulate an authenticated / consent-accepted session
        await context.add_cookies(cookies)

        page = await context.new_page()

        # Navigate to the top-level URL before manipulating localStorage
        await page.goto(topLevelURL)

        await page.evaluate("localStorage.clear();")
        for key, value in local_storage.items():
            await page.evaluate(f"localStorage.setItem('{key}', '{value}');")

        # Collect URLs starting from seed URLs
        for base_url in seed_urls:
            print(f"\n\n\033[KStart exploring from the seed URL: {base_url}")
            await collect_urls(page, base_url, 1, depth, all_urls, visited_urls)

        await browser.close()

    # Cancel the alarm if the process completes before the timeout
    signal.alarm(0)

    # ── Report how the crawl ended ──
    if crawl_status['timed_out']:
        print("\n⚠️  Crawl ended due to TIMEOUT.")
    else:
        print("\n✅  Crawl completed normally — all seed URLs fully explored.")

    print(f"   Pages visited : {len(visited_urls)}")
    print(f"   URLs collected: {len(all_urls)}")
    # Move to a new line after the loop
    print()
    return all_urls, visited_urls


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Post-processing Utility Functions**

    _**Note:**_

    - Once crawling is complete, these helper functions tidy up the results before saving them.
    - `extract_filename()` pulls out the **last part of a URL** (e.g. `sustainability-report-2023.pdf` from a long web address).
    - `extract_extension()` then extracts the **file type suffix** (e.g. `pdf`) from that filename — useful for sorting and filtering results.
    - `postprocess()` takes all collected URLs, saves them to `allURLs.csv`, and uses pandas to add two extra columns (`Filename` and `Extension`) that make the output easier to inspect. The enriched table is saved to `allURLs_df.csv`.
    - `keepPDF()` is a simple filter that returns only the URLs that end in `.pdf` — these are the downloadable document files found during the crawl.
    """)
    return


@app.cell
def _(pd, re, save_urls_to_csv):
    def extract_filename(url):
        return url.split('/')[-1]

    def extract_extension(filename):
        if '.' in filename:
            # Split on the last dot
            extension = filename.split('.')[-1]
            # Remove any special character (e.g., from query strings like ?v=1)
            extension = re.split(r'[?#/]', extension)[0]
            return extension
        return ''

    def postprocess(urls, topLevelURL):
        try:
            save_urls_to_csv('public/crawl/allURLs.csv', urls)
            # Read the CSV file into a DataFrame
            df = pd.read_csv('public/crawl/allURLs.csv', dtype=str)

            # Extract filenames and extensions from each URL
            df['Filename'] = df['URL'].apply(extract_filename)
            df['Extension'] = df['Filename'].apply(extract_extension)

            # Reorder columns for readability
            df = df[['Extension', 'Filename', 'URL']]

            # Save enriched DataFrame to CSV
            df.to_csv('public/crawl/allURLs_df.csv', index=False)

            return df['URL'].tolist()
        except Exception as e:
            print(f"Error in postprocess: {str(e)}")
            return list(urls)

    def keepPDF(urls):
        try:
            # Filter URLs that end with .pdf
            pdf_urls = [url for url in urls if url.lower().endswith('.pdf')]
            return pdf_urls
        except Exception as e:
            print(f"Error in keepPDF: {str(e)}")
            return []

    return keepPDF, postprocess


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Save Results to CSV Files**

    _**Note:**_

    - This final cell saves all the results collected during the crawl into four separate CSV files, each serving a different purpose:
        - **`allURLs.csv` / `allURLs_df.csv`** — every URL found during the crawl, with the enriched version also showing the filename and file type.
        - **`pdfURLs.csv`** — only the links that point to PDF documents.
        - **`pdfscreenedURLs.csv`** — a further-filtered subset: only PDFs whose **filename** contains a topic keyword (e.g. `sustainability-report-2023.pdf`). These are the most likely to be relevant reports.
        - **`visitedURLs.csv`** — the list of pages the crawler actually navigated to, useful for checking coverage and debugging.
    - The cell also prints the **total time** the notebook took to run from start to finish.
    """)
    return


@app.cell
def _(
    all_urls,
    get_filename,
    keepPDF,
    matches_keywords,
    postprocess,
    save_urls_to_csv,
    start_time,
    time,
    topLevelURL,
    topics,
    visited_urls,
):
    # Run post-processing: enrich allURLs.csv with filename and extension columns
    all_urls_processed = postprocess(all_urls, topLevelURL)
    # Note: postprocess() contains the following statements for saving csv files:
    #   - save_urls_to_csv('allURLs.csv', urls)
    #   - df.to_csv('allURLs_df.csv', index=False)

    # Extract and save PDF URLs
    pdfcollected_urls = keepPDF(all_urls_processed)
    save_urls_to_csv('public/crawl/pdfURLs.csv', pdfcollected_urls)

    # Further screen PDFs by topic keywords in the filename
    pdfscreened_urls = {url for url in pdfcollected_urls if matches_keywords(get_filename(url), topics)}
    save_urls_to_csv('public/pdfscreenedURLs.csv', pdfscreened_urls)

    # Save the list of all visited pages
    save_urls_to_csv('public/crawl/visitedURLs.csv', visited_urls)

    # Calculate and print the total processing time
    end_time = time.time()
    total_processing_time = end_time - start_time
    print(f"Total processing time: {total_processing_time:.2f} seconds")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ---

    ## **Summary** of all functions defined in the notebook:

    - **`commonDomain(url, benchmarkURL)`** — Checks whether a URL belongs to the same website as the benchmark (by comparing the last two parts of the domain name, e.g. `mercedes-benz.com`).

    - **`is_excluded(url)`** — Returns `True` if a URL should be skipped: either because it points to a non-HTML file (e.g. `.pdf`, `.zip`) or because it belongs to a different website.

    - **`filter_urls(urls)`** — Removes duplicate and redundant sub-path URLs, keeping only the highest-level (shortest) URL from each group, and returns a clean `set`.

    - **`save_urls_to_csv(filename, urls)`** — Writes a sorted list of URLs to a CSV file with a `URL` header column.

    - **`make_timeout_handler(get_all_urls_ref, get_visited_urls_ref)`** — Creates an emergency-stop function that saves collected URLs to CSV and exits if the crawl exceeds the time limit.

    - **`clean_url_segment(segment)`** — Strips punctuation from a URL path segment and lowercases it, so keywords can be matched reliably (e.g. `sustainability-reports` → `sustainabilityreports`).

    - **`matches_keywords(url, keywords)`** — Returns `True` if any segment of a URL contains at least one of the specified keywords (after cleaning).

    - **`get_filename(url)`** — Extracts the filename stem (without extension) from the last part of a URL path.

    - **`preprocess_href(href)`** — Cleans raw link strings found on web pages by removing spaces and fixing broken `://` patterns.

    - **`get_all_urls(page, base_url)`** — Visits a page using Playwright and returns a set of all absolute URLs found in its links.

    - **`collect_urls(page, base_url, current_depth, max_depth, all_urls_init, visited_urls)`** — The core recursive crawler: visits a page, collects all links, filters by keyword, and recursively follows relevant links up to `max_depth`.

    - **`extract_filename(url)`** — Returns the last path segment of a URL (the raw filename including extension).

    - **`extract_extension(filename)`** — Parses the file extension from a filename, stripping any query string characters.

    - **`postprocess(urls, topLevelURL)`** — Saves all collected URLs to `allURLs.csv` and enriches them with `Filename` and `Extension` columns, writing the result to `allURLs_df.csv`.

    - **`keepPDF(urls)`** — Filters a list of URLs to return only those ending in `.pdf`.
    """)
    return


if __name__ == "__main__":
    app.run()
