import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time
from tkinter import *
import tkinter.messagebox
from candlestick_charts import PLOTLY_CONFIG, create_candlestick_chart, update_candlestick_chart

# Default value for session variables
if 'timestamp' not in st.session_state:
	st.session_state['timestamp'] = '2023-04-11 13:45:00'

#CONFIGURATIONS#
st.set_page_config(layout="wide")
hide_table_row_index = """
<style>
	.appview-container .main .block-container {
		padding-bottom: 1rem;
		padding-top: 2rem;
	}
	thead tr th:first-child {display:none}
	tbody th {display:none}
	button[title="View fullscreen"]{visibility: hidden;}
</style>
"""
st.markdown(hide_table_row_index, unsafe_allow_html=True)

#parametres
max_inv_money=1000
prix_actu=50
prix_tot=[0,0,0,0,0,0,0,0,0]
num_part=[0,0,0,0,0,0,0,0,0]
comp = [ # List of stocks
    "MC.PA",  "TTE.PA", "SAN.PA", "OR.PA",  "SU.PA", \
    "AI.PA",  "AIR.PA", "BNP.PA", "DG.PA",  "CS.PA", \
    "RMS.PA", "EL.PA",  "SAF.PA", "KER.PA", "RI.PA", \
    "STLAM.MI",  "BN.PA",  "STMPA.PA",  "CAP.PA", "SGO.PA"
]
#CONFIGURATIONS#


def create_left_port():
	comp1=[]
	prix_tot1=[]
	num_part1=[]
	for i in range(5):
		comp1.append(comp[i])
		prix_tot1.append(prix_tot[i])
		num_part1.append(num_part[i])

	df1=pd.DataFrame({
		'Companie':comp1,
		'Nombre de part': num_part1,
		'Prix total': prix_tot1
		})
	return df1


def create_right_port():
	comp2=[]
	prix_tot2=[]
	num_part2=[]
	for j in range(5,9):
		comp2.append(comp[j])
		prix_tot2.append(prix_tot[j])
		num_part2.append(num_part[j])

	df2=pd.DataFrame({
		'Companie':comp2,
		'Nombre de part': num_part2,
		'Prix total': prix_tot2
		})
	return df2


def calcul_prix_tot_inv():
	tot=0
	for i in prix_tot:
		tot+=i
	tot+=max_inv_money
	return tot


def create_news_tab():
	dp = pd.DataFrame(
    {
    	"date": ["05/05/2023 10:03", "05/05/2023 11:27","05/05/2023 11:45"],
        "titre": ['Tesla bought Twitter','CAC40 is falling','News']
    })
	return dp


def write_requets_vente():
	st.write('En vente de ',part,' part(s) de ',compa,' à ',achat_vente,' eur/part.')
	st.button('Annuler')


def write_requets_achat():
	st.write('En achat de ',part,' part(s) de ',compa,' à ',achat_vente,' eur/part.')
	st.button('Annuler')


#BODY
left_column1, buff, right_column1 = st.columns([2,1,2])

#PORTFOLIO
with left_column1:
	st.write('Portfolio')

	left_colum, right_colum = st.columns(2)
	left_colum.table(create_left_port())
	right_colum.table(create_right_port())

	st.write('Votre investissement total :',calcul_prix_tot_inv(),'eur.')

#COMPANY GRAPH
with right_column1:
	compa = st.selectbox( 'Sélectionnez une companie :', comp )

	candlestick, market_dataframe, st.session_state['timestamp'] = create_candlestick_chart(
		compa,
		st.session_state['timestamp']
	)
	candlestick.update_layout(
		margin_t = 0,
        margin_b = 0,
        height = 300,
	)
	stream_candlestick = st.plotly_chart(candlestick, config = PLOTLY_CONFIG)


left_column2, buff,middle_column2, buff,right_column2 = st.columns([2,1,2,1,2])

#ACTUALITES
with left_column2:
	st.write('Actualités')

	st.table(create_news_tab())

#REQUETES
with right_column2:
	st.write('Requête en attente ...')

#PRIX ACHAT/VENTE
with middle_column2:
	#st.empty()

	st.text_input("Votre prix :", value='Entrez le prix souhaité (€)',key="price")
	achat_vente=st.session_state.price
	part=st.selectbox(
    	'Nombre de parts :',
    	[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
	)

	col1, col2, buff= st.columns([2,2,3])

	with col1:
		if st.button('Acheter','buy'):  #on_click (callable)
			#écriture du request
			with right_column2:
				write_requets_achat()

			#modification bdd et portfolio
			#acheter_part()

	with col2:
		if st.button('Vendre','sell'):
			#écriture du request
			i=comp.index(compa)
			if num_part[i]!=0:
				with right_column2:
					write_requets_vente()
				#modification bdd et portfolio
				#vente_part()
			else :
				tkinter.messagebox.showinfo("Erreur",  "Vous ne pouvez pas vendre de part !")


def acheter_part():
	if prix_actu==achat_vente:
		#modification des listes
		i=comp.index(compa)
		num_part[i]+=part
		prix_tot[i]+=num_part[i]*achat_vente

	#supprimer_request()
	#appeler un fonction pour modifier le portfolio ou rerun l'app


def vente_part():
	if prix_actu==achat_vente:
		#modification des listes
		i=comp.index(compa)
		num_part[i]-=part
		prix_tot[i]-=num_part[i]*achat_vente #modifier pour afficher 0

	#supprimer_request()
	#appeler un fonction pour modifier le portfolio ou rerun l'app

# def supprimer_request():

# Update layout depending of the current market data every 5 minutes
while True:
	time.sleep(5) #TODO: change to 5 minutes (300 seconds)

	# Graph part
	with right_column1:
		st.session_state['timestamp'] = update_candlestick_chart(
			candlestick,
			market_dataframe,
			st.session_state['timestamp']
		)
		stream_candlestick.plotly_chart(candlestick)