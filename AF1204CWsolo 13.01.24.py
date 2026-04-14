# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "marimo>=0.19.10",
#   "pandas>=2.3.3",
#   "plotly>=6.5.1",
#   "numpy>=1.26.0",
#   "pyzmq>=27.1.0",
# ]
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 🎓 Personal Portfolio Webpage — Ibrahim Khan

    A multi-tabbed personal portfolio demonstrating data literacy skills developed
    across **AF1204** (Weeks 1–10), plus self-directed exploration of AI, Monte Carlo
    simulation, NLP, and web scraping.

    ---
    """)
    return


@app.cell
def _():
    # 1: Imports
    import marimo as mo
    import pandas as pd
    import numpy as np
    import re
    import micropip
    from collections import Counter
    return Counter, micropip, mo, np, pd, re


@app.cell
async def _(micropip):
    # 2: Install packages needed in the WASM / GitHub Pages environment
    await micropip.install("plotly")
    import plotly.express as px
    import plotly.graph_objects as go
    return go, px


@app.cell
def _(mo):
    # 3: Define all UI controls used in the interactive demos

    # ── Z-Score inputs (Week 01–02 skill: mo.ui.number, reactive cells) ──
    ui_total_assets   = mo.ui.number(value=100_000, label="Total Assets ($)")
    ui_current_assets = mo.ui.number(value=40_000,  label="Current Assets ($)")
    ui_current_liab   = mo.ui.number(value=20_000,  label="Current Liabilities ($)")
    ui_retained_earn  = mo.ui.number(value=30_000,  label="Retained Earnings ($)")
    ui_ebit           = mo.ui.number(value=15_000,  label="EBIT ($)")
    ui_total_liab     = mo.ui.number(value=50_000,  label="Total Liabilities ($)")
    ui_sales          = mo.ui.number(value=120_000, label="Total Sales / Revenue ($)")
    ui_market_cap     = mo.ui.number(value=80_000,  label="Market Capitalisation ($)")

    # ── Monte Carlo inputs (Self-exploration: mo.ui.slider) ──
    ui_mc_days  = mo.ui.slider(start=30,    stop=365,  step=30,   value=252,  label="Forecast Days")
    ui_mc_sims  = mo.ui.slider(start=100,   stop=3000, step=100,  value=1000, label="Number of Simulations")
    ui_mc_vol   = mo.ui.slider(start=0.05,  stop=0.80, step=0.05, value=0.25, label="Annual Volatility (σ)")
    ui_mc_drift = mo.ui.slider(start=-0.10, stop=0.30, step=0.01, value=0.08, label="Annual Drift (μ)")

    # ── NLP input (Week 10 skill: text processing) ──
    ui_nlp_text = mo.ui.text_area(
        value=(
            "The company faces significant cybersecurity threats and data breaches. "
            "Artificial intelligence and machine learning models may produce unpredictable results. "
            "Supply chain disruptions and geopolitical risks could adversely affect revenue growth. "
            "Regulatory compliance requirements in multiple jurisdictions increase operational costs. "
            "Competition from technology companies and new market entrants remains intense. "
            "Climate change risks and environmental regulations may impact business operations."
        ),
        label="Paste any financial or business text (e.g. a 10-K risk factor section):",
        rows=6
    )
    ui_nlp_min = mo.ui.slider(start=1, stop=4, step=1, value=1, label="Minimum word frequency to display")

    return (
        ui_current_assets, ui_current_liab, ui_ebit, ui_market_cap,
        ui_mc_days, ui_mc_drift, ui_mc_sims, ui_mc_vol,
        ui_nlp_min, ui_nlp_text,
        ui_retained_earn, ui_sales, ui_total_assets, ui_total_liab,
    )


@app.cell
def _(
    mo, np,
    ui_current_assets, ui_current_liab, ui_ebit, ui_market_cap,
    ui_retained_earn, ui_sales, ui_total_assets, ui_total_liab,
):
    # 4: Reactive Z-Score computation
    # Demonstrates: Week 01 — try/except, NaN handling, function definitions
    #               Week 02 — reactive Marimo cells that update automatically

    def compute_zscore(ta, ca, cl, re_earn, ebit, tl, s, mc):
        """Compute Altman Z-Score with try/except for zero-liabilities edge case."""
        try:
            wc2ta   = (ca - cl) / ta
            re2ta   = re_earn / ta
            ebit2ta = ebit / ta
            mv2tl   = mc / tl    # raises ZeroDivisionError if tl == 0
            s2ta    = s / ta
            z = 1.2*wc2ta + 1.4*re2ta + 3.3*ebit2ta + 0.6*mv2tl + 1.0*s2ta
            return round(z, 3)
        except ZeroDivisionError:
            return float('nan')

    z_score = compute_zscore(
        ui_total_assets.value,
        ui_current_assets.value,
        ui_current_liab.value,
        ui_retained_earn.value,
        ui_ebit.value,
        ui_total_liab.value,
        ui_sales.value,
        ui_market_cap.value,
    )

    # Classify into zones (Week 02 logic)
    if np.isnan(z_score):
        z_zone, z_color = "Undefined — zero liabilities", "grey"
    elif z_score > 2.99:
        z_zone, z_color = "SAFE ZONE ✅", "green"
    elif z_score >= 1.81:
        z_zone, z_color = "GREY ZONE ⚠️ — Caution", "orange"
    else:
        z_zone, z_color = "DISTRESS ZONE 🚨", "red"

    z_result_display = mo.md(
        f"""
        ### Altman Z-Score: **{z_score if not np.isnan(z_score) else 'N/A'}**

        **Zone:** <span style='color:{z_color}; font-weight:700;'>{z_zone}</span>

        | Threshold | Interpretation |
        |---|---|
        | Z > 2.99 | ✅ Safe — low bankruptcy risk |
        | 1.81 ≤ Z ≤ 2.99 | ⚠️ Grey — caution advised |
        | Z < 1.81 | 🚨 Distress — high bankruptcy risk |
        """
    )

    return compute_zscore, z_result_display, z_score, z_zone, z_color


@app.cell
def _(go, mo, np, ui_mc_days, ui_mc_drift, ui_mc_sims, ui_mc_vol):
    # 5: Monte Carlo simulation chart
    # Demonstrates: Self-exploration — Geometric Brownian Motion,
    #               numpy random simulation, percentile analysis, Plotly

    np.random.seed(42)
    T   = ui_mc_days.value
    N   = ui_mc_sims.value
    sig = ui_mc_vol.value
    mu  = ui_mc_drift.value
    S0  = 185.0
    dt  = 1 / 252

    # Simulate N paths over T days using GBM
    daily_log_returns = (mu - 0.5 * sig**2) * dt + sig * np.sqrt(dt) * np.random.randn(T, N)
    mc_paths = S0 * np.cumprod(np.exp(daily_log_returns), axis=0)
    final_prices = mc_paths[-1, :]

    p5  = round(float(np.percentile(final_prices, 5)),  2)
    p50 = round(float(np.percentile(final_prices, 50)), 2)
    p95 = round(float(np.percentile(final_prices, 95)), 2)
    prob_profit = round(100 * float(np.mean(final_prices > S0)), 1)

    # Build Plotly figure — show up to 300 sample paths (Week 03 skill: Plotly)
    fig_mc = go.Figure()
    n_display = min(300, N)
    for _i in range(n_display):
        fig_mc.add_trace(go.Scatter(
            y=mc_paths[:, _i], mode="lines",
            line=dict(width=0.4, color="rgba(99,179,237,0.07)"),
            showlegend=False, hoverinfo="skip"
        ))
    for _pct, _col, _name in [(5, "red", "5th Pct"), (50, "white", "Median"), (95, "green", "95th Pct")]:
        fig_mc.add_trace(go.Scatter(
            y=np.percentile(mc_paths, _pct, axis=1),
            mode="lines",
            line=dict(width=2.5, color=_col),
            name=_name
        ))
    fig_mc.update_layout(
        title=f"Monte Carlo Simulation: {T} Days · {N:,} Paths · Starting Price ${S0}",
        xaxis_title="Trading Days",
        yaxis_title="Simulated Price ($)",
        template="plotly_dark",
        height=450,
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0)")
    )

    mc_chart   = mo.ui.plotly(fig_mc)
    mc_summary = mo.md(
        f"""
        | Metric | Value |
        |---|---|
        | 5th Percentile (Downside) | **${p5:,.2f}** |
        | Median Outcome | **${p50:,.2f}** |
        | 95th Percentile (Upside) | **${p95:,.2f}** |
        | Probability of Profit | **{prob_profit}%** |
        | Simulations run | **{N:,}** |
        """
    )

    return mc_chart, mc_summary


@app.cell
def _(Counter, mo, pd, px, re, ui_nlp_min, ui_nlp_text):
    # 6: NLP word and bigram frequency analysis
    # Demonstrates: Week 10 — tokenisation, stopword removal, bigram counting,
    #               regex text cleaning, Counter, Plotly bar chart

    _STOPWORDS = {
        "the","a","an","and","or","but","in","on","at","to","for","of","with",
        "from","is","are","was","were","be","been","by","as","it","its","this",
        "that","these","those","such","may","could","will","would","should","can",
        "their","our","have","has","had","not","also","which","we","us","they",
        "them","all","any","some","no","if","about","into","over","more","than",
        "being","further","once","here","when","where","each","both",
    }

    _text = ui_nlp_text.value.lower()
    _text = re.sub(r"[^a-z\s]", " ", _text)   # remove punctuation (Week 10: text cleaning)
    _tokens = [w for w in _text.split() if len(w) > 3 and w not in _STOPWORDS]

    _unigram_counts = Counter(_tokens)
    _bigrams = [f"{_tokens[i]} {_tokens[i+1]}" for i in range(len(_tokens) - 1)]
    _bigram_counts  = Counter(_bigrams)

    _min_freq = ui_nlp_min.value

    _df_uni = pd.DataFrame(
        [(w, c) for w, c in _unigram_counts.most_common(20) if c >= _min_freq],
        columns=["Word", "Frequency"]
    )
    _df_bi = pd.DataFrame(
        [(b, c) for b, c in _bigram_counts.most_common(15) if c >= _min_freq],
        columns=["Bigram", "Frequency"]
    )

    if len(_df_uni) > 0:
        _fig_uni = px.bar(
            _df_uni, x="Frequency", y="Word", orientation="h",
            title="Top Unigrams",
            color="Frequency",
            color_continuous_scale="Blues",
            template="plotly_dark",
            height=380
        )
        _fig_uni.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
        nlp_unigram_chart = mo.ui.plotly(_fig_uni)
    else:
        nlp_unigram_chart = mo.md("*No words found above the minimum frequency.*")

    if len(_df_bi) > 0:
        _fig_bi = px.bar(
            _df_bi, x="Frequency", y="Bigram", orientation="h",
            title="Top Bigrams (two-word phrases)",
            color="Frequency",
            color_continuous_scale="Teal",
            template="plotly_dark",
            height=340
        )
        _fig_bi.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
        nlp_bigram_chart = mo.ui.plotly(_fig_bi)
    else:
        nlp_bigram_chart = mo.md("*No bigrams found above the minimum frequency.*")

    nlp_stats = mo.md(
        f"**{len(_unigram_counts)}** unique words · "
        f"**{len(_bigram_counts)}** unique bigrams · "
        f"Showing frequency ≥ **{_min_freq}**"
    )

    return nlp_bigram_chart, nlp_stats, nlp_unigram_chart


@app.cell
def _(
    mc_chart, mc_summary,
    mo,
    nlp_bigram_chart, nlp_stats, nlp_unigram_chart,
    ui_current_assets, ui_current_liab, ui_ebit, ui_market_cap,
    ui_mc_days, ui_mc_drift, ui_mc_sims, ui_mc_vol,
    ui_nlp_min, ui_nlp_text,
    ui_retained_earn, ui_sales, ui_total_assets, ui_total_liab,
    z_result_display,
):
    # 7: Assemble the multi-tabbed portfolio layout
    # Demonstrates: Week 04 — mo.ui.tabs, mo.vstack, mo.hstack, mo.callout

    # ── Tab 1: About Me / CV ──────────────────────────────────────────────────
    tab_about = mo.md("""
    ### BSc Accounting & Finance | Data & AI Enthusiast

    **Summary:**
    - Motivated BSc Accounting & Finance student at Bayes Business School with a
      proven analytical background. My independent investment book has yielded a
      **90%+ net profit**.
    - Contributed to fixed-income analysis whilst shadowing a Partner at a boutique
      hedge fund overseeing **£500M+ in assets**.
    - Self-directed developer: independently designed and deployed **NutriScan AI**,
      a live PWA using Firebase and Gemini AI, currently in initial beta testing.
    - Strong interest in how AI can transform private markets and fintech.

    ---

    **Education:**

    * **BSc Accounting & Finance (Hons)**, Bayes Business School *(Sep 2025 – May 2028)*
      — Predicted: **1st Class**
    * **Bloomberg Market Concept (BMC) Certificate** *(Oct – Dec 2025)*
    * **John Lyon School** — A: Maths · B: Chemistry · C: Biology · 10 GCSEs at 9–7 *(2018 – 2025)*

    ---

    **Technical Skills:**

    | Category | Tools & Libraries |
    |---|---|
    | Programming | Python, Jupyter Notebook, Marimo |
    | Data & Visualisation | Pandas, NumPy, Plotly, Altair |
    | Web & AI | Playwright, spaCy NLP, Gemini AI, Firebase |
    | Finance | yfinance, PyMuPDF, EViews, Bloomberg Terminal, Monte Carlo |

    ---

    **Work Experience:**

    * **Tutor**, Sherpa *(Jul 2025 – Present)* — GCSE and A-Level Maths and Sciences
    * **Data & Operations Analyst**, Nice Smile Dental *(Jul – Sep 2025)*
      — Reduced reporting time by 1.5 hrs/week; improved data accuracy by 17%
    * **Investment Banking Shadow**, Observatory Capital Management LLP *(Jul – Sep 2022)*
      — Fixed-income research for £500M+ AUM; 96% data accuracy under tight deadlines
    """)

    # ── Tab 2: Passion Projects — interactive demos ───────────────────────────
    tab_projects = mo.vstack([

        mo.md("## 📊 Passion Projects — Interactive Demos"),

        # Demo A: Z-Score (Wk01–02)
        mo.md("### 📐 Demo 1: Altman Z-Score Calculator *(Weeks 01–02)*"),
        mo.callout(
            mo.md(
                "Enter company financials below. The score updates **reactively** "
                "(Week 02: Marimo reactive cells). "
                "The `try/except` block (Week 01) handles the edge case of zero liabilities, "
                "assigning `NaN` instead of crashing."
            ),
            kind="info"
        ),
        mo.hstack([
            mo.vstack([ui_total_assets, ui_current_assets, ui_current_liab, ui_retained_earn]),
            mo.vstack([ui_ebit, ui_total_liab, ui_sales, ui_market_cap]),
        ], justify="center", gap=4),
        z_result_display,

        mo.md("---"),

        # Demo B: Monte Carlo (Self-exploration)
        mo.md("### 🎲 Demo 2: Monte Carlo Stock Price Simulation *(Self-exploration)*"),
        mo.callout(
            mo.md(
                "Adjust the sliders to change simulation parameters. "
                "Uses **Geometric Brownian Motion (GBM)** — the same mathematical framework "
                "behind Black-Scholes options pricing. "
                "Directly inspired by my **10,000-iteration Monte Carlo LBO model** for Coca-Cola "
                "built independently outside the module."
            ),
            kind="info"
        ),
        mo.hstack([ui_mc_days, ui_mc_sims, ui_mc_vol, ui_mc_drift], justify="center", gap=2),
        mc_chart,
        mc_summary,

    ])

    # ── Tab 3: Technical Journey (Weeks 1–10 + NLP demo) ─────────────────────
    tab_technical = mo.vstack([

        mo.md("## 🧠 Technical Journey — Weeks 01 to 10"),

        mo.md("""
        | Week | Topic | Key Skills Demonstrated |
        |---|---|---|
        | 01 | Python Fundamentals | `try/except`, f-strings, `NaN` handling, function definitions |
        | 02 | Marimo + yfinance | Reactive notebooks, live financial data fetch, Altair gauge chart |
        | 02x | Panel Data | Nested loops, fiscal-year alignment, rate-limiting with `time.sleep` |
        | 03 | Interactive Plotly | Violin, joyplot, 3D scatter, `zip()`, colour scales |
        | 04 | Portfolio & GitHub Pages | HTML-WASM export, `mo.ui.tabs`, `mo.vstack`, `mo.callout` |
        | 06–07 | Web Scraping + OCR | Playwright async/await, shadow DOM, PyMuPDF, Tesseract OCR |
        | 09 | LLM API | Gemini 1.5 Flash, multi-modal prompting, structured JSON parsing |
        | 10 | NLP & Word Clouds | spaCy transformer, bigrams, lemmatisation, `Counter`, word clouds |
        """),

        mo.md("### 🧩 Live Demo: NLP Word & Bigram Frequency Analyser *(Week 10)*"),
        mo.callout(
            mo.md(
                "This demo applies the **tokenisation, stopword removal, and bigram counting** "
                "pipeline from Week 10 — the same approach used on SEC 10-K Risk Factor sections "
                "for Apple, Microsoft, Nvidia, and others. "
                "Paste any business or financial text and adjust the minimum frequency slider."
            ),
            kind="info"
        ),
        mo.hstack([ui_nlp_text, ui_nlp_min], justify="start", gap=2),
        nlp_stats,
        mo.hstack([nlp_unigram_chart, nlp_bigram_chart], justify="start", gap=2),

    ])

    # ── Tab 4: Personal Interests ─────────────────────────────────────────────
    tab_interests = mo.vstack([

        mo.md("## ✨ Personal Projects & Interests"),

        mo.md("""
        ### 📱 NutriScan AI — Live App *(Initial Beta Testing)*

        An independently built **Progressive Web App (PWA)** that uses
        **Gemini 1.5 Flash** multi-modal AI to scan meals from photos,
        nutrition labels, and barcodes — estimating calories and protein in seconds.

        **Live:** [food-app-cb863.web.app](https://food-app-cb863.web.app/)

        | Feature | Details |
        |---|---|
        | 📸 Photo scanning | AI estimates calories & protein from a plate photo |
        | 🏷️ Label OCR | Reads exact values from packaged food nutrition labels |
        | 📦 Barcode scanner | EAN/UPC lookup via Open Food Facts database |
        | ✍️ Natural language | "Bowl of pasta with chicken" — AI estimates macros |
        | 🔥 Streak & Badges | 7-day streak tracker, 8 achievement badges |
        | 📈 Progress charts | 14-day weight & body fat line charts |
        | 🤖 Weekly AI insight | Personalised Gemini paragraph about your week |
        | ☁️ Cloud sync | Firebase Firestore for multi-device data |

        **Stack:** Firebase Hosting · Firestore · Gemini 1.5 Flash · OpenRouter · Vanilla JS

        ---

        ### 📈 Independent Investment Portfolio

        Maintaining a personal investment book with a **90%+ net profit** since inception.
        Applies skills from the module and beyond: regression analysis, Monte Carlo simulation,
        DCF modelling, and time-series analysis using Python and Excel.

        ---

        ### 🎯 Interests & Activities

        * 🎹 Piano
        * ⚽ First-team football
        * 🏏 County Cup cricket
        * ♟ Regional-level chess
        * 🚴 Cycling
        """),

    ])

    # ── Assemble tabs and display final portfolio ─────────────────────────────
    portfolio_tabs = mo.ui.tabs({
        "📄 About Me":           tab_about,
        "📊 Passion Projects":   tab_projects,
        "🧠 Technical Journey":  tab_technical,
        "✨ Personal Interests": tab_interests,
    })

    mo.md(
        f"""
# **Ibrahim Khan**
### BSc Accounting & Finance · Bayes Business School · AF1204 Portfolio 2025/26

---

{portfolio_tabs}
        """
    )


if __name__ == "__main__":
    app.run()
