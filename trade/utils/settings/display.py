import plotly.graph_objects as go


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

    # Chart
    fig = go.Figure(data=[go.Candlestick(
                x=data['Date'],
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name=data_name)])

    fig.update_layout(
        title=data_name,
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
    )

    return fig

    # Display the chart on streamlit
    # st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
