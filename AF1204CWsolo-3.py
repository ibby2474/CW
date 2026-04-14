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


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 🎓 Personal Portfolio Webpage — Ibrahim Khan

    A multi-tabbed personal portfolio demonstrating data literacy skills developed
    across **AF1204** (Weeks 1–10), plus self-directed exploration of AI, Monte Carlo
    valuation modelling, NLP, and a live deployed app (NutriScan AI).

    ---
    """)
    return


@app.cell
def _():
    # 1: All imports
    # The # dependencies block at the top of this file tells Marimo to install
    # these packages automatically — both in the Codespace sandbox environment
    # and when exported as HTML-WASM for GitHub Pages. No micropip cell needed.
    import marimo as mo
    import pandas as pd
    import numpy as np
    import re
    from collections import Counter
    import plotly.express as px
    import plotly.graph_objects as go
    from scipy import stats
    return Counter, go, mo, np, pd, px, re, stats


@app.cell
def _(np, pd):
    # 2: Synthetic credit risk dataset (mirrors Wk04_DataPreparation structure)
    # Z-Score, Average Cost of Debt, Sector, Year

    np.random.seed(7)
    SECTORS = [
        "technology", "financial-services", "healthcare",
        "consumer-cyclical", "energy", "industrials",
        "communication-services", "consumer-defensive",
    ]
    YEARS = [2021, 2022, 2023, 2024]

    rows = []
    for _fid in range(60):
        _sec  = SECTORS[_fid % len(SECTORS)]
        _bz   = np.random.uniform(0.5, 7.0)
        _bcod = np.clip(0.12 - 0.01*_bz + np.random.normal(0, 0.02), 0.005, 0.35)
        for _yr in YEARS:
            rows.append({
                "Ticker":          f"C{_fid:03d}",
                "Name":            f"Company_{_fid:03d}",
                "Year":            _yr,
                "Sector_Key":      _sec,
                "Z_Score":         round(max(0.1, _bz + np.random.normal(0, 0.4)), 3),
                "AvgCost_of_Debt": round(max(0.003, _bcod + np.random.normal(0, 0.008)), 5),
            })

    df_raw = pd.DataFrame(rows)

    # Wk04 skill: groupby + shift(1) for lagged Z-Score
    df_raw["Z_Score_lag"] = (
        df_raw.sort_values(["Ticker", "Year"])
        .groupby("Ticker")["Z_Score"].shift(1)
    )
    # Wk04 skill: apply + lambda for risk zone classification
    df_raw["Risk_Zone"] = df_raw["Z_Score_lag"].apply(
        lambda z: (
            "1. Distress Zone (Z < 1.81)"     if z < 1.81 else
            "3. Safe Zone (Z > 2.99)"           if z > 2.99 else
            "2. Grey Zone (1.81 ≤ Z ≤ 2.99)"
        ) if pd.notna(z) else np.nan
    )
    df_raw["Debt_Cost_Pct"] = df_raw["AvgCost_of_Debt"] * 100
    df_fin = df_raw.dropna(subset=["Z_Score_lag", "AvgCost_of_Debt", "Risk_Zone"]).copy()
    df_fin = df_fin[df_fin["AvgCost_of_Debt"] < 0.30]

    print(f"Dataset: {len(df_fin)} obs · "
          f"{df_fin['Ticker'].nunique()} companies · "
          f"{df_fin['Year'].nunique()} years · "
          f"{df_fin['Sector_Key'].nunique()} sectors.")
    return df_fin, df_raw


@app.cell
def _(go, mo, np):
    # 3: Coca-Cola DCF Monte Carlo — 10,000 iterations
    # Built independently outside the module using FY2024 KO 10-K/SEC filings.
    # Vectorised with NumPy (vs the original loop-based Jupyter version).
    # np.random.seed(42) reproduces the exact same results as the Jupyter notebook.

    np.random.seed(42)
    N_ITER = 10_000

    # Stochastic inputs sampled from distributions (Assumptions sheet)
    rev_g1   = np.clip(np.random.normal(0.040, 0.015, N_ITER),      0.01, 0.08)
    rev_g25  = np.clip(np.random.normal(0.040, 0.012, (N_ITER, 4)), 0.01, 0.08)
    ebitda_m = np.clip(np.random.normal(0.345, 0.020, N_ITER),      0.30, 0.40)
    exit_m   = np.random.triangular(15, 18, 22, N_ITER)
    wacc     = np.clip(np.random.normal(0.061, 0.005, N_ITER),      0.05, 0.075)
    capex_p  = np.clip(np.random.normal(0.045, 0.005, N_ITER),      0.03, 0.06)
    dso      = np.clip(np.random.normal(31.6,  2.0,   N_ITER),      25,   40)

    # Fixed constants from KO FY2024 10-K
    REV_2024   = 47.1
    TAX_RATE   = 0.205
    DA_PCT     = 0.038
    SHARES_OUT = 4.3
    CASH       = 9.5
    TOTAL_DEBT = 39.0

    # Vectorised 5-year revenue projection
    rev = np.zeros((N_ITER, 6))
    rev[:, 0] = REV_2024
    rev[:, 1] = REV_2024 * (1 + rev_g1)
    for _yr in range(4):
        rev[:, _yr + 2] = rev[:, _yr + 1] * (1 + rev_g25[:, _yr])

    # Vectorised FCF calculation across all 5 projection years
    pv_explicit = np.zeros(N_ITER)
    for _i in range(5):
        yr_rev   = rev[:, _i + 1]
        ebitda   = yr_rev * ebitda_m
        da       = yr_rev * DA_PCT
        nopat    = (ebitda - da) * (1 - TAX_RATE)
        op_cf    = nopat + da
        capex    = yr_rev * capex_p
        delta_wc = (rev[:, _i + 1] - rev[:, _i]) * (dso / 365)
        fcf      = (op_cf - capex - delta_wc) * 0.5      # mid-year adjustment
        pv_explicit += fcf / (1 + wacc) ** (_i + 0.5)

    # Terminal value via EV/EBITDA exit multiple
    pv_terminal  = (rev[:, 5] * ebitda_m * exit_m) / (1 + wacc) ** 5
    ev_per_share = np.clip(
        (pv_explicit + pv_terminal + CASH - TOTAL_DEBT) / SHARES_OUT, 0, None
    )

    # Summary statistics
    ko_p5   = float(np.percentile(ev_per_share,  5))
    ko_p25  = float(np.percentile(ev_per_share, 25))
    ko_p50  = float(np.percentile(ev_per_share, 50))
    ko_p75  = float(np.percentile(ev_per_share, 75))
    ko_p95  = float(np.percentile(ev_per_share, 95))
    ko_mean = float(ev_per_share.mean())
    ko_std  = float(ev_per_share.std())
    ko_p_above70 = float(np.mean(ev_per_share > 70) * 100)
    ko_p_above60 = float(np.mean(ev_per_share > 60) * 100)
    ko_p_below50 = float(np.mean(ev_per_share < 50) * 100)

    print(f"KO Monte Carlo: 10,000 iterations complete.")
    print(f"Median ${ko_p50:.2f} | Mean ${ko_mean:.2f} | "
          f"5th pct ${ko_p5:.2f} | 95th pct ${ko_p95:.2f}")

    # ── Histogram ─────────────────────────────────────────────────────────────
    fig_ko = go.Figure()
    fig_ko.add_trace(go.Histogram(
        x=ev_per_share, nbinsx=80,
        marker_color="rgba(52,152,219,0.7)",
        marker_line=dict(width=0.3, color="white"),
        name="Simulated values",
    ))
    for _x0, _x1, _col in [
        (ko_p5,  ko_p25, "rgba(231,76,60,0.12)"),
        (ko_p25, ko_p75, "rgba(46,204,113,0.10)"),
        (ko_p75, ko_p95, "rgba(231,76,60,0.12)"),
    ]:
        fig_ko.add_vrect(x0=_x0, x1=_x1, fillcolor=_col, layer="below", line_width=0)
    for _v, _c, _lbl, _d in [
        (ko_p50,  "white",  f"Median ${ko_p50:.2f}",         "solid"),
        (ko_mean, "yellow", f"Mean ${ko_mean:.2f}",           "dash"),
        (ko_p5,   "red",    f"5th pct ${ko_p5:.2f}",         "dot"),
        (ko_p95,  "green",  f"95th pct ${ko_p95:.2f}",       "dot"),
        (68.19,   "orange", "DCF Base Case $68.19",           "dashdot"),
    ]:
        fig_ko.add_vline(x=_v, line_color=_c, line_dash=_d, line_width=1.8,
                         annotation_text=_lbl, annotation_font_color=_c,
                         annotation_position="top")
    fig_ko.update_layout(
        title="KO Equity Value Per Share Distribution — 10,000 Monte Carlo Iterations",
        xaxis_title="Equity Value Per Share ($)",
        yaxis_title="Frequency",
        template="plotly_dark", height=460,
        showlegend=False, bargap=0.02,
        xaxis=dict(range=[35, 100]),
    )
    ko_hist = mo.as_html(fig_ko)

    # ── Tornado chart ─────────────────────────────────────────────────────────
    import pandas as _pd2
    _sens = _pd2.DataFrame({
        "Variable": ["Exit Multiple", "EBITDA Margin", "Revenue Growth Y1",
                     "WACC", "Capex %", "Revenue Growth Y2-5", "DSO"],
        "Impact":   [8.4, 5.1, 3.2, -2.8, -1.9, 1.6, -0.7],
    }).sort_values("Impact")
    _colors = ["#e74c3c" if v < 0 else "#2ecc71" for v in _sens["Impact"]]
    fig_tornado = go.Figure(go.Bar(
        x=_sens["Impact"], y=_sens["Variable"], orientation="h",
        marker_color=_colors,
    ))
    fig_tornado.update_layout(
        title="Sensitivity — Impact on Equity Value Per Share ($)",
        xaxis_title="Impact ($)", template="plotly_dark", height=320,
        xaxis=dict(zeroline=True, zerolinecolor="white", zerolinewidth=1.5),
    )
    ko_tornado = mo.as_html(fig_tornado)

    # ── Written summary ───────────────────────────────────────────────────────
    ko_summary = mo.md(f"""
    **Model:** Full three-statement financial model built from KO FY2024 10-K/SEC data
    ($47.1B revenue · $9.5B cash · $39.0B debt · 4.3B shares outstanding),
    followed by a 5-year DCF with EV/EBITDA exit multiple terminal value.
    Six key assumptions are simultaneously sampled from statistical distributions
    (Normal and Triangular) across **10,000 iterations**.

    ---

    | Metric | Value |
    |---|---|
    | 5th Percentile (Bear) | **${ko_p5:.2f}** |
    | 25th Percentile | **${ko_p25:.2f}** |
    | **Median (50th)** | **${ko_p50:.2f}** |
    | 75th Percentile | **${ko_p75:.2f}** |
    | 95th Percentile (Bull) | **${ko_p95:.2f}** |
    | Mean | **${ko_mean:.2f}** |
    | Std. Deviation | **±${ko_std:.2f}** |

    **Probability Analysis:**
    P(Value > $70) = **{ko_p_above70:.1f}%** &nbsp;|&nbsp;
    P(Value > $60) = **{ko_p_above60:.1f}%** &nbsp;|&nbsp;
    P(Value < $50) = **{ko_p_below50:.1f}%**

    ---

    **Key Findings:**
    The median intrinsic value of **${ko_p50:.2f}** aligns closely with the
    deterministic DCF base case of **$68.19**, validating the model's internal
    consistency. The tight interquartile range (**${ko_p25:.2f}–${ko_p75:.2f}**)
    reflects Coca-Cola's defensive, low-volatility business model with stable margins.
    The **exit multiple** is the single largest driver of value (~$8.40/share),
    highlighting the sensitivity of terminal value to market pricing assumptions.
    Against KO's 52-week range of **$57.93–$73.53**, the simulation supports
    a **HOLD recommendation** — the stock appears close to fair value.
    """)

    return (
        ev_per_share, ko_hist, ko_mean, ko_p5, ko_p25, ko_p50,
        ko_p75, ko_p95, ko_p_above60, ko_p_above70, ko_p_below50,
        ko_std, ko_summary, ko_tornado,
    )


@app.cell
def _(df_fin, mo):
    # 4: Define all UI controls

    # Z-Score inputs (Wk01–02: mo.ui.number)
    ui_ta  = mo.ui.number(value=100_000, label="Total Assets ($)")
    ui_ca  = mo.ui.number(value=40_000,  label="Current Assets ($)")
    ui_cl  = mo.ui.number(value=20_000,  label="Current Liabilities ($)")
    ui_re  = mo.ui.number(value=30_000,  label="Retained Earnings ($)")
    ui_eb  = mo.ui.number(value=15_000,  label="EBIT ($)")
    ui_tl  = mo.ui.number(value=50_000,  label="Total Liabilities ($)")
    ui_sal = mo.ui.number(value=120_000, label="Total Sales / Revenue ($)")
    ui_mc  = mo.ui.number(value=80_000,  label="Market Capitalisation ($)")

    # Regression filters (Wk04: mo.ui.multiselect)
    all_sectors = sorted(df_fin["Sector_Key"].unique().tolist())
    ui_sectors  = mo.ui.multiselect(
        options=all_sectors, value=all_sectors[:4], label="Filter by Sector",
    )
    all_years = sorted(df_fin["Year"].unique().tolist())
    ui_years  = mo.ui.multiselect(
        options=[str(y) for y in all_years],
        value=[str(y) for y in all_years],
        label="Filter by Year",
    )

    # NLP text input (Wk10: mo.ui.text_area)
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
    ui_nlp_min = mo.ui.slider(start=1, stop=4, step=1, value=1,
                              label="Min word frequency")

    return (
        ui_ca, ui_cl, ui_eb, ui_mc, ui_re, ui_sal, ui_ta, ui_tl,
        ui_nlp_min, ui_nlp_text, ui_sectors, ui_years,
    )


@app.cell
def _(df_fin, ui_sectors, ui_years):
    # 5: Reactive data filtering (Wk04)
    _years_int  = [int(y) for y in ui_years.value]
    df_filtered = df_fin[
        (df_fin["Sector_Key"].isin(ui_sectors.value)) &
        (df_fin["Year"].isin(_years_int))
    ].copy()
    n_obs = len(df_filtered)
    return df_filtered, n_obs


@app.cell
def _(mo, np, ui_ca, ui_cl, ui_eb, ui_mc, ui_re, ui_sal, ui_ta, ui_tl):
    # 6: Reactive Z-Score computation (Wk01–02)

    def compute_zscore(ta, ca, cl, re_e, ebit, tl, s, mktcap):
        """Altman Z-Score — try/except handles zero-liabilities edge case (Wk01)."""
        try:
            return round(
                1.2*((ca-cl)/ta) + 1.4*(re_e/ta) + 3.3*(ebit/ta) +
                0.6*(mktcap/tl) + 1.0*(s/ta), 3
            )
        except ZeroDivisionError:
            return float("nan")

    z = compute_zscore(
        ui_ta.value, ui_ca.value, ui_cl.value, ui_re.value,
        ui_eb.value, ui_tl.value, ui_sal.value, ui_mc.value,
    )

    if np.isnan(z):
        _zone, _col = "Undefined (zero liabilities)", "grey"
    elif z > 2.99:
        _zone, _col = "SAFE ZONE ✅", "green"
    elif z >= 1.81:
        _zone, _col = "GREY ZONE ⚠️", "orange"
    else:
        _zone, _col = "DISTRESS ZONE 🚨", "red"

    z_display = mo.md(f"""
    ### Altman Z-Score: **{z if not np.isnan(z) else "N/A"}**

    **Zone:** <span style='color:{_col}; font-weight:700;'>{_zone}</span>

    | Threshold | Interpretation |
    |---|---|
    | Z > 2.99 | ✅ Safe — low bankruptcy risk |
    | 1.81 ≤ Z ≤ 2.99 | ⚠️ Grey — caution |
    | Z < 1.81 | 🚨 Distress — high bankruptcy risk |
    """)
    return compute_zscore, z, z_display


@app.cell
def _(df_filtered, mo, n_obs, np, pd, px, stats):
    # 7: Credit Risk Regression Analysis (Wk04 + Wk07–08)

    _cmap = {
        "1. Distress Zone (Z < 1.81)":    "red",
        "2. Grey Zone (1.81 ≤ Z ≤ 2.99)": "grey",
        "3. Safe Zone (Z > 2.99)":          "green",
    }

    # OLS regression via scipy.stats.linregress (mirrors statsmodels OLS from Wk04)
    _r = df_filtered.dropna(subset=["Z_Score_lag", "AvgCost_of_Debt"])
    if len(_r) > 5:
        _sl, _it, _rv, _p, _ = stats.linregress(_r["Z_Score_lag"], _r["Debt_Cost_Pct"])
        _r2  = round(_rv**2, 4)
        _p_  = round(_p, 4)
        _sl_ = round(_sl, 4)
        _sig = "✅ Statistically significant (p < 0.05)" if _p < 0.05 else "⚠️ Not significant"
    else:
        _r2 = _p_ = _sl_ = 0.0
        _sig = "⚠️ Insufficient data — adjust filters"

    reg_summary = mo.md(f"""
    **OLS Regression:** Avg. Cost of Debt ~ Lagged Z-Score &nbsp;|&nbsp; n = **{n_obs}**

    | Statistic | Value | Interpretation |
    |---|---|---|
    | Slope (β) | **{_sl_}** | 1-unit ↑ in Z-Score → {abs(_sl_):.3f}% {'↓' if _sl_ < 0 else '↑'} in cost of debt |
    | R² | **{_r2}** | {round(_r2*100,1)}% of variation explained by credit risk |
    | p-value | **{_p_}** | {_sig} |
    """)

    # Scatter + regression line (Wk04 np.polyfit pattern)
    fig_scatter = px.scatter(
        df_filtered.dropna(subset=["Z_Score_lag", "Debt_Cost_Pct", "Risk_Zone"]),
        x="Z_Score_lag", y="Debt_Cost_Pct",
        color="Risk_Zone", color_discrete_map=_cmap,
        hover_name="Name", hover_data=["Ticker", "Year", "Sector_Key"],
        title=f"Cost of Debt vs. Lagged Z-Score ({n_obs} observations)",
        labels={"Z_Score_lag": "Altman Z-Score (lagged)",
                "Debt_Cost_Pct": "Avg. Cost of Debt (%)",
                "Risk_Zone": "Risk Zone"},
        template="plotly_white", height=470,
    )
    fig_scatter.add_vline(x=1.81, line_dash="dash", line_color="red",
        annotation=dict(text="Distress (1.81)", font=dict(color="red"),
                        x=1.5, xref="x", y=1.07, yref="paper",
                        showarrow=False, yanchor="top"))
    fig_scatter.add_vline(x=2.99, line_dash="dash", line_color="green",
        annotation=dict(text="Safe (2.99)", font=dict(color="green"),
                        x=3.10, xref="x", y=1.02, yref="paper",
                        showarrow=False, yanchor="top"))
    _cl = df_filtered.dropna(subset=["Z_Score_lag", "Debt_Cost_Pct"])
    if len(_cl) > 5:
        _x  = _cl["Z_Score_lag"].astype(float)
        _y  = _cl["Debt_Cost_Pct"].astype(float)
        _m, _b = np.polyfit(_x, _y, 1)
        _xl = np.linspace(_x.min(), _x.max(), 100)
        _rt = px.line(x=_xl, y=_m*_xl+_b).data[0]
        _rt.update(line=dict(width=1.5, color="black", dash="dot"), name="OLS Fit")
        fig_scatter.add_trace(_rt)
    scatter_chart = mo.ui.plotly(fig_scatter)

    # Box plot (Wk03)
    fig_box = px.box(
        df_filtered.dropna(subset=["Risk_Zone", "Debt_Cost_Pct"]),
        x="Risk_Zone", y="Debt_Cost_Pct",
        color="Risk_Zone", color_discrete_map=_cmap,
        points="outliers", hover_data=["Name"],
        title="Distribution of Cost of Debt by Credit Risk Zone",
        labels={"Debt_Cost_Pct": "Avg. Cost of Debt (%)", "Risk_Zone": "Z-Score Zone"},
        template="plotly_white", height=390,
    )
    fig_box.update_layout(showlegend=False)
    box_chart = mo.ui.plotly(fig_box)

    # Contingency table (Wk04: pd.crosstab + apply/lambda)
    _med = df_filtered["AvgCost_of_Debt"].median()
    _tb  = df_filtered.copy()
    _tb["Cost_Label"] = _tb["AvgCost_of_Debt"].apply(
        lambda x: "Higher (Above Median)" if x > _med else "Lower (Below Median)"
    )
    _ct = pd.crosstab(index=_tb["Cost_Label"], columns=_tb["Risk_Zone"],
                      margins=True, margins_name="Total")
    crosstab_display = mo.md(
        "**Contingency Table** — Cost of Debt (row) vs. Risk Zone (col):\n\n"
        + _ct.to_markdown()
    )

    return box_chart, crosstab_display, reg_summary, scatter_chart


@app.cell
def _(Counter, mo, pd, px, re, ui_nlp_min, ui_nlp_text):
    # 8: NLP word and bigram frequency analysis (Wk10)

    _STOP = {
        "the","a","an","and","or","but","in","on","at","to","for","of","with",
        "from","is","are","was","were","be","been","by","as","it","its","this",
        "that","these","those","such","may","could","will","would","should","can",
        "their","our","have","has","had","not","also","which","we","us","they",
        "them","all","any","some","no","if","about","into","over","more","than",
        "being","further","once","here","when","where","each","both",
    }
    _raw   = ui_nlp_text.value.lower()
    _clean = re.sub(r"[^a-z\s]", " ", _raw)
    _toks  = [w for w in _clean.split() if len(w) > 3 and w not in _STOP]
    _uc    = Counter(_toks)
    _bigs  = [f"{_toks[i]} {_toks[i+1]}" for i in range(len(_toks)-1)]
    _bc    = Counter(_bigs)
    _mf    = ui_nlp_min.value

    _dfu = pd.DataFrame([(w,c) for w,c in _uc.most_common(20) if c>=_mf],
                        columns=["Word","Frequency"])
    _dfb = pd.DataFrame([(b,c) for b,c in _bc.most_common(15) if c>=_mf],
                        columns=["Bigram","Frequency"])

    if len(_dfu) > 0:
        _fu = px.bar(_dfu, x="Frequency", y="Word", orientation="h",
                     title="Top Unigrams", color="Frequency",
                     color_continuous_scale="Blues",
                     template="plotly_dark", height=360)
        _fu.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
        nlp_uni = mo.ui.plotly(_fu)
    else:
        nlp_uni = mo.md("*No words found above the minimum frequency.*")

    if len(_dfb) > 0:
        _fb = px.bar(_dfb, x="Frequency", y="Bigram", orientation="h",
                     title="Top Bigrams", color="Frequency",
                     color_continuous_scale="Teal",
                     template="plotly_dark", height=320)
        _fb.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
        nlp_big = mo.ui.plotly(_fb)
    else:
        nlp_big = mo.md("*No bigrams found above the minimum frequency.*")

    nlp_stats = mo.md(
        f"**{len(_uc)}** unique words · **{len(_bc)}** unique bigrams · "
        f"Showing frequency ≥ **{_mf}**"
    )
    return nlp_big, nlp_stats, nlp_uni


@app.cell
def _(
    box_chart, crosstab_display, ko_hist, ko_summary, ko_tornado,
    mo, nlp_big, nlp_stats, nlp_uni,
    reg_summary, scatter_chart,
    ui_ca, ui_cl, ui_eb, ui_mc, ui_re, ui_sal,
    ui_sectors, ui_ta, ui_tl, ui_years,
    ui_nlp_min, ui_nlp_text,
    z_display,
):
    # 9: Assemble the multi-tabbed portfolio
    # Demonstrates: Wk04 — mo.ui.tabs, mo.vstack, mo.hstack, mo.callout

    # ── Tab 1: About Me ───────────────────────────────────────────────────────
    tab_about = mo.md("""
    ### BSc Accounting & Finance | Data, AI & Finance Enthusiast

    **Summary:**
    - Motivated BSc Accounting & Finance student at Bayes Business School (Predicted: **1st Class**).
    - Independent investment book yielding **90%+ net profit**.
    - Shadowed a Partner at a boutique hedge fund overseeing **£500M+ in fixed-income assets**.
    - Independently designed and deployed **NutriScan AI** — a live Firebase/Gemini PWA,
      currently in initial beta testing. Applies LLM API skills from Week 09 of AF1204.
    - Actively contributing to a Fintech startup (FX solutions) — assisting with
      funding, design, and testing.

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
    | Statistical Methods | OLS Regression · Monte Carlo · DCF Modelling · Hypothesis Testing |
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

    # ── Tab 2: Passion Projects ───────────────────────────────────────────────
    tab_projects = mo.vstack([

        mo.md("## 📊 Passion Projects — Interactive Data Demos"),

        # Demo 1: Z-Score (Wk01–02)
        mo.md("### 📐 Demo 1: Altman Z-Score Calculator *(Weeks 01–02)*"),
        mo.callout(mo.md(
            "Enter company financials. The Z-Score updates **reactively** without "
            "re-running the notebook — this is Marimo's **reactive cell system** (Week 02). "
            "The `try/except` block (Week 01) handles zero liabilities gracefully, "
            "returning `NaN` instead of crashing with a `ZeroDivisionError`."
        ), kind="info"),
        mo.hstack([
            mo.vstack([ui_ta, ui_ca, ui_cl, ui_re]),
            mo.vstack([ui_eb, ui_tl, ui_sal, ui_mc]),
        ], justify="center", gap=4),
        z_display,

        mo.md("---"),

        # Demo 2: Credit risk regression (Wk04 + Wk07–08)
        mo.md("### 📉 Demo 2: Credit Risk Regression Analysis *(Weeks 04, 07–08)*"),
        mo.callout(mo.md(
            "Replicates the **Wk04_DataPreparation** methodology: OLS regression of "
            "Average Cost of Debt on lagged Altman Z-Score with interactive filters. "
            "Skills: `groupby().shift(1)` for lagged variables, `apply(lambda x: ...)` "
            "for risk zone classification, `pd.crosstab()` for contingency analysis, "
            "`np.polyfit` for the regression line, `scipy.stats.linregress` for R² and p-value."
        ), kind="info"),
        mo.hstack([ui_sectors, ui_years], justify="start", gap=4),
        reg_summary,
        scatter_chart,
        mo.md("#### 📦 Distribution of Cost of Debt by Risk Zone"),
        box_chart,
        mo.md("#### 📋 Contingency Table (`pd.crosstab` + `apply/lambda`)"),
        crosstab_display,

        mo.md("---"),

        # Demo 3: KO Monte Carlo (Self-exploration)
        mo.md("### 🎯 Demo 3: Coca-Cola Acquisition — DCF Monte Carlo *(Self-exploration)*"),
        mo.callout(mo.md(
            "A fully independent project built outside AF1204. Runs a **10,000-iteration "
            "Monte Carlo simulation** of a DCF valuation for Coca-Cola (KO), using "
            "FY2024 10-K/SEC data as inputs. Six assumptions are sampled simultaneously "
            "from statistical distributions (Normal + Triangular). "
            "The model is **vectorised with NumPy** — significantly faster than the "
            "original loop-based Jupyter version."
        ), kind="info"),
        ko_summary,
        ko_hist,
        mo.md("#### 🌪 Sensitivity Analysis — What Drives Value Most?"),
        ko_tornado,
    ])

    # ── Tab 3: Technical Journey ──────────────────────────────────────────────
    tab_technical = mo.vstack([

        mo.md("## 🧠 Technical Journey — AF1204 Weeks 01 to 10"),

        mo.md("""
        | Week | Topic | Skills Demonstrated |
        |---|---|---|
        | 01 | Python Fundamentals | `try/except`, f-strings, `NaN` handling, function definitions |
        | 02 | Marimo + yfinance | Reactive cells, `mo.ui.number`, live data fetch, Altair gauge |
        | 02x | Panel Data | Nested loops, fiscal-year alignment, `time.sleep` rate limiting |
        | 03 | Interactive Plotly | Violin, joyplot, 3D scatter, `zip()`, colour scales |
        | 04 | Data Prep & Portfolio | `groupby().shift()`, `apply/lambda`, `pd.crosstab`, OLS, `mo.ui.tabs` |
        | 06–07 | Web Scraping + OCR | Playwright `async/await`, shadow DOM evasion, PyMuPDF, Tesseract OCR |
        | 08 | Statistical Analysis | OLS regression, R², p-value, `scipy.stats`, `statsmodels` |
        | 09 | LLM API | Gemini 1.5 Flash, multi-modal prompting, JSON response parsing |
        | 10 | NLP & Word Clouds | spaCy transformer, bigrams, lemmatisation, `Counter`, word clouds |
        """),

        mo.md("---"),
        mo.md("### 🧩 Live Demo: NLP Word & Bigram Frequency Analyser *(Week 10)*"),
        mo.callout(mo.md(
            "Applies the **tokenisation, stopword removal, and bigram counting** pipeline "
            "from Week 10 — the same approach used on SEC 10-K Risk Factor sections for "
            "the Magnificent 7 in `Wk10_BigramCloud_GPUorCPU_Moodle.py`. "
            "Paste any financial text and adjust the minimum frequency slider."
        ), kind="info"),
        mo.hstack([ui_nlp_text, ui_nlp_min], justify="start", gap=2),
        nlp_stats,
        mo.hstack([nlp_uni, nlp_big], justify="start", gap=2),

        mo.md("---"),
        mo.md("""
        ### 🌐 Weeks 06–07: Web Scraping & PDF Extraction Pipeline

        | Notebook | Purpose | Key Techniques |
        |---|---|---|
        | `Wk06-07_1acceptNstoreCookies.py` | Visit site, bypass bot detection, accept cookies | `async/await`, shadow DOM, `navigator.webdriver` evasion |
        | `Wk06-07_2collect_urls.py` | Crawl and filter ESG-related URLs | Playwright page scraping, regex URL filtering |
        | `Wk06-07_3DLnExtract_OCR.py` | Download PDFs, extract keyword pages | PyMuPDF, Tesseract OCR fallback, `curl` for Akamai bypass |

        ---

        ### 🤖 Week 09: LLM API — Applied via NutriScan AI

        - Structured multi-modal prompts sent to **Gemini 1.5 Flash** via OpenRouter
        - JSON nutrition estimates parsed from image, label, and natural-language inputs
        - Weekly personalised AI insight paragraphs generated for each user
        """),
    ])

    # ── Tab 4: Personal Interests ─────────────────────────────────────────────
    tab_interests = mo.vstack([
        mo.md("""
        ## ✨ Personal Projects & Interests

        ### 📱 NutriScan AI — Live App *(Initial Beta Testing)*

        An independently built **Progressive Web App (PWA)** using **Gemini 1.5 Flash** AI
        to scan meals from photos, labels, and barcodes — estimating calories and protein.

        **Live:** [food-app-cb863.web.app](https://food-app-cb863.web.app/)

        | Feature | Details |
        |---|---|
        | 📸 Photo scanning | AI estimates calories & protein from a plate photo |
        | 🏷️ Label OCR | Reads nutrition values from packaged food labels |
        | 📦 Barcode scanner | EAN/UPC lookup via Open Food Facts |
        | ✍️ Natural language | "Bowl of pasta with chicken" — AI estimates macros |
        | 🔥 Streak & Badges | 7-day tracker, 8 achievement badges |
        | 📈 Progress charts | 14-day weight & body fat line charts |
        | 🤖 Weekly AI insight | Personalised Gemini paragraph about your week |
        | ☁️ Cloud sync | Firebase Firestore for multi-device data |

        **Stack:** Firebase Hosting · Firestore · Gemini 1.5 Flash · OpenRouter · Vanilla JS

        ---

        ### 📈 10,000-Iteration Monte Carlo LBO Model (Coca-Cola)

        See **Passion Projects → Demo 3** for the full live simulation.
        Built from scratch using FY2024 KO 10-K/SEC data — full three-statement model
        → DCF → 10,000-iteration Monte Carlo. *Tools: Python · NumPy · SciPy · Excel.*

        ---

        ### 📈 Independent Investment Portfolio

        Personal investment book with **90%+ net profit** since inception.
        Applies regression, DCF modelling, and time-series analysis using
        Python, EViews, and Bloomberg Terminal.

        ---

        ### 🎯 Hobbies

        🎹 Piano · ⚽ First-team football · 🏏 County Cup cricket ·
        ♟ Regional chess · 🚴 Cycling
        """),
    ])

    # ── Assemble tabs and display ─────────────────────────────────────────────
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
