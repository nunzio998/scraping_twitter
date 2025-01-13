"""
Questo script fornisce tre funzioni principali che utilizzano la libreria BeautifulSoup per analizzare il contenuto HTML di una pagina web contenente tweet e profili utente. Le funzioni estraggono informazioni rilevanti dai tweet, dagli utenti e dalle connessioni tra utenti, come descritto di seguito:

1. **Funzione `analisys_with_beautifulsoup(response_html)`**:\n
   - Analizza il contenuto HTML di una pagina con tweet.\n
   - Estrae informazioni da ciascun tweet, come:\n
        - **Autore** (nome e username).\n
        - **Data di pubblicazione** del tweet.\n
        - **Contenuto del tweet** (testo del tweet, eventualmente ricondiviso da altri utenti).\n
        - **Immagini e video** presenti nel tweet.\n
        - **Interazioni** (numero di like, retweet, commenti).\n
        - **URL del tweet**.\n

2. **Funzione `beautifulsoup_user_analisys(html_content)`**:\n
   - Analizza il contenuto HTML di una pagina di un profilo utente.\n
   - Estrae le informazioni principali dell'utente, come:\n
        - **Username** e **tag** dell'utente.\n
        - **Verifica dell'utente** (se l'utente è verificato tramite icona).\n
        - **Numero di tweet** pubblicati.\n
        - **Numero di follower** e **numero di following**.\n
        - **Localizzazione** (se disponibile).\n
        - **Descrizione professionale** dell'utente.\n

3. **Funzione `find_related_user(html_content)`**:\n
   - Analizza il contenuto HTML di una pagina utente alla ricerca di **utenti correlati**.\n
   - Estrae una lista di **utenti suggeriti** o correlati (come nel caso di follower o utenti seguiti) a partire dalle informazioni nel profilo.\n
   - Restituisce i nomi e gli username degli utenti suggeriti.\n

4. **Gestione delle eccezioni**:\n
   - Ogni volta che una sezione del contenuto non è presente o non può essere estratta, il codice gestisce l'errore evitando che lo script si interrompa. Vengono stampati messaggi di errore informativi per ogni elemento mancante (ad esempio, se il contenuto del tweet non è presente o se un utente non è verificato).\n

Lo script è pensato per raccogliere e organizzare in modo strutturato i dati dei tweet, degli utenti e delle loro connessioni, rendendoli pronti per un'analisi successiva o per ulteriori elaborazioni.

**Autore**: Francesco Pinsone.
"""
import logging

from bs4 import BeautifulSoup

# Configuro il logger
logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                    format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log


def analisys_with_beautifulsoup(response_html):
    """
    La funzione `analisys_with_beautifulsoup` analizza il contenuto HTML della pagina web dell'utente su X (Twitter)
    per estrarre informazioni sui tweet. La funzione esamina i tweet, estraendo i dati principali come l'autore, la data,
    il contenuto testuale, i media (immagini, video) e i contenuti ricondivisi. Inoltre, raccoglie il numero di interazioni
    (come like, retweet) e restituisce una lista di righe contenenti tutte le informazioni estratte per ogni tweet.

    **Funzionamento**:\n
    1. Utilizza BeautifulSoup per effettuare il parsing del contenuto HTML della pagina.\n
    2. Trova tutti i div che contengono i tweet, identificati da specifiche classi.\n
    3. Per ogni tweet, estrae:\n
        - L'autore del tweet (nome utente e tag).\n
        - La data di pubblicazione.\n
        - Il contenuto testuale del tweet, se presente.\n
        - Eventuali tweet ricondivisi (autore e contenuto, se presenti).\n
        - Le immagini e/o video inclusi nel tweet.\n
        - Le informazioni sul numero di interazioni (like, retweet, ecc.).\n
        - L'URL del tweet.\n
    4. Raccoglie tutte queste informazioni in una lista di righe, con ogni riga contenente i dati di un singolo tweet.\n
    5. Restituisce la lista delle righe, che può essere successivamente elaborata o analizzata.\n

    **Gestione degli errori**:\n
    - Se un tweet non contiene alcune delle informazioni richieste (ad esempio, l'autore, il contenuto o i media), la funzione ignora il tweet e prosegue l'elaborazione degli altri.\n
    - La funzione gestisce i possibili errori dovuti all'assenza di alcuni tag HTML attraverso try-except.\n

    :param response_html: str, il contenuto HTML della pagina web dell'utente X\n
    :return: **filtered_lines**: list, lista delle righe filtrate contenenti le informazioni estratte per ogni tweet.
    """

    soup = BeautifulSoup(response_html, 'html.parser')

    # Mi sposto sul body lasciando stare il resto dell'html
    soup = soup.body

    # Cerco i div che contengono il tweet per intero (comprensivo si nome, data, testo, ecc.)
    results = soup.find_all("article", class_="css-175oi2r r-18u37iz r-1udh08x r-1c4vpko r-1c7gwzm r-o7ynqc r-6416eg r-1ny4l3l r-1loqt21")

    # estraggo il testo dai div ottenuti e lo salvo in un file
    tweets = []
    for result in results:
        a_url = result.find("a", class_="css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-xoduu5 r-1q142lx r-1w6e6rj r-9aw3ui r-3s2u2q r-1loqt21")
        url = f"https://x.com{a_url['href']}"

        # Se non è presente l'autore il tweet viene scartato
        try:
            div_username = result.find("div", class_="css-175oi2r r-1awozwy r-18u37iz r-1wbh5a2 r-dnmrzs")
            username = div_username.find("span", class_="css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3").text.strip()


            div_tag_username = result.find("div", class_="css-146c3p1 r-dnmrzs r-1udh08x r-1udbk01 r-3s2u2q r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-18u37iz r-1wvb978")
            tag_username = div_tag_username.find("span", class_="css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3").text.strip()

        except AttributeError:
            logging.exception(f"Tweet {url} scartato per assenza autore..")
            continue

        div_date = result.find("div", class_="css-175oi2r r-18u37iz r-1q142lx")
        date = div_date.find("time")['datetime']

        # Controllo che il tweet abbia contenuto testuale
        try:
            div_contenuto = result.find("div", class_="css-146c3p1 r-8akbws r-krxsd3 r-dnmrzs r-1udh08x r-1udbk01 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-bnwqim")
            content = div_contenuto.text.strip()
        except AttributeError:
            content = None
            logging.info(f"Il tweet {url} non ha contenuto..")

        # Provo a cercare contenuti ricondivisi
        reshared = []
        try:
            div_ricondiviso = result.find("div", class_="css-175oi2r r-9aw3ui r-1s2bzr4")

            div_utente_ricondiviso = div_ricondiviso.find("div", class_="css-146c3p1 r-dnmrzs r-1udh08x r-3s2u2q r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-18u37iz r-1wvb978")
            utente_ricondiviso = div_utente_ricondiviso.find("span", class_="css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3").text.strip()
            contenuto_ricondiviso = None
            try:
                div_contenuto_ricondiviso = result.find("div", class_="css-146c3p1 r-8akbws r-krxsd3 r-dnmrzs r-1udh08x r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-bnwqim r-14gqq1x")
                contenuto_ricondiviso = div_contenuto_ricondiviso.find("span", class_="css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3").strip()
            except TypeError:
                logging.info(f"Nessun contenuto ricondivisibile per il tweet {url}..")

            reshared = [utente_ricondiviso, contenuto_ricondiviso]
        except AttributeError:
            logging.info(f"Nessun contenuto ricondiviso per il tweet {url}..")

        # Cerco presenza d'immagini e/o video nei tweet
        img_list = []
        try:
            # Trovo il div che contiene i media del post
            div_imgs = result.find("div", class_="css-175oi2r r-9aw3ui r-1s2bzr4")
            # Trovo tutte le immagini presenti nel div
            imgs = div_imgs.find_all("img", class_="css-9pa8cd")
            img_list = []
            for img in imgs:
                img_list.append(img['src'])
        except AttributeError:
            logging.info(f"Immagini non trovate per il tweet {url}..")

        video_list = []
        try:
            # Trovo il div che contiene i media del post
            div_videos = result.find("div", class_="css-175oi2r r-9aw3ui r-1s2bzr4")
            # Trovo tutti i video presenti nel div
            videos = div_videos.find_all("source", attrs={'type': 'video/mp4'})
            video_list = []
            for video in videos:
                video_list.append(video['src'])
        except AttributeError:
            logging.info(f"Video non trovati per il tweet {url}..")

        div_numeri = result.find("div", class_="css-175oi2r r-1kbdv8c r-18u37iz r-1wtj0ep r-1ye8kvj r-1s2bzr4")
        numbers = div_numeri.text.strip()

        tweet = [username, tag_username, date, content, reshared, img_list, video_list, numbers, url]

        tweets.append(tweet)

    return tweets


def beautifulsoup_user_analisys(html_content):
    """
    La funzione `beautifulsoup_user_analisys` analizza il contenuto HTML della pagina di un utente su X (Twitter) per estrarre informazioni relative al profilo dell'utente. Queste informazioni vengono restituite sotto forma di dizionario.

    **Informazioni estratte**:\n
        - Nome utente (tag username)\n
        - Stato di verifica (spunta blu, se presente)\n
        - Numero di post pubblicati\n
        - Numero di persone seguite (following)\n
        - Numero di follower (followers)\n
        - Posizione lavorativa (se presente)\n
        - Località (se presente)\n
        - Data di iscrizione al servizio (se presente)\n
        - Data di nascita (se presente)\n
        - Sito web (se presente)\n

    **Funzionamento**:\n
    1. Utilizza BeautifulSoup per effettuare il parsing del contenuto HTML della pagina.\n
    2. Crea un dizionario vuoto per raccogliere le informazioni dell'utente.\n
    3. Estrae il nome utente cercando il tag `<h1>` con una classe specifica.\n
    4. Verifica se l'utente è verificato cercando un tag `<span>` che contiene l'indicatore di verifica.\n
    5. Estrae il numero di post cercando il tag `<span>` corrispondente al conteggio dei post.\n
    6. Estrae il numero di persone seguite e i followers, analizzando i rispettivi tag `<span>`.\n
    7. Estrae informazioni sul lavoro, la località, la data di iscrizione e la data di nascita, se disponibili.\n
    8. Estrae il sito web dell'utente, se presente.\n
    9. Raccoglie tutte le informazioni in un dizionario.\n

    **Gestione degli errori**:\n
    - Se uno dei dati richiesti non è presente, la funzione restituisce `None` per quel dato specifico, senza interrompere l'esecuzione.

    :param html_content: str, il contenuto HTML della pagina web dell'utente X\n
    :return: **user_data**: dict, un dizionario contenente le informazioni estratte dal profilo dell'utente. Se alcune informazioni non sono presenti, saranno indicate come `None`.
    """
    # Salvo gli attributi 'd' dei tag 'path' che definiscono le icone che identificano le info dell'utente nel profilo. Uso quindi le icone per riconoscere i vari elementi e distinguerli
    job_path = 'M19.5 6H17V4.5C17 3.12 15.88 2 14.5 2h-5C8.12 2 7 3.12 7 4.5V6H4.5C3.12 6 2 7.12 2 8.5v10C2 19.88 3.12 21 4.5 21h15c1.38 0 2.5-1.12 2.5-2.5v-10C22 7.12 20.88 6 19.5 6zM9 4.5c0-.28.23-.5.5-.5h5c.28 0 .5.22.5.5V6H9V4.5zm11 14c0 .28-.22.5-.5.5h-15c-.27 0-.5-.22-.5-.5v-3.04c.59.35 1.27.54 2 .54h5v1h2v-1h5c.73 0 1.41-.19 2-.54v3.04zm0-6.49c0 1.1-.9 1.99-2 1.99h-5v-1h-2v1H6c-1.1 0-2-.9-2-2V8.5c0-.28.23-.5.5-.5h15c.28 0 .5.22.5.5v3.51z'
    location_path = 'M12 7c-1.93 0-3.5 1.57-3.5 3.5S10.07 14 12 14s3.5-1.57 3.5-3.5S13.93 7 12 7zm0 5c-.827 0-1.5-.673-1.5-1.5S11.173 9 12 9s1.5.673 1.5 1.5S12.827 12 12 12zm0-10c-4.687 0-8.5 3.813-8.5 8.5 0 5.967 7.621 11.116 7.945 11.332l.555.37.555-.37c.324-.216 7.945-5.365 7.945-11.332C20.5 5.813 16.687 2 12 2zm0 17.77c-1.665-1.241-6.5-5.196-6.5-9.27C5.5 6.916 8.416 4 12 4s6.5 2.916 6.5 6.5c0 4.073-4.835 8.028-6.5 9.27z'
    subscription_path = 'M7 4V3h2v1h6V3h2v1h1.5C19.89 4 21 5.12 21 6.5v12c0 1.38-1.11 2.5-2.5 2.5h-13C4.12 21 3 19.88 3 18.5v-12C3 5.12 4.12 4 5.5 4H7zm0 2H5.5c-.27 0-.5.22-.5.5v12c0 .28.23.5.5.5h13c.28 0 .5-.22.5-.5v-12c0-.28-.22-.5-.5-.5H17v1h-2V6H9v1H7V6zm0 6h2v-2H7v2zm0 4h2v-2H7v2zm4-4h2v-2h-2v2zm0 4h2v-2h-2v2zm4-4h2v-2h-2v2z'
    website_path = 'M18.36 5.64c-1.95-1.96-5.11-1.96-7.07 0L9.88 7.05 8.46 5.64l1.42-1.42c2.73-2.73 7.16-2.73 9.9 0 2.73 2.74 2.73 7.17 0 9.9l-1.42 1.42-1.41-1.42 1.41-1.41c1.96-1.96 1.96-5.12 0-7.07zm-2.12 3.53l-7.07 7.07-1.41-1.41 7.07-7.07 1.41 1.41zm-12.02.71l1.42-1.42 1.41 1.42-1.41 1.41c-1.96 1.96-1.96 5.12 0 7.07 1.95 1.96 5.11 1.96 7.07 0l1.41-1.41 1.42 1.41-1.42 1.42c-2.73 2.73-7.16 2.73-9.9 0-2.73-2.74-2.73-7.17 0-9.9z'
    birth_path = 'M8 10c0-2.21 1.79-4 4-4v2c-1.1 0-2 .9-2 2H8zm12 1c0 4.27-2.69 8.01-6.44 8.83L15 22H9l1.45-2.17C6.7 19.01 4 15.27 4 11c0-4.84 3.46-9 8-9s8 4.16 8 9zm-8 7c3.19 0 6-3 6-7s-2.81-7-6-7-6 3-6 7 2.81 7 6 7z'
    verified_user1 = 'M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.854-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.688-.13.633-.08 1.29.144 1.896-.587.274-1.087.705-1.443 1.245-.356.54-.555 1.17-.574 1.817.02.647.218 1.276.574 1.817.356.54.856.972 1.443 1.245-.224.606-.274 1.263-.144 1.896.13.634.433 1.218.877 1.688.47.443 1.054.747 1.687.878.633.132 1.29.084 1.897-.136.274.586.705 1.084 1.246 1.439.54.354 1.17.551 1.816.569.647-.016 1.276-.213 1.817-.567s.972-.854 1.245-1.44c.604.239 1.266.296 1.903.164.636-.132 1.22-.447 1.68-.907.46-.46.776-1.044.908-1.681s.075-1.299-.165-1.903c.586-.274 1.084-.705 1.439-1.246.354-.54.551-1.17.569-1.816zM9.662 14.85l-3.429-3.428 1.293-1.302 2.072 2.072 4.4-4.794 1.347 1.246z'
    verified_user2 = 'M12.05 2.056c-.568-.608-1.532-.608-2.1 0l-1.393 1.49c-.284.303-.685.47-1.1.455L5.42 3.932c-.832-.028-1.514.654-1.486 1.486l.069 2.039c.014.415-.152.816-.456 1.1l-1.49 1.392c-.608.568-.608 1.533 0 2.101l1.49 1.393c.304.284.47.684.456 1.1l-.07 2.038c-.027.832.655 1.514 1.487 1.486l2.038-.069c.415-.014.816.152 1.1.455l1.392 1.49c.569.609 1.533.609 2.102 0l1.393-1.49c.283-.303.684-.47 1.099-.455l2.038.069c.832.028 1.515-.654 1.486-1.486L18 14.542c-.015-.415.152-.815.455-1.099l1.49-1.393c.608-.568.608-1.533 0-2.101l-1.49-1.393c-.303-.283-.47-.684-.455-1.1l.068-2.038c.029-.832-.654-1.514-1.486-1.486l-2.038.07c-.415.013-.816-.153-1.1-.456zm-5.817 9.367l3.429 3.428 5.683-6.206-1.347-1.247-4.4 4.795-2.072-2.072z'
    verified_user3 = 'M13.324 3.848L11 1.6 8.676 3.848l-3.201-.453-.559 3.184L2.06 8.095 3.48 11l-1.42 2.904 2.856 1.516.559 3.184 3.201-.452L11 20.4l2.324-2.248 3.201.452.559-3.184 2.856-1.516L18.52 11l1.42-2.905-2.856-1.516-.559-3.184zm-7.09 7.575l3.428 3.428 5.683-6.206-1.347-1.247-4.4 4.795-2.072-2.072z'

    soup = BeautifulSoup(html_content, 'html.parser')

    # Mi sposto nel tag main dove sono le info che mi interessano
    soup = soup.main

    soup = soup.find('div',
                     class_='css-175oi2r r-kemksi r-1kqtdi0 r-1ua6aaf r-th6na r-1phboty r-16y2uox r-184en5c r-1abdc3e r-1lg4w6u r-f8sm7e r-13qz1uu r-1ye8kvj')

    # Trovo il tag dell'utente
    try:
        tag = soup.find('div',
                        class_='css-146c3p1 r-dnmrzs r-1udh08x r-3s2u2q r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-18u37iz r-1wvb978')
        span_username = tag.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3')
        tag_username = span_username.text
    except AttributeError:
        tag_username = None
        logging.info("Username non trovato...")

    # Controllo se l'utente è verificato
    verified = False
    try:
        username_div = soup.find('div', class_='css-175oi2r r-xoduu5 r-1awozwy r-18u37iz r-dnmrzs')
        if username_div.find('span',
                             class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3 r-xoduu5 r-18u37iz r-1q142lx'):
            username_div_span = username_div.find('span',
                                                  class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3 r-xoduu5 r-18u37iz r-1q142lx')
            verified_path_tag = username_div_span.find('path')
            if verified_path_tag:
                if verified_path_tag['d'] == verified_user1 or verified_path_tag['d'] == verified_user2 or \
                        verified_path_tag['d'] == verified_user3:
                    verified = True
    except AttributeError:
        verified = False
        logging.info("Utente non verificato...")

    # Trovo il numero di post
    try:
        num_post = soup.find('div',
                             class_='css-146c3p1 r-dnmrzs r-1udh08x r-3s2u2q r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-n6v787 r-1cwl3u0 r-16dba41').text.split(
            ' ')[0]
    except AttributeError:
        num_post = None
        logging.info("Numero di post non trovato...")

    # Trovo il numero di following e followers
    if soup.find('div', class_='css-175oi2r r-13awgt0 r-18u37iz r-1w6e6rj'):
        follows_div = soup.find('div', class_='css-175oi2r r-13awgt0 r-18u37iz r-1w6e6rj')
        try:
            following_div = follows_div.find('div', class_='css-175oi2r r-1rtiivn')
            followings = following_div.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3').text

            following_div.decompose()
        except AttributeError:
            followings = None
            logging.info("Numero di following non trovato...")

        try:
            followers_div = follows_div.find('div', class_='css-175oi2r')
            followers = followers_div.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3').text
        except AttributeError:
            followers = None
            logging.info("Numero di followers non trovato...")
    else:
        followings = None
        followers = None
        logging.info("Numero di following e followers non trovati...")

    # Mi sposto sul div che contiene le informazioni dell'utente
    soup = soup.find('div', class_='css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-16dba41 r-56xrmm')

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
        logging.info("Campo lavoro non presente...")

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
            logging.info("Campo località/data iscrizione/data di nascita non presente...")

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
        logging.info("Campo sito web non presente...")

    return {
        "username_tag": tag_username,
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


def find_related_user(html_content):
    """
    La funzione `find_related_user` analizza l'HTML della pagina di un utente di X (Twitter) per estrarre e restituire una lista di utenti correlati suggeriti. Questi utenti sono visualizzati nella sezione aside presente nel menu laterale della pagina.

    **Funzionamento**:\n
    1. Utilizza BeautifulSoup per effettuare il parsing dell'HTML della pagina.\n
    2. Si concentra sul tag `<main>` per individuare la sezione principale contenente il menu laterale.\n
    3. Cerca il tag `<aside>` che include i suggerimenti degli utenti correlati.\n
    4. Analizza la lista non ordinata `<ul>` per trovare i nomi degli utenti all'interno dei relativi elementi `<li>`.\n
    5. Raccoglie i nomi degli utenti correlati e li inserisce in una lista.\n

    **Gestione degli errori**:\n
    - Se la sezione degli utenti correlati non è presente o non contiene dati, la funzione gestisce l'eccezione con un messaggio informativo e ritorna `None`.\n

    :param html_content: str, il contenuto HTML della pagina web dell'utente X\n
    :return: **related_users**: list, lista di utenti correlati. Se non presenti, ritorna None.
    """
    related_users = []

    soup = BeautifulSoup(html_content, 'html.parser')

    try:
        # Mi sposto nel tag main dove sono le info che mi interessano
        soup = soup.main

        soup = soup.find('aside', class_='css-175oi2r')

        user_ul = soup.find('ul', class_='css-175oi2r')

        # Dal tag <ul> trovo tutti i tag <span> che si trovano nei tag <li> che compongono la lista
        user_list = user_ul.find_all('li',
                                     class_='css-175oi2r r-1mmae3n r-3pj75a r-1loqt21 r-o7ynqc r-6416eg r-1ny4l3l')

        for user in user_list:
            user_div = user.find('div',
                                 class_='css-146c3p1 r-dnmrzs r-1udh08x r-3s2u2q r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-18u37iz r-1wvb978')
            related_users.append(user_div.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3').text)
    except AttributeError:
        logging.info("Utenti correlati non presenti...")
        return None

    return related_users
