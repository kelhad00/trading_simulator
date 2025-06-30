import json
import math
import dash
from dash import Output, Input, State, callback, page_registry, ctx, no_update, html
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

from trade.app import app
from trade.utils.graph.candlestick_charts import create_graph
from trade.utils.market import get_market_dataframe, get_last_timestamp, get_revenues_dataframe, get_price_dataframe
from trade.locales import translations as tls
from trade.defaults import defaults as dlt


def get_next_timestamp_by_granularity(current_timestamp, granularity):
    """
    Get the next timestamp based on the granularity setting
    
    Args:
        current_timestamp: The current timestamp
        granularity: The granularity setting ('H', 'D', 'W', 'M')
    
    Returns:
        The next timestamp based on granularity
    """
    if not current_timestamp:
        return current_timestamp
    
    # Ensure timestamp is properly parsed and convert to timezone-naive
    try:
        timestamp = pd.to_datetime(current_timestamp).tz_localize(None)
    except:
        # If parsing fails, try without timezone
        timestamp = pd.to_datetime(current_timestamp)
    
    if granularity == 'H':
        # Next hour
        return timestamp + pd.Timedelta(hours=1)
    elif granularity == 'D':
        # Next day
        return timestamp + pd.Timedelta(days=1)
    elif granularity == 'W':
        # Next week
        return timestamp + pd.Timedelta(weeks=1)
    elif granularity == 'M':
        # Next month
        return timestamp + pd.DateOffset(months=1)
    else:
        # Default to next day
        return timestamp + pd.Timedelta(days=1)


def get_timestamp_display_format(timestamp, granularity):
    """
    Get the appropriate display format for the timestamp based on granularity
    
    Args:
        timestamp: The timestamp to format
        granularity: The granularity setting
    
    Returns:
        Formatted timestamp string
    """
    if not timestamp:
        return ""
    
    # Ensure timestamp is properly parsed and convert to timezone-naive
    try:
        timestamp = pd.to_datetime(timestamp).tz_localize(None)
    except:
        # If parsing fails, try without timezone
        timestamp = pd.to_datetime(timestamp)
    
    if granularity == 'H':
        return timestamp.strftime("%Y-%m-%d %H:%M")
    elif granularity == 'D':
        return timestamp.strftime("%Y-%m-%d")
    elif granularity == 'W':
        return timestamp.strftime("%Y-%m-%d")
    elif granularity == 'M':
        return timestamp.strftime("%Y-%m")
    else:
        return timestamp.strftime("%Y-%m-%d")


@callback(
    Output("company-selector", "data"),
    Output("company-selector", "value"),
    Input("companies", "data"),
    State("company-selector", "data"),
)
def update_select_companies_options(companies, select_options):
    """
    Function to update the options of the company selector
    Args:
        companies: The list of companies --> it contains all the companies, even the ones that don't have charts assigned
        select_options: The current options of the company selector
    Returns:
        The new options of the company selector
        the value of the company selector
    """
    # Get the companies that are in the portfolio
    options = [{"label": value["label"], "value": key} for key, value in companies.items() if value["got_charts"]]

    if select_options == options:
        value = no_update
    else:
        value = list(companies.keys())[0]

    return options, value


@callback(
    Output("modal", "opened"),
    Input("timestamp", "data"),
    prevent_initial_call=True
)
def open_modal_on_end_or_last(timestamp):
    # Si simulation terminée (timestamp == "END")
    if timestamp == "END":
        return True
    # Si timestamp est le dernier disponible (logique héritée)
    last_timestamp = get_last_timestamp(get_market_dataframe())
    if timestamp == last_timestamp:
        return True
    return no_update


@callback(
    Output("periodic-updater", "interval"),
    Input("update-time", "data"),
)
def update_interval(update_time):
    """Function to update the interval of the periodic updater"""
    try:
        # Ensure update_time is numeric and not NaN
        if update_time is None or (isinstance(update_time, float) and math.isnan(update_time)):
            return 5000
        update_time = float(update_time)
        return int(update_time)
    except (ValueError, TypeError):
        # Default to 5000ms if conversion fails
        return 5000


@callback(
    Output('timestamp', 'data'),
    Output('company-graph', 'figure'),
    Output("company-select-cash","children"),
    Output("timer", "children"),
    Input('periodic-updater', 'n_intervals'),
    Input('company-selector', 'value'),
    State('timestamp', 'data'),
    State('company-graph', 'figure'),
)
def update_graph(n, company, timestamp, current_fig, range=100):
    """
    Function to update the market graph with the latest data and timestamp

    Args:
        company: The selected company
        timestamp: The last timestamp
        current_fig: The current state of the figure
    Returns:
        The updated timestamp and the new graph
    """
    try:
        # Determining which callback input changed
        if ctx.triggered_id == 'periodic-updater':
            next_graph = True
        else:
            next_graph = False  # Don't update the timestamp if the user selects a new company

        dftmp = get_market_dataframe()[company]
        
        # If we need to advance to the next timestamp based on granularity
        if next_graph and timestamp:
            # Calculate the next expected timestamp based on granularity
            next_expected_timestamp = get_next_timestamp_by_granularity(timestamp, dlt.granularity)
            
            # Convert index to DatetimeIndex (force utc, then localize to None)
            available_timestamps = pd.to_datetime(dftmp.index, utc=True).tz_localize(None)
            next_expected_timestamp = pd.to_datetime(next_expected_timestamp, utc=True).tz_localize(None)
            
            # Find the closest timestamp that is >= next_expected_timestamp
            future_timestamps = available_timestamps[available_timestamps >= next_expected_timestamp]
            
            if len(future_timestamps) > 0:
                # Use the closest available timestamp
                new_timestamp = future_timestamps[0]
                # Convert back to string format for consistency
                timestamp = new_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            else:
                # Si plus de timestamp disponible, signaler la fin de simulation
                fig = make_subplots()
                fig.add_annotation(text="Fin de simulation", xref="paper", yref="paper", showarrow=False, font=dict(size=20))
                return "END", fig, "N/A", "Fin de simulation"
        
        # Récupérer le prix de l'action de façon sécurisée
        try:
            stock_price_val = get_price_dataframe().loc[timestamp, company]
            if pd.isna(stock_price_val):
                stock_price = "N/A"
            else:
                stock_price = str(math.ceil(stock_price_val))+" €"
        except Exception as e:
            print(f"Error retrieving stock price for {company} at {timestamp}: {e}")
            stock_price = "N/A"

        # Ensure the columns are correctly named
        dftmp.columns = ['Open', 'High', 'Low', 'Close', 'adjclose', 'Volume', 'long_MA', 'short_MA', '200_MA']

        fig, timestamp = create_graph(
            dftmp,
            timestamp,
            next_graph,
            range
        )

        # Define chart layouts
        fig.update_layout(
            xaxis_title=tls[page_registry['lang']]["market-graph"]['x'],
            yaxis_title=tls[page_registry['lang']]["market-graph"]['y'],
            yaxis_tickprefix='€',
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(x=0, y=1.0),
            xaxis_rangeslider_visible=False,
            yaxis2=dict(
                title='RSI',
                overlaying='y',
                side='right',
                range=[0, 100]
            ),
            annotations=[
                dict(
                    x=0.5, y=85, xref="paper", yref="y2",
                    text=f"<b>{tls[page_registry['lang']]['market-graph']['legend']['upper zone']}</b>",
                    showarrow=False,
                    font=dict(size=14, color="black", family="Arial")
                ),
                dict(
                    x=0.5, y=15, xref="paper", yref="y2",
                    text=f"<b>{tls[page_registry['lang']]['market-graph']['legend']['lower zone']}</b>",
                    showarrow=False,
                    font=dict(size=14, color="black", family="Arial")
                ),
                dict(
                    x=0.05, y=75, xref="paper", yref="y2",
                    text=f"<b>{tls[page_registry['lang']]['market-graph']['legend']['upper-limit']}</b>",
                    showarrow=False,
                    font=dict(size=14, color="black", family="Arial")
                ),
                dict(
                    x=0.05, y=25, xref="paper", yref="y2",
                    text=f"<b>{tls[page_registry['lang']]['market-graph']['legend']['lower-limit']}</b>",
                    showarrow=False,
                    font=dict(size=14, color="black", family="Arial")
                )
            ]
        )

        # Change language on the legend
        fig.for_each_trace(
            lambda t: t.update(name=tls[page_registry["lang"]]["market-graph"]["legend"][t.name])
        )

        # Préserver l'état de visibilité des courbes du graphique précédent
        if current_fig and 'data' in current_fig and ctx.triggered_id == 'periodic-updater':
            for i, trace in enumerate(fig.data):
                if i < len(current_fig['data']):
                    # Vérifier si la visibilité est définie dans les données actuelles
                    if 'visible' in current_fig['data'][i]:
                        trace.visible = current_fig['data'][i]['visible']
                    # Si la visibilité n'est pas définie, vérifier la propriété legendgroup
                    elif 'legendgroup' in current_fig['data'][i]:
                        trace.visible = current_fig['data'][i]['legendgroup'] != 'hidden'
                    # Par défaut, garder la trace visible
                    else:
                        trace.visible = True

        # Format the timestamp display based on granularity
        formatted_timestamp = get_timestamp_display_format(timestamp, dlt.granularity)

        return timestamp, fig, stock_price, formatted_timestamp

    except Exception as e:
        print("Error", e)
        return no_update, no_update, no_update, no_update

@callback(
    Output('revenue-graph', 'figure'),
    Input('periodic-updater', 'n_intervals'),
    Input('company-selector', 'value'),
    State('timestamp', 'data'),
    State("companies", "data")
)
def update_revenue(n, company, timestamp, companies):
    """
    Function to update the revenue graph with the latest data
    Args:
        company: The selected company
        timestamp: The last timestamp
    Returns:
        The new revenue graph
    """
    try:
        # If the company is an index, don't display the revenue graph
        if companies[company]['activity'] == "Indice":
            return no_update

        timestamp = pd.to_datetime(timestamp)

        # When it's the timestamp that calls the callback,
        # it's possible that a new year is available, so update the information.
        # The logic depends on the granularity:
        # - For monthly granularity: update every month (revenues are annual data)
        # - For weekly granularity: update in the first week of a new year
        # - For daily granularity: update on January 1st
        # - For hourly granularity: update at 00:00 on January 1st
        
        if ctx.triggered_id == 'periodic-updater':
            current_year = timestamp.year
            current_month = timestamp.month
            current_week = timestamp.isocalendar()[1]
            current_day = timestamp.day
            current_hour = timestamp.hour
            
            # Check if we should update based on granularity
            should_update = False
            
            if dlt.granularity == 'M':
                # For monthly granularity, update every month since revenues are annual data
                # and we want to show the graph as soon as we have data for a new year
                should_update = True
            elif dlt.granularity == 'W' and current_week == 1:
                # For weekly granularity, update in the first week of the year
                should_update = True
            elif dlt.granularity == 'D' and current_day == 1 and current_month == 1:
                # For daily granularity, update on January 1st
                should_update = True
            elif dlt.granularity == 'H' and current_hour == 0 and current_day == 1 and current_month == 1:
                # For hourly granularity, update at 00:00 on January 1st
                should_update = True
            
            # If we shouldn't update based on granularity, return no_update
            if not should_update:
                return no_update

        df = get_revenues_dataframe()

        # Format these data to be easily used
        df = df[company].T.reset_index()
        df['asOfDate'] = pd.to_datetime(df['asOfDate']).dt.year
        df['NetIncome'] = pd.to_numeric(df['NetIncome'], errors='coerce')
        df['TotalRevenue'] = pd.to_numeric(df['TotalRevenue'], errors='coerce')

        # Filter the data to only keep the data from the previous years
        year = timestamp.year
        df = df.loc[df['asOfDate'] < year]

        # Create the graph
        fig = go.Figure(data=[
            go.Bar(
                name=tls[page_registry["lang"]]["revenue-graph"]['totalRevenue'],
                x=df['asOfDate'], y=df['TotalRevenue']
            ),
            go.Bar(
                name=tls[page_registry["lang"]]["revenue-graph"]['netIncome'],
                x=df['asOfDate'], y=df['NetIncome']
            )
        ])
        fig.update_layout(
            yaxis_tickprefix='€',
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(x=0, y=1.0)
        )

        if ctx.triggered_id == 'company-selector':
            # Go back to the market graph when the user selects a new company
            return fig
        else:
            # If new information has been added, add it to the revenue graph,
            # but don't change anything else.
            return fig
    except Exception as e:
        print("Error", e)
        return no_update


@callback(
    Output('revenue-graph', 'style'),
    Output('company-graph', 'style'),
    Input('segmented', "value")
)
def toggle_graph_type(value):
    """
    Function to toggle between the market graph and the revenue graph
    Args:
        value: The value of the segmented control
    Returns:
        The style of the revenue graph and the market graph
    """
    lang = page_registry['lang']

    if value == tls[lang]['tab-market']:
        return {'display': 'none'}, {'display': 'block'}
    else:
        return {'display': 'block'}, {'display': 'none'}

