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


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import numpy as np
    return mo, pd, px, go, np

@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## S&P 500 Historical Price Dashboard

    - An interactive dashboard exploring **monthly S&P 500 index prices** from **January 2020 to March 2026**
    - Covers price trends, monthly returns, volatility, and drawdown analysis
    ---
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### 1. **Load** Data
    """)
    return


@app.cell
def _(pd, np):
    # ── Load the CSV
    df = pd.read_csv("https://raw.githubusercontent.com/ibby2474/CW/main/S%26P%20500%20Historical%20Data%20(1).csv")

    # This line of code removes any leading or trailing whitespace characters from the column names in the DataFrame and the specific string '/ufeff' from the column names if it exists. 
    df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)

    # This line of code removes commas from the values and replaces them, thereby converting them into numeric (float) data through this process.
    for col in ['Price', 'Open', 'High', 'Low']:
        df[col] = df[col].str.replace(',', '', regex=False).astype(float)

    # This line of code removes the % symbol from the column called change and repalces it, thereby converting it to a float value during the process.
    df['Change_Pct'] = df['Change %'].str.replace('%', '', regex=False).astype(float)

     # This line of code converts the date column in the DataFrame into a datetime format, whereby the format of the date follwos the pattern/structure of month/day/year.
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')

     # This line of code organsies and sorts the dataset by date and resets the index numbers of the DataFrame
    df = df.sort_values('Date').reset_index(drop=True)

# These 4 lines of code below isloate and extract the month,year, year month and month label from the column titled date and creates new columns for each individual extracted column within the DataFrame.
    df['Year']       = df['Date'].dt.year
    df['Month']      = df['Date'].dt.month
    df['Month_Label'] = df['Date'].dt.strftime('%b')   # e.g. 'Jan', 'Feb'
    df['YearMonth']  = df['Date'].dt.strftime('%Y-%m')

# This line of code creates a brand new column titled Monthly_Range within the DataFrame. This column is designed to calculate the stock price range on a monthly basis by subtracting the low price form the hgh price for each entry in the dataset, thereby measuring volatility.
    df['Monthly_Range'] = df['High'] - df['Low']

# These 3 lines of code below create two new columns within the DataFrame. One is titled Cumulative_Return_Pct and calculates the cumulative return percentage through a comparison metric between the intial and final price  in the dataset, which is stored in the variable first_price. The other column is called Rolling_12m_Avg and calculates the stock price rolling avaerge numeric value over a time frame of 12 months, thereby showing the annual average price trend and is a long-term metric.
    first_price      = df['Price'].iloc[0]
    df['Cumulative_Return_Pct'] = ((df['Price'] - first_price) / first_price) * 100

    # Rolling 12-month price: the average closing price over the past 12 months
    df['Rolling_12m_Avg'] = df['Price'].rolling(window=12).mean()

      # These lines of code below identify and label the months as eitehr positive or negative based on the motnhly % change in price.
    df['Rolling_Max']     = df['Price'].cummax()
    df['Drawdown_Pct']    = ((df['Price'] - df['Rolling_Max']) / df['Rolling_Max']) * 100

 # These few lines of code print out the dataset summary in addition to the date rnage and total number of observations on a monthly basis.
    df['Return_Sign'] = df['Change_Pct'].apply(
        lambda x: 'Positive' if x >= 0 else 'Negative'
    )

    print(f"Data loaded: {len(df)} monthly observations from "
          f"{df['Date'].min().strftime('%b %Y')} to {df['Date'].max().strftime('%b %Y')}.")
    df
    return df, first_price

@app.cell
def _(mo):
    mo.md(r"""
    #### 2. Create **UI Controls**
    """)
    return


@app.cell
def _(df, mo):
    #This block of code below creates a year range slider which allows the interactive dashboard users to select a specific range of years to specifically filter the visualisations and dataset
    all_years = sorted(df['Year'].unique().tolist())

    year_range_slider = mo.ui.range_slider(
        start=min(all_years),
        stop=max(all_years),
        step=1,
        value=[min(all_years), max(all_years)],
        label="**Select Year Range:**"
    )

     #All of these lines of code below when executed create a dropdown menu, allowing users of the interactive dashboard to slsect/choose whcih specific price series to display in the visualisations like the main line chart in particular. The different options include closing price, monthly high, monthly low and opening price.
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



@app.cell
def _(mo):
    mo.md(r"""

    """)
    return


@app.cell
def _(df, year_range_slider):
   # These few lines of code below adapts when the year slider changes by re-running automatically
    df_filtered = df[
        (df['Year'] >= year_range_slider.value[0]) &
        (df['Year'] <= year_range_slider.value[1])
    ].copy()

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


@app.cell
def _(mo):
    mo.md(r"""
    #### #this piece of code is going to be the visulation part of the code.
# im going to create a notebook cell that renders markdown content for a dashboard interface and making interactive plots.
    """)
    return

#this is gonna be the main price line chart of the S&P500 over the last 6 years starting from 2020
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

# this has created a dropdown menu where i selected a closing price as my label because when i ran the code waith just price it didnt work due to having a collumn in the csv file called price already.
# then i linked them all to a short collumn with price and open, read vaule of selection and found matching label using it for chart title
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

    fig_line.update_layout(title=dict(y=0.97, x=0, xanchor='left'), legend=dict(x=0.01, y=0.99))
    print(" ")
    return (fig_line,)

# now i am going to do a bar chart with monthly percentage change. 
# creating a dictionary for the colour map the label Positive to green #2ecc71 and the label Negative to red #e74c3c.

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
    # now i am gonna add a line at the base value which is 0 to make a reference 
    fig_bar.add_hline(y=0, line_color='black', line_width=0.8)
    fig_bar.update_layout(
        xaxis_tickangle=-45,
        showlegend=True,
        title=dict(y=0.97, x=0, xanchor='left')
    )
    print(" ")
    return (fig_bar,)

#now i am gonna use the data to create a cumulative return line

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

    print(" ")
    return (fig_cumret,)


# now i am gonna do a drawndown chart to show how far a portfolio or asset price falls from its previous peak over time

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


#I create a violin chart using to show the distribution of Monthly_Range values for each Year including all data points 

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


#now doing a monthly return heatmap to show the average monthly return for each month and year. i will use a pivot table to reshape the data and then use plotly express to create a heatmap. ill format the chart with titles, axis labels, color scale, and text annotations before returning the figure so the dashboard displays the plot

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


#now i am gonna do a candle stick chart to show the S&P 500 monthly data. ill format the chart with titles, axis labels, layout settings, and remove the range slider before returning the figure so the dashboard displays the plot

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




@app.cell
def _(mo):
    mo.md(r"""
    #### Dashboard Layout
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
#  S&P 500 Historical Price Dashboard

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

## 1. Price Trend + 12-Month Rolling Average

*Use the dropdown above to switch between Closing, Opening, High, or Low price series.  
The orange dashed line is the 12-month rolling average.*

{mo.as_html(fig_line)}

---

## 2. Monthly OHLC Candlestick Chart

*Shows the Open, High, Low, and Close for each month.  
Green candles = month closed higher than it opened; red = lower.*

{mo.as_html(fig_candle)}

---

## 3. Monthly % Change

*Green bars = positive months; red bars = negative months.*

{mo.as_html(fig_bar)}

---

## 4.  Monthly Return Heatmap

*Each cell shows the % return for that month and year.  
Green = strong gains; red = losses.*

{mo.as_html(fig_heatmap)}

---

## 5.  Cumulative Return from January 2020

*How much has a dollar invested in January 2020 grown by each month?*

{mo.as_html(fig_cumret)}

---

## 6.  Drawdown from Rolling Peak

*How far below its all-time high was the S&P 500 each month?  
The COVID crash (March 2020) and the 2022 bear market are clearly visible.*

{mo.as_html(fig_drawdown)}

---

## 7.   Monthly Price Range (High − Low) by Year

*Higher violin = more intra-month volatility. Points show individual months.*

{mo.as_html(fig_violin)}

---
*Built with [marimo](https://marimo.io) · Source data: `S_P_500_Historical_Data__1_.csv`*
    """)
    return (dashboard,)



@app.cell
def _(mo):
    mo.md(r"""
    # 6. Display the Dashboard

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