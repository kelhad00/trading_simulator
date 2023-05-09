import plotly.graph_objects as go
import pandas as pd
import time

PLOTLY_CONFIG = {
    'displaylogo': False,
    'modeBarButtonsToRemove': ['toImage', 'select','lasso2d']
}

def create_candlestick_chart(company_id, timestamp):
    """
    Create a candlestick chart for the selected stock

    Parameters
    ----------
    company_id : str
        NASDAQ stock name

    timestamp : str
        timestamp of the initial market data to display (default: '2022-05-09 12:30:00-04:00')

    Returns
    -------
    plotly.graph_objects.Figure
        Candlestick chart for the selected stock

    pandas.DataFrame
        Saved market data for the selected stock

    datetime.datetime
        Last timestamp of the default market data used to create the chart
    """

    # Get saved market data
    df = pd.read_csv('market_data/' + company_id + '.csv', index_col=0)
    dftmp = df[:timestamp]

    # Create candlestick chart for the selected stock
    figure = go.Figure(
        data = [go.Candlestick(
            x = dftmp.index,
            open  = dftmp['Open'],
            high  = dftmp['High'],
            low   = dftmp['Low'],
            close = dftmp['Close']
        )]
    )

    # Define chart layout
    figure.update_layout(
        #title = company_id + ' stock price',
        xaxis_title = 'Date',
        yaxis_title = 'Price',
        yaxis_tickprefix = '€',
        showlegend=False
    )


    return figure, df, dftmp.index[-1]


def update_candlestick_chart(figure, dataframe, lasttimestamp, range = 10):
    """
    Update the candlestick chart with new market data

    Parameters
    ----------
    figure : plotly.graph_objects.Figure
        Candlestick chart for the selected stock to update

    dataframe : pandas.DataFrame
        Saved market data for the selected stock

    lasttimestamp : datetime.datetime
        Timestamp used to display the last iteration of the candlestick chart

    range : int
        number of data points to display (default: 10)

    Returns
    -------
    datetime.datetime
        Timestamp used to display the new iteration of the candlestick chart
    """

    idx = dataframe.index.get_loc(lasttimestamp)

    if (range == 0):
        # Apprend new data indefinitely
        newdata = dataframe.iloc[idx+1]

        figure.add_trace( go.Candlestick(
                x = [newdata.name],
                open  = [newdata['Open']],
                high  = [newdata['High']],
                low   = [newdata['Low']],
                close = [newdata['Close']],
        ))

        return  newdata.name

    else :
        # Append new data with a fixed range
        dftmp = dataframe.iloc[idx - (range - 2) : idx + 2]

        figure.update_traces(go.Candlestick(
                x = dftmp.index,
                open  = dftmp['Open'],
                high  = dftmp['High'],
                low   = dftmp['Low'],
                close = dftmp['Close']
        ))

        return dftmp.index[-1]


if __name__ == '__main__':
    name = 'TSLA'

    fig,df,endtime = create_candlestick_chart(name, '2022-05-05 07:00:00-04:00')
    fig.show()

    testtime = 3
    while testtime > 0:
        time.sleep(5)

        endtime = update_candlestick_chart(fig, df, endtime)
        print(endtime)

        fig.show()
        testtime -= 1