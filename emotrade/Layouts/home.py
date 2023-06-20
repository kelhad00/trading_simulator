from dash import html, dcc
from emotrade.Locales import translations as tls

import dash

# Layout of the home page
def main_layout(lang="fr"):
    return html.Div([

		# Dropdown to change the language
		html.Div([
			html.Button([
				html.Span(lang), html.Span(className="arrow")
			]),
			html.Ul([
				html.Li(dcc.Link(l, href=f'/{l}/')) for l in tls.keys() if l != lang
			])
		], className="switch-lang-btn"),

        # main content
        html.H1(children=tls[lang]['welcome'], style = {'margin-top' : 60}),
        
        html.P(children=tls[lang]['info_txt']),

		html.Img(src=dash.get_asset_url('photo_finance_2.png'), style = {'border-radius': 30, 'margin-top': 40, 'width': 500}),

		html.P(children=tls[lang]['signature'], style = {'margin-top': 40, 'font-size': 15, 'font-style': 'italic'}),
        
        ], style = {'font-family': 'Arial', 'text-align' : 'center'})