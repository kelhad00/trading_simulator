import os.path
import pandas as pd

from dash import callback, Input, Output, State, ALL, no_update

from trade.utils.settings.create_market_data import bull_trend, bear_trend, flat_trend, add_pattern
from trade.utils.settings.display import display_chart
from trade.utils.settings.data_handler import scale_market_data, load_data, get_data_size
from trade.layouts.settings import timeline_item, ordinal
from trade.defaults import defaults as dlt



@callback(
    Output("timeline", "children"),
    Input("number-trends", "value"),
    State("timeline", "children"),
    prevent_initial_call=True
)
def update_timeline(nb, children):
    if nb == "" or nb is None or nb < 1 or nb > 5:
        return no_update
    try:
        while len(children) != nb:
            if len(children) < nb:
                children.append(
                    timeline_item(
                        id=f"timeline",
                        index=len(children) + 1,
                        title=f"{ordinal(len(children) + 1)} market movement"

                    )
                )
            else:
                children.pop()
        return children
    except:
        return no_update


@callback(
    Output("timeline", "active"),
    Input({"type": f"timeline-radio", "index": ALL}, "value"),
)
def update_values(values):
    if None in values:
        return values.index(None)
    else:
        return len(values)-1




@callback(
    Output("final-chart", "figure"),
    Input("slider-alpha", "value"),
    Input("slider-length", "value"),
    Input("number-trends", "value"),
    Input({"type": f"timeline-radio", "index": ALL}, "value"),
    Input("number-patterns", "value"),
    prevent_initial_call=True
)
def update_chart(alpha, length, nb_trends, radio_trends, nb_patterns):
    if None in radio_trends:
        return no_update

    try:
        # Load the dataset
        dataset = load_data(os.path.join(dlt.data_path, 'CAC40.csv'))
        data_size = get_data_size(dataset)

        # Create the final chart
        trends = []
        for i in radio_trends:
            if i == "bull":
                trends.append(bull_trend(dataset, data_size, alpha, length))
            elif i == "bear":
                trends.append(bear_trend(dataset, data_size, alpha, length))
            else:
                trends.append(flat_trend(dataset, data_size, 20, length))

        data_list = []
        for index, trend in enumerate(trends):
            data_list.append(dataset[trend:trend + length].reset_index(drop=True))

        for index, trend in enumerate(data_list):
            if index == 0:
                data_list[0] = trend
            else:
                data_list[index] = scale_market_data(trend, data_list[index-1].at[length-1, 'Close'])

        # Concatenate the data
        final_chart = pd.concat(data_list).reset_index(drop=True)

        if nb_patterns > 0:
            final_chart = add_pattern(final_chart, nb_patterns)

        # Chnage the Date column
        final_chart['Date'] = pd.date_range(start='1/1/2005', periods=final_chart.shape[0], freq='D')

        # Plot the final chart
        return display_chart(final_chart, 0, final_chart.shape[0], 'Final Chart')

    except Exception as e:
        print(e)
        return no_update


