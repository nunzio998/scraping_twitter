from bs4 import BeautifulSoup
from utils import read_parse_save

# Apro l'html con BeautifulSoup
with open('dat_res/response.html', 'r') as f:
    soup = BeautifulSoup(f, 'html.parser')

# Mi sposto sul body lasciando stare il resto dell'html
soup = soup.body

# Cerco i div che contengono il tweet per intero (comprensivo si nome, data, testo, ecc.)
results = soup.find_all("div", class_="css-175oi2r r-1iusvr4 r-16y2uox r-1777fci r-kzbkwu")

# estraggo il testo dai div ottenuti e lo salvo in un file
for result in results:
    with open('dat_res/results.txt', 'w') as f:
        f.write(result.text)

#lines_prova = []
#for result in results:
#    lines_prova.append(result.text)

# Leggi il contenuto dal file di testo
with open("dat_res/results.txt", "r") as file:
    lines = file.readlines()



# Filtra le righe vuote
filtered_lines = [line.strip() for line in lines if line.strip()]

#filtered_lines = [line.strip() for line in lines_prova if line.strip()]

# Scrivi il contenuto filtrato in un nuovo file
with open("dat_res/filtered_results.txt", "w") as new_file:
    new_file.write("\n".join(filtered_lines))

print("Righe vuote rimosse e salvate in 'filtered_file.txt'")

# Divido le info nel file in post
read_parse_save("dat_res/filtered_results.txt", "dat_res/output.json")
