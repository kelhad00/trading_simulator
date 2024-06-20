import os.path
import pandas as pd

from dash import callback, Input, Output, State, ALL, no_update, dcc

from trade.utils.settings.create_market_data import bull_trend, bear_trend, flat_trend, export_generated_data, \
    get_generated_data, add_pattern
from trade.utils.settings.display import display_chart
from trade.utils.settings.data_handler import scale_market_data, load_data, get_data_size
from trade.layouts.settings.charts import timeline_item, ordinal
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
        return values.index(None) - 1
    else:
        return len(values) - 1




@callback(
    Output("modify-final-chart-container", "children"),
    Output("market", "data"),
    Input("slider-alpha", "value"),
    Input("slider-length", "value"),
    Input("slider-start", "value"),
    Input({"type": "timeline-radio", "index": ALL}, "value"),
    Input("select-company-modal", "value"),
    prevent_initial_call=True
)
def update_chart(alpha, length, start_value, radio_trends, companies):
    if None in radio_trends:
        return no_update

    try:
        # Load the dataset
        dataset = load_data(os.path.join(dlt.data_path, 'CAC40.csv'))
        data_size = get_data_size(dataset)

        figures = []
        dataframes = []
        for company in companies:
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
                    data_list[0] = scale_market_data(trend, start_value)
                else:
                    data_list[index] = scale_market_data(trend, data_list[index-1].at[length-1, 'Close'])

            # Concatenate the data and update the Date column
            final_chart = pd.concat(data_list).reset_index(drop=True)
            final_chart['Date'] = pd.date_range(start='1/1/2005', periods=final_chart.shape[0], freq='D')

            # Get the chart
            fig = display_chart(final_chart, 0, final_chart.shape[0], company)
            figures.append(fig)
            dataframes.append(final_chart.to_dict())

        print(len(figures))

        children = [dcc.Graph(figure=fig) for fig in figures]

        return children, dataframes

    except Exception as e:
        print(e)
        return no_update



@callback(
    Output("market", "data", allow_duplicate=True),
    Output("modal", "opened", allow_duplicate=True),
    Output({"type": "timeline-radio", "index": ALL}, "value"),

    Input("generate-button", "n_clicks"),
    State("market", "data"),
    State("select-company-modal", "value"),
    State("number-trends", "value"),
    prevent_initial_call=True
)
def cb_export_generated_data(n, datas, companies, nb_radio):
    if datas is None or datas == []:
        return no_update

    for index, data in enumerate(datas):
        df = pd.DataFrame.from_dict(data)
        export_generated_data(df, companies[index])

    return list(), False, [None] * nb_radio


@callback(
    Output("final-chart", "figure"),
    Input("select-company", "value"),
    Input("market", "data"),
)
def update_graph(company, data):
    try:
        df = get_generated_data().loc[company]
        fig = display_chart(df, 0, df.shape[0], company)
        return fig

    except Exception as e:
        return {"data": [], "layout": {}, "frames": []}


@callback(
    Output("modal", "opened"),
    Output("select-company-modal", "value"),
    Input("modify-button", "n_clicks"),
    State("modal", "opened"),
    State("select-company", "value"),
    prevent_initial_call=True
)
def open_modal(n, opened, company):
    print("comp", company)
    return not opened, [company]


