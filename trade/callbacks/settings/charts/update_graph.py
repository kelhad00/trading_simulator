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
    """Update the chart figure when the selected company or data changes.

    Args:
        company (str): Selected company ticker.
        data: Only used as a trigger when new charts are stored.

    Returns:
        dict: Plotly figure dict for the selected company's chart.
    """
    try:
        df = get_generated_data()[company]
        return display_chart(df, 0, df.shape[0], company)  # Display the chart

    except Exception as e:
        print('Error while rendering chart :', e)
        return {"data": [], "layout": {}, "frames": []}
