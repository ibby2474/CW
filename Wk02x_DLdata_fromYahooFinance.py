# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.19.0",
#     "pandas>=2.3.3",
#     "plotly>=6.5.0",
#     "pyzmq>=27.1.0",
#     "yahooquery>=2.4.1",
#     "yfinance>=1.0",
# ]
# ///

import marimo

__generated_with = "0.19.7"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    **Note:**

    - To create a new marimo notebook in Codespaces / VS Code, use the command palette (`Ctrl + Shift + P` or `Cmd + Shift + P`) and select `Create: New marimo notebook`".
        - This will open a new marimo notebook where you can start writing and executing your code.
    - To execute a code cell in a marimo notebook, a kernel must have been selected first.
        - Select a kernel by clicking on the `Select Kernel` button in the top right corner of the marimo notebook and choose `marimo sandbox` from the dropdown list.
    - If you are annoyed by inlay hints, such as type annotations (e.g., `: str`), displayed inline in the editor, this can be turned off by setting `editor.inlayHints.enabled` in Codespaces's Settings to `offUnlessPressed` (`Ctrl + Alt`)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## Download **Panel Data** (with Multiple Companies over Multiple Years)

    - Panel data vs.
        - Cross-sectional data
        - Time-series data
    """)
    return


@app.cell
def _():
    # Import necessary libraries

    import marimo as mo        # for interacting with Marimo API
    import pandas as pd      # for storing fetched data in DataFrame
    return mo, pd


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### Fetch **year-specific S&P 500** tickers

    - Open-source data of year-specific S&P 500 constituents:
        - **Option 1** - https://github.com/fja05680/sp500
        - Option 2 - https://github.com/hanshof/sp500_constituents
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### Set parameters for download period
    """)
    return


@app.cell
def _():
    # Only last 4/5 years of data are freely available on Yahoo Finance
    # (required paid subscription for earlier years)
    yearStart = 2021   
    yearEnd = 2025     

    # Fixed list of years we want (annual data for fiscal years ending in these calendar years)
    yearRange = list(range(yearStart, yearEnd + 1))  
    return (yearRange,)


@app.cell
def _(mo):
    mo.md(r"""
    #### Construct URL for fetching year-specific S&P 500 tickers
    """)
    return


@app.cell
def _():

    import requests
    import re

    # 1. List files in the repo directory using GitHub API
    api_url = "https://api.github.com/repos/fja05680/sp500/contents/"
    resp = requests.get(api_url)
    resp.raise_for_status()
    files = resp.json()

    # 2. Find all matching CSVs and extract dates
    pattern = re.compile(r"S&P 500 Historical Components & Changes\((\d{2}-\d{2}-\d{4})\)\.csv")
    latest_date = None
    latest_file = None

    for f in files:
        m = pattern.match(f["name"])
        if m:
            file_date = m.group(1)
            # Convert MM-DD-YYYY to tuple for comparison
            dt_tuple = tuple(map(int, file_date.split('-')[::-1]))  # (YYYY, MM, DD)
            if (latest_date is None) or (dt_tuple > latest_date):
                latest_date = dt_tuple
                latest_file = f["name"]

    if not latest_file:
        raise RuntimeError("No matching S&P 500 CSV file found in the repo.")

    # 3. Construct the raw URL
    from urllib.parse import quote
    hist_url = (
        "https://raw.githubusercontent.com/fja05680/sp500/master/"
        + quote(latest_file)
    )
    return (hist_url,)


@app.cell
def _(mo):
    mo.md(r"""
    #### Fetch historical constituents data
    """)
    return


@app.cell
def _(hist_url, pd, yearRange):
    hist_df = pd.read_csv(hist_url)

    # The CSV has columns: 'date' (YYYY-MM-DD) and 'tickers' (comma-separated string of symbols)
    hist_df['date'] = pd.to_datetime(hist_df['date'])
    print(f"Loaded historical constituents with {len(hist_df)} snapshot dates")

    # Pre-process: split tickers and fix formatting (e.g., BRK.B -> BRK-B)
    def clean_tickers(ticker_str):
        ticks = [t.strip().replace('.', '-') for t in ticker_str.split(',')]
        return sorted(ticks)  # Optional: sort for consistency

    hist_df['tickers_list'] = hist_df['tickers'].apply(clean_tickers)

    # For each year, select constituents as of December 31 (or closest prior date)
    tickers_per_year = {}
    for year in yearRange:

        target_date0 = pd.Timestamp(f"{year}-12-31")

        # Find the row with the latest date <= target_date0
        valid_rows = hist_df[hist_df['date'] <= target_date0]
        if valid_rows.empty:
            print(f"No constituent data available on or before {year}-12-31")
            tickers_per_year[year] = []
            continue

        latest_row = valid_rows.iloc[-1]
        tickers_per_year[year] = latest_row['tickers_list']
        print(f"{year}: {len(tickers_per_year[year])} constituents (as of {latest_row['date'].date()})")
    return (tickers_per_year,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### Fetch **accounting and stock data** from Yahoo Finance for year-specific S&P500 stocks

    - Open-source packages to access Yahoo Finance data:
        - **yfinance**
        - yahooquery
    """)
    return


@app.cell
def _():
    import yfinance as yf   # for fetching data from Yahoo Finance
    import time             # for adding delays between requests (to respect rate limits)
    return time, yf


@app.cell
def _(mo):
    mo.md(r"""
    _**Note:**_

    - Can use comment indicators (`#`) to disable temporary code used for testing. For example,

    ```python
    for ticker in tickers_for_year[:5]:  # Limit to first 5 tickers for testing
    ```

    &emsp; **versus**

    ```python
    for ticker in tickers_for_year:#[:5]:  # Restriction to first 5 tickers disabled
                                           # (must also add back the trailing colon in the original code)
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    #### Code logic summary

    _**Highlights:**_

    - **Nested `for`-loop** structure
    - **`try`-and-`except`** for exception handling
    - `time.sleep` to respect Yahoo Finance's **rate limits** for free, fair use

    ```python

    # 1. OUTER LOOP: Iterate through the years
    for year_int in yearRange:

        # ... Setup target date (Dec 31 of current loop year) ...
        # ... Get list of tickers available for this specific year ...

        # 2. INNER LOOP: Iterate through the tickers (limit 5)
        for ticker in tickers_for_year[:5]:

            try:
                # A. Fetch Financial Data
                # Initialize yfinance Ticker object
                # Select Balance Sheet/Income Statement columns closest to target_date

                # B. Extract Metrics
                # Parse variables: Assets, Liabilities, EBIT, Revenue, Sector/Industry keys

                # C. Determine Fiscal Year
                # Extract the report year from the balance sheet column name

                # D. Conditional Market Data Logic
                # ONLY proceed if the report's fiscal year matches the Loop Year
                if report_year == year_int:
                    # Fetch historical stock price data for this year
                    # Calculate Market_Cap (Shares * Closing_Price)

                # E. Store Data
                # Append row ONLY if report year matches and Total Assets > 0
                if report_year == year_int and total_assets_valid:
                    raw_rows.append({
                        "Ticker": ticker,
                        "Year": year_int,
                        "Financials": [Assets, Debt, EBIT, Sales, etc.],
                        "Market_Data": [Market_Cap, Closing_Price],
                        "Metadata": [Sector_Key, Industry_Key]
                    })

            except Exception:
                # Handle errors (e.g., missing data, network issues)
                pass

            # Brief sleep (throttle requests)
            time.sleep(0.05)

        # Longer sleep between years
        time.sleep(1)
    ```

    ---
    """)
    return


@app.cell
def _(pd, tickers_per_year, time, yearRange, yf):
    # Initialize the list to hold all rows
    raw_rows = []

    # Outer loop: Years
    for year_int in yearRange:

        year_str = str(year_int)
        print(f"\nProcessing year: {year_int}")

        tickers_for_year = tickers_per_year.get(year_int, [])
        if not tickers_for_year:
            print("  No tickers available for this year – skipping")
            continue

        target_date = pd.Timestamp(f"{year_int}-12-31")

        for ticker in tickers_for_year[:5]:  # Limit to first 5 tickers for testing
            #print(f"\n  Fetching data for {ticker}...", end=' ')

            try:
                stock = yf.Ticker(ticker)

                def _select_series_for_date(df, target_date):
                    if df is None or df.empty:
                        return None
                    try:
                        col_dates = pd.to_datetime(df.columns.astype(str), errors="coerce")
                        valid = col_dates[col_dates <= target_date]
                        if not valid.empty:
                            chosen = valid.max()
                            col_label = df.columns[(col_dates == chosen)][0]
                            return df[col_label]
                    except Exception:
                        pass
                    # fallback to most recent column if no match or on error
                    try:
                        return df.iloc[:, 0]
                    except Exception:
                        return None

                # Define objects to fetch balance-sheet and income-statement financials  
                balance_sheet = _select_series_for_date(getattr(stock, "balance_sheet", None), target_date)
                income_stmt = _select_series_for_date(getattr(stock, "income_stmt", None), target_date)


                def _get_numeric(series, key):
                    if series is None:
                        return None
                    v = series.get(key)
                    # unwrap accidental single-element tuples/lists
                    if isinstance(v, (tuple, list)) and len(v) == 1:
                        v = v[0]
                    # handle numpy scalars / pandas NA
                    try:
                        if pd.isna(v):
                            return None
                    except Exception:
                        pass
                    try:
                        return float(v)
                    except Exception:
                        return None

                # usage (after selecting the correct column into `balance_sheet` / `income_stmt`)
                total_assets = _get_numeric(balance_sheet, "Total Assets")
                current_assets = _get_numeric(balance_sheet, "Current Assets")
                current_liab = _get_numeric(balance_sheet, "Current Liabilities")
                retained_earnings = _get_numeric(balance_sheet, "Retained Earnings")
                total_liab = _get_numeric(balance_sheet, "Total Liabilities Net Minority Interest")
                total_debt = _get_numeric(balance_sheet, "Total Debt")
                common_shares_outstanding = _get_numeric(balance_sheet, "Ordinary Shares Number")

                ebit = _get_numeric(income_stmt, "EBIT")
                sales = _get_numeric(income_stmt, "Total Revenue")
                int_exp = _get_numeric(income_stmt, "Interest Expense") or 0.0


                # NEW: SectorKey and IndustryKey (machine-friendly, no spaces)
                sector_key = None
                industry_key = None
                try:
                    info = stock.info
                    short_name = info.get('shortName', 'N/A')
                    sector_key = info.get('sectorKey')
                    industry_key = info.get('industryKey')
                except Exception as e:
                    print(f"    Warning: Failed to get shortName/sectorKey/industryKey for {ticker}: {e}")


                # NEW: Fiscal year-end date for the selected financials
                fiscal_year_end_date = None
                report_year = None
                if balance_sheet is not None and not balance_sheet.empty:
                    try:
                        fiscal_year_end_date = balance_sheet.name.date()
                        report_year = balance_sheet.name.year
                    except Exception:
                        pass

                # STRICT: Only process if the selected report's fiscal year matches the loop year_int
                market_cap = None
                close_price = None
                close_price_date = None
                #shares = None

                if report_year == year_int and fiscal_year_end_date is not None:
                    # Only now proceed with shares and price alignment
                    price_target = pd.Timestamp(fiscal_year_end_date)
                    price_target_naive = price_target.tz_localize(None)

                    if common_shares_outstanding is not None and common_shares_outstanding > 0:
                        try:
                            start_date = f"{year_int}-01-01"
                            end_date = f"{year_int + 1}-03-31"

                            hist = stock.history(start=start_date, end=end_date, interval="1d")

                            if not hist.empty:
                                hist_index = hist.index.tz_localize(None)
                                hist_up_to_target = hist[hist_index <= price_target_naive]
                                if not hist_up_to_target.empty:
                                    close_price = hist_up_to_target['Close'].iloc[-1]
                                    close_price_date = hist_up_to_target.index[-1].date()
                                    market_cap = common_shares_outstanding * close_price
                        except Exception as e:
                            print(f"    Warning: Price history failed for {ticker} {year_int}: {e}")
                # Else: report_year != year_int → leave all as None (no data for this year)

                # append the row if data is available for this year
                if (report_year == year_int and 
                    total_assets is not None and 
                    total_assets > 0   # Z-Score components require Total Assets > 0
                    ):
                    raw_rows.append({
                        "Ticker": ticker,
                        "Year": year_int,
                        "Fiscal_Year_End": fiscal_year_end_date,
                        "Name": short_name,
                        "Sector_Key": sector_key,
                        "Industry_Key": industry_key,
                        "Total_Assets": total_assets if report_year == year_int else None,
                        "Current_Assets": current_assets if report_year == year_int else None,
                        "Current_Liab": current_liab if report_year == year_int else None,
                        "Retained_Earnings": retained_earnings if report_year == year_int else None,
                        "Total_Liab": total_liab if report_year == year_int else None,
                        "Total_Debt": total_debt if report_year == year_int else None,
                        "Shares_Number": common_shares_outstanding if report_year == year_int else None,
                        "EBIT": ebit if report_year == year_int else None,
                        "Sales": sales if report_year == year_int else None,
                        "Int_Exp": int_exp if report_year == year_int else None,
                        "Market_Cap": market_cap,
                        "Closing_Price": close_price,
                        "Closing_Price_Date": close_price_date
                    })

            except Exception as e:
                print(f"  Error for {ticker} in {year_int}: {e}")

            time.sleep(0.05)

        time.sleep(1)
    return (raw_rows,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    #### What does `pd.to_datetime` do in this command?

    ```python
    col_dates = pd.to_datetime(df.columns.astype(str), errors="coerce")
    ```

    - What does `errors="coerce"` do in the command?
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    \* Hidden **content** here (_**double-click**_ to view; _**uncomment**_ the lines to reveal them permanently).

    <!--
    - `pd.to_datetime` tries to convert each value in `df.columns` (after converting them to strings) into a pandas datetime object.
        - The result, `col_dates`, is a sequence of datetime objects (or `NaT` for failed conversions).
        - If a value cannot be converted to a datetime, it is replaced with `NaT` ("Not a Time") instead of raising an error.
        - This makes the conversion process robust to invalid or unexpected column names.

    _**Follow-up question:**_


    - _What does `df.columns` mean?_
        - `df.columns` returns the column labels (names) of the DataFrame `df` as a pandas Index object. It lists all the column names in the order they appear in the DataFrame.
      -->

    ---
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### Display the fetched data as a pandas dataframe
    """)
    return


@app.cell
def _(pd, raw_rows):
    df_raw = pd.DataFrame(raw_rows)
    df_raw
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### Save fetched data to a `.csv` file for future access (`sp500_raw_data.csv`)
    """)
    return


@app.cell
def _():
    """

    # Save fetched data to a .csv file
    df_raw.to_csv("sp500_raw_data.csv", index=False)

    print("\nData saved to sp500_raw_data.csv")
    print(f"Total records collected: {len(df_raw)}")

    """
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    _**Note:**_

    - It took over 30 minutes for `yfinance` to fetch completely the historical data of S&P 500 companies from 2021 to 2025 (saved as `sp500_raw_data.csv`)
    - A copy of the data has been saved as _**`sp500_raw_data_Backup.csv`**_ to prevent the data from being overwritten by only a slice of it during the demonstration of the sliced download for testing:
    ```python
        for ticker in tickers_for_year[:5]:  # Limit to first 5 tickers for testing
    ```
    """)
    return


if __name__ == "__main__":
    app.run()
