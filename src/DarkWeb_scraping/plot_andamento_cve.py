import pandas as pd
import matplotlib.pyplot as plt
import re
from src.DarkWeb_scraping.utils.utils import connect_to_mongo, connect_to_mongo_collection, disconnect_to_mongo


def plot_cve():
    # Connessione al database MongoDB
    client = connect_to_mongo()
    collection = connect_to_mongo_collection(client, 'ahmia_results')

    # Recupero dei dati dalla collection
    data = collection.find({}, {'keywords': 0})


    # Creazione di un dizionario per contare le CVE per anno
    cve_counts = {}

    # Iterazione sui documenti della collection
    for document in data:
        keywords = document.get('search_keywords', [])
        if len(keywords) == 1:  # Verifico che l'array abbia un solo elemento
            keyword = keywords[0]  # Estraggo la parola chiave
            # Match delle keyword nel formato 'CVE-YYYY'
            match = re.match(r'CVE-(\d{4})', keyword)
            if match:
                year = match.group(1)
                cve_counts[year] = cve_counts.get(year, 0) + 1

    # Conversione in DataFrame per analisi e visualizzazione
    cve_df = pd.DataFrame(list(cve_counts.items()), columns=['Year', 'Count'])
    cve_df['Year'] = cve_df['Year'].astype(int)  # Converto l'anno in intero
    cve_df = cve_df.sort_values('Year')  # Ordino per anno

    # Creazione del grafico
    plt.figure(figsize=(12, 6))
    plt.plot(cve_df['Year'], cve_df['Count'], marker='o', color='b', label='conteggio CVE')
    plt.title('Andamento delle CVE negli anni', fontsize=16)
    plt.xlabel('Anno', fontsize=14)
    plt.ylabel('Numero di CVE', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=12)

    # Salvataggio del grafico come file PNG
    plt.savefig('data_results/andamento_cve.png', format='png', dpi=300)  # Salva il grafico in alta qualità

    plt.show()

    # Disconnessione dal database
    disconnect_to_mongo(client)


if __name__ == "__main__":
    plot_cve()
