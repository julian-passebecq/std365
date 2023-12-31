# pages/page1.py

import pandas as pd
import random
from pyvis.network import Network
from collections import Counter
import streamlit as st

# Titre pour la première page
st.title("Graphe App Module")

def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Lecture des fichiers Excel
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Gérer les valeurs NaN pour le module d'application
d365_tables['App module'] = d365_tables['App module'].fillna("Non spécifié")

# Conversion en majuscules
erp_relations['Table Parent'] = erp_relations['Table Parent'].astype(str).str.upper()
erp_relations['Table Enfant'] = erp_relations['Table Enfant'].astype(str).str.upper()
d365_tables['Table name'] = d365_tables['Table name'].astype(str).str.upper()

# Dictionnaire de couleurs pour chaque module d'application
app_module_colors = {module: random_color() for module in d365_tables['App module'].unique() if module}

# Comptage des occurrences
total_counter = Counter(erp_relations['Table Parent']) + Counter(erp_relations['Table Enfant'])

# Barre de recherche pour les modules d'application
search_term_app_module = st.text_input("Rechercher un module d'application")
app_modules = sorted([x for x in d365_tables['App module'].unique() if x and (search_term_app_module.lower() in x.lower())])
app_module = st.selectbox('Module d\'Application:', app_modules)

# Filtrage des tables pour le module sélectionné
filtered_tables = d365_tables[d365_tables['App module'] == app_module]
filtered_tables['Total Associations'] = filtered_tables['Table name'].map(total_counter)

# Slider pour le nombre de tables
num_tables = st.slider('Nombre de tables:', min_value=1, max_value=len(filtered_tables), value=10)

# Tables avec le plus grand nombre de relations
top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table name'].tolist()

# Création du graphe
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

# Ajout des nœuds avec leurs attributs
for table in top_tables:
    table_info = d365_tables[d365_tables['Table name'] == table].iloc[0]
    title_str = "\n".join([f"{col}: {table_info[col]}" for col in table_info.index if pd.notna(table_info[col])])

    color = app_module_colors.get(app_module, random_color())
    net.add_node(table, title=title_str, color=color)

# Ajout des arêtes avec leurs attributs
filtered_relations = erp_relations[(erp_relations['Table Parent'].isin(top_tables)) | (erp_relations['Table Enfant'].isin(top_tables))]
for _, row in filtered_relations.iterrows():
    parent = row['Table Parent']
    child = row['Table Enfant']
    relation = row['Lien 1']
    if parent in top_tables and child in top_tables:
        net.add_edge(parent, child, title=relation)

# Affichage du graphe
net.save_graph("temp.html")
with open("temp.html", 'r', encoding='utf-8') as f:
    source_code = f.read()
st.components.v1.html(source_code, height=800)
