import os

from dash import Output, Input, State, callback
from dash.exceptions import PreventUpdate

from trade.defaults import defaults as dlt
from trade.utils.settings.create_market_data import get_generated_data


@callback(
    Output("chart", "figure", allow_duplicate=True),
    Output("companies", "data", allow_duplicate=True),
    Input("button-delete-charts", "n_clicks"),
    State("select-company", "value"),
    State("companies", "data"),
    prevent_initial_call=True
)
def delete_revenues(n, company, companies):
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

    companies[company]['got_charts'] = False

    return {"data": [], "layout": {}, "frames": []}, companies
