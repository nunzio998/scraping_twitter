"""
Questo script analizza l'andamento delle CVE (Common Vulnerabilities and Exposures) nei risultati della ricerca su
Ahmia, un motore di ricerca per il Dark Web. Utilizzando MongoDB, lo script estrae e conteggia le CVE trovate nelle
keyword di ricerca e genera un grafico temporale.

Autore: Francesco Pinsone.
"""
import pandas as pd
import matplotlib.pyplot as plt
import re
from src.DarkWeb_scraping.utils.utils import connect_to_mongo, connect_to_mongo_collection, disconnect_to_mongo


def plot_cve() -> None:
    """
    Questa funzione analizza la presenza di CVE nei risultati di ricerca su Ahmia e genera un grafico per visualizzarne
    l'andamento temporale.

    **Funzionamento**:
    1. **Connessione a MongoDB**: Si collega al database MongoDB e accede alla collection `ahmia_results`.

    2. **Estrazione dei dati**: Recupera i documenti dalla collection, escludendo il campo `keywords`.

    3. **Identificazione delle CVE**: Analizza il campo `search_keywords` per individuare CVE nel formato `CVE-YYYY` e
    conta il numero di occorrenze per ciascun anno.

    4. **Elaborazione dei dati**: Organizza i dati in un DataFrame pandas per ordinamento e analisi.

    5. **Generazione del grafico**: Crea un grafico a linee con il numero di CVE menzionate per anno.

    6. **Salvataggio e visualizzazione del grafico**: Il grafico viene salvato in formato PNG con alta risoluzione.
    Infine la connessione al database viene chiusa per evitare problemi di gestione.

    :return: Nessun valore ritornato.
    """
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
    plt.plot(cve_df['Year'], cve_df['Count'], marker='o', color='b', label='Conteggio CVE')
    plt.title('Andamento delle CVE negli anni', fontsize=16)
    plt.xlabel('Anno', fontsize=14)
    plt.ylabel('CVE', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=12)

    # Salvataggio del grafico come file PNG
    plt.savefig('data_results/andamento_cve.png', format='png', dpi=300)  # Salva il grafico in alta qualità

    plt.show()

    # Disconnessione dal database
    disconnect_to_mongo(client)


if __name__ == "__main__":
    plot_cve()
