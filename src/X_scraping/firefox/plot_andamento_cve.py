from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import re
from src.X_scraping.firefox.utils.utils import connect_to_mongo, connect_to_mongo_collection, save_to_mongo, get_db


def plot_andamento_cve():
    # Connessione al database MongoDB
    client = connect_to_mongo()
    db = get_db(client)

    # Pattern per identificare le collection relative alle CVE (es. 'CVE-2000', 'CVE-2025')
    cve_pattern = re.compile(r'^CVE-(\d{4})$')

    # Dizionario per contare i documenti delle CVE per anno
    cve_counts = {}

    # Iterazione su tutte le collection nel database
    for collection_name in db.list_collection_names():
        match = cve_pattern.match(collection_name)
        if match:
            year = match.group(1)  # Estraggo l'anno dal nome della collection
            # Conteggio dei documenti nella collection
            count = db[collection_name].count_documents({})
            cve_counts[year] = count

    # Conversione dei risultati in DataFrame per ordinamento e analisi
    cve_df = pd.DataFrame(list(cve_counts.items()), columns=['Year', 'Count'])
    cve_df['Year'] = cve_df['Year'].astype(int)  # Converto l'anno in intero
    cve_df = cve_df.sort_values('Year')  # Ordino per anno

    # Creazione del grafico
    plt.figure(figsize=(12, 6))
    plt.plot(cve_df['Year'], cve_df['Count'], marker='o', color='b', label='Conteggio CVE')
    plt.title('Andamento delle CVE nei Tweet raccolti', fontsize=16)
    plt.xlabel('Anno', fontsize=14)
    plt.ylabel('Tweet', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=12)

    # Salvataggio del grafico come file PNG
    plt.savefig('andamento_cve_tweet.png', format='png', dpi=300)  # Salva il grafico in alta qualità
    print("Grafico salvato come 'andamento_cve_tweet.png'")

    plt.savefig('data_results/andamento_cve_tweet.png', format='png', dpi=600)

    # Mostra il grafico (opzionale)
    plt.show()


if __name__ == "__main__":
    plot_andamento_cve()
