# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "anywidget>=0.9.21",
#     "ipywidgets>=8.1.8",
#     "marimo>=0.19.0",
#     "matplotlib>=3.10.8",
#     "pandas>=2.3.3",
#     "plotly>=6.5.0",
#     "pyzmq>=27.1.0",
#     "scipy>=1.17.0",
#     "yahooquery>=2.4.1",
#     "yfinance>=1.0",
# ]
# ///

import marimo

__generated_with = "0.19.9"
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

    _**Prompt for AI:**_

    Elaborate this into step-by-step instructions for GitHub Codespaces:

    - If you are annoyed by inlay hints, such as type annotations (e.g., `: str`), displayed inline in the editor, this can be turned off by setting `editor.inlayHints.enabled` in Codespaces's Settings to `offUnlessPressed` (`Ctrl + Alt`)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    # **Interactive Plots with Plotly**
    """)
    return


@app.cell
def _():
    # Import necessary libraries

    import marimo as mo
    import pandas as pd

    return mo, pd


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Reading and displaying** data


    _**Note:**_

    - It took over 30 minutes for `yfinance` to fetch completely the historical data of S&P 500 companies from 2021 to 2025 (saved as `sp500_raw_data.csv`)
    - A copy of the data has been saved as _**`sp500_raw_data_Backup.csv`**_ in the `public/` folder to prevent the data from being overwritten by only a slice of it during the demonstration of the sliced download for testing:
    ```python
        for ticker in tickers_for_year[:5]:  # Limit to first 5 tickers for testing
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **Questions:**

    - _**How to read in `sp500_raw_data_Backup.csv` (in the `public/` folder) as a pandas dataframe `df` and display the first 5 rows of it?**_
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Let's ask AI for help!

    **Prompt for AI:**

    - Provide Python code to read in sp500_raw_data_Backup.csv (in the public/ folder) as a pandas dataframe df and display the first 5 rows of it.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    \* Hidden **Python code** here (_**double-click**_ to view; _**copy**_ the Python code and _**paste**_ it in a code cell for execution).

    <!--
    #import pandas as pd

    # Read the CSV file into a DataFrame
    df = pd.read_csv("public/sp500_raw_data_Backup.csv")

    # Display the first 5 rows
    print(df.head())
      -->
    """)
    return


@app.cell
def _():
    # Place the AI suggested code here





    return


@app.cell
def _(mo):
    mo.md(r"""
    _**Note:**_

    - Sometimes, the code suggested by AI begins with `import pandas as pd`
    - Executing `import pandas as pd` a second time will throw an error in marimo because it does not allow redefining an object in another code cell in the same session. (When the command was executed the first time, `pd` was defined as the imported module `pandas`. Running the command a second time is an attempt to define `pd` again -- not permitted in marimo).
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    _**Note:**_

    - Before executing the code chunk above, there was not any variable named `df` in the current Python environment.
    - After executing the code chunk, `df` is now defined as a pandas dataframe containing the data read from the CSV file
       - Verify this with the list of variables in the `VARIABLES` column after clicking the `MARIMO` tab in the lower middle panel of Codespace (toggle the panel on and off by clicking the <img src="img/square-half.png" width="15" alt="Lower-middle panel Image" style="display: inline; vertical-align: middle; margin: 0 2px;"> <!-- ![Lower-middle panel Image](img/square-half.png){width="15"} --> icon in the upper right corner of Codespace).
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### Dataframe `df` displayed in marimo (instead of `print(df)`)
    """)
    return


@app.cell
def _(df):
    # Display dataFrame (and type information if in marimo)

    df 
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Dataframe `df` displayed in Jupyter
    - Show only top and bottom 5 rows without type information

    ![Display `df` in Jupyter](img/Display_df_in_Jupyter.png)

    ---

    \* Hidden **bonus content** here (_**double-click**_ to view; _**uncomment**_ the lines to reveal them permanently).

    <!--
    #### Bonus:

    - Images included in marimo markdown cells will not be embedded in the exported html file
    - Must use the following code to display an image in order to also embed the image in the exported html file

    ```python
    import base64
    from pathlib import Path

    image_data = Path("img/Display_df_in_Jupyter.png").read_bytes()
    b64 = base64.b64encode(image_data).decode()

    mo.image(src=f"data:image/png;base64,{b64}")
    ```
    -->
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## Features of **Interactive Plots** by Plotly
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### Preparation for plotting
    """)
    return


@app.cell
def _():
    # Import necessary libraries
    import plotly.express as px
    import plotly.graph_objects as go

    # Define the data column for plotting as the target metric
    target_metric = "Total_Debt"    # Can also try "Total_Assets" later

    # Note: This allows aligning the target metric to plot and its name to be displayed in the plot title
    return go, px, target_metric


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### **Violin plot**
    """)
    return


@app.cell
def _(df, px, target_metric):

    # Violin plot (shows vertical distributions per year); set box=True to show quartiles
    violin_fig = px.violin(
        df,
        x="Year",
        #y="Total_Assets",
        y=target_metric,          # Dynamically uses the y variable
        # Set a custom range that hides some data (e.g., zoom in on a specific asset range)
        range_y=[0, 8*1e11],   # 800,000,000,000 = 800 billion 
        box=True,           # True to show quartiles
        #points=False,       # False to show none
        #points="all",      # "all" to show all points (can be heavy) 
        #points="outliers", # Show only outliers (the default)
        hover_data=["Name"],    #["Ticker"],   
        title=f"Distribution of {target_metric} of S&P500 Index Companies by Year"
    )
    violin_fig.update_layout(xaxis_title="Year", yaxis_title=f"{target_metric}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### **Hover Labels**: Let's zoom in on Year 2025 to have a look

    - First **quartile** (Q1), **median** (Q2), third quartile (Q3), and **interquartile range** (IQR = Q3 - Q1)

    <img src="img/IQR_corrected.png" alt="Interquartile range (IQR)" width="900"/>
    <!-- This Markdown syntax to control the width does not work on GitHub Codespaces
    ![Interquartile range (IQR)](img/IQR_corrected.png){width=900px}
     -->

    - In the **box plot** inside a violin, the **lower fence** and **upper fence** define the boundaries for identifying outliers:

        - **Lower fence** = Q1 - 1.5 × IQR
        - **Upper fence** = Q3 + 1.5 × IQR

    - Data points outside these fences (i.e., on the whiskers at both ends) are typically considered **outliers** and may be plotted as individual dots (by commenting out `points=False` to use the default `points=outliers`)
        - This helps visualize the spread and detect anomalies in the data distribution.


    ---

    \* Hidden **bonus content** here (_**double-click**_ to view; _**uncomment**_ the lines to reveal them permanently).

    <!--
    #### Bonus:

    - Below is the code for generating the Interquartile Range (IQR) infographic

    ```python
    # Code for generating the Interquartile Range (IQR) infographic

    import numpy as np
    import matplotlib.pyplot as plt
    from scipy import stats

    # Create figure with dark background
    fig, ax = plt.subplots(figsize=(16, 9))   # (12, 8)
    fig.patch.set_facecolor('#1e3a5f')
    ax.set_facecolor('#1e3a5f')

    # Generate normal distribution with larger standard deviation (flatter, wider)
    std_dev = 6.5  # Much larger std dev for flatter distribution
    x = np.linspace(-12, 12, 1000)
    y = stats.norm.pdf(x, 0, std_dev)

    # Calculate quartile positions for this distribution
    q1 = stats.norm.ppf(0.25, 0, std_dev)  # -0.674 * std_dev
    median = 0
    q3 = stats.norm.ppf(0.75, 0, std_dev)  # 0.674 * std_dev

    # Fill the distribution
    ax.fill_between(x, y, alpha=0.9, color='#d4a854')

    # Add vertical lines for quartiles and median (height = peak of distribution)
    peak_height = max(y)
    line_props = {'color': 'white', 'linewidth': 2.5, 'linestyle': '--', 'alpha': 0.9}
    ax.plot([q1, q1], [0, peak_height], **line_props)
    ax.plot([median, median], [0, peak_height], **line_props)
    ax.plot([q3, q3], [0, peak_height], **line_props)

    # Add labels at the top
    label_y = max(y) * 1.05    # 1.05
    ax.text(q1, label_y, 'First\nQuartile\n(Q1)', ha='center', va='bottom',
            color='white', fontsize=16, fontweight='bold')
    ax.text(median, label_y, 'Median\n(50th Percentile)', ha='center', va='bottom',
            color='white', fontsize=16, fontweight='bold')
    ax.text(q3, label_y, 'Third\nQuartile\n(Q3)', ha='center', va='bottom',
            color='white', fontsize=16, fontweight='bold')

    # Add percentage labels
    label_y_lower = max(y) * 0.85     # 0.5
    ax.text(q1 - 2.5, label_y_lower, '25% of data\nbelow this point', ha='center', va='center',
            color='white', fontsize=12)
    ax.text(q3 + 2.5, label_y_lower, '75% of data\nbelow this point', ha='center', va='center',
            color='white', fontsize=12)

    # Add arrows pointing to the lines
    arrow_props = dict(arrowstyle='->', color='white', lw=2)
    ax.annotate('', xy=(q1, label_y_lower), xytext=(q1 - 1.05, label_y_lower),
                arrowprops=arrow_props)
    ax.annotate('', xy=(q3, label_y_lower), xytext=(q3 + 1.05, label_y_lower),
                arrowprops=arrow_props)

    # Add bottom labels
    bottom_y = -max(y) * 0.02  # 0.15
    ax.text(-13.75, bottom_y, 'Lowest\nValue', ha='center', va='top',
            color='white', fontsize=14, fontweight='bold')
    ax.text(q1, bottom_y, 'Q1', ha='center', va='top',
            color='white', fontsize=14, fontweight='bold')
    ax.text(median, bottom_y, 'Median', ha='center', va='top',
            color='white', fontsize=14, fontweight='bold')
    ax.text(q3, bottom_y, 'Q3', ha='center', va='top',
            color='white', fontsize=14, fontweight='bold')
    ax.text(13.75, bottom_y, 'Highest\nValue', ha='center', va='top',  #10
            color='white', fontsize=14, fontweight='bold')

    # Add IQR bracket and label
    bracket_y = -max(y) * 0.1
    ax.annotate('', xy=(q1, bracket_y), xytext=(q3, bracket_y),
                arrowprops=dict(arrowstyle='<->', color='white', lw=2))
    ax.text((q1 + q3) / 2, bracket_y - 0.002, 'Interquartile Range', ha='center', va='top',
            color='white', fontsize=13, fontweight='bold')

    ax.set_xlim(-15, 15)  # control horizontal space for labels and arrows
    ax.set_ylim(-max(y) * 0.3, max(y) * 1.3)   # control vertical space for labels and arrows
    # Add horizontal x-axis with arrows at both ends
    axis_y = 0  # Position at y=0
    ax.plot([-12, 12], [axis_y, axis_y], color='white', linewidth=2, alpha=0.9)
    # Add arrowheads at both ends
    ax.annotate('', xy=(-14, axis_y), xytext=(-11.5, axis_y),
                arrowprops=dict(arrowstyle='->', color='white', lw=2))   # <-
    ax.annotate('', xy=(14, axis_y), xytext=(11.5, axis_y),
                arrowprops=dict(arrowstyle='->', color='white', lw=2))
    ax.axis('off')

    # Add note about cut tails
    note_y = -max(y) * 0.25
    ax.text(0, note_y, 'Note: The distribution extends infinitely in both directions; tails are truncated for illustration.',
            ha='center', va='top', color='white', fontsize=10, style='italic', alpha=0.7)

    plt.tight_layout()
    plt.savefig('img/IQR_corrected.png',
                dpi=300, facecolor='#1e3a5f', bbox_inches='tight')
    print("Plot saved successfully!")
    print(f"\nCorrect positions:")
    print(f"Q1 (25th percentile): {q1:.3f}")
    print(f"Median (50th percentile): {median:.3f}")
    print(f"Q3 (75th percentile): {q3:.3f}")
    print(f"\nEach section contains exactly 25% of the data under the curve.")
    ```
    -->
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### **Joyplot**

    #### Ask AI to learn more!

    For example,
    - _**What does**_ `[n/(len(years)-1) for n in range(len(years))]` _**do in the code below?**_
        - `px.colors.sample_colorscale("viridis", [n/(len(years)-1) for n in range(len(years))])`


    \* Hidden **content** here (_**double-click**_ to view; _**uncomment**_ the lines to reveal them permanently).

    <!--
    - The list comprehension `[n/(len(years)-1) for n in range(len(years))]` generates a list of normalized values between 0 and 1, evenly spaced across the number of unique years.
        - len(years) gives the count of years (e.g., 5 if there are 5 years).
        - `range(len(years))` produces indices from 0 to `len(years)-1` (e.g., 0, 1, 2, 3, 4).
        - For each index n, it computes `n / (len(years)-1)`, resulting in a list like [0.0, 0.25, 0.5, 0.75, 1.0] for 5 years.
    - This list is passed to `px.colors.sample_colorscale("viridis", ...)` to sample colors from the Viridis color scale at these positions, assigning a unique color to each year in the sorted order.

    ---

    - _**What does**_ `zip` _**do in the code below? What if `zip` is not used here?**_
        - `for year, color in zip(reversed(years), reversed(colors_selected)):`

    - The `zip` function in Python takes two or more iterables (like lists) and returns an iterator of tuples, where each tuple contains one element from each iterable, paired by index. In this code:
        `for year, color in zip(reversed(years), reversed(colors_selected)):`
        - `reversed(years)` produces the years in descending order (e.g., [2025, 2024, ..., 2021]).
        - `reversed(colors_selected)` produces the colors in the same reversed order (e.g., the color originally assigned to 2025 first).
        - `zip` pairs them element-wise: the first year (2025) with the first reversed color (which is the color for 2025), the second year (2024) with the second reversed color (color for 2024), and so on.
        - This ensures each year gets its correct color from the Viridis scale, but the loop processes years in reverse order (2025 first), which affects the drawing order in the Plotly figure (placing later years in the background for the joyplot effect).

    - Without `zip`, the code would fail because the for loop expects to unpack tuples (one for `year` and one for `color`), but you'd only have one iterable.
     -->
    """)
    return


@app.cell
def _(df, go, px, target_metric):

    # 1. Get unique years (Keep this sorted ascending for the axis definition later)
    years = sorted(df["Year"].unique())

    # 2. Generate Viridis colors (Keep this aligned with the sorted years)
    colors_selected = px.colors.sample_colorscale("viridis", [n/(len(years)-1) for n in range(len(years))])

    # 3. Create the Joyplot using Violin traces
    joy_fig = go.Figure()     # Note: plotly.graph_objects was imported as go

    # Note: A violin trace is a graphical element that visualizes the distribution of data 
    #       as a smoothed kernel density. Alternatives include go.Scatter, go.Box, go.Histogram, etc.

    # 4. Loop to create a violin trace for each year (iterating in REVERSE order)
    #    - Zip the reversed years and reversed colors 
    #      - so 2025 gets the correct color but is drawn first (placing it in the background).
    for year, color in zip(reversed(years), reversed(colors_selected)):

        # Filter data for each year
        year_data = df[df["Year"] == year][target_metric]

        # Add the violin trace for the year
        joy_fig.add_trace(go.Violin(
            x=year_data,
            name=str(year),     # The 'name' property is a string; so convert year to str
            side='positive',    # draw only the right side 
            orientation='h',    # horizontal violins
            fillcolor=color,    # Use the zipped color
            opacity=0.85,          
            line_color='grey', 
            hoverlabel=dict(
                bgcolor='white',  # set background color of hover label to improve readability
                font_size=12,       
                font_color='black' 
                ),
            width=3,             
            points=False,      
            ))

    # 5. Style the layout
    joy_fig.update_layout(
        title=f"Joyplot: Distribution of {target_metric} by Year",
        xaxis_title=target_metric,
        yaxis_title="Year",
        violinmode='overlay', # Overlay violins on top of each other (instead of side by side)
        xaxis_range=[0, 8*1e11],
        # --- Force y-Axis Order ---
        # Since 2025 is drawnfirst, Plotly might try to put it at the bottom.
        # The below forces the Y-axis to display the original ascending order.
        yaxis=dict(
            categoryorder='array',
            categoryarray=[str(y) for y in years] # Ensure these match the 'name' in add_trace
        )
    )

    joy_fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### **3D scatter** plot (out-of-box)
    """)
    return


@app.cell
def _(df, px, target_metric):

    ThreeD_fig0 = px.scatter_3d(
        df, 
        x='Year', 
        y='Sector_Key', 
        z=target_metric, 
        color=f"{target_metric}",
        title=f"3D Scatter Plot of {target_metric} by Year and Sector",
        labels={'Year': 'Year', 'Sector_Key': 'Sector', target_metric: target_metric}
        ) 

    ThreeD_fig0
    return


@app.cell
def _(mo):
    mo.md(r"""
    _**Note:**_

    - It is easier to control the view angle with the `Turnable Rotation` mode.
    - However, only the `Orbital Rotation` mode lets you turn the 3D plot upside down.
        - In the `Turnable Rotation` mode, you can only rotate the 3D plot up by 90 degrees.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### 3D scatter plot (**fine-tuned**)
    """)
    return


@app.cell
def _(df, pd, px, target_metric):
    # Create a copy of df for fine-tuned 3D plotting
    df3D = df.copy()

    #==============================================
    # Define function to shorten and pad sector key names
    def adjust_sector_key(name):
        # 1. Check if the value is missing or not a string
        if pd.isna(name) or not isinstance(name, str):
            return name

        # 2. Handle specific exception
        if name == "communication-services":
            name = "communications"

        # 3. Pad the name with leading non-breaking spaces (\u2007) 
        # (a workaround to move labels away from the plot area to prevent overlap)
        # Must start with \u2E31 to prevent Plotly from trimming the leading spaces;
        # \u2E31 is the Unicode character for the least visible dot
        name = "\u2E31" + "\u2007"*13 + name

        return name    
    #==============================================

    # Apply the adjust_sector_key function to Sector_Key
    df3D['Sector_Key'] = df3D['Sector_Key'].apply(adjust_sector_key)

    # Create the 3D scatter plot with adjusted Sector_Key
    ThreeD_fig = px.scatter_3d(
        df3D, 
        x='Year', 
        y='Sector_Key', 
        z=target_metric, 
        color=target_metric,
        title=f"3D Scatter Plot: {target_metric} by Year and Sector",
        labels={'Year': 'Year', 'Sector_Key': 'Sector', target_metric: target_metric},
        # Use opacity so overlapping points are visible
        opacity=0.7
    )

    # Fine-tune the 3D plot layout
    ThreeD_fig.update_layout(
        # Reduces margins to increase the viewing window
        margin=dict(l=15, r=15, b=10, t=30), 
        # Adjust camera position
        scene_camera=dict(
            # Change 'z' to adjust the vertical location of the plot
            center=dict(x=0, y=0, z=-0.4),
            # Increasing eye values to zoom out the plot
            eye=dict(x=1.5, y=1.5, z=1.5)
            #eye=dict(x=1.25, y=1.25, z=1.25) # Default eye values
            ),
        # Adjust ticks of x- and y-axes and aspect ratio
        scene=dict(
            xaxis=dict(
                # force ticks to increase by every 1 unit, fixing "year decimal issue"
                dtick=1, 
            ),
            # Note: y='Sector_Key'
            yaxis=dict(
                title_text='Sector',
                tickfont=dict(size=11.5),
                # Rotate labels by 90 degree to prevent overlap
                tickangle=90, 
                # Increases the max number of allowed ticks
                nticks=len(df3D['Sector_Key'].unique()),
            ),
            # STRETCH the Y-axis (Sector axis) to create more space between labels
            aspectmode='manual',
            aspectratio=dict(x=1, y=1.75, z=1),
            # Sets turntable as the default active drag/rotation mode        
            dragmode='turntable',  
        )
    )

    ThreeD_fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    _**Note:**_

    - To export this marimo notebook as a self-contained **html** file,
        - start a New Terminal and use the command:

            ```bash
            marimo export html Wk03_InteractivePlots_Plotly_Moodle.py -o Wk03_InteractivePlots_Plotly_Moodle.html --sandbox --force
            ```
        - _Remark:_ Images in the `img/` folder that are inserted in this notebook **will not be embedded** in the exported html file **unless** using the code in a hidden bonus content cell (placed below the 'Dataframe df displayed in Jupyter' image)

    - To view the exported .html file with interactive plots,
        - download it to your device and open it with a browser
        - or you can start a local http server using the command below in the terminal in the bottom panel of Codespaces, followed by clicking the html file on the list in the newly opened browser tab that appears:

            ```bash
            python3 -m http.server 8000
            ```
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ---

    # **Data Preparation**
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## Get **unique values** in a dataframe column

    **Questions:**

    - _**How can you get the list of unique values in the `Sector_Key` column of dataframe `df`?**_
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### Let's ask AI again for help!

    **Prompt for AI:**

    - Provide Python code to get the list of unique values in the Sector_Key column of dataframe df.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    \* Hidden **Python code** here (_**double-click**_ to view; _**copy**_ the Python code and _**paste**_ it in a code cell for execution).

    <!--
    # Get the list of unique Sector_Key
    unique_sector_keys = df['Sector_Key'].dropna().unique()

    # Display the results
    print("Unique Sector_Key:", unique_sector_keys)
      -->
    """)
    return


@app.cell
def _():
    # Place the AI suggested code here




    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Filter rows** with a particular value in a dataframe column

    **Question:**

    - _**How can you filter dataframe `df` to display only the rows where `Sector_Key` is 'financial-services'?**_
    """)
    return


@app.cell
def _(df):
    print(df[df['Sector_Key'] == 'financial-services'])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Similarly,

    - _**To display only the rows where Industry_Key is credit-services, ...**_
    """)
    return


@app.cell
def _(df):
    print(df[df['Industry_Key'] == 'credit-services'])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## Pandas **display options**

    - To print all rows of a dataframe,
        - use the following code to set pandas display options temporarily:

    ```python
    # Change the display option ONLY inside this 'with' block
    with pd.option_context('display.max_rows', None):
        print(df[df['Industry_Key'] == 'credit-services'])

    # Outside the 'with' block, it is already back to the previous default
    print(df[df['Industry_Key'] == 'credit-services'])
    ```
    """)
    return


@app.cell
def _(df, pd):
    # Change the display option ONLY inside this 'with' block
    with pd.option_context('display.max_rows', None):
        print(df[df['Industry_Key'] == 'credit-services'])

    # Outside the 'with' block, it is already back to the previous default
    print("\n----------------------------------------------\n") # print a separator line 
    print(df[df['Industry_Key'] == 'credit-services'])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### Since you are using a **marimo notebook**,

    - you can directly display a dataFrame without using `print()`
    """)
    return


@app.cell
def _(df):
    df[df['Industry_Key'] == 'credit-services']
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## Filter rows with **missing values** in a dataframe column

    **Questions:**

    - _**How can you use Python code to display rows with `NaN` values, if any, in the `Total_Debt` column of dataframe df?**_
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    \* Hidden **Python code** here (_**double-click**_ to view; _**copy**_ the Python code and _**paste**_ it in a code cell for execution).

    <!--
    # Display rows where Total_Debt has NaN values
    df[df['Total_Debt'].isna()]
     -->
    """)
    return


@app.cell
def _():
    # Place the Python code here



    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Why doesn't the code below work?
    """)
    return


@app.cell
def _(NaN, df):
    df[df['Total_Debt'] == NaN]
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### This code doesn't work either!
    """)
    return


@app.cell
def _(df):
    df[df['Total_Debt'] == 'NaN']
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## Data **Cleaning**

    ### Example here:

    - Need to create a new variable to examine the relationship between _**credit risk**_ and _**borrowing costs**_:
        - A measure to capture borrowing costs is _**Average cost of debt**_
        - Conceptually,
            - **Average** cost of debt = Interest expense / Total debt
            - because in general,
                - **Total debt** consists of a mix of debts and
                - **Interest expense** is the total interest expense of the debts
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### Complication

    - For many companies, `Total debt` has a _**missing value**_!
        - **Why?**


    #### Task:
    - Replace the missing values in the `Total_Debt` column of dataframe `df` by `0`,
        - assuming `Total_Debt`'s missing values are due to companies **with zero debt _not_ reporting any line item** of debt
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    #### How to use Python code to replace the missing values in the `Total_Debt` column of dataframe `df` by `0`?
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    \* Hidden **Python code** here (_**double-click**_ to view; _**copy**_ the Python code and _**paste**_ it in a code cell for execution).

    <!--
    # Replace missing Total_Debt values with 0
    df['Total_Debt'] = df['Total_Debt'].fillna(0)
     -->
    """)
    return


@app.cell
def _():
    # Place the Python code here



    return


@app.cell
def _(df):
    # Confirmation: Any rows still with missing Total_Debt?
    df[df['Total_Debt'].isna()]
    return


if __name__ == "__main__":
    app.run()
