from dash import callback, Input, Output

from trade.utils.settings.create_market_data import get_generated_data
from trade.utils.settings.display import display_chart


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
        df = get_generated_data()[company]
        return display_chart(df, 0, df.shape[0], company)  # Display the chart

    except Exception as e:
        print('Error while rendering chart :', e)
        return {"data": [], "layout": {}, "frames": []}
