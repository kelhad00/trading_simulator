from dash import html, dcc
import dash

from tradesim.Locales import translations as tls


# Layout of the home page
def main_layout(lang="fr"):
    return html.Div([

		dcc.Interval(
			id = 'home-clock',
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
			href='/' + lang + '/dashboard',
			id='home-start-button'
		),

	], className="home-container")