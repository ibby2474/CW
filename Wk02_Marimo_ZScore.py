# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "altair>=6.0.0",
#     "ipython>=9.8.0",
#     "marimo>=0.19.0",
#     "plotly>=6.5.2",
#     "pyarrow>=23.0.0",
#     "pyzmq>=27.1.0",
#     "yfinance>=0.2.66",
# ]
# ///

import marimo

__generated_with = "0.19.7"
app = marimo.App(
    width="medium",
    css_file="/usr/local/_marimo/custom.css",
    auto_download=["html"],
)


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

    # Your First **Automated Financial Analysis** ... after

    ---

    # a bit **More on Python Basics**
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Exponentiation operator ** (i.e., ^ in Excel)

    - x**n raises the left operand x to the power of the right operand n
    """)
    return


@app.cell
def _():
    # Example

    10.0**3
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### Too large a number to be represented in computer accurately!
    """)
    return


@app.cell
def _():
    2.0*(10.0**308)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Impossible to determine the result of certain operations!

    - For example, computers see
        - `2.0*(10.0**308) - 2.0*(10.0**308)` as **Infinity** minus **Infinity**
    - **Infinity** is not an actual number
        - It is used by mathematicians to represent something _**extremely large**_ -- so large to be representable by any number
    - Mathematicians cannot tell for sure what **Infinity** minus **Infinity** is!
    """)
    return


@app.cell
def _():
    2.0*(10.0**308) - 2.0*(10.0**308)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    #### What does `nan` stand for in Python?
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    \* Hidden **expected AI reply** here (_**double-click**_ to view; use `Ctrl + /` to _**uncomment**_ the reply to reveal it permanently).


    <!-- - NaN in Python, particularly in libraries like NumPy and pandas, stands for "**Not a Number**". It represents _**missing, undefined, or unrepresentable numerical values (e.g., from division by zero or unavailable data)**_. It's based on the IEEE 754 floating-point standard and is equivalent to np.nan from NumPy. You can handle it using methods like isna(), fillna(), or dropna() in pandas.  -->

    ---
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **Note:**

    - `nan` is useful for representing _undefined, unrepresentable, or missing numerical values_ (e.g., due to unavailable data)
    - For example,
        - the _**market capitalization to total liabilities**_ ratio (MV2TL) of a company with _**no debt or any other liabilities**_ is undefined!
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    #### Undefined values from computation will throw an error, **disrupting** the execution of a code!
    """)
    return


@app.cell
def _():
    market_cap = 80000
    total_liab = 0

    # compute market capitalization to total liabilities ratio 
    market_cap / total_liab
    return market_cap, total_liab


@app.cell
def _(mo):
    mo.md(r"""
    #### _**Solution**_: Exception handling with `try` and `except`
    """)
    return


@app.cell
def _(market_cap, total_liab):
    print("market_cap =", market_cap, "; total_liab =", total_liab)
    print("market_cap to total_liab ratio (MV2TL) = ", market_cap, "/", total_liab, "\n")

    try:
        MV2TL = market_cap / total_liab
    except ZeroDivisionError:
        MV2TL = float('nan')  # Assign NaN if division by zero occurs

    print("MV2TL =", MV2TL)  # Display the value of MV2TL
    return


@app.cell
def _(mo):
    mo.md(r"""
    _**Note:**_

    - Sometimes, data are not available for all companies in a year (e.g., due to **delisting** following mergers and acquisitions)
    - Errors resulting from **unavailable data** can also be handled with `try` and `except` similarly
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### What does `"\n"` do in a `print()` command?
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    \* Hidden **expected AI reply** here (_**double-click**_ to view; use `Ctrl + /` to _**uncomment**_ the reply to reveal it permanently)


    <!--
    - It inserts a **newline** character, so `print()` moves subsequent output to the next line (like pressing `Enter`).
    -->


    ---
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Let's end our overview of Python basics with the command to `import` packages

    - Packages to install and import in Python is just like **apps** to install and use in the **iPhone ecosystem**
    """)
    return


@app.cell
def _():
    import marimo as mo

    # The warnings package below is used to suppress specific warnings that are annoying and not required to learn for this module
    import warnings

    # Suppress FutureWarning from the yfinance package
    warnings.filterwarnings("ignore", category=FutureWarning, module="yfinance")
    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    _**Note:**_

    - Executing the code cell above **for the first time** might trigger a suggestion to **install missing packages**
    - Follow the prompt to install them
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    # First **Automated Financial Analysis**

    <!-- *Focus: Computation, Data fetching, Interpretation, and Visualization* -->
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## Compute and Visualize Altman Z-Score using Marimo

    - For an overview of _**Z-Score**_, see the pre-session slides about its _**components**_ and the financial _**data required**_ for computation
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ### The Primitive Form (Compute Z-Score with Hardcoded Data)

    - Define **a function** to compute Altman Z-Score
    - Compute Z-Score with Hardcoded Data

    **Example:**

    To represent in Python a mathematical function

    $y = f(x_1, x_2, x_3)$,

    <br>
    use a code structure like this:

    ```python

    def f(x1, x2, x3):

        y = [The definition here, i.e.,
             the value of the function f
             when the inputs are x1, x2, and x3]

        return y
    ```

    _**Key elements:**_
     - `def`
     - `:`
     - indentation
     - ends with the `return` command to return the function value of the inputs
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### Define a function `zscore()` to calculate Altman Z-Score from input data

    _**Note:**_

    In practice, the computation of Altman's Z-Score uses only the **market value of common shares** (aka. **market capitalization**), instead of both preferred and common shares, because

    - Preferred stock is rare among public companies;
    - When issued, preferred shares are often not publicly traded (or have negligible liquidity), making a reliable market price unavailable.
    """)
    return


@app.function
def zscore(
    total_assets,
    current_assets,
    current_liab,
    retained_earnings,
    ebit,
    total_liab,
    sales,
    market_cap,
    ):  

    # Altman Z-Score Components
    WkCap2TA = (current_assets - current_liab) / total_assets
    RE2TA = retained_earnings / total_assets
    EBIT2TA = ebit / total_assets
    preferred_market_cap = 0  # assuming no preferred stock for simplification
    # Essentially, use only market capitalization (i.e., MV of Common Stock) for MVofStock below:
    MVofStock2BVofTL = (market_cap + preferred_market_cap) / total_liab 
    Sales2TA = sales / total_assets

    # Formula
    zscore = 1.2*WkCap2TA + 1.4*RE2TA + 3.3*EBIT2TA + 0.6*MVofStock2BVofTL + 1.0*Sales2TA

    return zscore


@app.cell
def _(mo):
    mo.md(r"""
    ### Compute Altman Z-Score with Hypothetical Company Data (Hardcoded)
    """)
    return


@app.cell
def _():

    zscore_0 = zscore(
        total_assets=100000,
        current_assets=40000,
        current_liab=20000,
        retained_earnings=30000,
        ebit=15000,
        total_liab=50000,
        sales=120000,
        market_cap=80000,
        )

    print(f"The Z-Score is: {zscore_0:.2f}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    #### What is the purpose of `f` in this print command?
    `print(f"The Z-Score is: {zscore_0:.2f}")`
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    \* Hidden **expected AI reply** here (_**double-click**_ to view; use `Ctrl + /` to _**uncomment**_ the reply to reveal it permanently)

    <!--
    - The `f` prefix denotes an **f-string** (_formatted string literal_) in Python, introduced in Python 3.6. It allows embedding expressions directly inside the string using **curly braces {}**. In `print(f"The Z-Score is: {zscore_0:.2f}")`, `{zscore_0:.2f}` evaluates `zscore_0` and formats it to **2 decimal places (`.2f` means fixed-point with 2 decimals)**.
    - Without `f`, it would print the literal text, not the variable's value.
      -->

    ---
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### What if a company has no debt or other liabilities?

    - What should such a company's Z-Score be?
    (check out the example below)
    """)
    return


@app.cell
def _():
    zscore(
        total_assets=100000,
        current_assets=40000,
        current_liab=20000,
        retained_earnings=30000,
        ebit=15000,
        total_liab=0,             # <-- testing division by zero handling
        sales=120000,
        market_cap=80000,
        )
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### Let's define a new function `ZScore()` with better _exception handling_

    - using `try` and `except` to assign a `nan` value when zero total liabilities results in undefined Z-Score
        - due to the undefined component `MVofStock2BVofTL`
    - _Note:_ This is a **new function** because the function name is `ZScore`, not `zscore` (lowercase)
    """)
    return


@app.function
def ZScore(
    total_assets,
    current_assets,
    current_liab,
    retained_earnings,
    ebit,
    total_liab,
    sales,
    market_cap,
    ):  

    try:
        # Altman Z-Score Components
        WkCap2TA = (current_assets - current_liab) / total_assets
        RE2TA = retained_earnings / total_assets
        EBIT2TA = ebit / total_assets
        preferred_market_cap = 0  # assuming no preferred stock for simplification
        # Essentially, use only market capitalization (i.e., MV of Common Stock) for MVofStock below:
        MVofStock2BVofTL = (market_cap + preferred_market_cap) / total_liab 
        Sales2TA = sales / total_assets

        # Formula
        ZScore = 1.2*WkCap2TA + 1.4*RE2TA + 3.3*EBIT2TA + 0.6*MVofStock2BVofTL + 1.0*Sales2TA

    except ZeroDivisionError:

        return float('nan')

    return ZScore


@app.cell
def _():
    # Will not throw an error given the try-except block in the ZScore function

    zscore_0TL = ZScore(
        total_assets=100000,
        current_assets=40000,
        current_liab=20000,
        retained_earnings=30000,
        ebit=15000,
        total_liab=0,             # <-- testing division by zero handling
        sales=120000,
        market_cap=80000,
        )

    print(f"The Z-Score is: {zscore_0TL:.2f}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### Compute Z-Score with real company data (fetched live from Yahoo Finance)

    - Use the `yfinance` library to fetch Balance Sheet and Income Statement data for **'AAPL'** (Apple)
    - Extract the specific values for Total Assets, EBIT, Retained Earnings, etc., required to calculate the Z-Score
    """)
    return


@app.cell
def _():
    import yfinance as yf
    return (yf,)


@app.cell
def _(mo):
    mo.md(r"""
    #### Define the objects to fetch data (`bs_AAPL` and `is_AAPL`)
    """)
    return


@app.cell
def _(yf):
    # AAPL is the ticker of Apple Inc.'s stock
    stock_AAPL = yf.Ticker("AAPL")   

    # Define objects to fetch balance-sheet and income-statement financials from last available year (i.e., from the most recent column)
    bs_AAPL = stock_AAPL.balance_sheet.iloc[:, 0] # 0 means Most recent column
    is_AAPL = stock_AAPL.income_stmt.iloc[:, 0]
    return bs_AAPL, is_AAPL, stock_AAPL


@app.cell
def _(mo):
    mo.md(r"""
    ---

    #### What does the dots (`.`) do in this command?

    ```python
    bs_AAPL = stock_AAPL.balance_sheet.iloc[:, 0]
    ```

    #### Also, what does the `.iloc` do in the command?
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    \* Hidden **expected AI reply** here (_**double-click**_ to view; use `Ctrl + /` to _**uncomment**_ the reply to reveal it permanently)

    <!--
    - The dot (`.`) in Python is the **attribute access operator**, used to access _attributes_ or _methods_ of an object. In `stock_AAPL.balance_sheet`, it accesses the `balance_sheet` attribute (a pandas DataFrame) of the stock_AAPL object.

    - `.iloc` is a pandas DataFrame method for **integer-location based indexing**. In `balance_sheet.iloc[:, 0]`, it selects all rows (`:`) and the _first column_ (_index 0_), which corresponds to the _most recent year's financial data_ in the balance sheet. This returns a pandas Series for that column.

    _**Follow-up question to ask:**_ _What is a pandas Series?_

    - A pandas Series is a **one-dimensional labeled array** in Python, capable of holding any data type (integers, floats, strings, etc.). Each value in a Series has an associated label called an **index**.
      - You can think of it as a column in a spreadsheet or a dictionary with ordered keys and values. **Series** are a core data structure in the pandas library and are used for data analysis and manipulation.
      -->

    ---
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### The revised code below fetches Apple Inc.'s financials using `yfinance` and calculate Z-score using the live data
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    _**Previous code copied here for contrast:**_

    ```python

    zscore_0 = zscore(
        total_assets=100000,
        current_assets=40000,
        current_liab=20000,
        retained_earnings=30000,
        ebit=15000,
        total_liab=50000,
        sales=120000,
        market_cap=80000,
        )

    print(f"The Z-Score is: {zscore_0:.2f}")

    ````
    """)
    return


@app.cell
def _(bs_AAPL, is_AAPL, mo, stock_AAPL):
    zscore_AAPL = ZScore(  

        # Fetch financials with the balance-sheet and income-statement objects
        total_assets = bs_AAPL.get('Total Assets'),
        current_assets = bs_AAPL.get('Current Assets'),
        current_liab = bs_AAPL.get('Current Liabilities'),
        retained_earnings = bs_AAPL.get('Retained Earnings'),
        total_liab = bs_AAPL.get('Total Liabilities Net Minority Interest'),
        ebit = is_AAPL.get('EBIT'), # Or Operating Income
        sales = is_AAPL.get('Total Revenue'),

        # Get live Market Cap data from stock.info dictionary
        market_cap = stock_AAPL.info.get('marketCap'),

        )  

    # Use marimo's .md() to display the Z-Score in a markdown format, instead of using Python's print statement
    mo.md(f"## Ticker: AAPL\n### Z-Score: **{zscore_AAPL:.2f}**")

    # previosuly used print command is commented out and retained here for reference
    #print(f"The Z-Score is: {zscore_AAPL:.2f}")   
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    #### What does `.get` do in this command?

    ```python
    bs_AAPL.get('Total Assets')
    ```

    where

    ```python
    bs_AAPL = stock_AAPL.balance_sheet.iloc[:, 0]
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    \* Hidden **content** here (_**double-click**_ to view; _**uncomment**_ the lines to reveal them permanently).

    <!--
    - `.get('Total Assets')` retrieves the value for the key 'Total Assets' from the `bs_AAPL` pandas Series.
      - If 'Total Assets' is not present, it returns None (or a default value if provided), instead of raising a KeyError.
      - This is safer than using `bs_AAPL['Total Assets']`, which would cause an error if the key is missing.
      - You can provide a default value as a second argument, e.g., `.get('Total Assets', 0)`.
      -->

    ---
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    _**Class exercise:**_

    - Revise the code below and run it to see Nvidia's Z-Score.
    - To do so,
        - **Prompt to AI:** _Give me the ticker of Nvidia's stock_
        - Hoover over to the top middle part of this markdown cell and click the `+ Code` button to create a new code cell
        - double-click the current markdown cell and copy-and-paste the code **inside the opening and closing triple backticks** (i.e., ```) into the newly created code cell
        - revise the code there and click the `play` button (&#9656;) of the code cell to run the code.

    ```python

    # Replace `?` and `AAPL` below by the ticker of Nvidia's stock
    stock_AAPL = yf.Ticker("?")

    # Define objects to fetch balance-sheet and income-statement financials from last available year
    # (i.e., from the most recent column, indicated by 0)
    bs_AAPL = stock_AAPL.balance_sheet.iloc[:, 0]
    is_AAPL = stock_AAPL.income_stmt.iloc[:, 0]

    zscore_AAPL = ZScore(
        # Fetch financials with the balance-sheet and income-statement objects
        total_assets = bs_AAPL.get('Total Assets'),
        current_assets = bs_AAPL.get('Current Assets'),
        current_liab = bs_AAPL.get('Current Liabilities'),
        retained_earnings = bs_AAPL.get('Retained Earnings'),
        total_liab = bs_AAPL.get('Total Liabilities Net Minority Interest'),
        ebit = is_AAPL.get('EBIT'), # Or Operating Income
        sales = is_AAPL.get('Total Revenue'),
        # Get live Market Cap data from stock.info dictionary
        market_cap = stock_AAPL.info.get('marketCap'),
        )

    # Use marimo's .md() to display the Z-Score in a markdown format, instead of using Python's print statement
    mo.md(f"## Ticker: AAPL\n### Z-Score: **{zscore_AAPL:.2f}**")

    ```
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### From "One Script for Apple" to "**A Tool for Any Company**"

    - Create a **text input box** where the user can type any ticker
    - Add logic to interpret the Z-Score by classifying it into 'Safe' (>2.99), 'Grey' (1.81-2.99), or 'Distress' (<1.81) and **display the status in colors**
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### Text Input Box for Ticker Symbol
    """)
    return


@app.cell
def _(mo):
    # Create the input box
    ticker_input = mo.ui.text(value="MSFT", label="Enter US Ticker:")

    # Display the input box
    mo.md(f"{ticker_input}") 
    return (ticker_input,)


@app.cell
def _(mo):
    mo.md(r"""
    #### Print the `value` of `ticker_input` to confirm the value
    """)
    return


@app.cell
def _(ticker_input):
    print(f"{ticker_input.value}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### Go back to change the ticker in the text input box. Then **what happens?**
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    #### What does `mo.ui.text` do in this command?

    ```python
    mo.ui.text(value="MSFT", label="Enter US Ticker:")
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    \* Hidden **content** here (_**double-click**_ to view; _**uncomment**_ the lines to reveal permanently).

    <!--
    - creates an **interactive text input widget** in Marimo notebooks, allowing users to enter or edit string values. In this command, it initializes the widget with a **default value** of "MSFT" and a label "Enter US Ticker:". The widget can be displayed using `mo.md()` and supports **reactive updates**, where changes trigger re-runs of dependent cells.
      -->

    ---
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    #### What are the major variants of `mo.ui.`?
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    \* Hidden **content** here (_**double-click**_ to view; _**uncomment**_ the lines to reveal permanently).

    <!--
    Major Variants of mo.ui in Marimo
    Marimo's mo.ui module offers various interactive UI elements for notebooks. Here are the major variants (widgets) for user input and interaction:

    mo.ui.text(): Text input field (e.g., for strings like tickers).
    mo.ui.number(): Numeric input field (supports integers/floats with optional min/max).
    mo.ui.slider(): Horizontal slider for selecting a number within a range.
    mo.ui.dropdown(): Single-select dropdown menu from a list of options.
    mo.ui.multiselect(): Multi-select dropdown for choosing multiple items.
    mo.ui.checkbox(): Boolean checkbox (true/false toggle).
    mo.ui.radio(): Radio button group for single selection from options.
    mo.ui.button(): Clickable button to trigger actions or re-runs.
    mo.ui.date(): Date picker for selecting dates.
    mo.ui.file(): File uploader for handling file inputs.
    mo.ui.table(): Editable table for data entry or display.
    mo.ui.array(): Input for arrays/lists of values.
    mo.ui.dictionary(): Input for key-value pairs (dictionaries).
    mo.ui.form(): Container to group multiple UI elements into a form.
    Each widget can be displayed using mo.md() and supports reactive updates. For examples and parameters, refer to the Marimo UI documentation.
     -->

    ---
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### Putting everything together

    - text input box with reactive updates
    - fetching live data
    - automated computation of Z-Score
    - indicating the zone of the Z-Score in color
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### Define object to fetch data based on `ticker_input` and compute Z-Score dynamically


    - This cell automatically re-runs when ticker_input changes!
    """)
    return


@app.cell
def _(ticker_input, yf):

    ticker = ticker_input.value
    stock = yf.Ticker(ticker)

    # Define objects to fetch balance-sheet and income-statement financials from last available year (i.e., from the most recent column)
    balance_sheet = stock.balance_sheet.iloc[:, 0] # 0 means Most recent column
    income_stmt = stock.income_stmt.iloc[:, 0]

    z_score = ZScore(  
        # Fetch financials with the balance-sheet and income-statement objects
        total_assets = balance_sheet.get('Total Assets'),
        current_assets = balance_sheet.get('Current Assets'),
        current_liab = balance_sheet.get('Current Liabilities'),
        retained_earnings = balance_sheet.get('Retained Earnings'),
        total_liab = balance_sheet.get('Total Liabilities Net Minority Interest'),
        ebit = income_stmt.get('EBIT'), # Or Operating Income
        sales = income_stmt.get('Total Revenue'),
        # Get live Market Cap data from stock.info dictionary
        market_cap = stock.info.get('marketCap'),
        )  
    return ticker, z_score


@app.cell
def _(mo):
    mo.md(r"""
    ### Display the ticker and Z-Score and indicate the financial health status in colors dynamically
    """)
    return


@app.cell
def _(mo, ticker, z_score):

    # Initialize status and color variables
    status = ""
    color = ""

    # Set status and color based on Z-Score value
    if z_score > 2.99:
        status = "SAFE ZONE"
        color = "green"
    elif z_score >= 1.81:
        status = "GREY ZONE (Caution)"
        color = "grey"
    else:
        status = "DISTRESS ZONE"
        color = "red"

    # Display information using Markdown/HTML
    mo.md(f"""
    ## Ticker: {ticker}
    ### Z-Score: {z_score:.2f}
    ### Status: <span style='color:{color}'>{status}</span>
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### Finally, Visual Gauge to show Z-Score relative to Safe and Distress thresholds

    - visualizing Z-score in a bar chart
    - displaying thresholds to aid interpretation
    """)
    return


@app.cell
def _():
    # Import necessary libraries
    import pandas as pd    # for handling the fetched data for altair
    import altair as alt   # for visualization
    import pyarrow         # expected by altair
    return alt, pd


@app.cell
def _(pd, ticker, z_score):
    # Create a DataFrame for the plot
    df = pd.DataFrame({'Score': [z_score], 'Label': [ticker]})
    return (df,)


@app.cell
def _(alt, df, mo, pd, ticker):

    # Compute explicit color per row 
    df['Color'] = df['Score'].apply(lambda s: 'red' if s < 1.81 else ('grey' if s <= 2.99 else 'green'))

    # The Base Bar (use the precomputed Color column)
    bar = alt.Chart(df).mark_bar(size=30).encode(
        x=alt.X('Score:Q', scale=alt.Scale(domain=[0, 12], clamp=True), title='Altman Z-Score',
        axis=alt.Axis(grid=False, domain=False)
        ),
        y=alt.Y('Label:N', title='Ticker'),
        color=alt.Color('Color:N', scale=None, legend=None)
    ).properties(width=500, height=80)

    # Zone boundary rules
    rule1 = alt.Chart(pd.DataFrame({'x': [1.81]})).mark_rule(color='red', strokeDash=[5,5]).encode(x='x:Q')
    rule2 = alt.Chart(pd.DataFrame({'x': [2.99]})).mark_rule(color='green', strokeDash=[5,5]).encode(x='x:Q')
    # Combine into layered chart
    chart = (bar + rule1 + rule2).properties(title=f"Altman Z-Score Analysis for {ticker}")

    # Display the chart in marimo using mo.ui.altair_chart()
    mo.ui.altair_chart(chart)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ---

    ## From Any Single Company to **Multiple Companies** over **Multiple Years**
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
    ---

    ### Fetch **accounting and stock data** from Yahoo Finance for year-specific S&P500 stocks

    - Open-source packages to access Yahoo Finance data:
        - **yfinance**
        - yahooquery
    """)
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
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### Running a child marimo notebook from a parent marimo notebook

    - In marimo, each notebook is a valid Python script. You can import and run another marimo notebook as follows: -
    """)
    return


@app.cell
def _():
    # Import the 'app' object from another marimo notebook
    from Wk02x_DLdata_fromYahooFinance import app
    return (app,)


@app.cell
async def _(app):
    # This executes the notebook and captures the variables
    # NOTE: 'await' works automatically inside a marimo cell
    result = await app.embed()

    # Access the dataframe with the fetched S&P 500 data
    SP500_data = result.defs["df_raw"]

    # Display the fetched data
    SP500_data
    return (SP500_data,)


@app.cell
def _(mo):
    mo.md(r"""
    _**Note:**_

    - The marimo notebook `Wk02x_DLdata_fromYahooFinance.py` is currently restricted to fetch 5 tickers each year for testing only
    - You can edit the notebook to remove the restriction (the original download code will take over 30 minutes to finish)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### Save fetched data to a `.csv` file for future access (`sp500_raw_data.csv`)
    """)
    return


@app.cell
def _(SP500_data):
    # Save fetched data to a .csv file
    SP500_data.to_csv("sp500_raw_data.csv", index=False)   

    print("\nData saved to sp500_raw_data.csv")
    print(f"Total records collected: {len(SP500_data)}")  
    return


if __name__ == "__main__":
    app.run()
