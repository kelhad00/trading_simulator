"""The moving averages are always plain lines, from the first candle to the last.
Without mode='lines', Plotly drew a marker on every point while there were
fewer than 20 candles, then the markers vanished at candle 20."""
from trade.utils.graph.candlestick_charts import create_graph


def moving_averages(fig):
    return [t for t in fig.data if t.type == "scatter"]


def test_few_candles_plain_lines(market_df):
    fig, _ = create_graph(market_df["AAA"], market_df.index[5], next_graph=False)   # 6 candles
    lines = moving_averages(fig)
    assert len(lines) == 3 and len(lines[0].x) < 20
    assert all(t.mode == "lines" for t in lines)


def test_many_candles_plain_lines(market_df):
    fig, _ = create_graph(market_df["AAA"], market_df.index[100], next_graph=False)
    assert all(t.mode == "lines" for t in moving_averages(fig))
