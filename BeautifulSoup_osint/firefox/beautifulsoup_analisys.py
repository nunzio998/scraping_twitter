from bs4 import BeautifulSoup
from utils import read_parse_save, interest_groups, connect_to_mongo, disconnect_to_mongo

# Connessione al database
client = connect_to_mongo()

for group in interest_groups:
    # Apro l'html con BeautifulSoup
    with open(f'data_results/{group}.html', 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Mi sposto sul body lasciando stare il resto dell'html
    soup = soup.body

    # Cerco i div che contengono il tweet per intero (comprensivo si nome, data, testo, ecc.)
    results = soup.find_all("div", class_="css-175oi2r r-1iusvr4 r-16y2uox r-1777fci r-kzbkwu")

    # a partire da quello che ottengo da results, cerco i tag <a> che contengono l'url del tweet

    # cerco i tag <a> che contengono l'url del tweet
    urls = soup.find_all("a", class_="css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-xoduu5 r-1q142lx r-1w6e6rj r-9aw3ui r-3s2u2q r-1loqt21")

    # estraggo il testo dai div ottenuti e lo salvo in un file
    i = 0
    lines = []
    for result in results:
        tmp_list = result.text.split("\n")  # lista temporanea per salvare il testo del tweet
        # aggiungo la lista temporanea alla lista delle righe
        for line in tmp_list:
            lines.append(line)
        lines.append(f"https://x.com{urls[i]['href']}") # aggiungo l'url del tweet
        i += 1

    # Filtra le righe vuote
    filtered_lines = [line.strip() for line in lines if line.strip()]

    # Divido le info in post e le salvo nel database
    read_parse_save(filtered_lines, group, client)


disconnect_to_mongo(client)
