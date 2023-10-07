# Importation des bibliothèques
import streamlit as st
import pandas as pd
import random
from pyvis.network import Network
from collections import Counter

# Fonction pour générer une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Upload des fichiers Excel
uploaded_file_erp = st.file_uploader("Télécharger erp_all_table_relations_finalV2.xlsx", type=['xlsx'])
uploaded_file_d365fo = st.file_uploader("Télécharger D365FO.xlsx", type=['xlsx'])
uploaded_file_field_list = st.file_uploader("Télécharger Table and Field List.xlsx", type=['xlsx'])

if all([uploaded_file_erp, uploaded_file_d365fo, uploaded_file_field_list]):
    
    # Lecture des fichiers Excel
    erp_relations = pd.read_excel(uploaded_file_erp, sheet_name='Sheet1')
    d365_tables = pd.read_excel(uploaded_file_d365fo, sheet_name='D365 Table')
    field_list = pd.read_excel(uploaded_file_field_list, sheet_name='Field List')

    # Comptage des occurrences
    total_counter = Counter(erp_relations['Table Parent']) + Counter(erp_relations['Table Enfant'])

    # Conversion en DataFrame
    df_total_counter = pd.DataFrame.from_dict(total_counter, orient='index', columns=['Total Associations']).reset_index()
    df_total_counter.rename(columns={'index': 'Table'}, inplace=True)

    # Jointure pour récupérer les modules d'application
    df_total_counter = df_total_counter.merge(d365_tables[['Table name', 'App module']], left_on='Table', right_on='Table name', how='left')

    # Liste des modules d'application
    app_modules = d365_tables['App module'].unique().tolist()

    # Sélection du module d'application
    app_module = st.selectbox('Module d\'Application:', app_modules)
    
    # Filtrage des tables pour le module d'application sélectionné
    filtered_tables = df_total_counter[df_total_counter['App module'] == app_module]
    
    # Slider pour le nombre de tables
    num_tables = st.slider('Nombre de tables:', min_value=1, max_value=len(filtered_tables), value=10)
    
    # Sélection des 'num_tables' tables avec le plus grand nombre de relations
    top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table'].tolist()

    # Filtrage des relations pour inclure seulement ces tables
    filtered_relations = erp_relations[
        (erp_relations['Table Parent'].isin(top_tables)) | 
        (erp_relations['Table Enfant'].isin(top_tables))
    ]
    
    # Création du graphe
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    
    # Ajout des nœuds avec leurs attributs
    for table in top_tables:
        color = random_color()
        columns_info = field_list[field_list['TABLE_NAME'] == table]
        title_str = "<h4>" + table + "</h4><p>Champs :</p><p>" + "<br>".join(columns_info['COLUMN_NAME'].astype(str) + ' (' + columns_info['DATA_TYPE'].astype(str) + ')') + "</p>"
        net.add_node(table, title=title_str, color=color)
    
    # Ajout des arêtes avec leurs attributs
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