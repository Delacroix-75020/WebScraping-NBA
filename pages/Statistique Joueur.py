import streamlit as st
from functions import get_player_data, save_search_history, get_search_history, truncate_history

def main():
    st.sidebar.title("Historique de recherche")

    history = get_search_history("basketball_data.db")
    if history:
        history_items = [f"{year} - {player}" for year, player in history]
        for item in history_items:
            st.sidebar.info(item)

        clear_history = st.sidebar.button("Effacer Historique Globale", type="primary")

        if clear_history:
            truncate_history()

    st.title("Recherche de Joueurs de NBA")

    all_years = st.checkbox("Afficher toutes les années")
    year = st.selectbox("Choisissez une année", range(2001, 2024), index=len(range(2001, 2024)) - 1, disabled=all_years)
    player_name = st.text_input("Entrez le nom du joueur pour obtenir ses informations")

    search_button = st.button("Rechercher")

    if search_button and player_name:
        save_search_history("basketball_data.db", year, player_name)
        years = range(2001, 2024) if all_years else [year]

        player_data = get_player_data("basketball_data.db", player_name, years)

        if player_data is not None and not player_data.empty:
            st.write(f"Données pour {player_name}:")
            st.dataframe(player_data)
        else:
            st.error("Joueur non trouvé. Veuillez vérifier l'orthographe.")


if __name__ == "__main__":
    main()
