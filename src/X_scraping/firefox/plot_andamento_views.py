import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from src.X_scraping.firefox.utils.utils import connect_to_mongo, connect_to_mongo_collection, disconnect_to_mongo


def plot_tweet_views_by_fortnight(collection_name):
    """
    Estrae i tweet da una collection MongoDB e genera un grafico a barre delle views
    raggruppate per intervalli di 15 giorni.
    """

    # Connessione a MongoDB
    client = connect_to_mongo()
    collection = connect_to_mongo_collection(client, collection_name)

    # Recupero dei dati dalla collection
    data = collection.find({}, {'date': 1, 'views': 1})

    # Lista per raccogliere i dati
    tweet_data = []

    for document in data:
        try:
            date_time = datetime.strptime(document['date'], "%Y-%m-%dT%H:%M:%S.%fZ")
            views = document.get('views', 0)  # Se manca, assume 0
            tweet_data.append({'date': date_time, 'views': views})
        except Exception as e:
            print(f"Errore nella conversione della data: {e}")

    # Creazione del DataFrame
    tweet_df = pd.DataFrame(tweet_data)

    if tweet_df.empty:
        print("⚠ Nessun dato trovato nella collection.")
        disconnect_to_mongo(client)
        return

    # 🔹 **Convertire views in numerico**
    tweet_df['views'] = pd.to_numeric(tweet_df['views'], errors='coerce')
    tweet_df = tweet_df.dropna(subset=['views'])

    # 🔹 **Verifica se ci sono dati validi**
    if tweet_df.empty or tweet_df['views'].max() == 0:
        print("⚠ Nessun valore valido per 'views' trovato.")
        disconnect_to_mongo(client)
        return

    # 🔹 **Creare intervalli di 15 giorni**
    tweet_df['fortnight'] = tweet_df['date'].apply(lambda x: f"{x.year}-{x.month:02d}-01" if x.day <= 15 else f"{x.year}-{x.month:02d}-16")

    # Raggruppare e sommare le views per ogni intervallo
    fortnightly_views = tweet_df.groupby('fortnight')['views'].sum().reset_index()

    # Convertire la colonna 'fortnight' in datetime per un ordinamento corretto
    fortnightly_views['fortnight'] = pd.to_datetime(fortnightly_views['fortnight'])

    # Creazione del grafico a barre
    plt.figure(figsize=(12, 6))
    plt.bar(fortnightly_views['fortnight'], fortnightly_views['views'], color='royalblue', alpha=0.8, width=10)

    # Ottimizzazione asse X
    plt.xticks(ticks=fortnightly_views['fortnight'], labels=fortnightly_views['fortnight'].dt.strftime('%Y-%m-%d'), rotation=45, ha='right')

    # Ottimizzazione asse Y: partire da 0 fino al massimo +5%
    plt.ylim(0, fortnightly_views['views'].max() * 1.05)

    # Titoli e etichette
    plt.title(f"Andamento delle Visualizzazioni - {collection_name}", fontsize=16)
    plt.xlabel("Intervallo (15 giorni)", fontsize=14)
    plt.ylabel("Numero di Visualizzazioni", fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.6)

    # Salvataggio del grafico
    plt.tight_layout()
    plt.savefig('data_results/andamento_views_15giorni_bar.png', format='png', dpi=300)

    # Mostra il grafico
    plt.show()

    disconnect_to_mongo(client)


if __name__ == "__main__":
    plot_tweet_views_by_fortnight('CVE-2024-55591')