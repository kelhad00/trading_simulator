from dash import Dash, dash_table, html, dcc, callback, Output, Input, State
import pandas as pd
from datetime import datetime
import time

from candlestick_charts import create_next_graph, PLOTLY_CONFIG

# Constants
MAX_INV_MONEY=100000
COMP= ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "META", "NVDA", "PEP", "COST"]
NEWS_DATA = pd.DataFrame({
	"date": ["05/05/2023 10:03", "05/05/2023 11:27","05/05/2023 11:45","05/05/2023 11:45","05/05/2023 11:45"],
	"titre": ['Tesla bought Twitter','CAC40 is falling','News','News 23', 'News NEWS']
})

#TODO: Change to dcc.Store
prix_tot= [0,0,0,0,0,0,0,0,0]
def calcul_prix_tot_inv():
	tot=0
	for i in prix_tot:
		tot+=i
	tot+=MAX_INV_MONEY
	return tot


# Components
def generate_portfolio_table(df):
	return html.Div([
		html.Table([
			html.Thead(
				html.Tr([html.Th(col) for col in  df.columns])
			),
			html.Tbody([
				html.Tr([
					html.Td(df.iloc[i][col]) for col in df.columns
				]) for i in range(5)
			])
		], style={'padding': 10, 'flex': 1,'width': 50}),
		html.Table([
			html.Thead(
				html.Tr([html.Th(col) for col in  df.columns])
			),
			html.Tbody([
				html.Tr([
					html.Td(df.iloc[i][col]) for col in df.columns
				]) for i in range(6, 9)
			])
		], style={'padding': 10, 'flex': 1, 'width': 50})
    ], style={'display': 'flex', 'flex-direction': 'row'})


# Initialize Dash app
app = Dash(__name__)


# Layout of the app
app.layout = html.Div([

	# Global variables
	dcc.Store(id = 'market-timestamp-value', data = ''), # Store timestamp value in the browser
	# dcc.Store(id = 'market-dataframe'),                  # Store market data in the browser
	dcc.Store(id = 'listes_requetes', data = []),
	dcc.Store(id = 'prix_actu', data = []),
	dcc.Store(id = 'portfolio_info',data = {
		'Companie':COMP,
		'Nombre de part': [0,0,0,0,0,0,0,0,0],
		'Prix total': [0,0,0,0,0,0,0,0,0]
	}),

	# Periodic updater
	dcc.Interval(
		id='periodic-updater',
		interval=5*1000, # in milliseconds
	),

	# Upper part
	html.Div([
		# Portfolio
		html.Div(children=[
			html.H1(children='Portfolio'),
			# generate_portfolio_table(portfolio_info)
			html.P(
				id='portfolio-total-price',
				children=['Votre investissement total :',calcul_prix_tot_inv(),'eur.']
			)
		], style={'padding': 10, 'flex': 1}),

		# Company graph
		html.Div(children=[
			dcc.Dropdown(COMP, COMP[0], id='company-selector'),
			dcc.Graph(
				id='company-graph',
				config = PLOTLY_CONFIG,
				style={'padding': 30}
			)
		], style={'padding': 10, 'flex': 1})
	], style={'display': 'flex', 'flex-direction': 'row', 'height': '50vh'}),

	# Lower part
	html.Div([
		# News
		html.Div(children=[
			html.H1(children='Market News'),
			dash_table.DataTable(
				id='news-table',
				data=NEWS_DATA.to_dict('records'),
			)
		], style={'padding': 10, 'flex': 1}),

		# Requests
		html.Div(children=[

		], style={'padding': 10, 'flex': 1}),
		html.Div(children=[

		], style={'padding': 10, 'flex': 1})

	], style={'display': 'flex', 'flex-direction': 'row', 'height': '50vh'})

])


# Callbacks
@app.callback(
	Output('company-graph', 'figure'),
	Output('market-timestamp-value', 'data'),
	# Output('market-dataframe', 'data'),
	Input('periodic-updater', 'n_intervals'), # periodicly updated
	Input('company-selector', 'value'), # User action
	State('market-timestamp-value', 'data')
)
def update_graph(n, company_id, timestamp, range=10):
	""" Update the graph with the latest market data
		Periodicly updated or when the user selects a new company
	"""
	fig, timestamp = create_next_graph(
        company_id,
        timestamp,
        range
    )
	fig.update_layout(
        margin_t = 0,
        margin_b = 0,
        height = 300,
    )
	return fig, timestamp


# def ajouter_requetes(action):
# 	longu=len(st.session_state.listes_requetes)
# 	if longu<=3:
# 		req=[longu+1,action,compa,achat_vente,part]
# 		st.session_state.listes_requetes.append(req)
# 	else:
# 		tkinter.messagebox.showinfo("Erreur",  "Vous avez déjà 3 requêtes en attente !")

# def afficher_requetes():
# 	rq=pd.DataFrame(st.session_state.listes_requetes,columns=['index','action','companie','prix (€)','nb part'])
# 	print(rq)
# 	print(st.session_state.listes_requetes)
# 	return rq

# def supprimer_requete(index):
# 	for req in st.session_state.listes_requetes:
# 		if req[0]==index:
# 			st.session_state.listes_requetes.remove(req)
# 			return 'Requêtes supprimer'
# 		else:
# 			return 'Cette requêtes n\'existe pas !'

# #REQUETES
# with right_column2:
# 	afficher=st.button('Afficher les requêtes')
# 	if afficher:
# 		st.table(afficher_requetes())
# 	left,right=st.columns(2)
# 	ind=left.selectbox('index :',[1,2,3])
# 	right.write(' ')
# 	right.write(' ')
# 	supprimer=right.button('Supprimer')
# 	if supprimer:
# 		st.write(supprimer_requete(ind))


# #PRIX ACHAT/VENTE
# with middle_column2:
# 	#st.empty()

# 	st.text_input("Votre prix :", value='(€)',key="price")
# 	achat_vente=st.session_state.price
# 	part=st.selectbox(
#     	'Nombre de parts :',
#     	[1,2,3,4,5,6,7,8,9,10]
# 	)

# 	col1, col2, buff= st.columns([2,2,3])

# 	with col1:
# 		acheter=st.button('Acheter','buy')
# 		if acheter:
# 			st.session_state.action='achat'
# 			ajouter_requetes(st.session_state.action)

# 	with col2:
# 		vendre=st.button('Vendre','sell')
# 		if vendre:
# 			st.session_state.action='vente'
# 			ajouter_requetes(st.session_state.action)

if __name__ == '__main__':
    app.run_server(debug=True) #TODO: change to False when deploying