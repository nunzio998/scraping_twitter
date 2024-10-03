from bs4 import BeautifulSoup


def analisys_with_beautifulsoup(response_html, group):
    soup = BeautifulSoup(response_html, 'html.parser')

    # Mi sposto sul body lasciando stare il resto dell'html
    soup = soup.body

    # Cerco i div che contengono il tweet per intero (comprensivo si nome, data, testo, ecc.)
    results = soup.find_all("div", class_="css-175oi2r r-1iusvr4 r-16y2uox r-1777fci r-kzbkwu")

    # estraggo il testo dai div ottenuti e lo salvo in un file
    i = 0
    lines = []
    for result in results:
        tmp_list = result.text.split("\n")  # lista temporanea per salvare il testo del tweet
        # aggiungo la lista temporanea alla lista delle righe
        for line in tmp_list:
            lines.append(line)
        url = result.find("a", class_="css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-xoduu5 r-1q142lx r-1w6e6rj r-9aw3ui r-3s2u2q r-1loqt21")
        lines.append(f"https://x.com{url['href']}")  # aggiungo l'url del tweet
        # lines.append(f"https://x.com{urls[i]['href']}")  # aggiungo l'url del tweet

        # Cerco presenza d'immagini e/o video nei tweet
        try:
            # Trovo il div che contiene i media del post
            div_imgs = result.find("div", class_="css-175oi2r r-9aw3ui r-1s2bzr4")
            # Trovo tutte le immagini presenti nel div
            imgs = div_imgs.find_all("img", class_="css-9pa8cd")
            for img in imgs:
                lines.append(img['src'])
                print(f"IMMAGINE: {img['src']}")
        except AttributeError:
            print("Immagini non trovate...")

        try:
            # Trovo il div che contiene i media del post
            div_videos = result.find("div", class_="css-175oi2r r-9aw3ui r-1s2bzr4")
            # Trovo tutti i video presenti nel div
            videos = div_videos.find_all("source", attrs={'type': 'video/mp4'})
            for video in videos:
                lines.append(video['src'])
                print(f"VIDEO: {video['src']}")
        except AttributeError:
            print("Video non trovati...")

        i += 1

    # Filtra le righe vuote
    filtered_lines = [line.strip() for line in lines if line.strip()]
    print(filtered_lines)

    return filtered_lines


def beautifulsoup_user_analisys(html_content):
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

    soup = soup.find('div', class_='css-175oi2r r-kemksi r-1kqtdi0 r-1ua6aaf r-th6na r-1phboty r-16y2uox r-184en5c r-1c4cdxw r-1t251xo r-f8sm7e r-13qz1uu r-1ye8kvj')

    # Trovo il tag dell'utente
    try:
        tag = soup.find('div', class_='css-146c3p1 r-dnmrzs r-1udh08x r-3s2u2q r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-18u37iz r-1wvb978')
        span_username = tag.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3')
        tag_username = span_username.text
    except AttributeError:
        tag_username = None
        print("Username non trovato...")

    # Controllo se l'utente è verificato
    verified = False
    try:
        username_div = soup.find('div', class_='css-175oi2r r-xoduu5 r-1awozwy r-18u37iz r-dnmrzs')
        if username_div.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3 r-xoduu5 r-18u37iz r-1q142lx'):
            username_div_span = username_div.find('span',
                                                  class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3 r-xoduu5 r-18u37iz r-1q142lx')
            verified_path_tag = username_div_span.find('path')
            if verified_path_tag:
                if verified_path_tag['d'] == verified_user1 or verified_path_tag['d'] == verified_user2 or \
                        verified_path_tag['d'] == verified_user3:
                    verified = True
    except AttributeError:
        verified = False
        print("Utente non verificato...")

    # Trovo il numero di post
    try:
        num_post = soup.find('div', class_='css-146c3p1 r-dnmrzs r-1udh08x r-3s2u2q r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-n6v787 r-1cwl3u0 r-16dba41').text.split(
            ' ')[0]
    except AttributeError:
        num_post = None
        print("Numero di post non trovato...")

    # Trovo il numero di following e followers
    try:
        follows = soup.find('div', class_='css-175oi2r r-13awgt0 r-18u37iz r-1w6e6rj')

        following_div = follows.find('div', class_='css-175oi2r r-1rtiivn')
        followings = following_div.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3').text

        following_div.decompose()
    except AttributeError:
        followings = None
        print("Numero di following non trovato...")

    try:
        followers_div = follows.find('div', class_='css-175oi2r')
        followers = followers_div.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3').text
    except AttributeError:
        followers = None
        print("Numero di followers non trovato...")

    # Mi sposto sul div che contiene le informazioni dell'utente
    soup = soup.find('div', class_='css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-16dba41 r-56xrmm')

    # Cerco elemento lavoro
    job = None
    try:
        el_span = soup.find('span',  class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3 r-4qtqp9 r-1a11zyx r-1loqt21')

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
    related_users = []

    soup = BeautifulSoup(html_content, 'html.parser')

    try:
        # Mi sposto nel tag main dove sono le info che mi interessano
        soup = soup.main

        soup = soup.find('aside', class_='css-175oi2r')

        user_ul = soup.find('ul', class_='css-175oi2r')

        # Dal tag <ul> trovo tutti i tag <span> che si trovano nei tag <li> che compongono la lista
        user_list = user_ul.find_all('li', class_='css-175oi2r r-1mmae3n r-3pj75a r-1loqt21 r-o7ynqc r-6416eg r-1ny4l3l')

        for user in user_list:
            user_div = user.find('div', class_='css-146c3p1 r-dnmrzs r-1udh08x r-3s2u2q r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-18u37iz r-1wvb978')
            related_users.append(user_div.find('span', class_='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3').text)
    except AttributeError:
        print("Utenti correlati non presenti...")
        return None

    return related_users
