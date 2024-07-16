from dash import callback, Input, Output, State

from trade.utils.settings.create_market_data import get_generated_data
from trade.utils.settings.display import display_chart


@callback(
    Output("chart", "figure"),
    Input("select-company", "value"),
    Input("figures", "data"),
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
        df = get_generated_data()[company]  # Get the data of the selected company
        return display_chart(df, 0, df.shape[0], company)  # Display the chart

    except Exception as e:
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



