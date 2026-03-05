# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.19.10",
#     "pandas>=2.3.3",
#     "plotly>=6.5.1",
#     "numpy>=1.26.0",
#     "pyzmq>=27.1.0",
# ]
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


# ─────────────────────────────────────────────
# CELL 1 — IMPORTS
# ─────────────────────────────────────────────

@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import numpy as np
    return mo, pd, px, go, np


# ─────────────────────────────────────────────
# CELL 2 — TITLE
# ─────────────────────────────────────────────

@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## 📈 S&P 500 Historical Price Dashboard

    - An interactive dashboard exploring **monthly S&P 500 index prices** from **January 2020 to March 2026**
    - Covers price trends, monthly returns, volatility, and drawdown analysis

    > **How to run as a web app:**
    > ```bash
    > marimo run sp500_dashboard.py --sandbox
    > ```
    > Then open the `PORTS` tab and click the 🌐 globe icon next to `Marimo App (2718)`.

    ---
    """)
    return


# ─────────────────────────────────────────────
# CELL 3 — LOAD DATA
# ─────────────────────────────────────────────

@app.cell
def _(mo):
    mo.md(r"""
    #### 1. **Load** Data
    """)
    return


@app.cell
def _(pd, np):
    # ── Load the CSV (same folder as the notebook) ────────────────────────
    df = pd.read_csv("https://raw.githubusercontent.com/ibby2474/CW/main/S%26P%20500%20Historical%20Data%20(1).csv")

    # ── Strip BOM character from column names if present ─────────────────
    df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)

    # ── Clean numeric columns (remove commas from price strings) ─────────
    for col in ['Price', 'Open', 'High', 'Low']:
        df[col] = df[col].str.replace(',', '', regex=False).astype(float)

    # ── Clean Change % column (remove % sign and convert to float) ───────
    df['Change_Pct'] = df['Change %'].str.replace('%', '', regex=False).astype(float)

    # ── Parse Date column to datetime ────────────────────────────────────
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')

    # ── Sort chronologically (oldest first) ──────────────────────────────
    df = df.sort_values('Date').reset_index(drop=True)

    # ── Derived columns ───────────────────────────────────────────────────

    # Year and Month labels for grouping
    df['Year']       = df['Date'].dt.year
    df['Month']      = df['Date'].dt.month
    df['Month_Label'] = df['Date'].dt.strftime('%b')   # e.g. 'Jan', 'Feb'
    df['YearMonth']  = df['Date'].dt.strftime('%Y-%m')

    # Monthly range (High - Low)  — measures intra-month volatility
    df['Monthly_Range'] = df['High'] - df['Low']

    # Cumulative return from the very first date in the dataset
    first_price      = df['Price'].iloc[0]
    df['Cumulative_Return_Pct'] = ((df['Price'] - first_price) / first_price) * 100

    # Rolling 12-month price: the average closing price over the past 12 months
    df['Rolling_12m_Avg'] = df['Price'].rolling(window=12).mean()

    # Drawdown from rolling maximum (shows how far the index is below its peak)
    df['Rolling_Max']     = df['Price'].cummax()
    df['Drawdown_Pct']    = ((df['Price'] - df['Rolling_Max']) / df['Rolling_Max']) * 100

    # Label: positive or negative month
    df['Return_Sign'] = df['Change_Pct'].apply(
        lambda x: 'Positive' if x >= 0 else 'Negative'
    )

    print(f"Data loaded: {len(df)} monthly observations from "
          f"{df['Date'].min().strftime('%b %Y')} to {df['Date'].max().strftime('%b %Y')}.")
    df
    return df, first_price


# ─────────────────────────────────────────────
# CELL 4 — UI CONTROLS
# ─────────────────────────────────────────────

@app.cell
def _(mo):
    mo.md(r"""
    #### 2. Create **UI Controls**
    """)
    return


@app.cell
def _(df, mo):
    # Year range slider — lets user zoom into a specific period
    all_years = sorted(df['Year'].unique().tolist())

    year_range_slider = mo.ui.range_slider(
        start=min(all_years),
        stop=max(all_years),
        step=1,
        value=[min(all_years), max(all_years)],
        label="**Select Year Range:**"
    )

    # Dropdown to choose which price series to display on the main line chart
    price_series_dropdown = mo.ui.dropdown(
        options={
            'Closing Price':    'Price',
            'Opening Price':    'Open',
            'Monthly High':     'High',
            'Monthly Low':      'Low',
        },
        value='Closing Price',
        label="**Price Series to Display:**"
    )

    mo.hstack([year_range_slider, price_series_dropdown], justify="start", gap=4)
    return year_range_slider, price_series_dropdown


# ─────────────────────────────────────────────
# CELL 5 — REACTIVE FILTER
# ─────────────────────────────────────────────

@app.cell
def _(mo):
    mo.md(r"""
    #### 3. Set Selector to **Filter Data Reactively** (`.isin` / range filter)
    """)
    return


@app.cell
def _(df, year_range_slider):
    # Re-runs automatically when the year slider changes
    df_filtered = df[
        (df['Year'] >= year_range_slider.value[0]) &
        (df['Year'] <= year_range_slider.value[1])
    ].copy()

    # Key metrics from the filtered data
    n_months       = len(df_filtered)
    price_start    = df_filtered['Price'].iloc[0]  if n_months > 0 else 0
    price_end      = df_filtered['Price'].iloc[-1] if n_months > 0 else 0
    total_return   = ((price_end - price_start) / price_start * 100) if price_start != 0 else 0
    avg_monthly_chg= df_filtered['Change_Pct'].mean()
    max_drawdown   = df_filtered['Drawdown_Pct'].min()
    best_month     = df_filtered.loc[df_filtered['Change_Pct'].idxmax(), 'YearMonth'] if n_months > 0 else 'N/A'
    worst_month    = df_filtered.loc[df_filtered['Change_Pct'].idxmin(), 'YearMonth'] if n_months > 0 else 'N/A'
    return (df_filtered, n_months, price_start, price_end,
            total_return, avg_monthly_chg, max_drawdown,
            best_month, worst_month)


# ─────────────────────────────────────────────
# CELL 6 — VISUALISATIONS
# ─────────────────────────────────────────────

@app.cell
def _(mo):
    mo.md(r"""
    #### 4. Create the **Interactive Plots** on the Dashboard
    """)
    return


# ── Plot 1: Main price line chart ────────────────────────────────────────────

@app.cell
def _(df_filtered, px, go, price_series_dropdown):
    _col   = price_series_dropdown.value
    _label = price_series_dropdown.options
    # Reverse-lookup the label from the value
    _col_label = [k for k, v in {
        'Closing Price': 'Price',
        'Opening Price': 'Open',
        'Monthly High':  'High',
        'Monthly Low':   'Low',
    }.items() if v == _col][0]

    fig_line = px.line(
        df_filtered,
        x='Date',
        y=_col,
        title=f"S&P 500 Monthly {_col_label} (2020 – 2026)",
        labels={'Date': 'Date', _col: f'Index Level ({_col_label})'},
        template='presentation',
        width=900,
        height=480
    )

    # Overlay 12-month rolling average (only where it has values)
    _roll_df = df_filtered.dropna(subset=['Rolling_12m_Avg'])
    if not _roll_df.empty:
        fig_line.add_trace(
            go.Scatter(
                x=_roll_df['Date'],
                y=_roll_df['Rolling_12m_Avg'],
                mode='lines',
                name='12-Month Rolling Avg',
                line=dict(color='orange', dash='dash', width=1.5)
            )
        )

    fig_line.update_layout(title=dict(y=0.97, x=0, xanchor='left'), legend=dict(x=0.01, y=0.99))
    print(" ")
    return (fig_line,)


# ── Plot 2: Monthly % change bar chart ───────────────────────────────────────

@app.cell
def _(df_filtered, px):
    _color_map = {'Positive': '#2ecc71', 'Negative': '#e74c3c'}

    fig_bar = px.bar(
        df_filtered,
        x='YearMonth',
        y='Change_Pct',
        color='Return_Sign',
        color_discrete_map=_color_map,
        title="Monthly % Change in the S&P 500",
        labels={'YearMonth': 'Month', 'Change_Pct': 'Monthly Change (%)', 'Return_Sign': ''},
        template='presentation',
        width=900,
        height=460
    )
    # Add a zero line for reference
    fig_bar.add_hline(y=0, line_color='black', line_width=0.8)
    fig_bar.update_layout(
        xaxis_tickangle=-45,
        showlegend=True,
        title=dict(y=0.97, x=0, xanchor='left')
    )
    print(" ")
    return (fig_bar,)


# ── Plot 3: Cumulative return line ────────────────────────────────────────────

@app.cell
def _(df_filtered, px):
    fig_cumret = px.line(
        df_filtered,
        x='Date',
        y='Cumulative_Return_Pct',
        title="Cumulative Return of the S&P 500 from January 2020 (%)",
        labels={'Date': 'Date', 'Cumulative_Return_Pct': 'Cumulative Return (%)'},
        template='presentation',
        width=900,
        height=460
    )
    # Shade area under the line
    fig_cumret.update_traces(fill='tozeroy', fillcolor='rgba(46,204,113,0.15)')
    fig_cumret.add_hline(y=0, line_dash='dash', line_color='grey', line_width=0.8)
    fig_cumret.update_layout(title=dict(y=0.97, x=0, xanchor='left'))
    print(" ")
    return (fig_cumret,)


# ── Plot 4: Drawdown chart ────────────────────────────────────────────────────

@app.cell
def _(df_filtered, px):
    fig_drawdown = px.area(
        df_filtered,
        x='Date',
        y='Drawdown_Pct',
        title="S&P 500 Drawdown from Rolling Peak (%)",
        labels={'Date': 'Date', 'Drawdown_Pct': 'Drawdown from Peak (%)'},
        template='presentation',
        color_discrete_sequence=['#e74c3c'],
        width=900,
        height=420
    )
    fig_drawdown.add_hline(y=0, line_color='black', line_width=0.8)
    fig_drawdown.update_layout(title=dict(y=0.97, x=0, xanchor='left'))
    print(" ")
    return (fig_drawdown,)


# ── Plot 5: Intra-month range (High - Low) violin by year ─────────────────────

@app.cell
def _(df_filtered, px):
    fig_violin = px.violin(
        df_filtered,
        x='Year',
        y='Monthly_Range',
        box=True,
        points='all',
        color='Year',
        hover_data=['YearMonth'],
        title="Distribution of Monthly Price Range (High − Low) by Year",
        labels={'Monthly_Range': 'Monthly Range (pts)', 'Year': 'Year'},
        template='presentation',
        width=900,
        height=480
    )
    fig_violin.update_layout(showlegend=False, title=dict(y=0.97, x=0, xanchor='left'))
    print(" ")
    return (fig_violin,)


# ── Plot 6: Monthly return heatmap (Month vs Year) ───────────────────────────

@app.cell
def _(df_filtered, px, pd):
    _pivot = df_filtered.pivot_table(
        index='Month_Label',
        columns='Year',
        values='Change_Pct',
        aggfunc='mean'
    )
    # Order months Jan → Dec
    _month_order = ['Jan','Feb','Mar','Apr','May','Jun',
                    'Jul','Aug','Sep','Oct','Nov','Dec']
    _pivot = _pivot.reindex([m for m in _month_order if m in _pivot.index])

    fig_heatmap = px.imshow(
        _pivot,
        color_continuous_scale='RdYlGn',
        zmin=-15, zmax=15,
        aspect='auto',
        title="Monthly Return Heatmap: Month vs. Year (%)",
        labels=dict(x='Year', y='Month', color='Return (%)'),
        text_auto='.1f',
        width=900,
        height=420
    )
    fig_heatmap.update_layout(title=dict(y=0.97, x=0, xanchor='left'))
    print(" ")
    return (fig_heatmap,)


# ── Plot 7: Candlestick OHLC chart ───────────────────────────────────────────

@app.cell
def _(df_filtered, go):
    fig_candle = go.Figure(
        data=[
            go.Candlestick(
                x=df_filtered['Date'],
                open=df_filtered['Open'],
                high=df_filtered['High'],
                low=df_filtered['Low'],
                close=df_filtered['Price'],
                name='OHLC'
            )
        ]
    )
    fig_candle.update_layout(
        title="S&P 500 Monthly OHLC Candlestick Chart",
        xaxis_title="Date",
        yaxis_title="Index Level",
        template='presentation',
        width=900,
        height=500,
        title_x=0,
        xaxis_rangeslider_visible=False
    )
    print(" ")
    return (fig_candle,)


# ─────────────────────────────────────────────
# CELL 7 — DASHBOARD LAYOUT
# ─────────────────────────────────────────────

@app.cell
def _(mo):
    mo.md(r"""
    #### 5. Define the **Dashboard Layout** (using `mo.md()`)
    """)
    return


@app.cell
def _(
    mo,
    year_range_slider, price_series_dropdown,
    n_months, price_start, price_end,
    total_return, avg_monthly_chg, max_drawdown,
    best_month, worst_month,
    fig_line, fig_bar, fig_cumret,
    fig_drawdown, fig_violin, fig_heatmap, fig_candle
):
    dashboard = mo.md(f"""
# 📈 S&P 500 Historical Price Dashboard

Interactive analysis of **monthly S&P 500 index performance** from January 2020 to March 2026.

---

{year_range_slider}

{price_series_dropdown}

---

## Key Metrics

| Metric | Value |
| :--- | :---: |
| Months Analysed | **{n_months}** |
| Start Price | **{price_start:,.2f}** |
| End Price | **{price_end:,.2f}** |
| Total Return | **{total_return:+.2f}%** |
| Avg. Monthly Change | **{avg_monthly_chg:+.2f}%** |
| Max Drawdown | **{max_drawdown:.2f}%** |
| Best Month | **{best_month}** |
| Worst Month | **{worst_month}** |

---

## 1️⃣  Price Trend + 12-Month Rolling Average

*Use the dropdown above to switch between Closing, Opening, High, or Low price series.  
The orange dashed line is the 12-month rolling average.*

{mo.as_html(fig_line)}

---

## 2️⃣  Monthly OHLC Candlestick Chart

*Shows the Open, High, Low, and Close for each month.  
Green candles = month closed higher than it opened; red = lower.*

{mo.as_html(fig_candle)}

---

## 3️⃣  Monthly % Change

*Green bars = positive months; red bars = negative months.*

{mo.as_html(fig_bar)}

---

## 4️⃣  Monthly Return Heatmap

*Each cell shows the % return for that month and year.  
Green = strong gains; red = losses.*

{mo.as_html(fig_heatmap)}

---

## 5️⃣  Cumulative Return from January 2020

*How much has a dollar invested in January 2020 grown by each month?*

{mo.as_html(fig_cumret)}

---

## 6️⃣  Drawdown from Rolling Peak

*How far below its all-time high was the S&P 500 each month?  
The COVID crash (March 2020) and the 2022 bear market are clearly visible.*

{mo.as_html(fig_drawdown)}

---

## 7️⃣  Monthly Price Range (High − Low) by Year

*Higher violin = more intra-month volatility. Points show individual months.*

{mo.as_html(fig_violin)}

---
*Built with [marimo](https://marimo.io) · Source data: `S_P_500_Historical_Data__1_.csv`*
    """)
    return (dashboard,)


# ─────────────────────────────────────────────
# CELL 8 — DISPLAY
# ─────────────────────────────────────────────

@app.cell
def _(mo):
    mo.md(r"""
    #### 6. **Display** the Dashboard

    - Try changing the **year range** slider to zoom in on the 2022 bear market or the 2020 COVID crash
    - Switch the **price series** dropdown to compare Opening vs Closing prices
    """)
    return


@app.cell
def _(dashboard):
    dashboard
    return


if __name__ == "__main__":
    app.run()