import os
from datetime import datetime

import pandas as pd

from trade.defaults import defaults as dlt

# def get_market_dataframe():
#     try:
#         # file_path = os.path.join(dlt.data_path, 'generated_data.csv')
#         file_path = os.path.join(dlt.data_path, 'market_data.csv')
#         df = pd.read_csv(file_path, index_col=0, header=[0, 1])
#
#         return df
#     except:
#         print('ERROR: No market data found in ' + dlt.data_path + ' folder.')
#         raise FileNotFoundError

def get_revenues_dataframe():
    # Import income data of the selected company
    file_path = os.path.join(dlt.data_path, 'revenue.csv')
    df = pd.read_csv(file_path, index_col=0, header=[0, 1])
    return df


def aggregate_ohlc_data(df, interval):
    """
    Aggregate OHLC data according to the selected interval
    
    Args:
        df: DataFrame with OHLC data
        interval: The interval to aggregate to ('h', 'D', 'W', 'ME')
    
    Returns:
        Aggregated DataFrame with OHLC data
    """
    if interval == 'h':
        # No aggregation needed for hourly data
        return df
    
    # Create a copy to avoid modifying the original
    df_agg = df.copy()
    
    # Resample based on interval
    if interval == 'D':
        # Aggregate to daily
        resampled = df_agg.resample('D')
    elif interval == 'W':
        # Aggregate to weekly (Monday as start of week)
        resampled = df_agg.resample('W-MON')
    elif interval == 'ME':
        # Aggregate to monthly (Month End)
        resampled = df_agg.resample('M')
    else:
        return df_agg
    
    # Apply OHLC aggregation rules
    aggregated = {}
    
    for company in df_agg.columns.get_level_values(0).unique():
        company_data = df_agg[company]
        
        # Aggregate OHLC for each company
        agg_open = resampled[company]['Open'].first()
        agg_high = resampled[company]['High'].max()
        agg_low = resampled[company]['Low'].min()
        agg_close = resampled[company]['Close'].last()
        
        # Create aggregated DataFrame for this company
        company_agg = pd.DataFrame({
            'Open': agg_open,
            'High': agg_high,
            'Low': agg_low,
            'Close': agg_close
        })
        
        # Add volume if it exists
        if 'Volume' in company_data.columns:
            company_agg['Volume'] = resampled[company]['Volume'].sum()
        
        # Add moving averages if they exist (use last value of the period)
        if 'long_MA' in company_data.columns:
            company_agg['long_MA'] = resampled[company]['long_MA'].last()
        if 'short_MA' in company_data.columns:
            company_agg['short_MA'] = resampled[company]['short_MA'].last()
        if '200_MA' in company_data.columns:
            company_agg['200_MA'] = resampled[company]['200_MA'].last()
        if 'RSI' in company_data.columns:
            company_agg['RSI'] = resampled[company]['RSI'].last()
        
        aggregated[company] = company_agg
    
    # Combine all companies
    if aggregated:
        result = pd.concat(aggregated.values(), axis=1, keys=aggregated.keys())
        # Drop rows with all NaN values
        result = result.dropna(how='all')
        return result
    
    return df_agg


def get_market_dataframe(generated=True, interval=None):
    file = 'generated_data.csv' if generated else 'market_data.csv'

    try:
        file_path = os.path.join(dlt.data_path, file)
        # Read CSV without parsing dates
        df = pd.read_csv(file_path, index_col=0, header=[0, 1])
        # Always parse index as datetime with utc=True
        df.index = pd.to_datetime(df.index, utc=True, errors='coerce')
        # Convert to Europe/Paris for local time compatibility
        df.index = df.index.tz_convert('Europe/Paris')
        
        # Aggregate data if interval is specified
        if interval and interval != 'h':
            df = aggregate_ohlc_data(df, interval)
        
        return df
    except Exception as e:
        print('ERROR: No market data found in ' + dlt.data_path + ' folder.')
        print(e)
        return None
        # raise FileNotFoundError



def get_price_dataframe(interval=None):
    df = get_market_dataframe(interval=interval)
    if df is None:
        return None
    df.index = df.index.map(lambda x: format_timestamp(x, interval))
    price_list = df.xs('Close', axis=1, level=1)
    return price_list


def get_first_timestamp(market_df, range=0):
    try:
        timestamp = market_df.index[range]
        return timestamp
    except:
        return 0


def get_last_timestamp(market_df):
    try:
        timestamp = market_df.index[-1]
        return timestamp
    except:
        return 0

def format_timestamp(timestamp, interval=None):
    if not isinstance(timestamp, str):
        if timestamp.tzinfo is not None :
            timestamp = timestamp.replace(tzinfo=None)
    
    # Use provided interval or default granularity
    current_interval = interval if interval else dlt.granularity
    
    if current_interval == 'h':
        return timestamp.strftime('%Y-%m-%d %H:%M')
    elif current_interval == 'ME':
        return timestamp.strftime('%Y-%m')
    else:
        return timestamp.strftime('%Y-%m-%d')