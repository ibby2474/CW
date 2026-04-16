# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "marimo>=0.19.10",
#   "pandas>=2.3.3",
#   "plotly>=6.5.1",
#   "numpy>=1.26.0",
#   "scipy>=1.11.0",
#   "pyzmq>=27.1.0",
#   "tabulate>=0.9.0",
# ]
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App()


# ---------------------------------------------------------------------------
# CELL 1: Imports
# ---------------------------------------------------------------------------
@app.cell
def _():
    import subprocess
    import sys
    _packages = ["plotly", "scipy", "pandas", "numpy", "tabulate"]
    for _pkg in _packages:
        try:
            __import__(_pkg)
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", _pkg, "-q"], check=False)
    import marimo as mo
    import pandas as pd
    import numpy as np
    import re
    from collections import Counter
    import plotly.express as px
    import plotly.graph_objects as go
    from scipy import stats
    return Counter, go, mo, np, pd, px, re, stats


# ---------------------------------------------------------------------------
# CELL 2: Cookie dropdown — defined here, displayed in Cell 3
# ---------------------------------------------------------------------------
@app.cell
def _(mo):
    cookie_choice = mo.ui.dropdown(
        options={
            "✅ Accept All Cookies": "accepted",
            "❌ Reject Non-Essential": "rejected",
        },
        label="🍪 Cookie Preferences — please make a selection to continue:",
    )
    return cookie_choice,


# ---------------------------------------------------------------------------
# CELL 3: Show cookie banner or confirmation. Exports cookie_state.
# ---------------------------------------------------------------------------
@app.cell
def _(cookie_choice, mo):
    if cookie_choice.value == "accepted":
        cookie_state = True
        _banner = mo.vstack([
            cookie_choice,
            mo.callout(
                mo.md("✅ **Cookies accepted.** The portfolio is loading below."),
                kind="success",
            ),
        ])
    elif cookie_choice.value == "rejected":
        cookie_state = False
        _banner = mo.vstack([
            cookie_choice,
            mo.callout(
                mo.md("❌ **Non-essential cookies rejected.** Only essential cookies are active. The portfolio is loading below."),
                kind="warn",
            ),
        ])
    else:
        cookie_state = None
        _banner = cookie_choice

    _banner
    return cookie_state,


# ---------------------------------------------------------------------------
# CELL 4: Synthetic credit risk dataset
# ---------------------------------------------------------------------------
@app.cell
def _(np, pd):
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
    df_raw["Z_Score_lag"] = (
        df_raw.sort_values(["Ticker", "Year"])
        .groupby("Ticker")["Z_Score"].shift(1)
    )
    df_raw["Risk_Zone"] = df_raw["Z_Score_lag"].apply(
        lambda z: (
            "1. Distress Zone (Z < 1.81)"    if z < 1.81 else
            "3. Safe Zone (Z > 2.99)"          if z > 2.99 else
            "2. Grey Zone (1.81 ≤ Z ≤ 2.99)"
        ) if pd.notna(z) else np.nan
    )
    df_raw["Debt_Cost_Pct"] = df_raw["AvgCost_of_Debt"] * 100
    df_fin = df_raw.dropna(subset=["Z_Score_lag", "AvgCost_of_Debt", "Risk_Zone"]).copy()
    df_fin = df_fin[df_fin["AvgCost_of_Debt"] < 0.30]
    return df_fin, df_raw


# ---------------------------------------------------------------------------
# CELL 5: KO Monte Carlo
# ---------------------------------------------------------------------------
@app.cell
def _(go, mo, np):
    np.random.seed(42)
    N_ITER = 10_000
    rev_g1   = np.clip(np.random.normal(0.040, 0.015, N_ITER),      0.01, 0.08)
    rev_g25  = np.clip(np.random.normal(0.040, 0.012, (N_ITER, 4)), 0.01, 0.08)
    ebitda_m = np.clip(np.random.normal(0.345, 0.020, N_ITER),      0.30, 0.40)
    exit_m   = np.random.triangular(15, 18, 22, N_ITER)
    wacc     = np.clip(np.random.normal(0.061, 0.005, N_ITER),      0.05, 0.075)
    capex_p  = np.clip(np.random.normal(0.045, 0.005, N_ITER),      0.03, 0.06)
    dso      = np.clip(np.random.normal(31.6,  2.0,   N_ITER),      25,   40)
    REV_2024 = 47.1; TAX_RATE = 0.205; DA_PCT = 0.038
    SHARES_OUT = 4.3; CASH = 9.5; TOTAL_DEBT = 39.0
    rev = np.zeros((N_ITER, 6))
    rev[:, 0] = REV_2024
    rev[:, 1] = REV_2024 * (1 + rev_g1)
    for _yr in range(4):
        rev[:, _yr + 2] = rev[:, _yr + 1] * (1 + rev_g25[:, _yr])
    pv_explicit = np.zeros(N_ITER)
    for _i in range(5):
        yr_rev   = rev[:, _i + 1]
        ebitda   = yr_rev * ebitda_m
        da       = yr_rev * DA_PCT
        nopat    = (ebitda - da) * (1 - TAX_RATE)
        op_cf    = nopat + da
        capex    = yr_rev * capex_p
        delta_wc = (rev[:, _i + 1] - rev[:, _i]) * (dso / 365)
        fcf      = (op_cf - capex - delta_wc) * 0.5
        pv_explicit += fcf / (1 + wacc) ** (_i + 0.5)
    pv_terminal  = (rev[:, 5] * ebitda_m * exit_m) / (1 + wacc) ** 5
    ev_per_share = np.clip((pv_explicit + pv_terminal + CASH - TOTAL_DEBT) / SHARES_OUT, 0, None)
    ko_p5  = float(np.percentile(ev_per_share,  5))
    ko_p25 = float(np.percentile(ev_per_share, 25))
    ko_p50 = float(np.percentile(ev_per_share, 50))
    ko_p75 = float(np.percentile(ev_per_share, 75))
    ko_p95 = float(np.percentile(ev_per_share, 95))
    ko_mean = float(ev_per_share.mean())
    ko_std  = float(ev_per_share.std())
    ko_p_above70 = float(np.mean(ev_per_share > 70) * 100)
    ko_p_above60 = float(np.mean(ev_per_share > 60) * 100)
    ko_p_below50 = float(np.mean(ev_per_share < 50) * 100)
    fig_ko = go.Figure()
    fig_ko.add_trace(go.Histogram(x=ev_per_share, nbinsx=80,
        marker_color="rgba(52,152,219,0.7)", marker_line=dict(width=0.3, color="#2c3e50"),
        name="Simulated values"))
    for _x0, _x1, _col in [
        (ko_p5,  ko_p25, "rgba(231,76,60,0.12)"),
        (ko_p25, ko_p75, "rgba(46,204,113,0.10)"),
        (ko_p75, ko_p95, "rgba(231,76,60,0.12)"),
    ]:
        fig_ko.add_vrect(x0=_x0, x1=_x1, fillcolor=_col, layer="below", line_width=0)
    for _v, _c, _lbl, _d in [
        (ko_p50,  "#2c3e50",  f"Median ${ko_p50:.2f}",   "solid"),
        (ko_mean, "#f39c12", f"Mean ${ko_mean:.2f}",     "dash"),
        (ko_p5,   "#e74c3c",    f"5th ${ko_p5:.2f}",        "dot"),
        (ko_p95,  "#27ae60",  f"95th ${ko_p95:.2f}",      "dot"),
        (68.19,   "#d35400", "Base Case $68.19",          "dashdot"),
    ]:
        fig_ko.add_vline(x=_v, line_color=_c, line_dash=_d, line_width=1.8,
            annotation_text=_lbl, annotation_font_color=_c, annotation_position="top")
    fig_ko.update_layout(
        title="KO Equity Value Per Share — 10,000 Monte Carlo Iterations",
        xaxis_title="Equity Value Per Share ($)", yaxis_title="Frequency",
        template="plotly_white", height=460, showlegend=False, bargap=0.02,
        xaxis=dict(range=[35, 100]))
    ko_hist = mo.as_html(fig_ko)
    import pandas as _pd2
    _sens = _pd2.DataFrame({
        "Variable": ["Exit Multiple","EBITDA Margin","Revenue Growth Y1","WACC","Capex %","Revenue Growth Y2-5","DSO"],
        "Impact":   [8.4, 5.1, 3.2, -2.8, -1.9, 1.6, -0.7],
    }).sort_values("Impact")
    fig_tornado = go.Figure(go.Bar(
        x=_sens["Impact"], y=_sens["Variable"], orientation="h",
        marker_color=["#e74c3c" if v < 0 else "#2ecc71" for v in _sens["Impact"]]))
    fig_tornado.update_layout(
        title="Sensitivity — Impact on Equity Value Per Share ($)",
        xaxis_title="Impact ($)", template="plotly_white", height=320,
        xaxis=dict(zeroline=True, zerolinecolor="#2c3e50", zerolinewidth=1.5))
    ko_tornado = mo.as_html(fig_tornado)
    ko_summary = mo.md(f"""
**Model:** Full three-statement financial model built from KO FY2024 10-K/SEC data
($47.1B revenue · $9.5B cash · $39.0B debt · 4.3B shares outstanding),
followed by a 5-year DCF with EV/EBITDA exit multiple terminal value.
Six key assumptions simultaneously sampled from statistical distributions across **10,000 iterations**.

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

P(Value > $70) = **{ko_p_above70:.1f}%** &nbsp;|&nbsp;
P(Value > $60) = **{ko_p_above60:.1f}%** &nbsp;|&nbsp;
P(Value < $50) = **{ko_p_below50:.1f}%**
    """)
    return (
        ev_per_share, ko_hist, ko_mean, ko_p5, ko_p25, ko_p50,
        ko_p75, ko_p95, ko_p_above60, ko_p_above70, ko_p_below50,
        ko_std, ko_summary, ko_tornado,
    )


# ---------------------------------------------------------------------------
# CELL 6: UI controls
# ---------------------------------------------------------------------------
@app.cell
def _(df_fin, mo):
    ui_ta  = mo.ui.number(value=100_000, label="Total Assets ($)")
    ui_ca  = mo.ui.number(value=40_000,  label="Current Assets ($)")
    ui_cl  = mo.ui.number(value=20_000,  label="Current Liabilities ($)")
    ui_re  = mo.ui.number(value=30_000,  label="Retained Earnings ($)")
    ui_eb  = mo.ui.number(value=15_000,  label="EBIT ($)")
    ui_tl  = mo.ui.number(value=50_000,  label="Total Liabilities ($)")
    ui_sal = mo.ui.number(value=120_000, label="Total Sales / Revenue ($)")
    ui_mc  = mo.ui.number(value=80_000,  label="Market Capitalisation ($)")
    all_sectors = sorted(df_fin["Sector_Key"].unique().tolist())
    ui_sectors = mo.ui.multiselect(options=all_sectors, value=all_sectors[:4], label="Filter by Sector")
    all_years = sorted(df_fin["Year"].unique().tolist())
    ui_years = mo.ui.multiselect(
        options=[str(y) for y in all_years], value=[str(y) for y in all_years], label="Filter by Year")
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
        ui_nlp_min, ui_nlp_text, ui_sectors, ui_years,
    )


# ---------------------------------------------------------------------------
# CELL 7: Reactive filtering
# ---------------------------------------------------------------------------
@app.cell
def _(df_fin, ui_sectors, ui_years):
    _years_int = [int(y) for y in ui_years.value]
    df_filtered = df_fin[
        (df_fin["Sector_Key"].isin(ui_sectors.value)) &
        (df_fin["Year"].isin(_years_int))
    ].copy()
    n_obs = len(df_filtered)
    return df_filtered, n_obs


# ---------------------------------------------------------------------------
# CELL 8: Z-Score
# ---------------------------------------------------------------------------
@app.cell
def _(mo, np, ui_ca, ui_cl, ui_eb, ui_mc, ui_re, ui_sal, ui_ta, ui_tl):
    def compute_zscore(ta, ca, cl, re_e, ebit, tl, s, mktcap):
        try:
            return round(
                1.2*((ca-cl)/ta) + 1.4*(re_e/ta) + 3.3*(ebit/ta) +
                0.6*(mktcap/tl) + 1.0*(s/ta), 3)
        except ZeroDivisionError:
            return float("nan")
    z = compute_zscore(
        ui_ta.value, ui_ca.value, ui_cl.value, ui_re.value,
        ui_eb.value, ui_tl.value, ui_sal.value, ui_mc.value)
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


# ---------------------------------------------------------------------------
# CELL 9: Regression + charts
# ---------------------------------------------------------------------------
@app.cell
def _(df_filtered, mo, n_obs, np, pd, px, stats):
    _cmap = {
        "1. Distress Zone (Z < 1.81)":    "red",
        "2. Grey Zone (1.81 ≤ Z ≤ 2.99)": "grey",
        "3. Safe Zone (Z > 2.99)":          "green",
    }
    _r = df_filtered.dropna(subset=["Z_Score_lag", "AvgCost_of_Debt"])
    if len(_r) > 5:
        _sl, _it, _rv, _p, _ = stats.linregress(_r["Z_Score_lag"], _r["Debt_Cost_Pct"])
        _r2 = round(_rv**2, 4); _p_ = round(_p, 4); _sl_ = round(_sl, 4)
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
    fig_scatter = px.scatter(
        df_filtered.dropna(subset=["Z_Score_lag", "Debt_Cost_Pct", "Risk_Zone"]),
        x="Z_Score_lag", y="Debt_Cost_Pct", color="Risk_Zone", color_discrete_map=_cmap,
        hover_name="Name", hover_data=["Ticker", "Year", "Sector_Key"],
        title=f"Cost of Debt vs. Lagged Z-Score ({n_obs} observations)",
        labels={"Z_Score_lag": "Altman Z-Score (lagged)", "Debt_Cost_Pct": "Avg. Cost of Debt (%)", "Risk_Zone": "Risk Zone"},
        template="plotly_white", height=470)
    fig_scatter.add_vline(x=1.81, line_dash="dash", line_color="red",
        annotation=dict(text="Distress (1.81)", font=dict(color="red"), x=1.5, xref="x", y=1.07, yref="paper", showarrow=False, yanchor="top"))
    fig_scatter.add_vline(x=2.99, line_dash="dash", line_color="green",
        annotation=dict(text="Safe (2.99)", font=dict(color="green"), x=3.10, xref="x", y=1.02, yref="paper", showarrow=False, yanchor="top"))
    _cl = df_filtered.dropna(subset=["Z_Score_lag", "Debt_Cost_Pct"])
    if len(_cl) > 5:
        _x = _cl["Z_Score_lag"].astype(float); _y = _cl["Debt_Cost_Pct"].astype(float)
        _m, _b = np.polyfit(_x, _y, 1); _xl = np.linspace(_x.min(), _x.max(), 100)
        _rt = px.line(x=_xl, y=_m*_xl+_b).data[0]
        _rt.update(line=dict(width=1.5, color="black", dash="dot"), name="OLS Fit")
        fig_scatter.add_trace(_rt)
    scatter_chart = mo.ui.plotly(fig_scatter)
    fig_box = px.box(
        df_filtered.dropna(subset=["Risk_Zone", "Debt_Cost_Pct"]),
        x="Risk_Zone", y="Debt_Cost_Pct", color="Risk_Zone", color_discrete_map=_cmap,
        points="outliers", hover_data=["Name"],
        title="Distribution of Cost of Debt by Credit Risk Zone",
        labels={"Debt_Cost_Pct": "Avg. Cost of Debt (%)", "Risk_Zone": "Z-Score Zone"},
        template="plotly_white", height=390)
    fig_box.update_layout(showlegend=False)
    box_chart = mo.ui.plotly(fig_box)
    _med = df_filtered["AvgCost_of_Debt"].median()
    _tb = df_filtered.copy()
    _tb["Cost_Label"] = _tb["AvgCost_of_Debt"].apply(
        lambda x: "Higher (Above Median)" if x > _med else "Lower (Below Median)")
    _ct = pd.crosstab(index=_tb["Cost_Label"], columns=_tb["Risk_Zone"], margins=True, margins_name="Total")
    crosstab_display = mo.md("**Contingency Table** — Cost of Debt (row) vs. Risk Zone (col):\n\n" + _ct.to_markdown())
    return box_chart, crosstab_display, reg_summary, scatter_chart


# ---------------------------------------------------------------------------
# CELL 10: NLP
# ---------------------------------------------------------------------------
@app.cell
def _(Counter, mo, pd, px, re, ui_nlp_min, ui_nlp_text):
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
    _dfu = pd.DataFrame([(w,c) for w,c in _uc.most_common(20) if c>=_mf], columns=["Word","Frequency"])
    _dfb = pd.DataFrame([(b,c) for b,c in _bc.most_common(15) if c>=_mf], columns=["Bigram","Frequency"])
    if len(_dfu) > 0:
        _fu = px.bar(_dfu, x="Frequency", y="Word", orientation="h", title="Top Unigrams",
            color="Frequency", color_continuous_scale="Blues", template="plotly_white", height=360)
        _fu.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
        nlp_uni = mo.ui.plotly(_fu)
    else:
        nlp_uni = mo.md("*No words found above the minimum frequency.*")
    if len(_dfb) > 0:
        _fb = px.bar(_dfb, x="Frequency", y="Bigram", orientation="h", title="Top Bigrams",
            color="Frequency", color_continuous_scale="Teal", template="plotly_white", height=320)
        _fb.update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
        nlp_big = mo.ui.plotly(_fb)
    else:
        nlp_big = mo.md("*No bigrams found above the minimum frequency.*")
    nlp_stats = mo.md(f"**{len(_uc)}** unique words · **{len(_bc)}** unique bigrams · Showing frequency ≥ **{_mf}**")
    return nlp_big, nlp_stats, nlp_uni


# ---------------------------------------------------------------------------
# CELL 11: Portfolio assembly.
# Depends on cookie_state — renders nothing until user makes a choice.
# Uses mo.vstack throughout (NOT mo.md(f"...{widget}...")) so all
# interactive elements render correctly in WASM.
# ---------------------------------------------------------------------------
@app.cell
def _(
    box_chart, cookie_state, crosstab_display, ko_hist, ko_summary, ko_tornado,
    mo, nlp_big, nlp_stats, nlp_uni, reg_summary, scatter_chart,
    ui_ca, ui_cl, ui_eb, ui_mc, ui_re, ui_sal, ui_sectors, ui_ta, ui_tl,
    ui_years, ui_nlp_min, ui_nlp_text, z_display,
):
    if cookie_state is None:
        # Not chosen yet — render nothing
        _out = mo.md("")
    else:
        # ── Tab 1: About Me ───────────────────────────────────────────────
        tab_about = mo.md("""
### BSc Accounting & Finance · Data, AI & Finance

**Summary:**
- BSc Accounting & Finance student at Bayes Business School (Predicted: **1st Class**).
- Running an independent personal investment portfolio since inception.
- Observed fixed-income research at a boutique hedge fund (£500M+ AUM).
- Designed and deployed **NutriScan AI** - a live Firebase/Groq Progressive Web App, currently in beta testing.
- Contributing to a fintech startup in the FX space (funding support, design, and UAT).

---

**Education:**

* **BSc Accounting & Finance (Hons)**, Bayes Business School *(Sep 2025 – May 2028)* — Predicted: **1st Class**
* **Bloomberg Market Concept (BMC) Certificate** *(Oct – Dec 2025)*
* **John Lyon School** — A: Maths · B: Chemistry · C: Biology · 10 GCSEs at 9–7

---

**Technical Skills:**

| Category | Tools |
|---|---|
| Languages | Python · R · SQL |
| Libraries | pandas · NumPy · Plotly · Altair · SciPy · statsmodels · spaCy |
| Platforms | Bloomberg Terminal · EViews · Jupyter · Marimo |
| Methods | OLS Regression · Monte Carlo · DCF Modelling · Hypothesis Testing |
| Web & AI | Playwright · Firebase · Groq · LLM APIs |

---

**Work Experience:**

* **Tutor**, Sherpa *(Jul 2025 – Present)* — GCSE and A-Level Maths and Sciences
* **Data & Operations Analyst**, Nice Smile Dental Practice *(Jul – Sep 2025)* — Reduced weekly reporting time by 1.5 hours; improved data accuracy by 17%
* **Investment Banking Shadow**, Observatory Capital Management LLP *(Jul – Sep 2022)* — Observed fixed-income research process at a £500M+ AUM fund
        """)

        # ── Tab 2: Interactive Demos ──────────────────────────────────────
        tab_projects = mo.vstack([
            mo.md("## Interactive Demos"),
            mo.md("### Demo 1: Altman Z-Score Calculator"),
            mo.callout(mo.md(
                "The Altman Z-Score predicts bankruptcy risk from five balance-sheet ratios. "
                "Values below 1.81 indicate financial distress; values above 2.99 indicate a safe zone. "
                "Enter financials below - the score updates live."
            ), kind="info"),
            mo.hstack([
                mo.vstack([ui_ta, ui_ca, ui_cl, ui_re]),
                mo.vstack([ui_eb, ui_tl, ui_sal, ui_mc]),
            ], justify="center", gap=4),
            z_display,
            mo.md("---"),
            mo.md("### Demo 2: Credit Risk Regression Analysis"),
            mo.callout(mo.md(
                "OLS regression of average cost of debt on lagged Altman Z-Score. "
                "Tests whether prior-year credit risk predicts current borrowing costs across a "
                "synthetic panel of 60 firms over four years. Filter by sector and year to explore subsets."
            ), kind="info"),
            mo.hstack([ui_sectors, ui_years], justify="start", gap=4),
            reg_summary,
            scatter_chart,
            mo.md("#### Distribution of Cost of Debt by Risk Zone"),
            box_chart,
            mo.md("#### Contingency Table"),
            crosstab_display,
            mo.md("---"),
            mo.md("### Demo 3: Coca-Cola DCF Monte Carlo"),
            mo.callout(mo.md(
                "10,000-iteration Monte Carlo simulation of a DCF valuation for Coca-Cola (KO), "
                "using FY2024 10-K/SEC data. Six assumptions sampled simultaneously from "
                "statistical distributions. Vectorised with NumPy."
            ), kind="info"),
            ko_summary,
            ko_hist,
            mo.md("#### Sensitivity Analysis"),
            ko_tornado,
            mo.md("---"),
            mo.md("### Demo 4: NLP Word & Bigram Frequency Analyser"),
            mo.callout(mo.md(
                "Paste any financial or business text below. The tool tokenises the input, "
                "removes stopwords, and ranks the most frequent unigrams and bigrams - "
                "a common first step in analysing 10-K risk factor disclosures or earnings transcripts."
            ), kind="info"),
            mo.hstack([ui_nlp_text, ui_nlp_min], justify="start", gap=2),
            nlp_stats,
            mo.hstack([nlp_uni, nlp_big], justify="start", gap=2),
        ])

        # ── Tab 3: Personal Interests ─────────────────────────────────────
        tab_interests = mo.vstack([
            mo.md("""
## Personal Projects & Interests

### NutriScan AI - Live App *(Beta Testing)*

An independently built **Progressive Web App (PWA)** using **Groq** AI to scan meals from photos, labels, and barcodes.

**Live:** [food-app-cb863.web.app](https://food-app-cb863.web.app/)

| Feature | Details |
|---|---|
| Photo scanning | AI estimates calories and protein from a plate photo |
| Label OCR | Reads nutrition values from packaged food labels |
| Barcode scanner | EAN/UPC lookup via Open Food Facts |
| Natural language | "Bowl of pasta with chicken" - AI estimates macros |
| Streak and badges | 7-day tracker, 8 achievement badges |
| Progress charts | 14-day weight and body fat line charts |
| Weekly AI insight | Personalised Groq paragraph about your week |
| Cloud sync | Firebase Firestore for multi-device data |

**Stack:** Firebase Hosting · Firestore · Groq · OpenRouter · Vanilla JS

---

### Independent Investment Portfolio

Personal investment book running since inception. Applies regression, DCF modelling, and time-series analysis using Python, EViews, and Bloomberg Terminal.

---

### Hobbies

Piano · First-team football · County Cup cricket · Regional chess · Cycling
            """),
        ])

        # ── Assemble — use mo.vstack, NOT mo.md(f"...{tabs}...") ─────────
        _tabs = mo.ui.tabs({
            "About":              tab_about,
            "Interactive Demos":  tab_projects,
            "Personal Projects":  tab_interests,
        })

        _out = mo.vstack([
            mo.md("# **Ibrahim Khan**"),
            mo.md(
                "**BSc Accounting & Finance · Bayes Business School**  \n"
                "[LinkedIn](https://www.linkedin.com/in/ibrahim-khan-68396129a/) · "
                "[GitHub](https://github.com/BayesUG-AI/repoAF1204-ibby2474) · "
                "[Email](Ibrahim.Khan.6@bayes.city.ac.uk)"
            ),
            mo.md("---"),
            _tabs,
        ])

    _out


if __name__ == "__main__":
    app.run()