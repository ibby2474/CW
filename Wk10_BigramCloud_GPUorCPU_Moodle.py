# /// script
# requires-python = ">=3.12"
# dependencies =[
#     "edgartools",
#     "ipython>=9.11.0",
#     "marimo>=0.20.2",
#     "matplotlib",
#     "nltk>=3.9.3",    # nltk stays for stopwords and ngrams only
#     "spacy",
#     "spacy-transformers",
#     "pyzmq>=27.1.0",
#     "wordcloud",
#     "beautifulsoup4",
#     "groq>=1.1.1",
#     "spacy-curated-transformers>=0.3.1",
#     "cupy-cuda13x",   # ← add this
#     "en-core-web-trf @ https://github.com/explosion/spacy-models/releases/download/en_core_web_trf-3.8.0/en_core_web_trf-3.8.0-py3-none-any.whl",  # ← and this
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
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    # **Extracting & Visualizing SEC 10-K Risk Factors**

    This notebook explores how **Natural Language Processing (NLP)** can be used to extract business insights from financial documents.

    Specifically, we will:
    1. **Fetch** annual financial reports (10-K filings) from the U.S. Securities and Exchange Commission (SEC) for the "Magnificent 7" tech companies.
    2. **Extract** the "Item 1A: Risk Factors" section, where companies must legally disclose the most significant risks to their business.
    3. **Process** the text using an advanced AI model to find the most frequent and meaningful phrases (single words and two-word combinations).
    4. **Visualize** these phrases as Word Clouds to see how the landscape of business risks has evolved over a decade (2015 vs. 2025).
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Notebook Flow — Outline Pseudocode**

    _Read this section first to understand the overall logic of the notebook before diving into the code._

    - STEP 1 — SET UP & LIBRARIES
        - Load the required Python tools (for data manipulation, web scraping, NLP, and visualizations).
        - Define our target companies (Mag 7) and target years (2015, 2025).

    - STEP 2 — LOAD THE AI MODEL
        - Load a `spaCy` Transformer model.
        - Tell the model to use the GPU (Graphics Processing Unit) if available, which makes processing massive amounts of text much faster.

    - STEP 3 — PREPARE SEC FETCHING TOOLS (Functions)
        - `get_cik()` → Convert a company ticker (like AAPL) into the SEC's internal ID number.
        - `get_10k_filings()` → Search the SEC database for 10-K documents matching that ID.
        - `get_risk_factors()` & `_extract_risk_factors()` → Download the document and mathematically "scissor out" just the Item 1A text using text patterns.

    - STEP 4 — PREPARE NLP TEXT PROCESSING TOOLS (Functions)
        - `remove_redundant_unigrams()` → Drop single words if they are mostly used inside a two-word phrase (e.g., drop "united" if we already count "united states").
        - `get_stemmed_ngram_freqs()` → The brain of the operation. Chops text into sentences, removes useless filler words (stopwords), and counts the frequency of meaningful phrases (n-grams).

    - STEP 5 — DOWNLOAD AND CACHE THE DATA
        - Download the risk factors for our companies and save them to a file (`risk_data.json`).
        - *Why?* So if we run the notebook again, we just load the file instantly instead of re-downloading everything from the SEC.

    - STEP 6 — VISUALIZE THE RESULTS
        - Filter out "boilerplate" legal jargon (like "forward-looking statements").
        - Generate side-by-side Word Clouds (2015 vs 2025) and top-20 phrase tables.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Imports and Libraries**

    _**Note:**_
    - `BeautifulSoup` and `requests` are used for downloading and reading websites (web scraping).
    - `spacy` is our heavy-duty NLP library that understands English grammar and context.
    - `nltk` provides simple tools for counting word groupings (n-grams) and lists of common "stop words" (like "the", "and", "is") that we want to ignore.
    - `WordCloud` turns our word frequency numbers into pretty visual graphics.
    """)
    return


@app.cell
def _():
    # Cell 1: Load necessary libraries

    import marimo as mo
    import pandas as pd
    import textwrap
    import json
    import os
    import io
    import re
    import time
    from datetime import datetime

    from bs4 import BeautifulSoup  
    import requests
    #import urllib.request
    import spacy
    import spacy_curated_transformers  # ensure curated_transformers factory is registered

    from wordcloud import WordCloud
    from collections import Counter
    import nltk
    from nltk.corpus import stopwords
    from nltk.util import ngrams

    # Ensure classic punkt is there (harmless redundancy)
    nltk.download('punkt')      # tokenizer
    nltk.download('stopwords')  # if you still want some
    nltk_stop = set(stopwords.words('english'))


    #------------------------------------------------------
    # Note: Not working as intended
    import warnings
    # This works regardless of NumPy version (as long as warnings module exists)
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,          # ← VisibleDeprecationWarning is a subclass
        module="thinc.*"
    )
    # Or more precisely by message if you want to be very targeted
    warnings.filterwarnings(
        "ignore",
        message=r".*toDlpack.*cupy.from_dlpack.*",
        module="thinc.*"
    )
    #------------------------------------------------------
    return (
        BeautifulSoup,
        Counter,
        WordCloud,
        io,
        json,
        mo,
        ngrams,
        os,
        pd,
        re,
        requests,
        spacy,
        stopwords,
        textwrap,
        time,
    )


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **User-configurable Parameters**

    _**Note:**_
    - The SEC requires automated programs to identify themselves. Update the `SEC_HEADERS` with your own email so they know who is requesting data.
    - `mag7` defines the stock tickers and names for the companies we are analyzing.
    - `FIRMS2DISPLAY` limits how many companies we process during testing to save time.
    """)
    return


@app.cell
def _():
    # Cell 2: Define the Mag7 and years

    # SEC requires a User-Agent header identifying you
    # Format: "Name email@domain.com" or just "email@domain.com"
    SEC_HEADERS = {"User-Agent": "Your Name yourname@example.com"}

    years = [2015, 2025]  # We'll target 10-K for fiscal periods ending in these years

    mag7 = {
        'AAPL': 'Apple',
        'MSFT': 'Microsoft',
        'GOOGL': 'Alphabet',
        'AMZN': 'Amazon',
        'META': 'Meta Platforms',
        'NVDA': 'Nvidia',
        'TSLA': 'Tesla'
    }

    FIRMS2DISPLAY = 2  # Number of firms to display in the word clouds (for testing, set to 2)

    # Force download or use cached versions of the filings
    force_refresh = True  # False  # set True to re-download

    #model = "en_core_web_sm"   # small transformer-based model for testing and development
    model = "en_core_web_trf"   # true transformer-based model requiring GPU for best performance

    UNIGRAM_COVERAGE_THRESHOLD = 0.9   # If a bigram covers 90% of the unigram occurrences, we can drop the unigram
    return (
        FIRMS2DISPLAY,
        SEC_HEADERS,
        UNIGRAM_COVERAGE_THRESHOLD,
        force_refresh,
        mag7,
        model,
        years,
    )


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Load the AI Brain (spaCy Model)**

    _**Note:**_
    - Processing thousands of pages of text requires serious computing power.
    - `spacy.prefer_gpu()` attempts to route the mathematical heavy-lifting to a Graphics Processing Unit (GPU) if your machine has one.
    - The loaded `model` is a pre-trained "Transformer" — similar to the technology behind ChatGPT — which understands the complex structures of English sentences.
    """)
    return


@app.cell
def _(model, spacy):

    success = spacy.prefer_gpu()
    print("✅ Running on GPU" if success else "✅ Running on CPU (no GPU/cupy available)")

    nlp = spacy.load(model)
    print(f"✅ Loaded {model}")
    return (nlp,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Helper Functions: Interacting with the SEC Database**

    _**Note:**_
    - `get_cik`: The SEC does not use stock tickers (like AAPL) natively. They use a Central Index Key (CIK). This function translates a ticker to a CIK.
    - `get_10k_filings`: Connects to the SEC's EDGAR database API to get a historical list of every document a company has submitted, and filters it down to only "10-K" annual reports.
    """)
    return


@app.cell
def _(SEC_HEADERS, requests):

    # ── EDGAR helpers (unchanged from earlier) ───────────────────────
    def get_cik(ticker):
        r = requests.get(
            "https://www.sec.gov/files/company_tickers.json",
            headers=SEC_HEADERS, timeout=15
        )
        for entry in r.json().values():
            if entry["ticker"].upper() == ticker.upper():
                return str(entry["cik_str"]).zfill(10)
        return None

    def get_10k_filings(cik):
        url  = f"https://data.sec.gov/submissions/CIK{cik}.json"
        data = requests.get(url, headers=SEC_HEADERS, timeout=15).json()
        recent = data["filings"]["recent"]
        filings =[]
        for i, form in enumerate(recent["form"]):
            if form == "10-K":
                filings.append({
                    "accession":   recent["accessionNumber"][i],
                    "filing_date": recent["filingDate"][i],
                    "primary_doc": recent["primaryDocument"][i],
                })
        for page in data["filings"].get("files",[]):
            page_data = requests.get(
                f"https://data.sec.gov/submissions/{page['name']}",
                headers=SEC_HEADERS, timeout=15
            ).json()
            for i, form in enumerate(page_data["form"]):
                if form == "10-K":
                    filings.append({
                        "accession":   page_data["accessionNumber"][i],
                        "filing_date": page_data["filingDate"][i],
                        "primary_doc": page_data["primaryDocument"][i],
                    })
        return filings


    return get_10k_filings, get_cik


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Helper Functions: Extracting the 'Risk Factors' Section**

    _**Note:**_
    - A 10-K report is often hundreds of pages long. We only care about "Item 1A".
    - `_extract_risk_factors`: Uses **Regular Expressions (regex)**—a powerful way to search for text patterns. It hunts for the start phrase "Item 1A" and stops reading when it hits "Item 1B" or "Item 2".
    - `get_risk_factors`: The master function that combines the CIK lookup, the 10-K download, and the text extraction into one step. It includes a `time.sleep(0.5)` to be polite so we don't crash the SEC website.
    """)
    return


@app.cell
def _(BeautifulSoup, SEC_HEADERS, get_10k_filings, get_cik, re, requests):

    def _extract_risk_factors(html_bytes):
        """Extract Item 1A text using BeautifulSoup + regex."""
        soup = BeautifulSoup(html_bytes, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r'\s+', ' ', text)

        # Match Item 1A header in various formats
        start_pat = re.compile(
            r'Item\s+1A[\.\s]*[\u2014\-]?\s*Risk\s+Factors',
            re.IGNORECASE
        )
        # Stop at the next major item (Item 1B or Item 2)
        end_pat = re.compile(
            r'Item\s+1B[\.\s]|Item\s+2[\.\s]',
            re.IGNORECASE
        )

        m_start = start_pat.search(text)
        if not m_start:
            return ""

        tail = text[m_start.start():]
        # Skip past the header itself before looking for the end
        m_end = end_pat.search(tail, pos=200)
        if m_end:
            return tail[:m_end.start()].strip()

        return tail[:80_000].strip()   # safety cap


    # ── Main entry point ─────────────────────────────────────────────
    def get_risk_factors(ticker, target_year):
        from datetime import datetime
        import time

        cik = get_cik(ticker)
        if not cik:
            print(f"CIK not found for {ticker}")
            return ""

        for filing in get_10k_filings(cik):
            filing_year = int(filing["filing_date"][:4])
            if filing_year not in (target_year, target_year + 1):
                continue

            accession_clean = filing["accession"].replace("-", "")
            doc_url = (
                f"https://www.sec.gov/Archives/edgar/data/"
                f"{int(cik)}/{accession_clean}/{filing['primary_doc']}"
            )
            try:
                html = requests.get(doc_url, headers=SEC_HEADERS, timeout=30).content
                result = _extract_risk_factors(html)

                if result and len(result) > 500:
                    print(f"✅ {ticker} ({filing['filing_date']}): {len(result)} chars")
                    time.sleep(0.5)   # be polite to SEC servers
                    return result
                else:
                    print(f"  ⚠️ {ticker} {filing_year}: extracted only {len(result)} chars, trying next filing")

            except Exception as e:
                print(f"  Error {ticker} {filing_year}: {e}")

        print(f"❌ No suitable 10-K found for {ticker} around {target_year}")
        return ""


    return (get_risk_factors,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Helper Function: Filtering Redundant Words (Unigrams vs Bigrams)**

    _**Note:**_
    - A **unigram** is a single word (e.g., "supply"). A **bigram** is a two-word phrase (e.g., "supply chain").
    - If the word "supply" almost always appears next to "chain" in the text, keeping both "supply" and "supply chain" in our Word Cloud is redundant.
    - This function drops single words if they are mostly "covered" by a larger phrase.
    """)
    return


@app.cell
def _(UNIGRAM_COVERAGE_THRESHOLD):
    # ────────────────────────────────────────────────────────────────
    def remove_redundant_unigrams(unigram_freq, bigram_freq, threshold=UNIGRAM_COVERAGE_THRESHOLD):
        cleaned = unigram_freq.copy()  # default to noun
        for word, uni_count in list(unigram_freq.items()):
            if uni_count == 0:
                continue
            covered = 0
            for bigram_str, bi_count in bigram_freq.items():
                parts = bigram_str.split('_')
                if len(parts) == 2 and (parts[0] == word or parts[1] == word):
                    covered = covered + bi_count
            coverage_ratio = covered / uni_count if uni_count > 0 else 0
            if coverage_ratio >= threshold:
                del cleaned[word]
        return cleaned

    return (remove_redundant_unigrams,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Helper Function: The NLP Text Pipeline**

    _**Note:**_
    This is the "engine" that turns raw text into quantifiable data:
    1. **Normalization**: Forces uniform spelling for things like "U.S." to "unitedstates".
    2. **Stopword Removal**: Ignores common grammar filler words (like "the", "and") and common corporate jargon (like "company", "fiscal", "quarter").
    3. **Chunking**: Splits sentences safely so we don't accidentally link the end of one thought to the beginning of another.
    4. **Lemmatization**: Groups words by their base form (e.g., "factors" and "factor" become the same word).
    """)
    return


@app.cell
def _(
    Counter,
    UNIGRAM_COVERAGE_THRESHOLD,
    ngrams,
    re,
    remove_redundant_unigrams,
    stopwords,
    time,
):

    # nlp is passed in from the cell above
    # ────────────────────────────────────────────────────────────────
    #def get_stemmed_ngram_freqs(text, nlp, ns=[1, 2], min_count=3):
    def get_stemmed_ngram_freqs(text, nlp, ns=None, min_count=3):
        if ns is None:
            ns = [1, 2]

        if not text:
            return {}, {}

        # Step 0: same US normalization
        text = re.sub(r'\bUnited States\b', 'unitedstates', text, flags=re.IGNORECASE)
        text = re.sub(r'\bU\.?S\.?\b',      'unitedstates', text, flags=re.IGNORECASE)
        text = re.sub(r'\bUS\b',            'unitedstates', text)

        early_stop = set(stopwords.words('english')).union({
            'in', 'the', 'to', 'of', 'and', 'or', 'by', 'as', 'at', 'on', 'for',
            'with', 'from', 'our', 'we', 'us', 'their', 'its', 'this', 'that',
            'these', 'those', 'such', 'other', 'any', 'all', 'some', 'no', 'not',
            'be', 'is', 'are', 'was', 'were', 'being', 'inc', 'corp', 'corporation',
            'llc', 'co', 'may', 'could', 'will', 'would', 'should', 'shall',
            'subject', 'including', 'however', 'also', 'per', 'within', 'without',
            'form', 'state', 'believe', 'addition', 'example', 'event', 'expect', 'partner',
            'year', 'years', 'fiscal', 'period', 'quarter', 'note', 'item',
            'company', 'factor', 'risk', 'business', 'operation', 'product', 'service', 'result',
            'unitedstate', 'unitedstates'   # ← add these
        })

        ngram_counts = Counter()
        ngram_contexts = {}   # gram_str → list of up to 2 example sentences


        t0 = time.perf_counter()
        doc = nlp(text[:100_000]) # Run the text through the spaCy AI model
        t1 = time.perf_counter()
        #--------------------------------------------
        BOUNDARY_POS    = {'CCONJ', 'SCONJ'}
        BOUNDARY_LEMMAS = {'and', 'or', 'but', 'nor', 'yet', 'so', 'although', 'whereas'}

        for sent in doc.sents:
            # ── Fix 1: conjunctions become chunk boundaries, not tokens ─────
            token_stream =[]
            for token in sent:
                lemma = token.lemma_.lower() # "Lemmatize" word (e.g. running -> run)

                if token.pos_ in BOUNDARY_POS or lemma in BOUNDARY_LEMMAS:
                    token_stream.append(None)   # sentinel — splits the stream
                    continue

                if (
                    not token.is_alpha
                    or token.is_stop
                    or token.is_punct
                    or token.is_space
                    or len(lemma) <= 2
                    or lemma in early_stop
                ):
                    continue

                token_stream.append(lemma)

            # ── Split stream into chunks at None boundaries ──────────────────
            chunks = []
            current_chunk =[]
            for item in token_stream:
                if item is None:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk =[]
                else:
                    current_chunk.append(item)
            if current_chunk:
                chunks.append(current_chunk)

            # ── Build ngrams within each chunk only ──────────────────────────
            for chunk in chunks:
                for n in ns:
                    for gram in ngrams(chunk, n):
                        # ── Fix 3: drop identical-token bigrams ("time time", "model model") ──
                        if n > 1 and len(set(gram)) == 1:
                            continue

                        gram_str = '_'.join(gram)
                        ngram_counts[gram_str] += 1
                        if gram_str not in ngram_contexts:
                            ngram_contexts[gram_str] = []
                        if len(ngram_contexts[gram_str]) < 2:
                            ngram_contexts[gram_str].append(sent.text.strip()[:500])   #:300
        #--------------------------------------------
        t2 = time.perf_counter()
        #print(f"nlp() inference: {t1-t0:.1f}s | ngram building: {t2-t1:.1f}s")

        # ── Existing filtering logic (unchanged) ──
        unigram_freq = {k: v for k, v in ngram_counts.items() if '_' not in k}
        bigram_freq  = {k: v for k, v in ngram_counts.items() if '_' in k and k.count('_') == 1}
        clean_unigrams = remove_redundant_unigrams(unigram_freq, bigram_freq, threshold=UNIGRAM_COVERAGE_THRESHOLD)


        final_freq = {}
        #final_freq.update(unigram_freq)   # ← add this, bypasses remove_redundant_unigrams entirely
        final_freq.update(bigram_freq)
        final_freq.update(clean_unigrams)
        filtered_freq = {k: v for k, v in final_freq.items() if v >= min_count}


        return filtered_freq, ngram_contexts   # ← now returns two things

    return (get_stemmed_ngram_freqs,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Download and Cache the Data**

    _**Note:**_
    - Web scraping can be slow, and we don't want to rely on the SEC's servers every time we run the notebook.
    - We check if a local file (`risk_data.json`) already exists.
        - If it exists, we load our data from there instantly.
        - If it doesn't (or if we force a refresh), we download the reports and save them into the JSON file for next time.
    """)
    return


@app.cell
def _(force_refresh, get_risk_factors, json, mag7, os, years):
    RISK_DATA_PATH = "public/risk_data.json"

    # --- Step 1: risk_data ---
    if not force_refresh and os.path.exists(RISK_DATA_PATH):
        with open(RISK_DATA_PATH) as f:
            raw = json.load(f)
        # JSON keys are always strings — convert year keys back to int
        risk_data0 = {ticker: {int(y): text for y, text in years.items()} 
                      for ticker, years in raw.items()}
        print(f"✓ Loaded existing risk_data from {RISK_DATA_PATH}")
    else:
        print("Downloading filings (~1-5 min)...")
        risk_data0 = {}
        for ticker, name in mag7.items():
            risk_data0[ticker] = {}
            for y in years:
                text = get_risk_factors(ticker, y)
                risk_data0[ticker][y] = text
            print(f"  ✓ {ticker}")

        os.makedirs("public", exist_ok=True)
        with open(RISK_DATA_PATH, "w") as f:
            json.dump(risk_data0, f)
        print(f"✓ Saved to {RISK_DATA_PATH}")
    return risk_data0, ticker


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Sanity Check: Viewing a Snippet**

    Let's print out the first 1500 characters of Amazon's 2015 Risk Factors to make sure our data looks like readable text instead of jumbled HTML.
    """)
    return


@app.cell
def _(json, risk_data0, textwrap, ticker):

    # Load back risk_data from external file  
    with open("public/risk_data.json") as f2:
        risk_data = json.load(f2)
    # Note: Uses a context manager (with statement), which ensures the file is properly closed after reading, even if an error occurs

    # Show a snippet of Amazon 2015 risk factors
    # JSON keys become strings when saved/loaded
    yr = 2015
    tic = "AMZN"
    ticker_data = risk_data0.get(tic, {})
    snippet_text = ticker_data.get(str(yr)) or ticker_data.get(yr)
    if not snippet_text:
        print(f"No risk factors found for {ticker} {yr}")
    else:
        snippet = snippet_text[:1500]
        print(textwrap.fill(snippet, width=96)) 
    # Adjust width as needed (e.g., 80 for typical editors)
    return (risk_data,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Generating Word Clouds and Top Phrases**

    _**Note:**_
    - Here, we create visual insights. We iterate over the companies and the years (2015 vs 2025).
    - We use a **blacklist** to aggressively filter out "boilerplate" legal phrases that lawyers force companies to include but that don't reveal much about real business risks (e.g., "forward-looking statements", "financial condition").
    - Two pieces of output are generated for each company:
        1. **Side-by-side Word Clouds**: 2015 (Red) vs. 2025 (Blue). Larger text means the phrase was used more frequently.
        2. **Top 20 Phrases Table**: A precise count of the most used phrases, alongside an example sentence showing how it was used in context.
    """)
    return


@app.cell
def _(
    FIRMS2DISPLAY,
    WordCloud,
    get_stemmed_ngram_freqs,
    io,
    mag7,
    mo,
    nlp,
    pd,
    risk_data,
    time,
):
    # ────────────────────────────────────────────────────────────────
    # Side-by-side clouds + Top 20 phrases tables for debugging
    # ────────────────────────────────────────────────────────────────

    outputs =[]
    # Blacklist after stemming (add more as needed)
    blacklist_stem_patterns = {
        # ── existing single-token blacklist ──
        'product', 'service',

        # ── existing bigram blacklist ──
        'subject_to', 
        'unitedstates', 'unitedstates_government',
        'may_result', 'could_adversely', 'would_adversely',
        'adversely_affect', 'negatively_impact', 
        'business_may', 
    #    'adverse_impact',

        # ── boilerplate bigrams (lemmatized, so covers plurals automatically) ──
        'reputation_financial',
        'financial_condition',   # "financial condition/conditions"
    #    'operating_result',      # "operating result/results"
    #    'result_operation',      # "result of operations"
        'table_content',         # "table of contents" → 'of' is a stopword, so becomes table_content
        'table_contents',        
        'risk_factor',           # section header noise
        'forward_look',          # "forward-looking statements"
        'look_statement',        # "forward-looking statements" after lemmatization
        'report_form',         # "annual report on form 10-K"
        'annual_report',
        'vice_president',      # common title, not a risk factor
        'executive_vice',
        'common_stock',
        'per_share',
    #    'share_price',
        }


    elapsed = None
    t00 = time.perf_counter()
    # ────────────────────────────────────────────────────────────────
    for ticker_1, name_1 in list(mag7.items())[:FIRMS2DISPLAY]:  # ← limit to 1 company for now
        cloud_imgs = []
        table_outputs = []

        for year in[2015, 2025]:
            text_1 = risk_data[ticker_1][str(year)]
            # Note: risk_data keys are strings due to prior saving to and loading back from JSON , so we use str(year) here
            if not text_1 or len(text_1.strip()) < 200:
                cloud_imgs.append(mo.md(f"**{year}**: No / insufficient data"))
                continue

            # Unpack both return values
            freq_dict, contexts = get_stemmed_ngram_freqs(text_1, nlp, ns=[1, 2], min_count=3)

            if not freq_dict:
                cloud_imgs.append(mo.md(f"**{year}**: No frequent n-grams"))
                continue

            # Prepare display version + apply final filtering
            display_freq = {}
            top_phrases =[]  # for table
            for stemmed_ngram, count in sorted(freq_dict.items(), key=lambda x: x[1], reverse=True):
                if stemmed_ngram in blacklist_stem_patterns:
                    continue

                parts = stemmed_ngram.split('_')
                if parts[0] in {'product', 'servic', 'busi', 'oper', 'result'} and len(parts) == 2:
                    continue

                readable = ' '.join(parts)
                display_freq[readable] = count

                # Collect top phrases (limit to 20 later)
                example = contexts.get(stemmed_ngram, [""])[0]   # ← extract from contexts here
                top_phrases.append((count, readable, example))    # count first for display


            if not display_freq:
                cloud_imgs.append(mo.md(f"**{year}**: No qualifying phrases"))
                continue

            # Generate word cloud as PIL Image  
            wc = WordCloud(width=600, height=350, background_color='white',
                           colormap='Reds' if year == 2015 else 'Blues',
                           max_words=70, min_font_size=10,
                           prefer_horizontal=0.9).generate_from_frequencies(display_freq)

            buf = io.BytesIO()
            wc.to_image().save(buf, format='PNG', optimize=True, compress_level=9)
            buf.seek(0)

            cloud_imgs.append(mo.vstack([
                mo.md(f"**{year}**"),
                mo.image(buf.getvalue())
            ]))

            # ─── Top 20 table (right next to / below cloud in Colab output) ───
            top_20 = top_phrases[:20]
            if top_20:
                df_top = pd.DataFrame(top_20, columns=['Count', 'Phrase', 'Example'])
                table_outputs.append(mo.vstack([
                    mo.md(f"**Top 20 – {name_1} ({ticker_1}) {year}**"),
                    mo.ui.table(df_top)
                ]))

        outputs.append(mo.md(f"### {name_1} ({ticker_1}) – Risk Factors 2015 vs 2025"))
        outputs.append(mo.hstack(cloud_imgs, justify='start'))
        outputs.extend(table_outputs)
        outputs.append(mo.md("---"))

    elapsed = time.perf_counter() - t00
    print(f"NLP pipeline completed in {elapsed:.1f}s")

    mo.vstack(outputs)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    """)
    return


if __name__ == "__main__":
    app.run()
