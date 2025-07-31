from bs4 import BeautifulSoup
import requests
import csv
from datetime import datetime
heardes = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.'
}

url = 'https://www.bbc.com/news'

response = requests.get(url,headers=heardes)

parse = BeautifulSoup(response.text, 'html.parser')

news = parse.find_all('div', attrs = {'data-testid':'dundee-card'})

fecha = datetime.now().strftime('%Y-%m-%d  %H-%M-%S')
nombre_archivo = f'news{fecha}.csv'

with open(nombre_archivo, 'w', newline='', encoding='utf-8' ) as f:
    writer = csv.writer(f)
    writer.writerow(['#', 'titulo', 'url', 'descripcion'])

    visto = set()

    for i, new in enumerate(news, start=1):
        
        try: 
            titulo = new.find('h2').text.strip().replace('\n', '',).replace( '\r', '',).replace('\t', '')
            if titulo in visto:
                continue 
            visto.add(titulo)
            print(titulo)
            link_tag = new.find('a')
            link = 'https://www.bbc.com' + link_tag.get('href') if link_tag else 'No link'
            print(link)
            descripcion = new.find('p').text.strip().replace('\n', '',).replace( '\r', '',).replace('\t', '')[:50]
        except Exception as e:
            print(e)
            print('error')
        writer.writerow([i, titulo, link, descripcion])
