import streamlit as st
from functions import scrape_mvp_data, scrape_player_data, scrape_team_data, save_data_to_csv, save_data_to_sqlite

def main():

    st.set_page_config(page_title="Scraping NBA Data", page_icon="🏀", layout="wide")

    st.sidebar.info("Adrien Delacroix")

    st.title("Scraping NBA Data")
    st.write("""
        Bienvenue sur l'application de Scraping Basketball Data! 
        Cette application a été créée dans le cadre d'un projet scolaire et utilise Streamlit, un framework open-source pour créer des applications web en Python. 
        Streamlit a été choisi pour sa simplicité et sa capacité à transformer rapidement des scripts Python en applications web interactives.

        Nous utilisons BeautifulSoup et Selenium pour scraper les données du site [Basketball Reference](https://www.basketball-reference.com/), une ressource complète pour les statistiques historiques de la NBA. 
        L'objectif de ce projet est de fournir un accès facile et interactif aux données des joueurs et des équipes à travers les années.

        N'hésitez pas à utiliser le menu latéral pour naviguer et interagir avec les données !""")

    
    st.title("Collecte de Données de NBA")
    
    if st.button("Collecter les Données des MVPs"):
        years = range(2001, 2024)
        mvp_data = scrape_mvp_data(years)
        save_data_to_sqlite(mvp_data, "basketball_data.db", "MVPs")
        save_data_to_csv(mvp_data, "mvp_data.csv")

    if st.button("Collecter les Données des Joueurs"):
        years = range(2001, 2024)
        player_data = scrape_player_data(years)
        save_data_to_sqlite(player_data, "basketball_data.db", "players")
        save_data_to_csv(player_data, "player_data.csv")

    if st.button("Collecter les Données des Équipes"):
        years = range(2001, 2024)
        team_data = scrape_team_data(years)
        save_data_to_sqlite(team_data, "basketball_data.db", "teams")
        save_data_to_csv(team_data, "team_data.csv")

if __name__ == "__main__":
    main()
