import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from src.X_scraping.firefox.utils.utils import connect_to_mongo, connect_to_mongo_collection, disconnect_to_mongo


def plot_tweet_views_by_day(collection_name):
    """

    :param collection_name:
    :return:
    """

    client = connect_to_mongo()
    collection = connect_to_mongo_collection(client, collection_name)

    data = collection.find({}, {'date': 1, 'views': 1})

    tweet_data = []

    for document in data:
        try:
            date_time = datetime.strptime(document['date'], "%Y-%m-%dT%H:%M:%S.%fZ")
            views = document.get('views', 0)  # Se manca, assume 0
            tweet_data.append({'date': date_time.date(), 'views': views})
        except Exception as e:
            print(f"Errore nella conversione della data: {e}")

    tweet_df = pd.DataFrame(tweet_data)

    if tweet_df.empty:
        print("⚠ Nessun dato trovato nella collection.")
        disconnect_to_mongo(client)
        return

    tweet_df['views'] = pd.to_numeric(tweet_df['views'], errors='coerce')
    tweet_df = tweet_df.dropna(subset=['views'])

    if tweet_df.empty or tweet_df['views'].max() == 0:
        print("⚠ Nessun valore valido per 'views' trovato.")
        disconnect_to_mongo(client)
        return

    # Raggruppamento per ogni giorno
    daily_views = tweet_df.groupby('date')['views'].sum().reset_index()

    # Visualizzazione
    plt.figure(figsize=(12, 6))
    plt.bar(daily_views['date'], daily_views['views'], color='royalblue', alpha=0.8)

    plt.xticks(rotation=45, ha='right')
    plt.xlabel("Data", fontsize=14)
    plt.ylabel("Numero di Visualizzazioni", fontsize=14)
    plt.title(f"Andamento delle Visualizzazioni - {collection_name}", fontsize=16)
    plt.grid(axis='y', linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig(f'data_results/andamento_views_{collection_name}_daily.png', format='png', dpi=300)
    plt.show()

    disconnect_to_mongo(client)


if __name__ == "__main__":
    plot_tweet_views_by_day('CVE-2024-55591')