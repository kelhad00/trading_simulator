import os

from dash import callback, Input, Output, State, no_update, dcc

from trade.utils.settings.create_market_data import get_generated_data
from trade.utils.settings.display import display_chart

from trade.defaults import defaults as dlt

from dash.exceptions import PreventUpdate


@callback(
    Output("chart", "figure"),
    Input("select-company", "value"),
    Input("figures", "data"),
    prevent_initial_call=True
)
def update_graph(company, data):
    """
    Update the graph with the selected company
    Args:
        company: The selected company
        (data: (is only used to trigger the callback when new generated charts are stored in the csv file))
    Returns:
        The updated graph
    """
    try:
        df = get_generated_data()  # Get the data of all companies

        # companies = df.columns.get_level_values('symbol').unique()
        # portfolio_value = {c: 0 for c in companies}

        df = df[company]  # Get the data of the selected company

        return display_chart(df, 0, df.shape[0], company) # Display the chart

    except Exception as e:
        print('Error :', e)
        return {"data": [], "layout": {}, "frames": []}


@callback(
    Output("modal", "opened"),
    Output("modal-select-companies", "value"),
    Input("modify-button", "n_clicks"),
    State("modal", "opened"),
    State("select-company", "value"),
    prevent_initial_call=True
)
def open_modal(n, opened, company):
    """
    Open the modal to generate charts and automatically select the company in the dropdown
    """
    return not opened, [company]




@callback(
    Output("chart", "figure", allow_duplicate=True),
    Input("button-delete-charts", "n_clicks"),
    State("select-company", "value"),
    prevent_initial_call=True
)
def delete_revenues(n, company):
    """
    Delete the revenues
    Args:
        n: The number of clicks
        company: The company selected
    Returns:
        The revenues
    """
    if company is None:
        raise PreventUpdate

    df = get_generated_data()
    symbols = df.columns.get_level_values('symbol').unique()
    if company in symbols:
        df = df.drop(company, axis=1, level='symbol')

    # Save data to single CSV file
    file_path = os.path.join(dlt.data_path, 'generated_data.csv')
    df.to_csv(file_path)

    return {"data": [], "layout": {}, "frames": []}



