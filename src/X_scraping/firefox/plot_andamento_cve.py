"""
Questo script si connette a un database MongoDB contenente collezioni di dati sulle CVE (Common Vulnerabilities and
Exposures) estratti dai tweet. Analizza il numero di tweet che menzionano CVE per ogni anno, genera un grafico
dell'andamento temporale e salva il risultato come immagine.

Autore: Francesco Pinsone.
"""
import pandas as pd
import matplotlib.pyplot as plt
import re
from src.X_scraping.firefox.utils.utils import connect_to_mongo, connect_to_mongo_collection, save_to_mongo, get_db


def plot_andamento_cve() -> None:
    """
    **Funzionamento**:

    1. **Connessione al database MongoDB**: Si collega al database MongoDB utilizzando `connect_to_mongo()`.

    2. **Identificazione delle collezioni CVE**: Filtra le collezioni il cui nome segue il formato `CVE-YYYY` per identificare
         gli anni delle CVE presenti.

    3. **Conteggio dei tweet per anno**: Conta il numero di documenti in ogni collezione corrispondente a un anno specifico.

    4. **Elaborazione dei dati**: I dati vengono organizzati in un DataFrame pandas per ordinamento e analisi.

    5. **Generazione del grafico**: Crea un grafico a linee che mostra il numero di tweet con riferimenti a CVE nel tempo.

    6. **Salvataggio e visualizzazione del grafico**: Il grafico viene salvato in formato PNG con alta risoluzione e opzionalmente mostrato a schermo.\n

    :return: Nessun valore ritornato.
    """
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
