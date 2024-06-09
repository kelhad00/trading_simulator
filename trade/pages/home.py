import dash
from dash import html, dcc, Input, Output, callback
from dash.exceptions import PreventUpdate

from trade.Locales import translations as tls


dash.register_page(
    __name__,
	path="/",
)

def layout(lang="fr", **kwargs):
	dash.page_registry['lang'] = lang

	return html.Div([
		dcc.Interval(
			id='home-clock',
			interval = 5000, # in milliseconds
		),

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

		html.P(tls[lang]['signature'], className="signature"),

		html.P(tls[lang]['button-start-info'],
			style={'display': 'none'},
			id='home-start-button-info'
		),
		dcc.Link(
			tls[lang]['button-start'],
			href='/dashboard?lang=' + lang,
			id='home-start-button'
		),
		dcc.Link(
			tls[lang]['button-settings'],
			href='/settings',
		),

		html.Br(),
		html.Button(tls[lang]['button-restart-sim'], id='restart_sim'),
		html.Button('hhrhr', id='restart_simu'),

	], className="home-container")

