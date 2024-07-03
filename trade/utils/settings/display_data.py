import pandas as pd
import streamlit as st
import create_market_data
import plotly.graph_objects as go
from utils import scale_market_data, load_data, get_data_size

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

    # Display the chart on streamlit
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)


def display_page(dataset):
    '''
    Display the streamlit page
    '''

    # Title
    st.write("## Market data creation :")

    # Parameters
    alpha = st.slider('Select alpha value', 0, 2000, 500)
    length = st.slider('Select length value', 0, 500, 100)
    start_value = st.slider('Select start value', 0, 1000, 100)

    # Load the dataset
    dataset = load_data(dataset)
    data_size = get_data_size(dataset)

    # Title
    st.write("## Chart trends :")

    # Columns
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.radio(
        "1st market movement",
        key="trend1",
        options=["Bull 📈", "Bear 📉", "Flat"],
        )

    with col2:
        st.radio(
        "2nd market movement",
        key="trend2",
        options=["Bull 📈", "Bear 📉", "Flat"],
        )
    
    with col3:
        st.radio(
        "3rd market movement",
        key="trend3",
        options=["Bull 📈", "Bear 📉", "Flat"],
        )

    with col4:
        st.radio(
        "4th market movement",
        key="trend4",
        options=["Bull 📈", "Bear 📉", "Flat"],
        )

    with col5:
        st.radio(
        "5th market movement",
        key="trend5",
        options=["Bull 📈", "Bear 📉", "Flat"],
        )

    # Tiltle
    st.write("## Chart patterns :")

    # Parameters
    nbr_patterns = st.number_input("Number of patterns", min_value=0, max_value=4, value=0, step=1)

    # Title
    st.write("## Final chart :")

    # Create the final chart
    trends = {}
    for i in range(1, 6):
        if st.session_state[f'trend{i}'] == "Bull 📈":
            trends[f'trend{i}'] = create_market_data.bull_trend(dataset, data_size, alpha, length)
        elif st.session_state[f'trend{i}'] == "Bear 📉":
            trends[f'trend{i}'] = create_market_data.bear_trend(dataset, data_size, alpha, length)
        else:
            trends[f'trend{i}'] = create_market_data.flat_trend(dataset, data_size, 20, length)


    data1 = dataset[trends['trend1']:trends['trend1']+length].reset_index(drop=True)
    data2 = dataset[trends['trend2']:trends['trend2']+length].reset_index(drop=True)
    data3 = dataset[trends['trend3']:trends['trend3']+length].reset_index(drop=True)
    data4 = dataset[trends['trend4']:trends['trend4']+length].reset_index(drop=True)
    data5 = dataset[trends['trend5']:trends['trend5']+length].reset_index(drop=True)

    # Scale the data
    data1 = scale_market_data(data1, start_value)
    data2 = scale_market_data(data2, data1.at[length-1, 'Close'])
    data3 = scale_market_data(data3, data2.at[length-1, 'Close'])
    data4 = scale_market_data(data4, data3.at[length-1, 'Close'])
    data5 = scale_market_data(data5, data4.at[length-1, 'Close'])

    # Concatenate the data
    final_chart = pd.concat([data1, data2, data3, data4, data5]).reset_index(drop=True)

    # Add patterns
    if nbr_patterns > 0:
        final_chart = create_market_data.add_pattern(final_chart, nbr_patterns)
        
    # Chnage the Date column
    final_chart['Date'] = pd.date_range(start='1/1/2005', periods=final_chart.shape[0], freq='D')

    # Plot the final chart
    display_chart(final_chart, 0, final_chart.shape[0], 'Final Chart')

    # Save the final chart
    if st.button("Save the chart", type="primary"):
        final_chart.to_csv('final_chart.csv', index=False)
        st.success("The chart has been saved successfully !")