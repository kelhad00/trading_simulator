import plotly.graph_objects as go

def display_chart(data, data_name, news_position):
    '''
    Display a candlestick chart using Plotly
    '''

    # Plotly configuration
    PLOTLY_CONFIG = {
        'displaylogo': False,
        'modeBarButtonsToRemove': ['select', 'lasso2d', 'zoom', 'resetScale'],
        'scrollZoom': True
    }

    # Chart
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=data_name)])

    if news_position is not None:
        # Ajouter des lignes verticales pour les news positives
        for pos_index in news_position[0]:  # news_position[0] contient les index des news positives
            pos_date = data.index[pos_index]
            fig.add_vline(x=pos_date, line_color="green")

        # Ajouter des lignes verticales pour les news négatives
        for neg_index in news_position[1]:  # news_position[1] contient les index des news négatives
            neg_date = data.index[neg_index]
            fig.add_vline(x=neg_date, line_color="red")

    fig.update_layout(
        title=data_name,
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
    )

    return fig

