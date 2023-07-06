from dash import html, dcc, Output, Input
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
        html.H1(tls[lang]['welcome']),

        html.P(tls[lang]['info_txt']),

		html.Img(src=dash.get_asset_url('photo_finance_2.png')),

		html.P(tls[lang]['signature']),

		dcc.Link(tls[lang]['button-start'], href='/' + lang + '/dashboard'),

		html.Button(tls[lang]['quit-btn']),

		html.P(id = 'stop-msg'),
		
	], className="home-container")