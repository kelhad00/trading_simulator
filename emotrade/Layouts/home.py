from dash import html, dcc
from emotrade.Locales import translations as tls

import dash

# Layout of the home page
def main_layout(lang="fr"):
    return html.Div([

        # Dropdown to change the language
        html.Div([
			dcc.Link( l, href=f'/{l}/', style = {
				'display': 'block',
				'padding': '0.7em 0.5em',
				'color': '#2f3238',
				'margin': '0.1em 0',
				'text-decoration': 'none',
				'background': '#fff',
				'border-radius': '4px',
				'border': '1px solid #ccc',
			}) for l in tls.keys() if l != lang
		], style = {'width' : '60px', 'position' : 'absolute', 'top': '10px', 'right': '10px'}),

        # main content
        html.H1(children=tls[lang]['welcome'], style = {'margin-top' : 60}),
        
        html.P(children=tls[lang]['info_txt']),

		html.Img(src=dash.get_asset_url('photo_finance_2.png'), style = {'border-radius': 30, 'margin-top': 40, 'width': 500}),

		html.P(children=tls[lang]['signature'], style = {'margin-top': 40, 'font-size': 15, 'font-style': 'italic'}),
        
        ], style = {'font-family': 'Arial', 'text-align' : 'center'})