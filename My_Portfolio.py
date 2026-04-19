# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.19.10",
#     "pandas>=2.3.3",
#     "plotly>=6.5.1",
#     "pyarrow>=22.0.0",
#     "pyzmq>=27.1.0",
# ]
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 🎓 Personal Portfolio Webpage
    Combine everything learned so far (e.g., data loading, preparation, and visualization) into a multi-tabbed webpage featuring interactive chart and dashboard
    """)
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd

    # Require micropip to install packages in the WASM environment
    import micropip

    return micropip, mo, pd


@app.cell
def _(pd):
    # 1: Setup & Data Prep

    # Load S&P 500 Z-Score vs Average Cost of Debt dataset from remote gist URL
    csv_url = "https://gist.githubusercontent.com/DrAYim/80393243abdbb4bfe3b45fef58e8d3c8/raw/ed5cfd9f210bf80cb59a5f420bf8f2b88a9c2dcd/sp500_ZScore_AvgCostofDebt.csv"

    df_final = pd.read_csv(csv_url)

    df_final = df_final.dropna(subset=['AvgCost_of_Debt', 'Z_Score_lag', 'Sector_Key'])
    # Filter outliers to reduce distortion in visualizations
    df_final = df_final[(df_final['AvgCost_of_Debt'] < 5)]   # 5 means 500%
    df_final['Debt_Cost_Percent'] = df_final['AvgCost_of_Debt'] * 100
    return (df_final,)


@app.cell
def _(df_final, mo):
    # 2: Define the UI Controls (The "Inputs")

    # 1. A Multiselect Dropdown to filter by Sector
    all_sectors = sorted(df_final['Sector_Key'].unique().tolist())
    sector_dropdown = mo.ui.multiselect(
        options=all_sectors,
        value=all_sectors[:3],  # Default to first 3 sectors
        label="Filter by Sector",
    )

    # 2. A Slider for minimum Market Cap (in Billions)
    df_final['Market_Cap_B'] = df_final['Market_Cap'] / 1e9

    cap_slider = mo.ui.slider(
        start=0,
        stop=200,
        step=10,
        value=0,  # Default: show all
        label="Min Market Cap ($ Billions)"
    )
    return cap_slider, sector_dropdown


@app.cell
def _(cap_slider, df_final, sector_dropdown):
    # 3: The Filter Logic (Reactive Data)

    # This cell re-runs automatically when the user changes the slider or dropdown
    filtered_portfolio = df_final[
        (df_final['Sector_Key'].isin(sector_dropdown.value)) &
        (df_final['Market_Cap_B'] >= cap_slider.value)
    ]

    count = len(filtered_portfolio)
    return count, filtered_portfolio


@app.cell
async def _(micropip):
    # Install plotly in the WASM environment asynchronously
    await micropip.install('plotly')

    import plotly.express as px

    return (px,)


@app.cell
def _(count, filtered_portfolio, mo, pd, px):
    # 4: The Visualizations

    # =========================================
    # Plot 1: Financial Analysis Scatter Chart
    # =========================================
    fig_portfolio = px.scatter(
        filtered_portfolio,
        x='Z_Score_lag',
        y='Debt_Cost_Percent',
        color='Sector_Key',
        size='Market_Cap_B',
        hover_name='Name',
        title=f"Cost of Debt vs. Altman Z-Score ({count} observations)",
        labels={
            'Z_Score_lag': 'Altman Z-Score (lagged)',
            'Debt_Cost_Percent': 'Avg. Cost of Debt (%)'
        },
        template='presentation',
        width=900,
        height=600
    )

    # Distress threshold vertical line
    fig_portfolio.add_vline(
        x=1.81,
        line_dash="dash",
        line_color="red",
        annotation=dict(
            text="Distress Threshold (Z = 1.81)",
            font=dict(color="red"),
            x=1.5, xref="x",
            y=1.07, yref="paper",
            showarrow=False,
            yanchor="top"
        )
    )

    # Safe zone threshold vertical line
    fig_portfolio.add_vline(
        x=2.99,
        line_dash="dash",
        line_color="green",
        annotation=dict(
            text="Safe Threshold (Z = 2.99)",
            font=dict(color="green"),
            x=3.10, xref="x",
            y=1.02, yref="paper",
            showarrow=False,
            yanchor="top"
        )
    )

    # Wrap the plot in a marimo UI element so it is interactive
    chart_element = mo.ui.plotly(fig_portfolio)

    # =========================================
    # Plot 2: UK Cities Map (Places I Have Lived/Studied)
    # =========================================
    # Hardcoded data reflecting Mahmudur's real locations from his CV
    places_data = pd.DataFrame({
        'Place': [
            'Bayes Business School (City, London)',
            'Ilford County High School',
            'Swanlea School (Whitechapel)',
            'Kroo Bank (City of London)',
            'APDA Volunteer (Harlesden)',
            'BNP Paribas Discovery Day (City of London)'
        ],
        'Lat': [51.5270, 51.5720, 51.5145, 51.5135, 51.5362, 51.5155],
        'Lon': [-0.1025, 0.0560, -0.0635, -0.0885, -0.2439, -0.0922],
        'Category': [
            'University',
            'Secondary School',
            'Secondary School',
            'Work Experience',
            'Volunteering',
            'Work Experience'
        ],
        'Year': ['2025–Present', '2023–2025', '2018–2023', '2023', '2024–2025', '2024']
    })

    fig_places = px.scatter_mapbox(
        places_data,
        lat='Lat',
        lon='Lon',
        hover_name='Place',
        color='Category',
        hover_data={'Year': True, 'Lat': False, 'Lon': False},
        zoom=9,
        height=500,
        title="My London Journey — Education & Experience",
        labels={'Category': 'Type'}
    )

    fig_places.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 50, "l": 0, "b": 0}
    )

    fig_places.update_traces(marker=dict(size=14))

    return chart_element, fig_places


@app.cell
def _(cap_slider, chart_element, fig_places, mo, sector_dropdown):
    # 5: The Portfolio Layout (Multi-Tab Webpage)

    # --- Tab 1: About Me (CV) ---
    tab_cv = mo.md(
        """
        ### Aspiring Auditor & Financial Analyst | Data Science Enthusiast

        **Personal Profile:**

        First-year Accounting and Finance student with hands-on bookkeeping experience using Xero,
        exposure to audit risk assessment through EY's Audit Job Simulation, and strong client-facing
        skills developed through tutoring and volunteering. Motivated to pursue a career in audit to
        develop technical expertise in assurance, internal controls, and financial reporting.

        ---

        **Education:**

        - 🎓 **BSc Hons Accounting & Finance** — Bayes Business School, EC1Y *(Sep 2025 – May 2029)*
          - *Relevant Modules:* Introduction to Data Science & AI Tools, Financial Accounting
        - 📘 **A-Levels** (Economics, History, Mathematics, EPQ) — Ilford County High School *(2023–2025)*
        - 📗 **GCSEs** (10 subjects, incl. Grade 8 Maths) — Swanlea School *(2018–2023)*

        ---

        **Work Experience:**

        - 📐 **Private Tutor** *(Mar 2024 – Present)* — GCSE Maths tuition; improved student grades by at least one grade
        - 🤝 **Volunteer Bookkeeper, APDA** *(Aug 2024 – Jan 2025)* — Reconciled 50+ transactions in Xero; assisted with budgeting
        - 🏦 **Intern, Kroo Bank** *(Aug–Sep 2023)* — Client onboarding (15+ clients), cross-team collaboration, senior presentations

        ---

        **Certificates & Additional Experience:**

        - ✅ **EY Audit Job Simulation** *(Oct 2025)* — Risk assessment, control & substantive testing, accounts analysis
        - 🏆 **BNP Paribas Discovery Day** *(Oct 2024)* — Selected from across the UK (44 students); trading simulation

        ---

        **Skills:**

        🐍 Python &nbsp;&nbsp; 📊 Data Visualisation &nbsp;&nbsp; 📒 Xero Bookkeeping &nbsp;&nbsp; 📉 Financial Modelling &nbsp;&nbsp; 🗣️ Client Communication
        """
    )

    # --- Tab 2: Interactive Financial Analysis ---
    tab_data_content = mo.vstack([
        mo.md("## 📊 Interactive Credit Risk Analyser"),
        mo.callout(
            mo.md(
                "Explore the relationship between **Borrowing Costs** and **Credit Risk** (Altman Z-Score) "
                "across S&P 500 companies. Use the filters to drill into sectors and company sizes of interest."
            ),
            kind="info"
        ),
        mo.hstack([sector_dropdown, cap_slider], justify="center", gap=2),
        chart_element
    ])

    # --- Tab 3: Personal Interests / London Journey Map ---
    tab_personal = mo.vstack([
        mo.md("## 🗺️ My London Journey"),
        mo.md(
            "From school in Whitechapel to interning in the City of London — this map traces the key locations "
            "of my academic and professional journey so far. Each pin represents a place that has shaped my "
            "skills, perspectives, and career ambitions in finance and audit."
        ),
        mo.ui.plotly(fig_places)
    ])

    return tab_cv, tab_data_content, tab_personal


@app.cell
def _(mo, tab_cv, tab_data_content, tab_personal):
    # 6: Assemble and Display the Multi-Tab Webpage

    app_tabs = mo.ui.tabs({
        "📄 About Me": tab_cv,
        "📊 Financial Analysis": tab_data_content,
        "🗺️ My Journey": tab_personal
    })

    mo.md(
        f"""
        # **Mahmudur Rahman**
        #### BSc Accounting & Finance | Bayes Business School | Aspiring Auditor
        ---
        {app_tabs}
        """
    )
    return


if __name__ == "__main__":
    app.run()
