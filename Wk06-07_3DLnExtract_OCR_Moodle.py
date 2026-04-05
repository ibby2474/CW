# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.20.2",
#     "nest-asyncio>=1.6.0",
#     "nltk>=3.9.2",
#     "pandas>=3.0.1",
#     "playwright>=1.58.0",
#     "pymupdf>=1.27.1",
#     "pytesseract>=0.3.13",
#     "pyzmq>=27.1.0",
# ]
# ///

import marimo

__generated_with = "0.20.4"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    **Note:**

    - To create a new marimo notebook in Codespaces / VS Code, use the command palette (`Ctrl + Shift + P` or `Cmd + Shift + P`) and select `Create: New marimo notebook`".
        - This will open a new marimo notebook where you can start writing and executing your code.
    - To execute a code cell in a marimo notebook, a kernel must have been selected first.
        - Select a kernel by clicking on the `Select Kernel` button in the top right corner of the marimo notebook and choose `marimo sandbox` from the dropdown list.
    - This marimo notebook may be executed directly as an ordinary **Python script** as follows:
        - Click the hamburger button (≡) in the top-left corner of GitHub Codespaces and select `Terminal | New Terminal` to start a new terminal, followed by entering the command below:

        ```bash
            python3 Wk06-07_3DLnExtract_OCR.py
        ```
    - To open Codespace's Explorer as a **Directory listing** on a webpage, click the hamburger button (≡) and select `Terminal | Run Task...`, followed by clicking the choice `Serve workspace (python3 -m http.server 8000)`
        - To **view pdf files** in the `docArchive/pagesExtracted/` subfolder,
            - click `docArchive/` in the Directory listing, followed by `pagesExtracted/`
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    # **Download PDFs and Extract Pages with Specified Keywords**

    This notebook automates three stages of a PDF data collection pipeline:

    1. **Download** — fetch PDF sustainability reports from a list of screened URLs
    2. **Analyse** — count occurrences of user-defined keywords on every page of each PDF
    3. **Extract** — save only the matching pages as individual single-page PDFs

    For PDFs that are not text-searchable (i.e., scanned image-based documents), the notebook falls back to **OCR** using Tesseract via Option 2.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Notebook Flow — Outline Pseudocode**

    _Read this section first to understand the overall logic of the notebook before diving into the code._

    - STEP 1 — SET UP
        - Define settings: input CSV file, year to target, keywords to search for, fraction of reports to download
        - Load required tools (libraries)
        - Create output folders: `docArchive/DLdocs/` (for downloaded PDFs) and `docArchive/pagesExtracted/` (for extracted pages)

    - STEP 2 — LOAD AND FILTER THE REPORT LIST
        - Read the screened PDF URL list from a CSV file into a table
        - Keep only the rows whose URL contains the target year (e.g. `2019`)
        - This gives a filtered list of reports ready for downloading

    - STEP 3 — DOWNLOAD PDFs
        - Load saved browser cookies (so the downloader looks like a real user)
        - For each URL in the filtered list (up to the chosen fraction):
            - Skip if already downloaded (check the download ledger `df_DL.csv`)
            - Otherwise, download the PDF using `curl` and save it to `DLdocs/`
            - Record the result in the download ledger `df_DL.csv`

    - STEP 4 — PREPARE HELPER TOOLS (functions) for keyword analysis
        - `process_pdf()` → **Option 1** — count keyword occurrences page-by-page in a text-searchable PDF:
            - `clean_word_inner()` &emsp; → strip accents, punctuation, and capitalisation from each word before matching
        - `is_text_searchable()` → check whether a PDF has a readable text layer (or is a scanned image)
        - `process_pdf_ocr()` → **Option 2** — count keywords using OCR for scanned/image-only PDFs:
            - `ocr_extract_text()` &emsp; → render a page as an image and read it with Tesseract OCR
            - `clean_word_ocr()` &emsp; → clean words extracted by OCR (preserves numbers and currency symbols)
            - `is_meaningful()` &emsp; &emsp; → filter out OCR noise by checking if a word is a real English word or number

    - STEP 5 — ANALYSE EACH DOWNLOADED PDF FOR KEYWORDS
        - For each PDF in `DLdocs/`:
            - Check and fix internal page numbering if broken → back up the original to `bad/` subfolder first
            - Decide which method to use:
                - If text-searchable → use `process_pdf()` (Option 1)
                - If scanned / image-only → use `process_pdf_ocr()` (Option 2)
            - Record the result: a list of `[page number, keyword count]` pairs saved back to `df_DL.csv`

    - STEP 6 — EXTRACT AND SAVE MATCHING PAGES
        - For each analysed PDF in `df_DL.csv`:
            - Read the list of `[page number, keyword count]` pairs
            - For each matching page:
                - Extract that single page as a new PDF
                - Save it to `pagesExtracted/` with a filename that encodes the page number and keyword count
            - Mark the row as `Extracted = 1` in `df_DL.csv`
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **User-configurable Parameters**

    _**Note:**_

    - `reportList` points to the CSV file produced by an upstream notebook that screened URLs by topic keyword and file extension.
    - `years` filters the URL list to only download reports whose filename contains the specified year — change this to target a different year.
    - `keywords` sets the keywords to search for in a report (e.g., ['pollution'], ['air', 'water'], etc)
    - `pct2DL` controls what **fraction** of the filtered report list to download on each run (e.g., `0.5` = 50%); set to `1` to download everything.
    - `DetailedPage` is a **0-indexed** page number used for verbose debug output during keyword analysis — useful for inspecting exactly which words are being detected on a specific page.
    """)
    return


@app.cell
def _():
    #==============================================================================
    # Parameters adjustable by the user
    #==============================================================================
    reportList = 'public/pdfscreenedURLs.csv'    # Contains the list of reports to download
    #reportList = 'public/pdfscreenedURLs_Backup.csv'    # Contains the list of reports to download
    col_name = 'URL'  # Column name in the reportList file that contains the URLs

    # Set parameter for the 'year to download'
    years = 2019  # 2023 # 

    # Set keywords to search for in a report
    keywords = ['water']  # ['air', 'water']  # ['pollution']  # ['segment', 'segments']

    # Set parameter for the 'percentage (in decimal point) of reports to download'
    pct2DL = 1    # .5
    # [For debugging] Set parameter for reporting details of the page numbered 'DetailedPage'
    DetailedPage = 1   # Note: Python is 0-indexed; so DetailedPage = 1 means the second page of the report

    #==============================================================================
    # Unused parameters
    #==============================================================================
    #yearEnd = 2023
    #yearStart = 2014
    #years = [yearStart - i for i in range(yearStart - yearEnd + 1)]
    #==============================================================================
    return DetailedPage, col_name, keywords, pct2DL, reportList, years


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Imports**

    _**Note:**_

    - `pymupdf` and `fitz` refer to the **same library** — `fitz` is the legacy module name for PyMuPDF and both must be imported for full compatibility with the API used throughout this notebook.
    - `unicodedata` and `string` are used later for text normalisation — stripping accents, punctuation, and non-ASCII characters before keyword matching.
    - `shutil` provides high-level file operations such as copying files, used here to back up problematic PDFs before overwriting them.
    """)
    return


@app.cell
def _():
    # Import the required libraries

    import marimo as mo
    import pandas as pd
    import pymupdf
    import fitz  # require pymupdf
    import unicodedata
    import shutil

    import subprocess
    import os
    from urllib.parse import urlparse
    from collections import defaultdict
    import ast
    import math
    import json
    import string

    return (
        ast,
        defaultdict,
        fitz,
        json,
        math,
        mo,
        os,
        pd,
        pymupdf,
        shutil,
        string,
        subprocess,
        unicodedata,
        urlparse,
    )


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Prepare Folders for Storing Documents**

    - Identify the repository root directory from the `RepositoryName` environment variable
    - Create the `docArchive/` folder and its subfolders `DLdocs/` and `pagesExtracted/`
    - List folder contents to confirm successful creation

    _**Note:**_

    - `os.makedirs(..., exist_ok=True)` creates the full directory path in one call and **does not raise an error** if the directory already exists — safe to re-run.
    - The repository root is located by searching for `RepositoryName` inside the current working directory path using `str.find()`, which **returns the lowest index** where the substring is found, or `-1` if the substring is **not found**.
    """)
    return


@app.cell
def _(os, subprocess):

    # Get the current working directory and create a local directory there
    current_directory = os.getcwd()
    print(f"current_directory: {current_directory}\n")

    #==================================================================================
    # Get the value of the RepositoryName environment variable
    repository_name = os.getenv('RepositoryName')

    # Find the position of the repository name in the current directory path
    repo_index = current_directory.find(repository_name)

    # Retain only the part of the path up to and including the repository name
    if repo_index != -1:   # if the repository name is found in the current directory path
        repo_dir = current_directory[:repo_index + len(repository_name)]
    else:
        repo_dir = current_directory

    print(f"Repo directory: {repo_dir}\n")
    #==================================================================================

    # Path to the document directory
    doc_dir = os.path.join(repo_dir, 'docArchive')
    # Create the directory if it does not exist
    os.makedirs(doc_dir, exist_ok=True)

    # Create three subfolders (if not already created)
    subfolders = ['DLdocs', 'pagesExtracted']  # Define the subfolders to be created
    # Create the subfolders if they do not already exist
    for subfolder in subfolders:
        subfolder_path = os.path.join(doc_dir, subfolder)
        os.makedirs(subfolder_path, exist_ok=True)
        print(f"Subfolder created or already exists: {subfolder_path}")
    print(" ")

    # List contents in the document directory
    subprocess.run(['ls', '-la', doc_dir])
    return (repo_dir,)


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ---

    ## **Read the CSV with PDF URL Information**

    _**Note:**_

    - `pd.set_option('display.max_colwidth', None)` prevents pandas from truncating long URLs when printing the DataFrame — important for verifying the correct URLs are being used.
    """)
    return


@app.cell
def _(col_name, os, pd, repo_dir, reportList):

    # Step 1: Read the CSV file into a pandas DataFrame
    df_raw = pd.read_csv(os.path.join(repo_dir, reportList))

    # Rename the column with the name in col_name to 'full_urls' for consistent referencing later
    df_raw.rename(columns={col_name: 'full_urls'}, inplace=True)

    # Display the data type of the 'full_urls' column
    print("\nData type of 'full_urls' column:", df_raw['full_urls'].dtype)

    # Check the type of the first element in the 'full_urls' column
    first_element_type = type(df_raw['full_urls'].iloc[0])
    print("\nType of the first element in 'full_urls' column:", first_element_type)

    # Adjust pandas display options to show max colwidth
    pd.set_option('display.max_colwidth', None)

    # Create a copy of the DataFrame for further processing
    # Note: This ensures the read-in DataFrame, df_raw, is not altered in subsequent processing
    df_use0 = df_raw.copy()  # pandas's method to create a deep copy

    # Display the dataFrame used for further processing
    print("\nDataFrame df_raw:\n", df_use0)
    return (df_use0,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Filter the URL List by Year**

    _**Note:**_

    - The search string is simply the year as a string (e.g., `'2019'`), and `.str.contains()` checks whether it appears anywhere in the URL
        - most sustainability report filenames include their publication year
    - `.shape` is an attribute of pandas DataFrames that returns a tuple representing the dimensions: `(number_of_rows, number_of_columns)`.
        - `.shape[0]` gives the number of rows.
        - `.shape[1]` gives the number of columns.
    """)
    return


@app.cell
def _(df_use0, os, repo_dir, years):

    # Define the output directory
    output_dir = os.path.join(repo_dir, 'docArchive/DLdocs')
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Drop rows with NaN values in 'full_urls' column
    df_use = df_use0.dropna(subset=['full_urls'])
    # Note: Avoids running into errors when calling `.str.contains()` on `NaN` values

    # Create the string to search for
    search_str = f"{years}"   # e.g., '2019'
    # Display search string used
    print(f"Search string: {search_str}")

    # Refine df_use to include only rows where 'full_urls' contains the search string
    df_use = df_use[df_use['full_urls'].str.contains(search_str)]

    # Display the total number of rows
    print(f"Total number of rows: {df_use.shape[0]}")

    # Display the refined DataFrame
    print("DataFrame df_use for downloading:")
    print(df_use)
    return df_use, output_dir


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Download PDFs on the Filtered List**

    _**Note:**_

    - `curl` is used instead of Python's `requests` library to **bypass Akamai TLS fingerprint detection** — a security layer some corporate websites use that blocks automated HTTP clients but not browsers.
    - `df_use.sample(n=num2DL)` randomly selects `num2DL` rows to allow partial downloads for testing before committing to the full list.
    - `df_DL.csv` acts as a **persistent download ledger**: if the script is interrupted and re-run, already-downloaded URLs are detected and skipped, preventing duplicate downloads.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### What happens to `df_DL.csv` if it already exists?

    - If `df_DL.csv` already exists,
        - it is **read in** and new entries are appended to it via `pd.concat()`.
    - If it does not exist yet,
        - an empty DataFrame with the correct columns is created from scratch.
        - This makes the download step **safe to re-run** without losing progress.
    """)
    return


@app.cell
def _(
    df_use,
    json,
    math,
    os,
    output_dir,
    pct2DL,
    pd,
    repo_dir,
    subprocess,
    urlparse,
):

    # Load cookies from cookies.json (created by 1acceptNstoreCookies.py)
    def load_cookies(cookie_file):
        with open(cookie_file, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        return cookies  # Keep full list for both formats

    def cookies_to_curl_string(cookies):
        # Convert cookies list to curl cookie string
        return '; '.join(f"{c['name']}={c['value']}" for c in cookies)

    cookies_path = os.path.join(repo_dir, 'cookies.json')
    cookies_list = load_cookies(cookies_path)
    cookies_dict = {c['name']: c['value'] for c in cookies_list}  # keep for compatibility

    #------------------------------------

    def download_with_curl(url, output_path, cookies_list):
        """Use curl to download, bypassing Akamai TLS fingerprint detection."""
        cookie_str = cookies_to_curl_string(cookies_list)
        cmd = [
            'curl', '-L', '-o', output_path,
            '-w', '%{http_code}',    # print  HTTP status code to stdout after downloading ('200' confirms successful download)
            '--silent',
            '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '-H', 'Sec-CH-DPR: 1',
            '-H', 'Sec-CH-Viewport-Width: 1920',
            '-H', 'Sec-CH-Width: 1920',
            '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            '-H', 'Accept-Language: en-US,en;q=0.5',
            '-H', 'Accept-Encoding: gzip, deflate, br',
            '-H', 'Referer: https://group.mercedes-benz.com/',
            '-b', cookie_str,
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        http_code = result.stdout.strip()
        #==========================================
        success = http_code == '200'

        # Remove the output file if the download failed (curl creates an empty/error file regardless)
        if not success and os.path.exists(output_path):
            os.remove(output_path)
            print(f"Removed incomplete file: {output_path}")
        #==========================================
        return success
        #return http_code == '200'

    #------------------------------------

    # Define function to get the filename (incl. the extension) from the URL
    #   to be used for saving the downloaded file
    def get_filenameDOText(url):
        segments = urlparse(url).path.split('/')
        last_segment = segments[-1]
        return last_segment

    # Define the path for the df_DL.csv file
    df_DL_path = os.path.join(output_dir, 'df_DL.csv')

    # Read in/Create df_DL.csv for keeping track of downloaded files
    if os.path.exists(df_DL_path):
        # Read df_DL from the CSV file
        df_DL = pd.read_csv(df_DL_path)
    else:
        # Create an empty df_DL with the same columns as df_use plus an additional DL column
        df_DL = pd.DataFrame(columns=list(df_use.columns) + ['DL'])

    # Set the number of rows for downloading
    num2DL = math.ceil(pct2DL * df_use.shape[0])
    # Note: This rounds **up** to the nearest integer, ensuring at least one download even for small datasets

    for index, row in df_use.sample(n=num2DL).iterrows():  # pick n random rows
        full_url = row['full_urls']  # full_urls is now a single URL string

        # Check if the URL is already in df_DL
        if full_url in df_DL['full_urls'].values:
            print(f"URL already downloaded: {full_url}")
            continue

        # Display the full URL that is being used for download
        print(f"Downloading from URL: {full_url}")

        # Download the PDF file using curl and save it in the output directory
        # Note: Use curl instead of requests.get() to bypass Akamai TLS fingerprint detection
        output_path = os.path.join(output_dir, get_filenameDOText(full_url))
        success = download_with_curl(full_url, output_path, cookies_list)

        if success:
            # Update the DL column to 1 for the downloaded row
            row['DL'] = 1
            df_DL = pd.concat([df_DL, pd.DataFrame([row])], ignore_index=True)
            print(f"Downloaded successfully: {full_url}")
        else:
            print(f"Failed to download {full_url}")

    # Save the updated df_DL to the CSV file
    df_DL.to_csv(df_DL_path, index=False)

    # Display the updated df_DL
    print("\nDataFrame df_DL with all rows:")
    print(df_DL)
    return (df_DL_path,)


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ---

    ## **Option 1: Extract Keywords from Text-Searchable PDFs**

    ### Function: `process_pdf()`

    _**Note:**_

    - This approach uses PyMuPDF's `page.get_text("words")` method, which returns a list of word tuples.
    - Before matching, each word is passed through `clean_word_inner()`, which:
        1. Normalises Unicode characters by decomposing accented characters into **base character + diacritic mark**
        2. Strips **diacritics** (accent marks)
        3. Removes **punctuation** and **non-ASCII** characters
        4. Converts to **lowercase**
    - This normalisation ensures that words like `"water,"`, `"Water"`, and `"WATER"` all match the keyword `'water'`.
    - Results are returned as a list of `[page_number, frequency]` pairs for pages where at least one keyword was found.
    """)
    return


@app.cell
def _(defaultdict, pd, string, unicodedata):

    def process_pdf(pdf_document, keywords, DetailedPage):

        print(f"Keywords: {keywords}\n")

        # Initialize a dictionary to store the actual page numbers and the frequency of the keyword
        keyword_counts = defaultdict(int)

        # Function to normalize and clean words
        def clean_word_inner(word):
            # Normalize the word to NFKD form
            normalized_word = unicodedata.normalize('NFKD', word)
            # Remove diacritics and special characters
            cleaned_word = ''.join(c for c in normalized_word if unicodedata.category(c) != 'Mn')
            # Remove punctuation
            cleaned_word = cleaned_word.translate(str.maketrans('', '', string.punctuation))
            # Remove non-ASCII characters
            cleaned_word = ''.join(c for c in cleaned_word if c in string.printable)
            return cleaned_word.lower()

        # Loop through each page in the PDF
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)

            # Extract the words from each page
            words = page.get_text("words")

            # Count the occurrences of the keywords (case-insensitive) in the words
            count = sum(1 for word in words if any(keyword in clean_word_inner(word[4]) for keyword in keywords))
            # Note: Element [4] contains the word string; Elements [0:3] not used here are the bounding box coordinates
            keyword_counts[page_num + 1] += count  # Store the actual page number (1-indexed)
            # Note: PyMuPDF uses **0-based indexing**, but PDF page numbers in the real world are **1-based**. 
            #       Storing with `page_num + 1` ensures the page numbers in the output match what the reader sees in the PDF file

            # Additional debug: Print each word on page 'DetailedPage' after cleaning
            if page_num == DetailedPage:
                # Debug: Print the count for each page
                print(f"Page {page_num + 1}'s count of detected keyword(s): {count}\n")
                print(f"Displaying only first 15 or less of ...")
                for word in words[:15]:  # Limit to the first 15 words
                    cleaned = clean_word_inner(word[4])
                    print(f"Original Word: {word[4]}, Cleaned Word: {cleaned}")
                print(" ")

        # Convert the dictionary to a pandas DataFrame
        data = {'Page Number': list(keyword_counts.keys()), 'Frequency': list(keyword_counts.values())}
        df_freq = pd.DataFrame(data)

        # Sort the DataFrame by frequency in descending order
        df_freq = df_freq.sort_values(by='Frequency', ascending=False)

        # Filter the DataFrame to include only rows with non-zero frequencies
        df_non_zero = df_freq[df_freq['Frequency'] > 0]

        # Display the DataFrame
        print("Frequency table of detected keywords (after sorting):\n", df_non_zero, "\n")

        # Create a list of page numbers with frequencies
        page_numbers_with_frequencies = df_non_zero[['Page Number', 'Frequency']].values.tolist()

        return page_numbers_with_frequencies

    return (process_pdf,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### **Helper Function: `is_text_searchable()`**

    _**Note:**_

    - This function examines only the **first page** of the PDF as a quick proxy for the whole document.
    - The `threshold=0.5` parameter means: if fewer than 50% of extracted words are purely alphabetic, the page is considered **not reliably text-searchable** and OCR should be used instead.
    """)
    return


@app.function
def is_text_searchable(pdf_document, threshold=0.5):
    """
    Returns True if the first page of the PDF is mostly text-searchable.
    """
    page = pdf_document.load_page(0)
    words = page.get_text("words")
    if not words:
        return False
    # Optionally, check if most words are meaningful (using your is_meaningful function)
    meaningful_count = sum(1 for word in words if word[4].isalpha())
    total_count = len(words)
    return total_count > 0 and meaningful_count / total_count >= threshold


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Call `process_pdf()` to Analyse Keyword Frequency**

    _**Note:**_

    - Before keyword analysis, each PDF is checked for **page label integrity** using `has_proper_page_range()`. Some PDFs have a blank or non-`"1"` first-page label, which means their internal page numbering does not start at 1.
    - If the page range is broken, `fix_page_range()` reconstructs the PDF page by page into a new document and overwrites the original file — but only **after** a backup copy has been saved to the `bad/` subfolder.
    - Keyword analysis results are stored back in `df_DL_analyzed` as a stringified list in the column `'Page Numbers with Frequencies'`, and the `'Analyzed'` flag is set to `1` for each processed file.
    """)
    return


@app.cell
def _(
    DetailedPage,
    df_DL_path,
    fitz,
    keywords,
    os,
    output_dir,
    pd,
    process_pdf,
    process_pdf_ocr,
    shutil,
):

    # Define the directory paths
    pdf_dir = output_dir
    bad_pdf_dir = os.path.join(pdf_dir, 'bad')
    os.makedirs(bad_pdf_dir, exist_ok=True)

    # Read df_DL from the CSV file
    df_DL_analyzed = pd.read_csv(df_DL_path)

    #================================================
    def has_proper_page_range(pdf_document):
        # Check if the first page label is "1"
        first_page_label = pdf_document[0].get_label()
        print(f"First page label: {first_page_label}\n")  # Debug statement
        return first_page_label == "1"

    def fix_page_range(pdf_document):
        # Create a new PDF with corrected page numbers
        new_pdf = fitz.open()
        for page_num in range(len(pdf_document)):
            new_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
        return new_pdf
    #================================================

    # List all PDF files in the directory
    pdf_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]

    # Process each PDF file
    for pdf_file in pdf_files:
        print(f"------------------------------------------------------------\nPDF file: {pdf_file}\n")
        pdf_path = os.path.join(output_dir, pdf_file)
        pdf_document = fitz.open(pdf_path)

        #================================================
        # Check if the PDF has a proper page range
        first_page_label = pdf_document[0].get_label()
        if first_page_label == "":
            print(f"First page label is empty for {pdf_file}\n")
            # Copy the original PDF document to the 'bad' subfolder with _nolabel suffix
            nolabel_pdf_path = os.path.join(bad_pdf_dir, pdf_file.replace('.pdf', '_nolabel.pdf'))
            shutil.copy(pdf_path, nolabel_pdf_path)
        elif not has_proper_page_range(pdf_document):
            print(f"Fixing page range for {pdf_file}\n")

            # Copy the original problematic PDF document to the 'bad' subfolder
            bad_pdf_path = os.path.join(bad_pdf_dir, pdf_file.replace('.pdf', '_bad.pdf'))
            shutil.copy(pdf_path, bad_pdf_path)

            # Fix the page range
            pdf_document = fix_page_range(pdf_document)

            # Overwrite the original problematic PDF document with the fixed PDF document
            pdf_document.save(pdf_path, incremental=False)
        #================================================

        #================================================
        # Select the appropriate keyword extraction method
        # process_pdf() for text-searchable PDFs; process_pdf_ocr() as a fallback for scanned PDFs
        if is_text_searchable(pdf_document):
            page_numbers_with_frequencies = process_pdf(pdf_document, keywords, DetailedPage)
        else:
            page_numbers_with_frequencies = process_pdf_ocr(pdf_document, keywords, DetailedPage)
        #================================================

        # Close the PDF document
        pdf_document.close()

        # Update df_DL_analyzed with results
        df_DL_analyzed.loc[df_DL_analyzed['full_urls'].str.contains(pdf_file), 'Analyzed'] = 1
        df_DL_analyzed.loc[df_DL_analyzed['full_urls'].str.contains(pdf_file), 'Page Numbers with Frequencies'] = str(page_numbers_with_frequencies)
        # Note: Converts a Python list of lists (e.g., `[[3, 2], [7, 1]]`) into its string representation for saving to CSV 
        #       When reading back, `ast.literal_eval()` reconstructs the original Python object from that string 

    # Ensure the 'Analyzed' column is integer after updates
    df_DL_analyzed['Analyzed'] = df_DL_analyzed['Analyzed'].astype(int)

    # Display the updated df_DL_analyzed
    print("Updated df_DL_analyzed DataFrame: ")
    print(df_DL_analyzed)

    # Save the updated df_DL_analyzed to the CSV file (overwrite the existing file)
    df_DL_analyzed.to_csv(df_DL_path, index=False)
    return (df_DL_analyzed,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Store Extracted Pages in Folder**

    _**Note:**_

    - Only rows with `'Analyzed' == 1` in `df_DL_extract` are processed — i.e., only those pages analyzed for keyword frequency
    - The page list stored as a string in `'Page Numbers with Frequencies'` is reconstructed into a Python list of `[page_number, frequency]` pairs using `ast.literal_eval()`.
    - Page numbers are **1-indexed** in the stored data, so they are converted to **0-indexed** via `page_zeroIdx = int(page_number) - 1` before calling PyMuPDF.
    - The output filename encodes both the page number and its keyword frequency as `_[page, freq].pdf` for traceability.
    """)
    return


@app.cell
def _(ast, df_DL_analyzed, df_DL_path, fitz, os, pd, pymupdf, repo_dir):

    # Define the extraction directory
    extract_dir = os.path.join(repo_dir, 'docArchive/pagesExtracted')
    os.makedirs(extract_dir, exist_ok=True)

    # Define the directory with downloaded PDFs
    pdf_dir_extract = os.path.join(repo_dir, 'docArchive/DLdocs')

    # Not working: Read df_DL from the CSV file
    #df_DL_extract = pd.read_csv(df_DL_path)
    #---------------------------------------------------------
    # Use in-memory copy of df_DL_analyzed (thus always fresh)
    df_DL_extract = df_DL_analyzed.copy()
    
    # Iterate over the rows of df_DL_extract
    for idx, row_extract in df_DL_extract.iterrows():
        # Check if the row should be analyzed
        if row_extract['Analyzed'] == 1:
            # Extract the PDF filename from the full_urls column
            pdf_file_name = os.path.basename(row_extract['full_urls'])
            pdf_file_path = os.path.join(pdf_dir_extract, pdf_file_name)

            # Load the PDF document
            pdf_doc = fitz.open(pdf_file_path)

            # Extract the page numbers with frequencies from the DataFrame
            page_numbers_with_frequencies_str = row_extract['Page Numbers with Frequencies']

            # Convert the string back to a list of tuples using ast.literal_eval()
            page_numbers_with_freq = ast.literal_eval(page_numbers_with_frequencies_str)

            # Flag to track if all pages are extracted
            all_pages_extracted = True

            # Iterate over the list of page numbers and their frequencies (1-indexed)
            for page_number, frequency in page_numbers_with_freq:
                try:
                    #==============================================
                    # Set page number to be 0-indexed
                    page_zeroIdx = int(page_number) - 1   # Convert page_number to an integer
                    # Create a new PDF with the extracted page
                    new_pdf = pymupdf.open()                 # new empty PDF
                    new_pdf.insert_pdf(pdf_doc, to_page=page_zeroIdx)  # up to the page_zeroIdx page
                    # Remove all pages except the last one
                    if new_pdf.page_count > 1:
                        new_pdf.delete_pages(range(new_pdf.page_count - 1))  # Delete all pages except the last one
                    # Now new_pdf contains only the last page
                    # 
                    # Note: `insert_pdf(..., to_page=page_zeroIdx)` followed by deleting all pages except the last 
                    #       is a workaround for inserting a single specific page into a new document
                    #==============================================

                    # Define the output file name encoding page number and frequency
                    output_file_name = f"{pdf_file_name[:-4]}_[{page_number},{frequency}].pdf"
                    output_file_path = os.path.join(extract_dir, output_file_name)

                    # Save the new PDF
                    new_pdf.save(output_file_path)
                    new_pdf.close()
                except Exception as e:
                    # If any page extraction fails, set the flag to False
                    all_pages_extracted = False
                    print(f"Failed to extract page {page_number} from {pdf_file_name}: {e}\n")

            # Close the original PDF document
            pdf_doc.close()

            # Update the 'Extracted' column if all pages were successfully extracted
            if all_pages_extracted:
                df_DL_extract.at[idx, 'Extracted'] = 1

    # Save the updated DataFrame to the corresponding .csv file
    df_DL_extract.to_csv(df_DL_path, index=False)

    print("Pages extracted and saved successfully.")
    print(df_DL_extract)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ---

    ## **Option 2: OCR with Tesseract for Non-Text-Searchable PDFs**

    _**Note:**_

    - Some sustainability reports are **scanned image PDFs** — they contain no embedded text layer and return no words from `page.get_text("words")`. OCR (Optical Character Recognition) is needed to read them.
    - This section uses **Tesseract** (via `pytesseract`) to convert each page to an image and extract text from it.
    - Before running OCR, use a Terminal to install the required system package and Python libraries **if not already present**:

        ```bash
        sudo apt-get install tesseract-ocr
        pip install pytesseract nltk
        ```
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### **OCR Imports and Keyword Pattern**

    _**Note:**_

    - `nltk_words` provides an English word corpus used to decide whether an OCR-extracted token is a **real word** (`is_meaningful()`). This filters out OCR garbage characters (e.g., `"I#K2"`) that would inflate or pollute keyword counts.
    - `nltk.download('words')` is wrapped in a `try/except LookupError` block so the corpus is only downloaded **if not already present**, avoiding a redundant network request on every run.
    - The `numerical_pattern` regex matches common financial figures including currency prefixes (e.g., `$1,234.56`, `€99`, `SEK 1,000`) — these are treated as meaningful even though they are not in the English dictionary.
    """)
    return


@app.cell
def _():
    import nltk
    import pytesseract
    from PIL import Image

    from nltk.corpus import words as nltk_words
    import re
    from collections import defaultdict as defaultdict_ocr
    import io

    # Ensure NLTK words are downloaded only once
    try:
        english_words = set(nltk_words.words())
    except LookupError:
        nltk.download('words')
        english_words = set(nltk_words.words())

    # Define a regular expression pattern for numerical figures with specified currency symbols
    numerical_pattern = re.compile(r'^(?:[\$£€]|kr|SEK|DKK|NOK|CZK|PLN|HUF|RON|BGN|ISK|CHF)?\d{1,3}(?:,\d{3})*(\.\d+)?%?$')
    return (
        Image,
        defaultdict_ocr,
        english_words,
        io,
        numerical_pattern,
        pytesseract,
        re,
    )


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### **Function: `process_pdf_ocr()`**

    _**Note:**_

    - The OCR pipeline has **two fallback layers** per page:
        1. If `page.get_text("words")` returns nothing (blank text layer) → run `ocr_extract_text()`.
        2. If text was returned but fewer than 50% of words pass `is_meaningful()` (suggesting garbled text) → discard and run `ocr_extract_text()` anyway.
    - `ocr_extract_text()` renders each page as a **2× zoom pixmap** (higher resolution → better OCR accuracy), converts it to a PIL image, then calls `pytesseract.image_to_string()` with `--oem 3 --psm 6` (neural net OCR engine, uniform block of text layout).
    - `clean_word_ocr()` applies **more permissive cleaning** than `clean_word_inner()` in `process_pdf()` — it preserves `.`, `,`, and `%` when surrounded by digits (e.g., `1,234.56`) so that financial figures are not broken apart during cleaning.
    - The `DetailedPage` parameter triggers **full word-by-word debug output** for that specific page, helping diagnose why a keyword was or was not detected.
    """)
    return


@app.cell
def _(
    Image,
    defaultdict_ocr,
    english_words,
    fitz,
    io,
    numerical_pattern,
    pd,
    pytesseract,
    re,
    string,
    unicodedata,
):

    def process_pdf_ocr(pdf_document, keywords, DetailedPage):
        """
        OCR-based PDF keyword frequency extractor.
        Args:
            pdf_document: PyMuPDF document object
            keywords: list of keywords (lowercase)
            DetailedPage: int, 0-indexed page for debug output
        Returns:
            List of [page_number, frequency] for pages with nonzero frequency
        """
        print(f"Keywords: {keywords}\n")

        def clean_word_ocr(word):
            normalized_word = unicodedata.normalize('NFKD', word)
            cleaned_word = ''.join(c for c in normalized_word if unicodedata.category(c) != 'Mn')
            # Preserve . , % when surrounded by digits; remove otherwise
            cleaned_word = re.sub(r'(?<!\d)[.,%](?!\d)', '', cleaned_word)
            cleaned_word = cleaned_word.translate(str.maketrans('', '', string.punctuation.replace('.', '').replace(',', '').replace('%', '')))
            cleaned_word = ''.join(c for c in cleaned_word if c in string.printable)
            return cleaned_word.lower()

        def ocr_extract_text(page):
            # Render page at 2x zoom for better OCR accuracy
            zoom = 2
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes()))
            custom_config = r'--oem 3 --psm 6 -l eng'  # --psm 6` assumes a single uniform block of text
            text = pytesseract.image_to_string(img, config=custom_config)
            return text

        def is_meaningful(word):
            cleaned = clean_word_ocr(word)
            if cleaned.isalpha() and cleaned in english_words:
                return True
            if numerical_pattern.match(word):
                return True
            return False

        keyword_counts_ocr = defaultdict_ocr(int)

        for page_num_ocr in range(len(pdf_document)):
            page_ocr = pdf_document.load_page(page_num_ocr)
            words_ocr = page_ocr.get_text("words")

            # Fallback layer 1: no text layer found → use OCR
            if not words_ocr:
                text_ocr = ocr_extract_text(page_ocr)
                words_ocr = [(0, 0, 0, 0, word) for word in text_ocr.split()]

            # Fallback layer 2: text found but mostly garbled → use OCR
            if words_ocr:
                meaningful_count = sum(1 for word in words_ocr if is_meaningful(word[4]))
                total_count = len(words_ocr)
                if total_count > 0 and meaningful_count / total_count < 0.5:
                    text_ocr = ocr_extract_text(page_ocr)
                    words_ocr = [(0, 0, 0, 0, word) for word in text_ocr.split()]

            words_snippet = ' '.join(word[4] for word in words_ocr[:20])
            print(f"Page {page_num_ocr + 1} words snippet: {words_snippet}...")

            if page_num_ocr == DetailedPage:
                complete_words = ' '.join(word[4] for word in words_ocr)
                print(f"Complete words of {DetailedPage + 1}:\n{complete_words}")

            count_ocr = sum(1 for word in words_ocr if any(keyword in clean_word_ocr(word[4]) for keyword in keywords))
            keyword_counts_ocr[page_num_ocr + 1] += count_ocr  # 1-indexed

            print(f"Page {page_num_ocr + 1} count of detected keyword: {count_ocr}")

            if page_num_ocr == DetailedPage:
                for word in words_ocr:
                    cleaned_w = clean_word_ocr(word[4])
                    print(f"Original Word: {word[4]}, Cleaned Word: {cleaned_w}")

        # Convert to DataFrame-like output
        data = {'Page Number': list(keyword_counts_ocr.keys()), 'Frequency': list(keyword_counts_ocr.values())}
        df_freq = pd.DataFrame(data)
        df_freq = df_freq.sort_values(by='Frequency', ascending=False)
        df_non_zero = df_freq[df_freq['Frequency'] > 0]
        print("Frequency table of detected keywords (after sorting):\n", df_non_zero, "\n")
        page_numbers_with_frequencies = df_non_zero[['Page Number', 'Frequency']].values.tolist()
        return page_numbers_with_frequencies

    return (process_pdf_ocr,)


if __name__ == "__main__":
    app.run()
