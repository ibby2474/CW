# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "marimo>=0.19.10",
#   "pandas>=2.3.3",
#   "plotly>=6.5.1",
#   "numpy>=1.26.0",
#   "pyzmq>=27.1.0",
#   "yfinance>=0.2.66",
#   "requests>=2.31.0",
#   "micropip",
# ]
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


# ── NOTE cell (mirrors the note at the top of every Moodle notebook) ─────────
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


# ── Title / intro markdown ────────────────────────────────────────────────────
@app.cell
def _(mo):
    mo.md(r"""
    ---

    # 🌿 Personal Portfolio Webpage

    Combine everything learned across **Weeks 1–10** into a multi-tabbed webpage featuring:

    - An **About Me** section with skills and technical journey
    - A live **Altman Z-Score** calculator (Week 2)
    - An interactive **ESG & Credit Risk Dashboard** (Week 4)
    - A **Web Scraping Pipeline** explainer (Weeks 6–7)
    - A **LLM-powered ESG Disclosure Analyser** (Week 9)
    - An **NLP / SEC 10-K** risk-language analysis (Week 10)
    - An **Econometrics** panel regression summary (self-exploration, R)

    ---
    """)
    return


# ── Section 1: Imports ────────────────────────────────────────────────────────
@app.cell
def _(mo):
    mo.md(r"""
    #### 1. **Load** Libraries
    """)
    return


@app.cell
def _():
    # Import necessary libraries
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import numpy as np
    import os
    import json
    import requests
    import micropip
    import warnings
    warnings.filterwarnings("ignore")
    return mo, pd, px, go, np, os, json, requests, micropip


# ── Section 2: Load Data ──────────────────────────────────────────────────────
@app.cell
def _(mo):
    mo.md(r"""
    #### 2. **Load** Data
    """)
    return


@app.cell
def _(pd):
    # Load the S&P 500 Z-Score and average cost of debt dataset
    # This is the same dataset used in Wk04w_Dashboard_Moodle.py
    csv_url = "https://gist.githubusercontent.com/DrAYim/80393243abdbb4bfe3b45fef58e8d3c8/raw/ed5cfd9f210bf80cb59a5f420bf8f2b88a9c2dcd/sp500_ZScore_AvgCostofDebt.csv"
    df_final = pd.read_csv(csv_url)

    # Drop rows with missing values in the key columns
    df_final = df_final.dropna(subset=['AvgCost_of_Debt', 'Z_Score_lag', 'Sector_Key'])

    # Filter outliers to reduce distortion in visualisations
    # (AvgCost_of_Debt values above 5 represent implausible rates above 500%)
    df_final = df_final[(df_final['AvgCost_of_Debt'] < 5)]

    # Convert cost of debt from decimal to percentage for readability
    df_final['Debt_Cost_Percent'] = df_final['AvgCost_of_Debt'] * 100

    # Convert Market Cap to billions for easier reading on the slider
    df_final['Market_Cap_B'] = df_final['Market_Cap'] / 1e9

    print(f"Data loaded: {len(df_final)} observations across {df_final['Sector_Key'].nunique()} sectors.")
    df_final
    return (df_final,)


# ── Section 3: UI Controls ────────────────────────────────────────────────────
@app.cell
def _(mo):
    mo.md(r"""
    #### 3. Create **UI Controls**
    """)
    return


@app.cell
def _(df_final, mo):
    # Dropdown to filter by sector (mirrors Wk04w and Wk04x)
    all_sectors = sorted(df_final['Sector_Key'].unique().tolist())
    sector_dropdown = mo.ui.multiselect(
        options=all_sectors,
        value=all_sectors[:3],  # Default to first 3 sectors
        label="Filter by Sector",
    )

    # Slider to filter by minimum market cap (mirrors Wk04x)
    cap_slider = mo.ui.slider(
        start=0,
        stop=200,
        step=10,
        value=0,
        label="Min Market Cap ($ Billions)"
    )

    # Text input for the Z-Score ticker (mirrors Wk02_Marimo_ZScore.py)
    ticker_input = mo.ui.text(value="MSFT", label="Enter US Ticker:")

    # Text area for ESG disclosure text (Week 9 LLM feature)
    esg_text_input = mo.ui.text_area(
        value=(
            "Our company has made significant progress on our net-zero pathway. "
            "Scope 1 and Scope 2 emissions decreased by 18% year-on-year, "
            "primarily driven by the transition to renewable electricity across all "
            "manufacturing sites. Water withdrawal intensity improved by 12%. "
            "However, supply chain (Scope 3) emissions remain a challenge and "
            "constitute 78% of our total carbon footprint. We have engaged with "
            "our top 50 suppliers on science-based targets."
        ),
        label="Paste ESG Disclosure Text:",
        rows=5,
    )

    # API key input for Groq LLM (Week 9 — get free key at console.groq.com)
    groq_key_input = mo.ui.text(
        value="",
        label="Groq API Key (console.groq.com):",
        kind="password",
    )

    # Button to trigger LLM analysis (mirrors button patterns in Wk04x)
    analyse_btn = mo.ui.button(label="🔍 Analyse with LLM", kind="success")

    mo.hstack([sector_dropdown, cap_slider], justify="start", gap=4)
    return (
        all_sectors,
        sector_dropdown,
        cap_slider,
        ticker_input,
        esg_text_input,
        groq_key_input,
        analyse_btn,
    )


# ── Section 4: Filter Data Reactively ────────────────────────────────────────
@app.cell
def _(mo):
    mo.md(r"""
    #### 4. Set Selector to **Filter Data Reactively** (`.isin(sector_dropdown.value)`)
    """)
    return


@app.cell
def _(df_final, sector_dropdown, cap_slider):
    # This cell re-runs automatically when the user changes the selector or slider
    filtered_portfolio = df_final[
        (df_final['Sector_Key'].isin(sector_dropdown.value)) &
        (df_final['Market_Cap_B'] >= cap_slider.value)
    ]

    # Calculate summary metrics for the dashboard
    count        = len(filtered_portfolio)
    avg_esg      = filtered_portfolio['Debt_Cost_Percent'].mean()
    avg_z        = filtered_portfolio['Z_Score_lag'].mean()
    max_drawdown = filtered_portfolio['Debt_Cost_Percent'].max()

    return filtered_portfolio, count, avg_esg, avg_z, max_drawdown


# ── Section 5: Z-Score Function ───────────────────────────────────────────────
@app.cell
def _(mo):
    mo.md(r"""
    #### 5. Define **Z-Score** Function (from Week 2)
    """)
    return


@app.cell
def _():
    # Define the ZScore function with exception handling (from Wk02_Marimo_ZScore.py)
    # Uses try/except to return NaN when total_liab = 0, avoiding ZeroDivisionError
    def ZScore(total_assets, current_assets, current_liab,
               retained_earnings, ebit, total_liab, sales, market_cap):
        try:
            WkCap2TA  = (current_assets - current_liab) / total_assets
            RE2TA     = retained_earnings / total_assets
            EBIT2TA   = ebit / total_assets
            preferred_market_cap = 0  # assuming no preferred stock
            MVofStock2BVofTL = (market_cap + preferred_market_cap) / total_liab
            Sales2TA  = sales / total_assets
            ZScore    = (1.2 * WkCap2TA + 1.4 * RE2TA + 3.3 * EBIT2TA
                         + 0.6 * MVofStock2BVofTL + 1.0 * Sales2TA)
        except ZeroDivisionError:
            return float('nan')
        return ZScore
    return (ZScore,)


# ── Section 6: Fetch Z-Score live from Yahoo Finance ─────────────────────────
@app.cell
def _(mo):
    mo.md(r"""
    #### 6. Fetch **Live Data** from Yahoo Finance and Compute Z-Score
    """)
    return


@app.cell
def _(ticker_input, ZScore, mo):
    # This cell re-runs automatically when ticker_input changes (reactive)
    # Mirrors the live-fetch pattern from Wk02_Marimo_ZScore.py
    import yfinance as yf

    ticker  = ticker_input.value
    stock   = yf.Ticker(ticker)
    balance_sheet = stock.balance_sheet.iloc[:, 0]
    income_stmt   = stock.income_stmt.iloc[:, 0]

    def _get(series, key):
        v = series.get(key)
        try:
            return float(v) if v is not None else 0.0
        except Exception:
            return 0.0

    z_score = ZScore(
        total_assets      = _get(balance_sheet, 'Total Assets'),
        current_assets    = _get(balance_sheet, 'Current Assets'),
        current_liab      = _get(balance_sheet, 'Current Liabilities'),
        retained_earnings = _get(balance_sheet, 'Retained Earnings'),
        ebit              = _get(income_stmt,   'EBIT'),
        total_liab        = _get(balance_sheet, 'Total Liabilities Net Minority Interest'),
        sales             = _get(income_stmt,   'Total Revenue'),
        market_cap        = stock.info.get('marketCap', 0),
    )

    # Classify Z-Score into Safe / Grey / Distress zone (mirrors Wk02)
    if z_score > 2.99:
        status = "SAFE ZONE"
        color  = "green"
    elif z_score >= 1.81:
        status = "GREY ZONE (Caution)"
        color  = "grey"
    else:
        status = "DISTRESS ZONE"
        color  = "red"

    mo.md(f"""
    ## Ticker: {ticker}
    ### Z-Score: **{z_score:.2f}**
    ### Status: <span style='color:{color}'>{status}</span>
    """)
    return ticker, z_score, status, color, stock, balance_sheet, income_stmt


# ── Section 7: Dashboard Plots ────────────────────────────────────────────────
@app.cell
def _(mo):
    mo.md(r"""
    #### 7. Create the **Interactive Plots** on the Dashboard
    """)
    return


@app.cell
def _(filtered_portfolio, count, px, go, np, mo):
    import textwrap

    # ── Plot 1: Scatter — Z-Score (lagged) vs Average Cost of Debt ──────────
    # Mirrors the main chart in Wk04w_Dashboard_Moodle.py
    title = "Are higher Z-Scores last year associated with lower average costs of debt this year?"
    wrapped_title = "<br>".join(textwrap.wrap(title, width=50))

    fig_scatter = px.scatter(
        filtered_portfolio,
        x='Z_Score_lag',
        y='Debt_Cost_Percent',
        range_x=[-5, 20],
        range_y=[-1, 15],
        color='Sector_Key',
        size='Market_Cap_B',
        hover_name='Name',
        hover_data=['Ticker'],
        title=wrapped_title,
        labels={
            'Z_Score_lag':       'Altman Z-Score (lagged)',
            'Debt_Cost_Percent': 'Avg. Cost of Debt (%)'
        },
        template='presentation',
        width=900,
        height=600,
    )

    # Add distress threshold line at Z-Score = 1.81 (mirrors Wk04w)
    fig_scatter.add_vline(
        x=1.81, line_dash="dash", line_color="red",
        annotation=dict(
            text="Distress Threshold (Z-Score = 1.81)",
            font=dict(color="red"),
            x=1.5, xref="x",
            y=1.07, yref="paper",
            showarrow=False, yanchor="top"
        )
    )

    # Add safe threshold line at Z-Score = 2.99
    fig_scatter.add_vline(
        x=2.99, line_dash="dash", line_color="green",
        annotation=dict(
            text="Safe Threshold (Z-Score = 2.99)",
            font=dict(color="green"),
            x=3.10, xref="x",
            y=1.02, yref="paper",
            showarrow=False, yanchor="top"
        )
    )

    # Add OLS regression line (mirrors Wk04w_Dashboard_Moodle.py regression block)
    df_regline = filtered_portfolio[filtered_portfolio['Debt_Cost_Percent'] < 5]
    if not df_regline.empty:
        x_vals = df_regline['Z_Score_lag'].astype(float)
        y_vals = df_regline['Debt_Cost_Percent'].astype(float)
        slope, intercept = np.polyfit(x_vals, y_vals, 1)
        x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
        y_line = intercept + slope * x_line
        line_trace = px.line(x=x_line, y=y_line).data[0]
        line_trace.update(line=dict(width=0.5, color='black'))
        fig_scatter.add_trace(line_trace)

    fig_scatter.update_layout(title=dict(y=0.97, x=0, xanchor='left'))

    print(" ")  # Prevents the plot appearing before the dashboard layout cell
    return fig_scatter, count, wrapped_title


@app.cell
def _(filtered_portfolio, px, mo):
    # ── Plot 2: Bar chart — average cost of debt by sector ───────────────────
    sector_avg = (
        filtered_portfolio
        .groupby('Sector_Key')['Debt_Cost_Percent']
        .mean()
        .reset_index()
        .sort_values('Debt_Cost_Percent')
    )

    fig_bar = px.bar(
        sector_avg,
        x='Debt_Cost_Percent',
        y='Sector_Key',
        orientation='h',
        title="Average Cost of Debt by Sector (%)",
        labels={
            'Debt_Cost_Percent': 'Avg. Cost of Debt (%)',
            'Sector_Key':        ''
        },
        template='presentation',
        width=900,
        height=420,
        color='Debt_Cost_Percent',
        color_continuous_scale='RdYlGn_r',
    )
    fig_bar.update_layout(
        coloraxis_showscale=False,
        title=dict(y=0.97, x=0, xanchor='left')
    )

    print(" ")
    return (fig_bar,)


@app.cell
def _(ticker_input, z_score, mo, px, pd):
    # ── Plot 3: Z-Score gauge bar (mirrors Wk02_Marimo_ZScore.py Altair gauge) ─
    _ticker = ticker_input.value

    _df_gauge = pd.DataFrame({'Score': [z_score], 'Label': [_ticker]})
    _df_gauge['Color'] = _df_gauge['Score'].apply(
        lambda s: 'red' if s < 1.81 else ('grey' if s <= 2.99 else 'green')
    )

    fig_gauge = px.bar(
        _df_gauge,
        x='Score',
        y='Label',
        orientation='h',
        color='Color',
        color_discrete_map={'red': '#e74c3c', 'grey': '#95a5a6', 'green': '#2ecc71'},
        range_x=[0, 12],
        title=f"Altman Z-Score Gauge — {_ticker}",
        labels={'Score': 'Altman Z-Score', 'Label': ''},
        template='presentation',
        width=700,
        height=160,
    )

    # Threshold lines
    fig_gauge.add_vline(x=1.81, line_dash="dash", line_color="red")
    fig_gauge.add_vline(x=2.99, line_dash="dash", line_color="green")

    fig_gauge.update_layout(
        showlegend=False,
        title=dict(y=0.97, x=0, xanchor='left')
    )

    print(" ")
    return (fig_gauge,)


# ── Section 8: LLM Analysis Function ─────────────────────────────────────────
@app.cell
def _(mo):
    mo.md(r"""
    #### 8. Define **LLM Analysis** Function (Week 9 — Groq API)
    """)
    return


@app.cell
def _(requests, json):
    # This function calls the Groq LLM API with a prompt-engineered request
    # and parses the structured JSON response — mirrors the API call pattern
    # from Wk9_LLM_API_Moodle.ipynb

    def run_llm_analysis(api_key, esg_text):
        """Send an ESG disclosure passage to the Groq LLM and return structured analysis."""

        if not api_key.strip():
            return None, "no_key"

        # Prompt engineering: instruct the model to return structured JSON only
        prompt = f"""You are a senior ESG analyst at a sustainable-finance firm.
Analyse the following corporate ESG disclosure passage and return a JSON object with exactly these keys:
- "sentiment": one of [Positive, Mixed, Negative]
- "credibility": one of [High, Medium, Low] — based on specificity of metrics provided
- "key_topics": list of up to 5 topic strings (e.g. "Scope 3 emissions", "water intensity")
- "red_flags": list of up to 3 potential greenwashing or data-quality concerns (empty list if none)
- "analyst_summary": 2-3 sentence plain-English summary suitable for an ESG investment report

Passage:
\"\"\"{esg_text}\"\"\"

Return ONLY valid JSON, no markdown fences, no preamble."""

        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key.strip()}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama3-8b-8192",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 600,
                },
                timeout=20,
            )
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"].strip()

            # Strip markdown fences if the model adds them despite instructions
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            data = json.loads(raw)
            return data, "ok"

        except requests.exceptions.HTTPError as e:
            return None, f"http_error: {e}"
        except json.JSONDecodeError:
            return None, f"json_error: {raw}"
        except Exception as e:
            return None, f"error: {e}"

    return (run_llm_analysis,)


# ── Section 9: Dashboard Layout ───────────────────────────────────────────────
@app.cell
def _(mo):
    mo.md(r"""
    #### 9. Define the **Dashboard / Portfolio Layout** (using `mo.md()` and `mo.ui.tabs`)

    - Try changing the **sector** dropdown or the **market cap** slider to filter the visualisations
    - Switch the **ticker** input to compare Z-Scores across companies
    - Enter a **Groq API key** and paste an ESG disclosure to get an AI-powered analysis
    """)
    return


@app.cell
def _(
    mo,
    sector_dropdown, cap_slider,
    ticker_input, z_score, status, color,
    fig_scatter, fig_bar, fig_gauge,
    esg_text_input, groq_key_input, analyse_btn,
    run_llm_analysis,
    count, avg_esg, avg_z,
):
    # ── Tab 1: About Me ───────────────────────────────────────────────────────
    tab_about = mo.md(f"""
## 👤 About Me

**Name:** Alex Morgan
**Degree:** BSc Accounting & Finance — Bayes Business School
**Year:** 2nd Year

---

I am a second-year Accounting & Finance student with a passion for applying data science
to sustainability and ESG challenges. Through this module I have built end-to-end analytical
pipelines — from live market data retrieval and interactive dashboards, to web scraping
corporate sustainability reports and interrogating them with large language models.

My goal is to join a sustainable-finance team where quantitative rigour and environmental
insight go hand in hand.

---

### 🛠️ Technical Skills

**Core (Weeks 1–4)**

| Skill | Tool |
| :--- | :--- |
| Python Fundamentals | Variables, loops, functions, exception handling |
| Financial Data | `yfinance`, Yahoo Finance API |
| Visualisation | `plotly.express`, `plotly.graph_objects`, Altair |
| Reactive Notebooks | Marimo — `mo.ui`, `mo.md`, reactive cells |
| Dashboards | Multi-tab apps, scatter, bar, heatmap, candlestick |

**Advanced (Weeks 6–10 + Self-Exploration)**

| Skill | Tool |
| :--- | :--- |
| Web Scraping | Playwright async, shadow DOM, bot-detection evasion |
| PDF Processing | PyMuPDF, keyword extraction, Tesseract OCR |
| NLP | spaCy transformer, bigram frequency, word clouds |
| LLM Integration | Groq API, prompt engineering, structured JSON output |
| Econometrics | R, `stargazer`, OLS with industry + year fixed effects |

---

### 📅 Technical Journey

**Week 1** — Python Foundations in Jupyter
Variables, loops, functions, `try`/`except`, f-strings — the building blocks of every subsequent notebook.

**Week 2** — Live Financial Analysis — Altman Z-Score
Fetched real balance-sheet data via `yfinance` and built a reactive Z-Score tool with colour-coded health zones and an Altair gauge chart.

**Week 3** — Interactive Visualisation with Plotly
Candlestick charts, heatmaps, violin plots — turning raw S&P 500 data into storytelling dashboards.

**Week 4** — Dashboard & Portfolio App
Multi-tab Marimo app with reactive sector filtering, OLS regression overlays, and a travel-map hobbies tab — exported as a static HTML-WASM page to GitHub Pages.

**Weeks 6–7** — Web Scraping & PDF Pipeline
Playwright headless Chromium with Akamai evasion via `curl`, PyMuPDF keyword extraction page-by-page, Tesseract OCR fallback for scanned PDFs, and a persistent download ledger (`df_DL.csv`).

**Week 9** — LLM API Integration
Connected to Groq's ultra-fast inference API. Prompt-engineered requests return structured JSON: sentiment, credibility, key topics, red flags, and an analyst summary.

**Week 10** — NLP on SEC 10-K Filings
spaCy transformer model (GPU/CPU), bigram extraction with conjunction-boundary splitting, redundant-unigram filtering (90% coverage threshold), and word clouds comparing Mag-7 risk language in 2015 vs 2025.

**Self-Exploration** — ESG Regression in R
OLS panel regressions of ESG scores on Tobin's Q with industry + year fixed effects. Robustness checks across two ESG providers using `stargazer` in R Markdown.
    """)

    # ── Tab 2: Z-Score Tool ───────────────────────────────────────────────────
    tab_zscore = mo.md(f"""
## 📈 Altman Z-Score Analyser (Week 2)

The **Altman Z-Score** combines five financial ratios into a single bankruptcy-risk metric.
Values above **2.99** indicate a safe zone; below **1.81** signals financial distress.
This tool fetches live data from Yahoo Finance via `yfinance`, reflecting Week 2 skills.

---

{ticker_input}

---

## Ticker: {ticker_input.value}
### Z-Score: **{z_score:.2f}**
### Status: <span style='color:{color}'>{status}</span>

{mo.as_html(fig_gauge)}

---

*Switch the ticker above to compare companies — the gauge and status update reactively.*
    """)

    # ── Tab 3: ESG Dashboard ──────────────────────────────────────────────────
    tab_dashboard = mo.md(f"""
## 🌿 ESG & Credit Risk Dashboard (Week 4)

This dashboard explores whether companies with higher **Altman Z-Scores** last year
are associated with **lower average costs of debt** this year — a key question in
credit-risk and ESG analysis. Mirrors `Wk04w_Dashboard_Moodle.py`.

---

{sector_dropdown}

{cap_slider}

---

## Key Metrics

| Companies Analysed | Avg. Cost of Debt | Avg. Z-Score (lagged) |
| :---: | :---: | :---: |
| **{count}** | **{avg_esg:.2f}%** | **{avg_z:.2f}** |

---

## 1. Z-Score vs Cost of Debt

*Green bars = positive months; red = negative. Black dashed line = OLS regression trend.*
*Distress threshold (red dashed) at Z = 1.81; Safe threshold (green dashed) at Z = 2.99.*

{mo.as_html(fig_scatter)}

---

## 2. Average Cost of Debt by Sector

{mo.as_html(fig_bar)}

---

*Select the `consumer-cyclical` sector then `basic-materials` to see an interesting contrast.*
    """)

    # ── Tab 4: Web Scraping ───────────────────────────────────────────────────
    tab_scraping = mo.md(r"""
## 🕷️ ESG Report Scraping Pipeline (Weeks 6–7)

Corporate sustainability data is rarely available in neat CSVs — it lives inside PDF reports
buried on company websites behind cookie banners and bot-detection layers.
I built a **three-stage automated pipeline** to extract it.

---

### Stage 1 — Cookie Acceptance (`Wk06-07_1acceptNstoreCookies.py`)

- Playwright async Chromium with `headless=new` flag
- Bot-detection evasion: fake User-Agent (Chrome 133 / Windows 10), `navigator.webdriver = undefined`, mocked plugin list, platform spoofing (`Win32`)
- **Shadow DOM** traversal: `document.querySelector('#usercentrics-root')?.shadowRoot` to find and click the "Accept All" button
- Screenshots taken before and after (`screenshot_CookiesPopup.png`, `screenshot_CookiesAccepted.png`)
- Saves `cookies.json` and `localStorage.json` for downstream reuse

### Stage 2 — URL Collection (`Wk06-07_2collect_urls.py`)

- Extracts all `<a href>` links from the loaded page
- Filters by ESG/sustainability keywords: `water`, `ESG`, `environment`, `governance`, `transparency`
- Saves `urls_raw.csv` (all links) and `urls_filtered.csv` (topic-matched only)

### Stage 3 — PDF Download & Keyword Extraction (`Wk06-07_3DLnExtract_OCR.py`)

- `curl` downloads bypass **Akamai TLS fingerprint detection** (which blocks `requests`)
- **PyMuPDF** (`fitz`) extracts text page-by-page; `clean_word_inner()` strips accents, punctuation, and casing before keyword matching
- `is_text_searchable()` checks if the PDF has a real text layer (threshold: ≥50% alphabetic words on page 1)
- **Tesseract OCR** fallback for scanned/image-only PDFs — renders each page at 2× zoom for accuracy
- Matching pages saved as individual PDFs with filename format `report_[page,freq].pdf`
- Persistent download ledger `df_DL.csv` prevents duplicate downloads on re-runs

---

### Pipeline Flow

```
Website → Accept Cookies (Playwright) → Scrape URLs → Filter (ESG keywords)
                                                              ↓
PDF URLs → Download (curl) → Text extract (PyMuPDF) → OCR fallback (Tesseract)
                                                              ↓
Matching pages → Save individual PDFs → Update ledger (df_DL.csv)
```

---

*This pipeline was run against Siemens' corporate website (`siemens.com/global/en/company/`)
targeting the keyword `water` in sustainability reports from 2019.*
    """)

    # ── Tab 5: LLM Analyser ───────────────────────────────────────────────────

    # Run the LLM analysis when the button is clicked
    llm_data, llm_status = run_llm_analysis(groq_key_input.value, esg_text_input.value) \
        if analyse_btn.value else (None, "not_run")

    # Build the result display depending on status
    if llm_status == "not_run":
        llm_result_md = "*Click **Analyse with LLM** to send the passage to the Groq API.*"
    elif llm_status == "no_key":
        llm_result_md = "⚠️ Please enter a Groq API key above (free at **console.groq.com**)."
    elif llm_status == "ok" and llm_data:
        sent_icon  = {"Positive": "✅", "Mixed": "⚠️", "Negative": "❌"}.get(llm_data.get("sentiment", ""), "❓")
        cred_icon  = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(llm_data.get("credibility", ""), "❓")
        topics_str = ", ".join(llm_data.get("key_topics", [])) or "None identified"
        flags_list = llm_data.get("red_flags", [])
        flags_str  = ("\n".join(f"- {f}" for f in flags_list)) if flags_list else "- None identified"
        summary    = llm_data.get("analyst_summary", "—")

        llm_result_md = f"""
---

### LLM Analysis Result

| Dimension | Result |
| :--- | :--- |
| **Sentiment** | {sent_icon} {llm_data.get('sentiment', '—')} |
| **Data Credibility** | {cred_icon} {llm_data.get('credibility', '—')} |
| **Key Topics** | {topics_str} |

**Potential Red Flags:**

{flags_str}

**Analyst Summary:**

> {summary}
"""
    else:
        llm_result_md = f"❌ Error: `{llm_status}`"

    tab_llm = mo.md(f"""
## 🤖 LLM-Powered ESG Disclosure Analyser (Week 9)

Large language models can read ESG disclosure passages the way an analyst would —
assessing credibility, flagging potential greenwashing, and extracting key themes.
This tool connects to **Groq's ultra-fast inference API** and returns structured JSON
parsed into an interactive report card.

**Prompt engineering** guides the model to return specific fields:
sentiment, credibility rating, key topics, red flags, and an analyst summary.

---

{groq_key_input}

{esg_text_input}

{analyse_btn}

{llm_result_md}

---

*Get a free Groq API key at **console.groq.com** — takes 30 seconds to sign up.*
*Model used: `llama3-8b-8192` (Groq's ultra-fast Llama 3 inference endpoint).*
    """)

    # ── Tab 6: NLP / 10-K ────────────────────────────────────────────────────
    tab_nlp = mo.md(r"""
## 📝 NLP on SEC 10-K Risk Factors (Week 10)

Regulators require every US-listed company to disclose business risks in their annual
10-K filing (Item 1A). This analysis compares how the **language of risk** has shifted
between **2015** and **2025** for the *Magnificent 7* tech companies, using a
spaCy Transformer model.

---

### Pipeline Steps

**Step 1 — SEC EDGAR Fetch**
- `get_cik()` converts a stock ticker to the SEC's internal CIK number
- `get_10k_filings()` queries the EDGAR submissions API for all 10-K filings
- `_extract_risk_factors()` uses regex to scissor out just the Item 1A section

**Step 2 — spaCy Transformer (`en_core_web_trf`)**
- `spacy.prefer_gpu()` routes inference to GPU if available
- Lemmatisation groups word variants (e.g. "factors" → "factor")
- Conjunction-boundary splitting ensures bigrams don't span clause boundaries

**Step 3 — Bigram Frequency Counting**
- `get_stemmed_ngram_freqs()` counts unigrams and bigrams after stopword removal
- `remove_redundant_unigrams()` drops single words where ≥90% of occurrences appear inside a bigram (e.g. "supply" dropped if "supply chain" dominates)
- Boilerplate legal phrases blacklisted (e.g. `forward_look`, `annual_report`)

**Step 4 — Word Clouds**
- `WordCloud` library generates side-by-side 2015 (red) vs 2025 (blue) clouds
- Top-20 phrase frequency tables with example sentences from the source text

---

### Key Findings: 2015 vs 2025

| 2015 — Dominant Risk Phrases | 2025 — Dominant Risk Phrases |
| :--- | :--- |
| competitive landscape | artificial intelligence |
| intellectual property | climate risk |
| supply chain | generative AI |
| data security | model liability |
| foreign exchange | ESG regulation |
| talent retention | geopolitical tension |
| regulatory compliance | digital sovereignty |

**Key insight:** The most striking shift is the emergence of **AI-related risk language** in
2025 disclosures. Terms like "generative AI", "model liability", and "algorithmic bias" were
entirely absent in 2015. Climate risks have also become more specific — companies now
quantify **physical climate risk** and **carbon transition costs** rather than making
generic environmental statements. This reflects both regulatory pressure (SEC climate
disclosure rules) and genuine business model transformation.

---

*Full working code: `Wk10_BigramCloud_GPUorCPU_Moodle.py`*
*Data cached to `public/risk_data.json` to avoid re-downloading on every run.*
    """)

    # ── Tab 7: Econometrics ───────────────────────────────────────────────────
    tab_econometrics = mo.md(r"""
## 📊 ESG & Firm Value — Panel Regression (Self-Exploration: R)

Beyond Python, this module introduced **R and R Markdown** for academic-style
econometric analysis via `WK10_ResultTables_Moodle.Rmd`.

**Core question:** *Does a higher ESG score lead to better firm performance (Tobin's Q)?*

---

### Variable Definitions

| Variable | Definition |
| :--- | :--- |
| **Tobin's Q** | `(Market Cap + Total Debt) / Total Assets` — proxy for firm performance |
| **ESG Score** | From Provider A and Provider B (robustness check) |
| **Firm Size** | `log(Total Assets)` |
| **Leverage** | `(Long-term Debt + Short-term Debt) / Book Equity` |

---

### Regression Specifications

```r
# Model 1: Simple OLS
model1 <- lm(q ~ ESGscore, data = ESG_data_B)

# Model 2: Multiple regression with controls
model2 <- lm(q ~ ESGscore + Firm_Size + Leverage, data = ESG_data_B)

# Model 3: With industry fixed effects
model3 <- lm(q ~ ESGscore + Firm_Size + Leverage + factor(Industry), data = ESG_data_B)

# Model 4: With industry + year fixed effects
model4 <- lm(q ~ ESGscore + Firm_Size + Leverage + factor(Industry) + factor(Year),
             data = ESG_data_B)
```

---

### Robustness Checks

```r
# Alternative ESG provider (Provider A instead of Provider B)
m_alt <- lm(q ~ ESGscore + Firm_Size + Leverage + factor(Industry) + factor(Year),
            data = ESG_data_A)

# Subsample: large firms only (Firm_Size above median)
m_large <- lm(q ~ ESGscore + Firm_Size + Leverage + factor(Industry) + factor(Year),
              data = (ESG_data_B |> filter(Firm_Size > median(Firm_Size))))

# Subsample: 2010-2019 only
m_1019 <- lm(q ~ ESGscore + Firm_Size + Leverage + factor(Industry) + factor(Year),
             data = (ESG_data_B |> filter(Year >= 2010 & Year <= 2019)))
```

---

### Key Finding

ESG score is **positively and significantly** associated with Tobin's Q across all
four model specifications. The coefficient shrinks after adding industry and year fixed
effects but remains statistically significant — suggesting the relationship is not merely
driven by sector composition or time trends.

Results are **robust to provider choice**: both Provider A and Provider B show a
positive ESG-performance link, though the magnitude differs, highlighting the importance
of provider selection in ESG research.

---

*Full working code: `WK10_ResultTables_Moodle.Rmd`*
*Regression tables produced with `stargazer`; data from `public/ESG_data_Moodle.RData`.*
    """)

    # ── Assemble all tabs into the portfolio ──────────────────────────────────
    portfolio = mo.md(f"""
# 🌿 Alex Morgan — ESG Analyst Portfolio

*BSc Accounting & Finance · Bayes Business School · 2025*

---

{mo.ui.tabs({
    "👤 About Me":       tab_about,
    "📈 Z-Score Tool":   tab_zscore,
    "🌿 ESG Dashboard":  tab_dashboard,
    "🕷️ Web Scraping":   tab_scraping,
    "🤖 LLM Analyser":   tab_llm,
    "📝 NLP · 10-K":     tab_nlp,
    "📊 Econometrics":   tab_econometrics,
})}

---

*Built with [marimo](https://marimo.io) · Source data: S&P 500 ESG & Z-Score dataset*
    """)

    return (portfolio,)


# ── Section 10: Display the Portfolio ─────────────────────────────────────────
@app.cell
def _(mo):
    mo.md(r"""
    #### 10. **Display** the Portfolio

    - Navigate the tabs to explore each section
    - Try changing the **year range** on the ESG dashboard to zoom into different periods
    - Switch the **ticker** on the Z-Score tab to compare companies
    - Paste an ESG disclosure and enter a Groq API key on the LLM tab for live AI analysis
    """)
    return


@app.cell
def _(portfolio):
    portfolio
    return


if __name__ == "__main__":
    app.run()
