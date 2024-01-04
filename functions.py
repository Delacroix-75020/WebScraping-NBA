import os
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
import sqlite3
import openai

# Configuration initiale de pandas
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 1000)

# --------------------------- Région Scraping ---------------------------

player_stats_url = "https://www.basketball-reference.com/leagues/NBA_{}_per_game.html"
team_stats_url = "https://www.basketball-reference.com/leagues/NBA_{}_standings.html"
mvp_url = "https://www.basketball-reference.com/awards/awards_{}.html"

def scrape_mvp_data(years):
    driver = webdriver.Chrome()
    dfs_mvp = []
    for year in years:
        try:
            driver.get(mvp_url.format(year))
            time.sleep(2)
            soup = bs(driver.page_source, 'html.parser')
            soup.find("tr", class_="over_header").decompose()
            mvp_table = soup.find_all(id="mvp")[0]
            mvp = pd.read_html(str(mvp_table))[0]
            mvp["Year"] = year
            dfs_mvp.append(mvp)
        except Exception as e:
            print(f"Erreur lors du scraping des données MVP pour l'année {year}: {e}")
    driver.quit()
    return pd.concat(dfs_mvp)

def scrape_player_data(years):  
    driver = webdriver.Chrome()
    dfs_players = []
    for year in years:
        try:
            driver.get(player_stats_url.format(year))
            time.sleep(2)
            soup = bs(driver.page_source, 'html.parser')
            soup.find('tr', class_="thead").decompose()
            player_table = soup.find_all(id="per_game_stats")[0]
            player_df = pd.read_html(str(player_table))[0]
            player_df["Year"] = year
            dfs_players.append(player_df)
        except Exception as e:
            print(f"Erreur lors du scraping des statistiques des joueurs pour l'année {year}: {e}")
    driver.quit()
    return pd.concat(dfs_players)

def scrape_team_data(years):
    driver = webdriver.Chrome()
    dfs_teams = []
    for year in years:
        try:
            driver.get(team_stats_url.format(year))
            time.sleep(2)
            soup = bs(driver.page_source, 'html.parser')
            soup.find('tr', class_="thead").decompose()
            for conference_id in ["divs_standings_E", "divs_standings_W"]:
                conf_table = soup.find_all(id=conference_id)[0]
                conf_df = pd.read_html(str(conf_table))[0]
                conf_df["Year"] = year
                conf_df["Team"] = conf_df[conf_df.columns[0]]
                del conf_df[conf_df.columns[0]]
                dfs_teams.append(conf_df)
        except Exception as e:
            print(f"Erreur lors du scraping des statistiques des équipes pour l'année {year}: {e}")
    driver.quit()
    return pd.concat(dfs_teams)

# --------------------------- END Région ---------------------------


# --------------------------- Région Autres ---------------------------

def get_player_info(player_name, players_df):
    player_info = players_df[players_df['Player'] == player_name]
    return player_info

def get_player_years(player_name, players_df):
    player_data = players_df[players_df['Player'].str.contains(player_name, case=False, na=False)]
    years_played = player_data['Year'].unique().tolist()
    return years_played, player_data

# --------------------------- END Région ---------------------------


# --------------------------- Région CSV ---------------------------

def save_data_to_csv(data, filename):
    try:
        data.to_csv(filename, index=False)
        print(f"Données sauvegardées avec succès dans {filename}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des données : {e}")

# --------------------------- END Région ---------------------------
        

# --------------------------- Région Intéraction BDD ---------------------------

def save_data_to_sqlite(data, db_name, table_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        if cursor.fetchone():
            cursor.execute(f"DELETE FROM {table_name};")
        data.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.commit()
        conn.close()
        print(f"Données sauvegardées avec succès dans la table {table_name} de {db_name}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des données dans SQLite : {e}")


def save_search_history(db_name, year, player_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Historique
                          (Year INTEGER, PlayerName TEXT)''')

        cursor.execute("INSERT INTO Historique (Year, PlayerName) VALUES (?, ?)",
                       (year, player_name))

        conn.commit()
    except Exception as e:
        print(f"Erreur lors de l'enregistrement dans l'historique : {e}")
    finally:
        conn.close()

def get_search_history(db_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT Year, PlayerName FROM Historique")
        history_data = cursor.fetchall()
        return history_data
    except Exception as e:
        print(f"Erreur lors de la récupération de l'historique : {e}")
        return []
    finally:
        conn.close()

def get_player_data(db_path, player_name, years):
    try:
        query = """
            SELECT * FROM players 
            WHERE Player LIKE '%' || ? || '%' AND Year IN ({})
        """.format(','.join('?' for _ in years))

        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(query, conn, params=[player_name, *years])
        return df if df is not None else pd.DataFrame()

    except sqlite3.Error as e:
        print("Erreur SQLite:", e)
        return None
    except Exception as e:
        print("Une erreur s'est produite:", e)
        return None

def truncate_history():
    try:
        conn = sqlite3.connect('basketball_data.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Historique")
        conn.commit()
        conn.close()
        print("La table History a été tronquée avec succès.")
    except sqlite3.Error as e:
        print("Erreur lors de la troncation de la table History :", e)

# --------------------------- End Région ---------------------------
        
# --------------------------- Région OpenIA ---------------------------

def generate_historical_comparison(player_name):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    print(openai_api_key)
    if not openai_api_key:
        return "Clé API OpenAI non trouvée. Veuillez définir la variable d'environnement OPENAI_API_KEY."

    prompt = f"Générer une comparaison historique détaillée pour le joueur de NBA {player_name}, en se basant sur ses Statistiques, ses réalisations et sa contribution au jeu."

    openai.api_key = openai_api_key

    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=30
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Une erreur s'est produite lors de la génération de la comparaison historique: {e}"



# --------------------------- End Région ---------------------------
