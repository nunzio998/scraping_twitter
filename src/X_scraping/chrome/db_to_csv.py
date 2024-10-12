import pandas as pd

from src.X_scraping.chrome.utils.utils import *

# Mi connetto al database
client = connect_to_mongo()

# Ottengo la lista delle collezioni presenti nel database
collection_list = client.get_database(config_data['database']).list_collection_names()

data = ()

for collection in collection_list:
    data_coll = connect_to_mongo_collection(client, collection)

    data_tmp = list(data_coll.find())
    data = data + tuple(data_tmp)

df = pd.DataFrame(data)
df.to_csv('data_results/data.csv', index=False)
