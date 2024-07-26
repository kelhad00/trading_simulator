import os.path
import pandas as pd

from dash import callback, Input, Output, State, ALL, no_update, dcc, page_registry
from dash.exceptions import PreventUpdate

from trade.utils.market import get_first_timestamp
from trade.utils.ordinal import ordinal
from trade.utils.settings.create_market_data import bull_trend, bear_trend, flat_trend, export_generated_data, \
    get_generated_data
from trade.utils.settings.display import display_chart
from trade.utils.settings.data_handler import scale_market_data, load_data, get_data_size
from trade.layouts.settings.sections.charts import timeline_item
from trade.defaults import defaults as dlt
from trade.locales import translations as tls




@callback(
    Output("modal-generated-charts-container", "children"),
    Output("figures", "data"),
    Input("slider-alpha", "value"),
    Input("slider-length", "value"),
    Input("slider-start", "value"),
    Input({"type": "timeline-radio", "index": ALL}, "value"),
    Input("modal-select-companies", "value"),
    prevent_initial_call=True
)
def generate_new_charts(alpha, length, start_value, radio_trends, companies, start_date=dlt.start_date):
    """
    Generate the charts based on the parameters selected in the modal
    Args:
        alpha (int): alpha value for the trends
        length (int): length of the trends
        start_value (int): start value for the scaling
        radio_trends (list): list of the selected trends
        companies (list): list of the selected companies
    Returns:
        list: list of the charts
        list: list of the dataframes associated with the charts
    """

    if None in radio_trends:  # Check if all the fields are filled
        return no_update

    try:
        # Load the dataset
        dataset = load_data(os.path.join(dlt.data_path, 'CAC40.csv'))
        data_size = get_data_size(dataset)

        dataframes = []  # Store the dataframes to export them later
        figures = []  # Store the figures to display them

        try:
            # Put the same day as the generated_data file
            df = get_generated_data()
            first_timestamp = get_first_timestamp(df)
        except:
            # if there is no data, put start_date
            first_timestamp = start_date

        for company in companies:
            # Get the trends
            trends = []
            for i in radio_trends:
                if i == "bull":
                    trends.append(bull_trend(dataset, data_size, alpha, length))
                elif i == "bear":
                    trends.append(bear_trend(dataset, data_size, alpha, length))
                else:
                    trends.append(flat_trend(dataset, data_size, 20, length))

            # Get the data
            data_list = []
            for index, trend in enumerate(trends):
                data_list.append(dataset[trend:trend + length].reset_index(drop=True))

            # Scale the data
            for index, trend in enumerate(data_list):
                if index == 0:
                    data_list[0] = scale_market_data(trend, start_value)
                else:
                    data_list[index] = scale_market_data(trend, data_list[index-1].at[length-1, 'Close'])

            # Concatenate the data and update the Date column
            final_chart = pd.concat(data_list).reset_index(drop=True)
            final_chart['Date'] = pd.date_range(start=first_timestamp, periods=final_chart.shape[0], freq='D')

            # Get the chart
            fig = display_chart(final_chart, 0, final_chart.shape[0], company)
            figures.append(fig)
            dataframes.append(final_chart.to_dict())

        children = [dcc.Graph(figure=fig) for fig in figures]

        return children, dataframes

    except Exception as e:
        print('Error while generating charts :', e)
        return no_update


@callback(
    Output("figures", "data", allow_duplicate=True),
    Output("modal", "opened", allow_duplicate=True),
    Output({"type": "timeline-radio", "index": ALL}, "value"),
    Output("companies", "data", allow_duplicate=True),

    Input("generate-button", "n_clicks"),
    State("figures", "data"),
    State("modal-select-companies", "value"),
    State("number-trends", "value"),
    State("companies", "data"),
    prevent_initial_call=True
)
def export_generated_charts(n, datas, companies_selected, nb_radio, companies):
    """
    Export the generated charts in the data folder (generated_data.csv) when the generate button is clicked
    Args:
        n (int): number of clicks on the generate button
        datas (list): list of the dataframes associated with the charts
        companies_selected (list): list of the selected companies
        nb_radio (int): number of radio input
        companies (dict): companies data
    Returns:
        list: list of the dataframes associated with the charts (reset to empty list because the datas are exported)
        bool: opened state of the modal (closed)
        list: list of the radio input values (reset the trends)
        companies (dict): companies data with the got_charts flag updated
    """
    if datas is None or datas == []:
        raise PreventUpdate

    for index, data in enumerate(datas):
        # Get the company name
        company = companies_selected[index]

        # Export each graph in the csv file
        df = pd.DataFrame.from_dict(data)
        export_generated_data(df, company)

        # Update the got_charts flag
        companies[company]['got_charts'] = True

    # Reset the store and close the modal
    return list(), False, [None] * nb_radio, companies


@callback(
    Output("modal-select-companies", "value", allow_duplicate=True),
    Input("select-all-stocks", "n_clicks"),
    State("companies", "data"),
    prevent_initial_call=True
)
def select_all_stocks(n, companies):
    """
    Select all the stocks in the dropdown
    """
    return list(companies.keys())



@callback(
    Output("timeline", "children"),
    Input("number-trends", "value"),
    State("timeline", "children"),
    prevent_initial_call=True
)
def update_timeline(nb, children, min=1, max=5):
    """
    Update the number of radio input (for market movement) to displayed in the modal
    Args:
        nb (int): number of radio input to display
        children (list): list of radio input
        min (int): minimum number of radio input
        max (int): maximum number of radio input
    Returns:
        list: updated children
    """

    if nb == "" or nb is None or nb < min or nb > max:
        return no_update

    try:
        while len(children) != nb:
            if len(children) < nb:  # if there is fewer children than the number of trends
                # add a new radio item
                children.append(
                    timeline_item(
                        id="timeline",
                        index=len(children) + 1,
                        title=f"{ordinal(len(children) + 1, page_registry['lang'])} {tls[page_registry['lang']]['settings']['charts']['radio']['title']}",
                    )
                )
            else:  # if there is more children than the number of trends
                children.pop()

        return children

    except Exception as e:
        print('Error :', e)
        return no_update



@callback(
    Output("timeline", "active"),
    Input({"type": f"timeline-radio", "index": ALL}, "value"),
)
def update_values(values):
    """
    Update the active state of each point of the timeline
    It stops at the first None value found in the list
    """
    if None in values:
        return values.index(None) - 1
    else:
        return len(values) - 1




