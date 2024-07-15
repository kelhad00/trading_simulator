from dash import Output, Input, State, html, callback


@callback(
    Output('nbr-news-container', 'style'),
    Input('input-generation-mode', 'value'),
    State('nbr-news-container', 'children')
)
def update_nbr_news_container(mode, children):
    if mode == 'random':
        return {'display': 'block'}
    else:
        return {'display': 'none'}