import streamlit as st
from functions import generate_historical_comparison

def main():
    st.title("Comparaison Historique des Joueurs de NBA")

    # Champ de saisie pour le nom du joueur
    player_name = st.text_input("Nom du joueur")

    # Bouton pour déclencher la comparaison
    if st.button("Générer Comparaison Historique"):
        # Appel de la fonction de génération
        historical_comparison = generate_historical_comparison(player_name)

        # Affichage du résultat
        st.text("Résultat de la Comparaison Historique :")
        st.write(historical_comparison)

if __name__ == "__main__":
    main()
