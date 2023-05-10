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
	st.session_state['timestamp'] = '2022-05-05 07:00:00-04:00'

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
max_inv_money=100000

if 'prix_actu' not in st.session_state:
	st.session_state.prix_actu=[]

if 'prix_tot' not in st.session_state:
	st.session_state.prix_tot=[0,0,0,0,0,0,0,0,0]

if 'num_part' not in st.session_state:
	st.session_state.num_part=[0,0,0,0,0,0,0,0,0]

if 'listes_requetes' not in st.session_state:
	st.session_state.listes_requetes=[]

if 'action' not in st.session_state:
	st.session_state.action=''

comp= ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "META", "NVDA", "PEP", "COST"]
#CONFIGURATIONS#


def create_left_port():
	comp1=[]
	prix_tot1=[]
	num_part1=[]
	for i in range(5):
		comp1.append(comp[i])
		prix_tot1.append(st.session_state.prix_tot[i])
		num_part1.append(st.session_state.num_part[i])

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
		prix_tot2.append(st.session_state.prix_tot[j])
		num_part2.append(st.session_state.num_part[j])

	df2=pd.DataFrame({
		'Companie':comp2,
		'Nombre de part': num_part2,
		'Prix total': prix_tot2
		})
	return df2


def calcul_prix_tot_inv():
	tot=0
	for i in st.session_state.prix_tot:
		tot+=i
	tot+=max_inv_money
	return tot


def create_news_tab():
	dp = pd.DataFrame(
    {
    	"date": ["05/05/2023 10:03", "05/05/2023 11:27","05/05/2023 11:45","05/05/2023 11:45","05/05/2023 11:45"],
        "titre": ['Tesla bought Twitter','CAC40 is falling','News','News 23', 'News NEWS']
    })
	return dp


def ajouter_requetes(action):
	longu=len(st.session_state.listes_requetes)
	if longu<=3:
		req=[longu+1,action,compa,achat_vente,part]
		st.session_state.listes_requetes.append(req)
	else:
		tkinter.messagebox.showinfo("Erreur",  "Vous avez déjà 3 requêtes en attente !")			
		
def afficher_requetes():
	rq=pd.DataFrame(st.session_state.listes_requetes,columns=['index','action','companie','prix (€)','nb part'])
	print(rq)
	print(st.session_state.listes_requetes)
	return rq

def supprimer_requete(index):
	for req in st.session_state.listes_requetes:
		if req[0]==index:
			st.session_state.listes_requetes.remove(req)
			return 'Requêtes supprimer'
		else:
			return 'Cette requêtes n\'existe pas !'


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


left_column2, buff,middle_column2, buff,right_column2 = st.columns([2,1,2,0.5,2])

#ACTUALITES
with left_column2:
	st.write('Actualités')

	st.table(create_news_tab())

#REQUETES
with right_column2:
	afficher=st.button('Afficher les requêtes')
	if afficher:
		st.table(afficher_requetes())
	left,right=st.columns(2)
	ind=left.selectbox('index :',[1,2,3])
	right.write(' ')
	right.write(' ')
	supprimer=right.button('Supprimer')
	if supprimer:
		st.write(supprimer_requete(ind))


#PRIX ACHAT/VENTE
with middle_column2:
	#st.empty()

	st.text_input("Votre prix :", value='(€)',key="price")
	achat_vente=st.session_state.price
	part=st.selectbox(
    	'Nombre de parts :',
    	[1,2,3,4,5,6,7,8,9,10]
	)

	col1, col2, buff= st.columns([2,2,3])

	with col1:
		acheter=st.button('Acheter','buy')  
		if acheter:
			st.session_state.action='achat'
			ajouter_requetes(st.session_state.action)

	with col2:
		vendre=st.button('Vendre','sell')
		if vendre:
			st.session_state.action='vente'
			ajouter_requetes(st.session_state.action)

# Update layout depending of the current market data every 5 minutes
while True:
	time.sleep(3) #TODO: change to 5 minutes (300 seconds)

	# # Graph part
	# with right_column1:
	# 	st.session_state['timestamp'] = update_candlestick_chart(
	# 		candlestick,
	# 		market_dataframe,
	# 		st.session_state['timestamp']
	# 	)
	# 	stream_candlestick.plotly_chart(candlestick)

