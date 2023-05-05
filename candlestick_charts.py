import plotly.graph_objects as go
import pandas as pd

PLOTLY_CONFIG = {
    'displaylogo': False,
    'modeBarButtonsToRemove': ['toImage', 'select','lasso2d']
}

def create_candlestick_chart(company_id):
    """
    Create a candlestick chart for the selected stock

    Parameters
    ----------
    company_id : str
        NASDAQ stock name

    Returns
    -------
    plotly.graph_objects.Figure
        Candlestick chart for the selected stock

    """

    # Get saved market data
    df = pd.read_csv('market_data/' + company_id + '.csv', index_col=0)

    # Create candlestick chart for the selected stock
    figure = go.Figure(
        data = [go.Candlestick(
            x = df.index,
            open  = df['Open'],
            high  = df['High'],
            low   = df['Low'],
            close = df['Close']
        )]
    )

    # Define chart layout
    figure.update_layout(
        #title = company_id + ' stock price',
        xaxis_title = 'Date',
        yaxis_title = 'Price',
        yaxis_tickprefix = '€'
    )

    return figure


if __name__ == '__main__':
    # name = 'TSLA'
    name = input('Enter NASDAQ stock name: ')

    fig = create_candlestick_chart(name)
    fig.show()