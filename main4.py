import pandas as pd
import streamlit as st

# Lecture des fichiers Excel
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("/D365FO.xlsx", sheet_name='D365 Table')

# Sélection de l'App module
selected_app_module = st.selectbox('Sélectionnez un App module:', d365_tables['App module'].unique().tolist())

# Tableau des relations par App module
filtered_relations = erp_relations[(erp_relations['App Module Parent'] == selected_app_module)]
relation_summary = filtered_relations.groupby('App Module Enfant').size().reset_index(name='Total Relations')
relation_summary = relation_summary.sort_values(by='Total Relations', ascending=False)
st.table(relation_summary)

# Tableau des tables par App module
filtered_tables = d365_tables[d365_tables['App module'] == selected_app_module]
sorted_tables = filtered_tables.sort_values(by='Total Relations', ascending=False).head(20)  # Affiche les 20 premières tables triées par 'Total Relations'
st.table(sorted_tables[['Table name', 'Table label', 'Table group', 'Tabletype']])
