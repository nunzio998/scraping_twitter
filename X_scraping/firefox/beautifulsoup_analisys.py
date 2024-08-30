from bs4 import BeautifulSoup

from X_scraping.firefox.utils.utils import read_parse_save, connect_to_mongo, disconnect_to_mongo
from selenium.common.exceptions import NoSuchElementException


def analisys_with_beautifulsoup(response_html, group):
    client = connect_to_mongo()

    soup = BeautifulSoup(response_html, 'html.parser')

    # Mi sposto sul body lasciando stare il resto dell'html
    soup = soup.body

    # Cerco i div che contengono il tweet per intero (comprensivo si nome, data, testo, ecc.)
    results = soup.find_all("div", class_="css-175oi2r r-1iusvr4 r-16y2uox r-1777fci r-kzbkwu")

    # a partire da quello che ottengo da results, cerco i tag <a> che contengono l'url del tweet

    # cerco i tag <a> che contengono l'url del tweet
    urls = soup.find_all("a",
                         class_="css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-xoduu5 r-1q142lx r-1w6e6rj r-9aw3ui r-3s2u2q r-1loqt21")

    # estraggo il testo dai div ottenuti e lo salvo in un file
    i = 0
    lines = []
    for result in results:
        tmp_list = result.text.split("\n")  # lista temporanea per salvare il testo del tweet
        # aggiungo la lista temporanea alla lista delle righe
        for line in tmp_list:
            lines.append(line)
        lines.append(f"https://x.com{urls[i]['href']}")  # aggiungo l'url del tweet
        i += 1

    # Filtra le righe vuote
    filtered_lines = [line.strip() for line in lines if line.strip()]

    # Divido le info in post e le salvo nel database
    read_parse_save(filtered_lines, group, client)

    disconnect_to_mongo(client)


def beautifulsoup_user_analisys(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    soup = soup.find('div',
                     class_='css-175oi2r r-kemksi r-1kqtdi0 r-1ua6aaf r-th6na r-1phboty r-16y2uox r-184en5c r-1c4cdxw r-1t251xo r-f8sm7e r-13qz1uu r-1ye8kvj')

    # Trovo il tag dell'utente
    tag = soup.find('div',
                    class_='css-146c3p1 r-dnmrzs r-1udh08x r-3s2u2q r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-18u37iz r-1wvb978')
    if tag:
        span_username = tag.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3')
        if span_username:
            tag_username = span_username.text
        else:
            tag_username = None
            print("Username non trovato...")
    else:
        tag_username = None
        print("Username non trovato...")

    # Controllo se l'utente è verificato
    if soup.find('svg',
                 class_='r-4qtqp9 r-yyyyoo r-1xvli5t r-bnwqim r-lrvibr r-m6rgpd r-1cvl2hr r-f9ja8p r-og9te1 r-3t4u6i'):
        verified = True
    else:
        verified = False

    # Trovo il numero di post
    num_post = soup.find('div', class_='css-146c3p1 r-dnmrzs r-1udh08x r-3s2u2q r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-n6v787 r-1cwl3u0 r-16dba41').text.split(' ')[0]

    # Trovo il numero di following e followers
    follows = soup.find('div', class_='css-175oi2r r-13awgt0 r-18u37iz r-1w6e6rj')

    following_div = follows.find('div', class_='css-175oi2r r-1rtiivn')
    followings = following_div.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3').text

    following_div.decompose()

    followers_div = follows.find('div', class_='css-175oi2r')
    followers = followers_div.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3').text

    # Mi sposto sul div che contiene le informazioni dell'utente
    soup = soup.find('div', class_='css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-16dba41 r-56xrmm')

    # Salvo gli attributi 'd' dei tag 'path' che definiscono le icone che identificano le info dell'utente nel profilo. Uso quindi le icone per riconoscere i vari elementi e distinguerli
    job_path = 'M19.5 6H17V4.5C17 3.12 15.88 2 14.5 2h-5C8.12 2 7 3.12 7 4.5V6H4.5C3.12 6 2 7.12 2 8.5v10C2 19.88 3.12 21 4.5 21h15c1.38 0 2.5-1.12 2.5-2.5v-10C22 7.12 20.88 6 19.5 6zM9 4.5c0-.28.23-.5.5-.5h5c.28 0 .5.22.5.5V6H9V4.5zm11 14c0 .28-.22.5-.5.5h-15c-.27 0-.5-.22-.5-.5v-3.04c.59.35 1.27.54 2 .54h5v1h2v-1h5c.73 0 1.41-.19 2-.54v3.04zm0-6.49c0 1.1-.9 1.99-2 1.99h-5v-1h-2v1H6c-1.1 0-2-.9-2-2V8.5c0-.28.23-.5.5-.5h15c.28 0 .5.22.5.5v3.51z'
    location_path = 'M12 7c-1.93 0-3.5 1.57-3.5 3.5S10.07 14 12 14s3.5-1.57 3.5-3.5S13.93 7 12 7zm0 5c-.827 0-1.5-.673-1.5-1.5S11.173 9 12 9s1.5.673 1.5 1.5S12.827 12 12 12zm0-10c-4.687 0-8.5 3.813-8.5 8.5 0 5.967 7.621 11.116 7.945 11.332l.555.37.555-.37c.324-.216 7.945-5.365 7.945-11.332C20.5 5.813 16.687 2 12 2zm0 17.77c-1.665-1.241-6.5-5.196-6.5-9.27C5.5 6.916 8.416 4 12 4s6.5 2.916 6.5 6.5c0 4.073-4.835 8.028-6.5 9.27z'
    subscription_path = 'M7 4V3h2v1h6V3h2v1h1.5C19.89 4 21 5.12 21 6.5v12c0 1.38-1.11 2.5-2.5 2.5h-13C4.12 21 3 19.88 3 18.5v-12C3 5.12 4.12 4 5.5 4H7zm0 2H5.5c-.27 0-.5.22-.5.5v12c0 .28.23.5.5.5h13c.28 0 .5-.22.5-.5v-12c0-.28-.22-.5-.5-.5H17v1h-2V6H9v1H7V6zm0 6h2v-2H7v2zm0 4h2v-2H7v2zm4-4h2v-2h-2v2zm0 4h2v-2h-2v2zm4-4h2v-2h-2v2z'
    website_path = 'M18.36 5.64c-1.95-1.96-5.11-1.96-7.07 0L9.88 7.05 8.46 5.64l1.42-1.42c2.73-2.73 7.16-2.73 9.9 0 2.73 2.74 2.73 7.17 0 9.9l-1.42 1.42-1.41-1.42 1.41-1.41c1.96-1.96 1.96-5.12 0-7.07zm-2.12 3.53l-7.07 7.07-1.41-1.41 7.07-7.07 1.41 1.41zm-12.02.71l1.42-1.42 1.41 1.42-1.41 1.41c-1.96 1.96-1.96 5.12 0 7.07 1.95 1.96 5.11 1.96 7.07 0l1.41-1.41 1.42 1.41-1.42 1.42c-2.73 2.73-7.16 2.73-9.9 0-2.73-2.74-2.73-7.17 0-9.9z'
    birth_path = 'M8 10c0-2.21 1.79-4 4-4v2c-1.1 0-2 .9-2 2H8zm12 1c0 4.27-2.69 8.01-6.44 8.83L15 22H9l1.45-2.17C6.7 19.01 4 15.27 4 11c0-4.84 3.46-9 8-9s8 4.16 8 9zm-8 7c3.19 0 6-3 6-7s-2.81-7-6-7-6 3-6 7 2.81 7 6 7z'

    # Cerco elemento lavoro
    job = None
    try:
        el_span = soup.find('span',
                            class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3 r-4qtqp9 r-1a11zyx r-1loqt21')

        if el_span.find('path')['d'] == job_path:
            job = el_span.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3').text
            # rimuovo lo span dall'html per evitare errori nella ricerca del prossimo elemento
            el_span.decompose()
    except AttributeError:
        job = None
        print("Campo lavoro non presente...")

    # Cerco elementi località, data iscrizione e data di nascita poiché il loro html ha la stessa classe. Li inizializzo a None.
    location = None
    subscription = None
    birth = None
    for i in range(3):
        try:
            el_span = soup.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3 r-4qtqp9 r-1a11zyx')

            if el_span.find('path')['d'] == location_path:
                location = el_span.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3').text

            if el_span.find('path')['d'] == subscription_path:
                subscription = \
                    el_span.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3').text.split(': ')[1]

            if el_span.find('path')['d'] == birth_path:
                birth = el_span.text.split(': ')[1]

            # rimuovo lo span dall'html per evitare errori nella ricerca del prossimo elemento
            el_span.decompose()
        except AttributeError:
            print("Campo località/data iscrizione/data di nascita non presente...")

    # Cerco elemento sito web
    website = None
    try:
        el_span = soup.find('a', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3 r-4qtqp9 r-1a11zyx r-1loqt21')
        if el_span.find('path')['d'] == website_path:
            website = el_span.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3').text
        # rimuovo lo span dall'html per evitare errori nella ricerca del prossimo elemento
        el_span.decompose()
    except AttributeError:
        website = None
        print("Campo sito web non presente...")

    return {
        "username": tag_username,
        "verified": verified,
        "num_post": num_post,
        "following": followings,
        "followers": followers,
        "job": job,
        "location": location,
        "subscription": subscription,
        "birth": birth,
        "website": website
    }
