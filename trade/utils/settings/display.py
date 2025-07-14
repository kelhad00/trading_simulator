import plotly.graph_objects as go
from trade.defaults import defaults as dlt


def display_chart(data, index, length, data_name):
    '''
    Display a candlestick chart using Plotly
    '''

    # Plotly configuration
    PLOTLY_CONFIG = {
        'displaylogo': False,
        'modeBarButtonsToRemove': ['select','lasso2d', 'zoom', 'resetScale'],
        'scrollZoom': True
    }

    # Slice the data
    data = data.iloc[index:index+length]

    # Get the company label if it exists in companies_list
    if data_name in dlt.companies_list:
        display_name = dlt.companies_list[data_name]['label']
    else:
        display_name = data_name

    # Chart
    fig = go.Figure(data=[go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name=display_name)])

    fig.update_layout(
        title=display_name,
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
    )

    return fig

    # Display the chart on streamlit
    # st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
