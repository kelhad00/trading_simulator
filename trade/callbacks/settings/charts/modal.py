import os.path
import pandas as pd
import time

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

# --- Logging utils ---
VERBOSE_LOGS = False

def _debug(msg: str):
    if VERBOSE_LOGS:
        print(msg)


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
def generate_new_charts(alpha, length, start_value, radio_trends, companies, dates=None):
    """Generate OHLC charts based on modal parameters for selected companies.

    Args:
        alpha (int): Alpha used to scale trend amplitude.
        length (int): Number of candles per trend block.
        start_value (int): Initial scaling value for the first block.
        radio_trends (list[str]): Sequence of trends ('bull', 'bear', 'flat').
        companies (list[str]): Selected company tickers.
        dates (pd.DatetimeIndex|None): Optional explicit dates for the data.

    Returns:
        tuple[list, list]: (list of figures, list of DataFrame dicts)
    """
    start_date = dlt.start_date

    if not isinstance(companies, list):
        companies = [companies]

    if None in radio_trends:  # Check if all the fields are filled
        return no_update

    timeout = 1.0  # secondes
    start_time = time.time()
    attempt = 0
    current_alpha = alpha
    while True:
        try:
            # Load the dataset
            dataset = load_data(os.path.join(dlt.data_path, 'CAC40.csv'))
            data_size = get_data_size(dataset)

            dataframes = []  # Store the dataframes to export them later
            figures = []  # Store the figures to display them

            # Utiliser les dates fournies ou obtenir la première date
            if dates is None:
                try:
                    # Put the same day as the generated_data file
                    df = get_generated_data()
                    first_timestamp = get_first_timestamp(df)
                except:
                    # if there is no data, put start_date
                    first_timestamp = start_date
            else:
                first_timestamp = dates[0]

            for company in companies:
                # Get the trends
                trends = []
                for i in radio_trends:
                    if i == "bull":
                        trends.append(bull_trend(dataset, data_size, current_alpha, length))
                    elif i == "bear":
                        trends.append(bear_trend(dataset, data_size, current_alpha, length))
                    else:
                        trends.append(flat_trend(dataset, data_size, 20, length))

                # Get the data
                data_list = []
                for index, trend in enumerate(trends):
                    if isinstance(trend, pd.DataFrame):
                        # flat_trend retourne un DataFrame déjà prêt
                        df_flat = trend.copy()
                        if dates is not None:
                            df_flat['Date'] = dates[:len(df_flat)]
                        else:
                            df_flat['Date'] = pd.date_range(start=first_timestamp, periods=df_flat.shape[0], freq='D')
                        data_list.append(df_flat)
                    else:
                        # bull/bear : trend est un index
                        data_list.append(dataset[trend:trend + length].reset_index(drop=True))

                # Scale the data
                for index, trend in enumerate(data_list):
                    if isinstance(trend, pd.DataFrame) and trend.shape[1] == 4 and set(trend.columns) == {'Open', 'High', 'Low', 'Close'}:
                        # flat_trend : ne pas rescaler, déjà prêt
                        continue
                    if index == 0:
                        data_list[0] = scale_market_data(trend, start_value)
                    else:
                        data_list[index] = scale_market_data(trend, data_list[index-1].at[length-1, 'Close'])

                # Concatenate the data and update the Date column
                final_chart = pd.concat(data_list).reset_index(drop=True)
                if dates is not None:
                    # Utiliser les dates spécifiques fournies
                    final_chart['Date'] = dates[:len(final_chart)]
                else:
                    # Générer des dates séquentielles
                    final_chart['Date'] = pd.date_range(start=first_timestamp, periods=final_chart.shape[0], freq='D')

                # Get the chart
                fig = display_chart(final_chart, 0, final_chart.shape[0], company)
                figures.append(fig)
                dataframes.append(final_chart.to_dict())

            children = [dcc.Graph(figure=fig) for fig in figures]

            return children, dataframes
        except Exception as e:
            attempt += 1
            _debug(f"Tentative {attempt} échouée (alpha={current_alpha}) : {e}")
            current_alpha = max(int(current_alpha * 0.9), 1)
            if time.time() - start_time > timeout:
                _debug('Erreur persistante après 1 seconde d\'essais.')
                return no_update
            # sinon, on réessaie avec un alpha réduit


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
    """Persist generated charts into CSV and mark companies as configured.

    Args:
        n (int): Clicks on generate.
        datas (list): Generated DataFrames as dicts.
        companies_selected (list[str]): Selected tickers (aligned with datas).
        nb_radio (int): Number of trend blocks (to reset radios).
        companies (dict): Companies store.

    Returns:
        tuple: (cleared figures store, close modal, reset radio values, updated companies)
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
    """Select all companies in the modal multiselect."""
    return list(companies.keys())



@callback(
    Output("timeline", "children"),
    Input("number-trends", "value"),
    State("timeline", "children"),
    prevent_initial_call=True
)
def update_timeline(nb, children, min=1, max=5):
    """Update number of trend radio blocks to display in the modal.

    Args:
        nb (int): Desired count of radio inputs.
        children (list): Existing radio inputs.
        min (int): Minimum allowed.
        max (int): Maximum allowed.

    Returns:
        list: Updated children list.
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
    """Compute active index of the timeline, stopping at first None value."""
    if None in values:
        return values.index(None) - 1
    else:
        return len(values) - 1




