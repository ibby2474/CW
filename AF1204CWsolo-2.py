# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "marimo>=0.19.10",
#   "pandas>=2.3.3",
#   "plotly>=6.5.1",
#   "numpy>=1.26.0",
#   "scipy>=1.11.0",
#   "pyzmq>=27.1.0",
# ]
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App()


# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 🎓 Personal Portfolio Webpage — Ibrahim Khan

    A multi-tabbed personal portfolio demonstrating data literacy skills developed
    across **AF1204** (Weeks 1–10), plus self-directed exploration of AI, Monte Carlo
    simulation, NLP, and a live deployed app (NutriScan AI).

    ---
    """)
    return


# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _():
    # 1: Imports
    import marimo as mo
    import pandas as pd
    import numpy as np
    import re
    import io
    import micropip
    from collections import Counter
    return Counter, io, micropip, mo, np, pd, re


# ─────────────────────────────────────────────────────────────────────────────
@app.cell
async def _(micropip):
    # 2: Install packages needed in the WASM / GitHub Pages environment
    await micropip.install(["plotly", "scipy"])
    import plotly.express as px
    import plotly.graph_objects as go
    from scipy import stats
    return go, px, stats


# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _(np, pd):
    # 3: Generate synthetic financial dataset (mirrors sp500_ZScore_AvgCostofDebt.csv)
    # This replicates exactly the data structure used in Wk04_DataPreparation:
    # Z-Score, Average Cost of Debt, Sector, Year — used for regression and contingency analysis

    np.random.seed(7)

    SECTORS = [
        "technology", "financial-services", "healthcare",
        "consumer-cyclical", "energy", "industrials",
        "communication-services", "consumer-defensive",
    ]
    YEARS   = [2021, 2022, 2023, 2024]
    N_FIRMS = 60   # 60 companies × 4 years = 240 rows

    rows = []
    for _firm_id in range(N_FIRMS):
        _sector   = SECTORS[_firm_id % len(SECTORS)]
        _base_z   = np.random.uniform(0.5, 7.0)          # company's "true" credit quality
        _base_cod = np.clip(0.12 - 0.01 * _base_z + np.random.normal(0, 0.02), 0.005, 0.35)
        _name     = f"Company_{_firm_id:03d}"
        _ticker   = f"C{_firm_id:03d}"

        for _yr in YEARS:
            _z   = max(0.1, _base_z + np.random.normal(0, 0.4))
            _cod = max(0.003, _base_cod + np.random.normal(0, 0.008))
            rows.append({
                "Ticker":         _ticker,
                "Name":           _name,
                "Year":           _yr,
                "Sector_Key":     _sector,
                "Z_Score":        round(_z, 3),
                "AvgCost_of_Debt": round(_cod, 5),
            })

    df_raw = pd.DataFrame(rows)

    # ── Wk04 skill: groupby + shift(1) to create lagged Z-Score ──────────────
    df_raw["Z_Score_lag"] = (
        df_raw
        .sort_values(["Ticker", "Year"])
        .groupby("Ticker")["Z_Score"]
        .shift(1)
    )

    # ── Wk04 skill: apply + lambda to classify risk zones ────────────────────
    df_raw["Risk_Zone"] = df_raw["Z_Score_lag"].apply(
        lambda z: (
            "1. Distress Zone (Z < 1.81)"   if z < 1.81   else
            "3. Safe Zone (Z > 2.99)"        if z > 2.99   else
            "2. Grey Zone (1.81 ≤ Z ≤ 2.99)"
        ) if pd.notna(z) else np.nan
    )

    # ── Wk04 skill: convert to % and drop NaN rows ───────────────────────────
    df_raw["Debt_Cost_Pct"] = df_raw["AvgCost_of_Debt"] * 100

    df_fin = df_raw.dropna(subset=["Z_Score_lag", "AvgCost_of_Debt", "Risk_Zone"]).copy()
    df_fin = df_fin[df_fin["AvgCost_of_Debt"] < 0.30]   # remove extreme outliers

    print(f"Dataset ready: {len(df_fin)} observations across {df_fin['Ticker'].nunique()} companies, "
          f"{df_fin['Year'].nunique()} years, {df_fin['Sector_Key'].nunique()} sectors.")

    return df_fin, df_raw


# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _(df_fin, mo):
    # 4: Define all UI controls

    # ── Z-Score calculator (Wk01–02: mo.ui.number, reactive cells) ───────────
    ui_ta  = mo.ui.number(value=100_000, label="Total Assets ($)")
    ui_ca  = mo.ui.number(value=40_000,  label="Current Assets ($)")
    ui_cl  = mo.ui.number(value=20_000,  label="Current Liabilities ($)")
    ui_re  = mo.ui.number(value=30_000,  label="Retained Earnings ($)")
    ui_eb  = mo.ui.number(value=15_000,  label="EBIT ($)")
    ui_tl  = mo.ui.number(value=50_000,  label="Total Liabilities ($)")
    ui_sal = mo.ui.number(value=120_000, label="Total Sales / Revenue ($)")
    ui_mc  = mo.ui.number(value=80_000,  label="Market Capitalisation ($)")

    # ── Regression filters (Wk04: sector filter, Wk03: interactive chart) ────
    all_sectors  = sorted(df_fin["Sector_Key"].unique().tolist())
    ui_sectors   = mo.ui.multiselect(
        options=all_sectors,
        value=all_sectors[:4],
        label="Filter by Sector",
    )
    all_years = sorted(df_fin["Year"].unique().tolist())
    ui_years = mo.ui.multiselect(
        options=[str(y) for y in all_years],
        value=[str(y) for y in all_years],
        label="Filter by Year",
    )

    # ── Monte Carlo (self-exploration: mo.ui.slider) ──────────────────────────
    ui_mc_days  = mo.ui.slider(start=30,   stop=365, step=30,   value=252, label="Forecast Days")
    ui_mc_sims  = mo.ui.slider(start=100,  stop=3000, step=100, value=1000, label="Simulations")
    ui_mc_vol   = mo.ui.slider(start=0.05, stop=0.80, step=0.05, value=0.25, label="Volatility σ")
    ui_mc_drift = mo.ui.slider(start=-0.10, stop=0.30, step=0.01, value=0.08, label="Drift μ")

    # ── NLP (Wk10: mo.ui.text_area) ──────────────────────────────────────────
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
        rows=6,
    )
    ui_nlp_min = mo.ui.slider(start=1, stop=4, step=1, value=1, label="Min word frequency")

    return (
        ui_ca, ui_cl, ui_eb, ui_mc, ui_re, ui_sal, ui_ta, ui_tl,
        ui_mc_days, ui_mc_drift, ui_mc_sims, ui_mc_vol,
        ui_nlp_min, ui_nlp_text,
        ui_sectors, ui_years,
    )


# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _(df_fin, ui_sectors, ui_years):
    # 5: Reactive data filtering
    # Demonstrates: Wk04 — boolean indexing, .isin(), filtered DataFrames

    _years_int = [int(y) for y in ui_years.value]

    df_filtered = df_fin[
        (df_fin["Sector_Key"].isin(ui_sectors.value)) &
        (df_fin["Year"].isin(_years_int))
    ].copy()

    n_obs = len(df_filtered)

    return df_filtered, n_obs


# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _(mo, np, ui_ca, ui_cl, ui_eb, ui_mc, ui_re, ui_sal, ui_ta, ui_tl):
    # 6: Reactive Altman Z-Score computation
    # Demonstrates: Wk01 — try/except, NaN, function definition
    #               Wk02 — reactive Marimo cells

    def compute_zscore(ta, ca, cl, re_earn, ebit, tl, s, mktcap):
        """Altman Z-Score with try/except handling zero-liabilities edge case (Week 01)."""
        try:
            wc2ta    = (ca - cl) / ta
            re2ta    = re_earn / ta
            ebit2ta  = ebit / ta
            mv2tl    = mktcap / tl   # ZeroDivisionError if tl == 0
            s2ta     = s / ta
            return round(1.2*wc2ta + 1.4*re2ta + 3.3*ebit2ta + 0.6*mv2tl + 1.0*s2ta, 3)
        except ZeroDivisionError:
            return float("nan")

    z = compute_zscore(
        ui_ta.value, ui_ca.value, ui_cl.value, ui_re.value,
        ui_eb.value, ui_tl.value, ui_sal.value, ui_mc.value,
    )

    if np.isnan(z):
        z_zone, z_col = "Undefined (zero liabilities)", "grey"
    elif z > 2.99:
        z_zone, z_col = "SAFE ZONE ✅", "green"
    elif z >= 1.81:
        z_zone, z_col = "GREY ZONE ⚠️", "orange"
    else:
        z_zone, z_col = "DISTRESS ZONE 🚨", "red"

    z_display = mo.md(f"""
    ### Altman Z-Score: **{z if not np.isnan(z) else "N/A"}**

    **Zone:** <span style='color:{z_col}; font-weight:700;'>{z_zone}</span>

    | Threshold | Interpretation |
    |---|---|
    | Z > 2.99 | ✅ Safe — low bankruptcy risk |
    | 1.81 ≤ Z ≤ 2.99 | ⚠️ Grey — caution |
    | Z < 1.81 | 🚨 Distress — high risk |
    """)

    return compute_zscore, z, z_col, z_display, z_zone


# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _(df_filtered, go, mo, n_obs, np, px, stats, ui_sectors, ui_years):
    # 7: Credit Risk Regression Analysis
    # Demonstrates: Wk04 — OLS regression, scatter + regression line, np.polyfit
    #               Wk03 — Plotly scatter with threshold lines, box plot
    #               Wk04 — apply/lambda risk zone classification, pd.crosstab
    #               Wk07–08 — statistical analysis and interpretation

    # ── 7a. OLS Regression (scipy.stats.linregress mirrors statsmodels OLS) ──
    _reg = df_filtered.dropna(subset=["Z_Score_lag", "AvgCost_of_Debt"])

    if len(_reg) > 5:
        _slope, _intercept, _r, _p, _se = stats.linregress(
            _reg["Z_Score_lag"], _reg["Debt_Cost_Pct"]
        )
        _r2   = round(_r**2, 4)
        _p_   = round(_p, 4)
        _sl   = round(_slope, 4)
        _sig  = "✅ Statistically significant (p < 0.05)" if _p < 0.05 else "⚠️ Not significant (p ≥ 0.05)"
    else:
        _r2 = _p_ = _sl = 0.0
        _sig = "⚠️ Insufficient data"

    reg_summary = mo.md(f"""
    **OLS Regression:** Avg. Cost of Debt ~ Lagged Z-Score &nbsp;|&nbsp; n = **{n_obs}**

    | Statistic | Value | Interpretation |
    |---|---|---|
    | Slope (β) | **{_sl}** | A 1-unit ↑ in Z-Score → {abs(_sl):.3f}% {'↓' if _sl < 0 else '↑'} in cost of debt |
    | R² | **{_r2}** | {round(_r2*100, 1)}% of variation in borrowing costs explained by credit risk |
    | p-value | **{_p_}** | {_sig} |

    *A negative slope confirms the theory: safer companies (higher Z-Score) borrow more cheaply.*
    """)

    # ── 7b. Scatter plot with regression line (Wk03 + Wk04 pattern) ─────────
    _color_map = {
        "1. Distress Zone (Z < 1.81)":   "red",
        "2. Grey Zone (1.81 ≤ Z ≤ 2.99)": "grey",
        "3. Safe Zone (Z > 2.99)":         "green",
    }

    fig_scatter = px.scatter(
        df_filtered.dropna(subset=["Z_Score_lag", "Debt_Cost_Pct", "Risk_Zone"]),
        x="Z_Score_lag",
        y="Debt_Cost_Pct",
        color="Risk_Zone",
        color_discrete_map=_color_map,
        hover_name="Name",
        hover_data=["Ticker", "Year", "Sector_Key"],
        title=f"Cost of Debt vs. Lagged Z-Score ({n_obs} observations)",
        labels={
            "Z_Score_lag":  "Altman Z-Score (lagged — previous year)",
            "Debt_Cost_Pct": "Avg. Cost of Debt (%)",
            "Risk_Zone":     "Risk Zone",
        },
        template="plotly_white",
        height=500,
    )

    # Threshold lines (same as taught in Wk04)
    fig_scatter.add_vline(x=1.81, line_dash="dash", line_color="red",
        annotation=dict(text="Distress (1.81)", font=dict(color="red"),
                        x=1.5, xref="x", y=1.07, yref="paper",
                        showarrow=False, yanchor="top"))
    fig_scatter.add_vline(x=2.99, line_dash="dash", line_color="green",
        annotation=dict(text="Safe (2.99)", font=dict(color="green"),
                        x=3.10, xref="x", y=1.02, yref="paper",
                        showarrow=False, yanchor="top"))

    # Regression line (same np.polyfit approach as Wk04)
    _clean = df_filtered.dropna(subset=["Z_Score_lag", "Debt_Cost_Pct"])
    if len(_clean) > 5:
        _x  = _clean["Z_Score_lag"].astype(float)
        _y  = _clean["Debt_Cost_Pct"].astype(float)
        _m, _b = np.polyfit(_x, _y, 1)
        _xl = np.linspace(_x.min(), _x.max(), 100)
        _yl = _m * _xl + _b
        _rt = px.line(x=_xl, y=_yl).data[0]
        _rt.update(line=dict(width=1.5, color="black", dash="dot"), name="OLS Fit")
        fig_scatter.add_trace(_rt)

    scatter_chart = mo.ui.plotly(fig_scatter)

    # ── 7c. Box plot by Risk Zone (Wk03 + Wk04 pattern) ──────────────────────
    fig_box = px.box(
        df_filtered.dropna(subset=["Risk_Zone", "Debt_Cost_Pct"]),
        x="Risk_Zone",
        y="Debt_Cost_Pct",
        color="Risk_Zone",
        color_discrete_map=_color_map,
        points="outliers",
        hover_data=["Name"],
        title="Distribution of Cost of Debt by Credit Risk Zone",
        labels={
            "Debt_Cost_Pct": "Avg. Cost of Debt (%)",
            "Risk_Zone":      "Altman Z-Score Zone (lagged)",
        },
        template="plotly_white",
        height=420,
    )
    fig_box.update_layout(showlegend=False)
    box_chart = mo.ui.plotly(fig_box)

    # ── 7d. Contingency table (Wk04 skill: pd.crosstab + apply/lambda) ───────
    import pandas as _pd2
    _median_cod = df_filtered["AvgCost_of_Debt"].median()
    _tb = df_filtered.copy()
    _tb["Cost_Label"] = _tb["AvgCost_of_Debt"].apply(
        lambda x: "Higher (Above Median)" if x > _median_cod else "Lower (Below Median)"
    )
    _ct = _pd2.crosstab(
        index=_tb["Cost_Label"],
        columns=_tb["Risk_Zone"],
        margins=True,
        margins_name="Total",
    )
    crosstab_display = mo.md(
        "**Contingency Table** — Cost of Debt (row) vs. Risk Zone (col):\n\n"
        + _ct.to_markdown()
    )

    return box_chart, crosstab_display, reg_summary, scatter_chart


# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _(go, mo, np, ui_mc_days, ui_mc_drift, ui_mc_sims, ui_mc_vol):
    # 8: Monte Carlo simulation
    # Demonstrates: Self-exploration — Geometric Brownian Motion (GBM),
    #               numpy stochastic simulation, percentile risk analysis

    np.random.seed(42)
    _T   = ui_mc_days.value
    _N   = ui_mc_sims.value
    _sig = ui_mc_vol.value
    _mu  = ui_mc_drift.value
    _S0  = 185.0
    _dt  = 1 / 252

    # Simulate paths using GBM
    _log_ret = (_mu - 0.5 * _sig**2) * _dt + _sig * np.sqrt(_dt) * np.random.randn(_T, _N)
    _paths   = _S0 * np.cumprod(np.exp(_log_ret), axis=0)
    _finals  = _paths[-1, :]

    _p5  = round(float(np.percentile(_finals, 5)),  2)
    _p50 = round(float(np.percentile(_finals, 50)), 2)
    _p95 = round(float(np.percentile(_finals, 95)), 2)
    _prob = round(100 * float(np.mean(_finals > _S0)), 1)

    fig_mc = go.Figure()
    for _i in range(min(300, _N)):
        fig_mc.add_trace(go.Scatter(
            y=_paths[:, _i], mode="lines",
            line=dict(width=0.4, color="rgba(99,179,237,0.07)"),
            showlegend=False, hoverinfo="skip",
        ))
    for _pct, _col, _nm in [(5, "red", "5th Pct"), (50, "white", "Median"), (95, "green", "95th Pct")]:
        fig_mc.add_trace(go.Scatter(
            y=np.percentile(_paths, _pct, axis=1),
            mode="lines",
            line=dict(width=2.5, color=_col),
            name=_nm,
        ))
    fig_mc.update_layout(
        title=f"Monte Carlo GBM Simulation — {_T} Days · {_N:,} Paths · S₀ = ${_S0}",
        xaxis_title="Trading Days",
        yaxis_title="Simulated Price ($)",
        template="plotly_dark",
        height=430,
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0)"),
    )

    mc_chart   = mo.ui.plotly(fig_mc)
    mc_summary = mo.md(f"""
    | Metric | Value |
    |---|---|
    | 5th Percentile (Downside) | **${_p5:,.2f}** |
    | Median Outcome | **${_p50:,.2f}** |
    | 95th Percentile (Upside) | **${_p95:,.2f}** |
    | Probability of Profit | **{_prob}%** |
    | Paths simulated | **{_N:,}** |
    """)

    return mc_chart, mc_summary


# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _(Counter, mo, pd, px, re, ui_nlp_min, ui_nlp_text):
    # 9: NLP word and bigram frequency analysis
    # Demonstrates: Wk10 — tokenisation, stopword removal, bigram counting,
    #               regex cleaning, Counter, Plotly horizontal bar chart

    _STOP = {
        "the","a","an","and","or","but","in","on","at","to","for","of","with",
        "from","is","are","was","were","be","been","by","as","it","its","this",
        "that","these","those","such","may","could","will","would","should","can",
        "their","our","have","has","had","not","also","which","we","us","they",
        "them","all","any","some","no","if","about","into","over","more","than",
        "being","further","once","here","when","where","each","both",
    }

    _raw   = ui_nlp_text.value.lower()
    _clean = re.sub(r"[^a-z\s]", " ", _raw)    # remove punctuation
    _toks  = [w for w in _clean.split() if len(w) > 3 and w not in _STOP]

    _uni_c = Counter(_toks)
    _bigs  = [f"{_toks[i]} {_toks[i+1]}" for i in range(len(_toks) - 1)]
    _big_c = Counter(_bigs)

    _mf = ui_nlp_min.value

    _df_u = pd.DataFrame(
        [(w, c) for w, c in _uni_c.most_common(20) if c >= _mf],
        columns=["Word", "Frequency"],
    )
    _df_b = pd.DataFrame(
        [(b, c) for b, c in _big_c.most_common(15) if c >= _mf],
        columns=["Bigram", "Frequency"],
    )

    if len(_df_u) > 0:
        _fu = px.bar(_df_u, x="Frequency", y="Word", orientation="h",
                     title="Top Unigrams", color="Frequency",
                     color_continuous_scale="Blues", template="plotly_dark", height=370)
        _fu.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
        nlp_uni = mo.ui.plotly(_fu)
    else:
        nlp_uni = mo.md("*No words found above the minimum frequency.*")

    if len(_df_b) > 0:
        _fb = px.bar(_df_b, x="Frequency", y="Bigram", orientation="h",
                     title="Top Bigrams (two-word phrases)", color="Frequency",
                     color_continuous_scale="Teal", template="plotly_dark", height=340)
        _fb.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
        nlp_big = mo.ui.plotly(_fb)
    else:
        nlp_big = mo.md("*No bigrams found above the minimum frequency.*")

    nlp_stats = mo.md(
        f"**{len(_uni_c)}** unique words · **{len(_big_c)}** unique bigrams · "
        f"Showing frequency ≥ **{_mf}**"
    )

    return nlp_big, nlp_stats, nlp_uni


# ─────────────────────────────────────────────────────────────────────────────
@app.cell
def _(
    box_chart, crosstab_display, mc_chart, mc_summary, mo,
    nlp_big, nlp_stats, nlp_uni,
    reg_summary, scatter_chart,
    ui_ca, ui_cl, ui_eb, ui_mc, ui_re, ui_sal, ui_sectors, ui_ta, ui_tl, ui_years,
    ui_mc_days, ui_mc_drift, ui_mc_sims, ui_mc_vol,
    ui_nlp_min, ui_nlp_text,
    z_display,
):
    # 10: Assemble the multi-tabbed portfolio
    # Demonstrates: Wk04 — mo.ui.tabs, mo.vstack, mo.hstack, mo.callout

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 1: About Me
    # ─────────────────────────────────────────────────────────────────────────
    tab_about = mo.md("""
    ### BSc Accounting & Finance | Data, AI & Finance Enthusiast

    **Summary:**
    - Motivated BSc Accounting & Finance student at Bayes Business School (Predicted: **1st Class**).
    - Independent investment book yielding **90%+ net profit**.
    - Shadowed a Partner at a boutique hedge fund overseeing **£500M+ in fixed-income assets**.
    - Independently designed and deployed **NutriScan AI** — a live Firebase/Gemini PWA,
      currently in initial beta testing. Applying LLM API skills from Week 09 of AF1204.
    - Actively involved in a Fintech startup (FX solutions), assisting with funding, design and testing.

    ---

    **Education:**

    * **BSc Accounting & Finance (Hons)**, Bayes Business School *(Sep 2025 – May 2028)*
      — Predicted: **1st Class**
    * **Bloomberg Market Concept (BMC) Certificate** *(Oct – Dec 2025)*
    * **John Lyon School** — A: Maths · B: Chemistry · C: Biology · 10 GCSEs at 9–7

    ---

    **Technical Skills:**

    | Category | Tools |
    |---|---|
    | Programming | Python · Jupyter Notebook · Marimo |
    | Data & Visualisation | Pandas · NumPy · Plotly · Altair · SciPy |
    | Statistical Methods | OLS Regression · Monte Carlo · Time Series · Hypothesis Testing |
    | Web & AI | Playwright · spaCy NLP · Gemini 1.5 Flash · Firebase · LLM APIs |
    | Finance Tools | yfinance · PyMuPDF · EViews · Bloomberg Terminal |

    ---

    **Work Experience:**

    * **Tutor**, Sherpa *(Jul 2025 – Present)*
      — GCSE and A-Level Maths and Sciences; improved student grades by at least one level
    * **Data & Operations Analyst**, Nice Smile Dental Practice *(Jul – Sep 2025)*
      — Reduced weekly reporting time by 1.5 hours; improved data accuracy by 17%;
        boosted new patient volume by 15%
    * **Investment Banking Shadow**, Observatory Capital Management LLP *(Jul – Sep 2022)*
      — Fixed-income research for £500M+ AUM portfolio; 96% data accuracy under tight deadlines
    """)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 2: Passion Projects — Z-Score + Regression + Monte Carlo
    # ─────────────────────────────────────────────────────────────────────────
    tab_projects = mo.vstack([

        mo.md("## 📊 Passion Projects — Interactive Data Demos"),

        # ── Demo A: Altman Z-Score (Wk01–02) ─────────────────────────────────
        mo.md("### 📐 Demo 1: Altman Z-Score Calculator *(Weeks 01–02)*"),
        mo.callout(mo.md(
            "Enter company financials. The score updates **reactively** — Marimo re-runs "
            "the dependent cell automatically the moment any input changes (Week 02). "
            "The `try/except` block (Week 01) catches `ZeroDivisionError` when "
            "total liabilities are zero, returning `NaN` instead of crashing."
        ), kind="info"),
        mo.hstack([
            mo.vstack([ui_ta, ui_ca, ui_cl, ui_re]),
            mo.vstack([ui_eb, ui_tl, ui_sal, ui_mc]),
        ], justify="center", gap=4),
        z_display,

        mo.md("---"),

        # ── Demo B: Credit Risk Regression (Wk04 + Wk07–08) ──────────────────
        mo.md("### 📉 Demo 2: Credit Risk Regression Analysis *(Weeks 04, 07–08)*"),
        mo.callout(mo.md(
            "This analysis replicates exactly the methodology from **Wk04_DataPreparation**: "
            "OLS regression of Average Cost of Debt on lagged Altman Z-Score, with "
            "interactive sector and year filters. "
            "Techniques used: `groupby().shift(1)` for lagged variables, "
            "`apply(lambda x: ...)` for risk zone classification, "
            "`pd.crosstab()` for contingency analysis, and `np.polyfit` for the "
            "regression line. Statistical significance is tested via "
            "`scipy.stats.linregress`."
        ), kind="info"),
        mo.hstack([ui_sectors, ui_years], justify="start", gap=4),
        reg_summary,
        scatter_chart,
        mo.md("#### 📦 Distribution of Borrowing Costs by Credit Risk Zone"),
        box_chart,
        mo.md("#### 📋 Contingency Table (Wk04: `pd.crosstab` + `apply/lambda`)"),
        crosstab_display,

        mo.md("---"),

        # ── Demo C: Monte Carlo (Self-exploration) ────────────────────────────
        mo.md("### 🎲 Demo 3: Monte Carlo Stock Price Simulation *(Self-exploration)*"),
        mo.callout(mo.md(
            "Uses **Geometric Brownian Motion (GBM)** — the mathematical framework underlying "
            "Black-Scholes options pricing. Directly extends my independent "
            "**10,000-iteration Monte Carlo LBO model** for Coca-Cola, built outside the module "
            "using 10-K/SEC data to stress-test a $92–$96 acquisition price and quantify "
            "IRR/NPV distributions."
        ), kind="info"),
        mo.hstack([ui_mc_days, ui_mc_sims, ui_mc_vol, ui_mc_drift], justify="center", gap=2),
        mc_chart,
        mc_summary,
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 3: Technical Journey — Wk01–10 + NLP Demo
    # ─────────────────────────────────────────────────────────────────────────
    tab_technical = mo.vstack([

        mo.md("## 🧠 Technical Journey — AF1204 Weeks 01 to 10"),

        mo.md("""
        | Week | Topic | Skills Demonstrated |
        |---|---|---|
        | 01 | Python Fundamentals | `try/except`, f-strings, `NaN` handling, function definitions |
        | 02 | Marimo + yfinance | Reactive cells, `mo.ui.number`, live data fetch, Altair gauge |
        | 02x | Panel Data | Nested `for` loops, fiscal-year alignment, `time.sleep` rate limiting |
        | 03 | Interactive Plotly | Violin, joyplot, 3D scatter, `zip()`, colour scales, `hover_data` |
        | 04 | Data Prep & Portfolio | `groupby().shift()`, `apply/lambda`, `pd.crosstab`, OLS regression, HTML-WASM |
        | 06–07 | Web Scraping + OCR | Playwright `async/await`, shadow DOM, PyMuPDF, Tesseract OCR, `curl` bypass |
        | 08 | Statistical Analysis | OLS regression, R², p-value interpretation, `scipy.stats`, `statsmodels` |
        | 09 | LLM API | Gemini 1.5 Flash, multi-modal prompting, JSON response parsing |
        | 10 | NLP & Word Clouds | spaCy transformer, bigrams, lemmatisation, `Counter`, word clouds, GPU/CPU |
        """),

        mo.md("---"),
        mo.md("### 🧩 Live Demo: NLP Word & Bigram Frequency Analyser *(Week 10)*"),
        mo.callout(mo.md(
            "Applies the **tokenisation, stopword removal, and bigram counting** pipeline "
            "from Week 10 — the same approach used on SEC 10-K Risk Factor sections for "
            "Apple, Microsoft, Nvidia and others in `Wk10_BigramCloud_GPUorCPU_Moodle.py`. "
            "Paste any business text and adjust the frequency slider to explore the results."
        ), kind="info"),
        mo.hstack([ui_nlp_text, ui_nlp_min], justify="start", gap=2),
        nlp_stats,
        mo.hstack([nlp_uni, nlp_big], justify="start", gap=2),

        mo.md("---"),
        mo.md("""
        ### 🌐 Week 06–07: Web Scraping & PDF Extraction Pipeline

        Built a **three-notebook Playwright pipeline** for corporate ESG report collection:

        | Notebook | Purpose | Key Techniques |
        |---|---|---|
        | `Wk06-07_1acceptNstoreCookies.py` | Visit site, bypass bot detection, accept cookies | `async/await`, shadow DOM, `navigator.webdriver` evasion |
        | `Wk06-07_2collect_urls.py` | Crawl and filter ESG-related URLs | Playwright page scraping, regex URL filtering |
        | `Wk06-07_3DLnExtract_OCR.py` | Download PDFs, extract keyword pages | PyMuPDF, Tesseract OCR fallback, `curl` for Akamai bypass |

        The pipeline targets Siemens' sustainability pages, collects PDF sustainability
        reports, and extracts pages matching keywords like `"water"`, `"ESG"`, `"pollution"`.
        For scanned PDFs with no text layer, **Tesseract OCR** (`pytesseract`) renders each
        page as an image and extracts text — with an NLTK-based `is_meaningful()` filter to
        remove OCR noise.

        ---

        ### 🤖 Week 09: LLM API — Applied to NutriScan AI

        The LLM API techniques from Week 09 were applied directly in **NutriScan AI**:
        - Sends structured multi-modal prompts to **Gemini 1.5 Flash** via OpenRouter
        - Parses JSON nutrition estimates from image, label, and natural-language inputs
        - Generates weekly personalised insight paragraphs summarising the user's nutrition
        """),
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 4: Personal Interests
    # ─────────────────────────────────────────────────────────────────────────
    tab_interests = mo.vstack([

        mo.md("## ✨ Personal Projects & Interests"),

        mo.md("""
        ### 📱 NutriScan AI — Live App *(Initial Beta Testing)*

        An independently designed and deployed **Progressive Web App (PWA)** that uses
        **Gemini 1.5 Flash** multi-modal AI to scan meals from photos, nutrition labels,
        and barcodes — estimating calories and protein instantly.
        Applies **LLM API skills from Week 09** in a real production environment.

        **Live:** [food-app-cb863.web.app](https://food-app-cb863.web.app/)

        | Feature | Details |
        |---|---|
        | 📸 Photo scanning | AI estimates calories & protein from a plate photo |
        | 🏷️ Label OCR | Reads exact values from packaged food nutrition labels |
        | 📦 Barcode scanner | EAN/UPC lookup via Open Food Facts |
        | ✍️ Natural language | "Bowl of pasta with chicken" — AI estimates macros |
        | 🔥 Streak & Badges | 7-day tracker, 8 achievement badges |
        | 📈 Progress charts | 14-day weight & body fat line charts |
        | 🤖 Weekly AI insight | Personalised Gemini paragraph about your week's nutrition |
        | ☁️ Cloud sync | Firebase Firestore for multi-device data |

        **Stack:** Firebase Hosting · Firestore · Gemini 1.5 Flash · OpenRouter · Vanilla JS

        ---

        ### 📈 Probabilistic Investment Analysis: 10,000-Iteration Monte Carlo

        Built a full **three-statement LBO model for Coca-Cola** using 10-K/SEC data:
        - Projected revenue, EBITDA, net income, capex, D&A, working capital, and FCF
        - Valued via DCF, EV, equity value, and exit multiples
        - Executed **10,000-iteration Monte Carlo simulation** in Python/Excel
        - Stress-tested $92–$96 acquisition price; quantified IRR/NPV distributions,
          probability of negative cash flows; produced histogram, tornado chart,
          and correlation matrix

        *Tools: Python · NumPy · SciPy · Excel · SEC EDGAR 10-K data*

        ---

        ### 📈 Independent Investment Portfolio

        Maintaining a personal investment book with a **90%+ net profit** since inception.
        Applies regression analysis, DCF modelling, and time-series analysis using
        Python, EViews, and Bloomberg Terminal.

        ---

        ### 🎯 Hobbies

        🎹 Piano · ⚽ First-team football · 🏏 County Cup cricket · ♟ Regional chess · 🚴 Cycling
        """),
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # Assemble tabs and display
    # ─────────────────────────────────────────────────────────────────────────
    portfolio_tabs = mo.ui.tabs({
        "📄 About Me":            tab_about,
        "📊 Passion Projects":    tab_projects,
        "🧠 Technical Journey":   tab_technical,
        "✨ Personal Interests":  tab_interests,
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
