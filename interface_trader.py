import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

#CONFIGURATIONS
st.set_page_config(layout="wide")
st.markdown(
	f"""
<style>
	.appview-container .main .block-container{{
		padding-bottom: 1rem;
		padding-top: 2rem;
    }}
</style>
""",
		unsafe_allow_html=True)

# CSS to inject contained in a string
hide_table_row_index = """
        <style>
        thead tr th:first-child {display:none}
        tbody th {display:none}
        </style>
        """

# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)

#BODY
left_column1, buff, right_column1 = st.columns([2,1,2])



#PORTFOLIO
with left_column1:
	st.title('Portfolio')

	#parametres
	max_inv_money=1000
	prix_tot=[10, 20, 30, 40]
	num_part=[1, 2, 3, 4]
	comp= ['Tesla', 'Apple', 'Amazon', 'Engie']


	@st.cache_data
	def update_data():
		df=pd.DataFrame({
  			'Companie':comp,
  			'Nombre de part': num_part,
  			'Prix total': prix_tot
			})
		return df

	df=update_data()
	st.table(df)

	prix_inv=0
	for i in prix_tot:
		prix_inv=prix_inv+i

	st.write('Votre investissement total :',prix_inv,'eur')

	
#COMPANY
with right_column1: 

	compa = st.selectbox(
    	'Sélectionnez une companie :',
    	['Tesla','Apple','Engie','Amazon'])
    
    #graph cartouche
	DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
			'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

	def load_data(nrows):
   		data = pd.read_csv(DATA_URL, nrows=nrows)
   		lowercase = lambda x: str(x).lower()
   		data.rename(lowercase, axis='columns', inplace=True)
   		data['date/time'] = pd.to_datetime(data['date/time'])
   		return data

	data = load_data(10000)

	hist_values = np.histogram(
   		data['date/time'].dt.hour, bins=24, range=(0,24))[0]
	st.bar_chart(hist_values)



left_column2, buff,right_column2 = st.columns([2,1,2])



#ACTUALITES
with left_column2: 
	st.title('Actualités')

	link='https://www.automobile-propre.com/marque/tesla/actualites/'

	#revoir les titres des colonnes !!
	df = pd.DataFrame(
    {
    	"date": ["05/05/2023 10:03", "05/05/2023 11:27","05/05/2023 11:45"],
        "url": [f'<a target="_blank" href="{link}">Tesla bought Twitter</a>',f'<a target="_blank" href="{link}">CAC40 is falling</a>',f'<a target="_blank" href="{link}">News</a>']
    })

	st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)


#PRIX ACHAT/VENTE
with right_column2: 

	st.write('')

	col, coll = st.columns([2,2])
	col.text_input("Votre prix :", value='Entrez le prix souhaité (€)',key="price")
	achat_vente=st.session_state.price
	part=coll.selectbox(
    	'Nombre de parts :',
    	[1,2,3,4,5,6,7,8,9,10])

	
	col1, col2, buff= st.columns([2,2,3])

	with col1:
		if st.button('Acheter','buy'):
			prix_tot.append(part*achat_vente)
			num_part.append(part)
			comp.append(compa)


		#on_click (callable)

	with col2:
		if st.button('Vendre','sell'):
			i=comp.index(compa)
			comp.remove(compa)
			num_part.remove(num_part[i])
			prix_tot.remove(prix_tot[i])
	
	st.write(comp,num_part,prix_tot)