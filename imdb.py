# IMDb Top Scraper

**Qué hace**  
Extrae el Top 250 de películas de https://m.imdb.com/chart/top/, guardando:
- `rank` (posición)
- `title` (título)
- `year` (año)
- `rating` (puntuación)

import requests 
from lxml import html
import csv 

# # Definimos headers para evitar detección anti-bots
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.'
}


# URL semilla: página con lista de películas Top IMDb móvil
url = 'https://m.imdb.com/chart/top/'

#  Hacemos la petición GET con headers
response= requests.get(url=url, headers=headers)

#  Parseamos el contenido HTML a DOM
parse = html.fromstring(response.text)

# Extraemos la lista de películas usando XPath (cada <li> con clase específica)
peliculas = parse.xpath('//li[@class="ipc-metadata-list-summary-item"]')

with open ('Pelicula.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['#', 'titulo', 'year', 'rating'])

# Aqui vamos a hacer un bucle for para para iterar la lista de peliculas
# y sacarle la info a cada una 
    for i, pelicula in enumerate(peliculas, start=1):
    # el try except lo usamos para evitar que nuestro script caiga en error 
    # y no detenga la ejecucion del codigo de manera abructa
        nombre = 'Desconocido'
        year = 'Desconocido'
        ratings = 'N/A'
        try:
        # Aqui estamos sacando el titulo de la pelicula con xpath 
            titulo = pelicula.xpath('.//h3[@class="ipc-title__text ipc-title__text--reduced"]/text()')
        # Aqui estamos sacanso el texto sin el numero y limpiamos 
            nombre = titulo[0].split('.')[1].strip()
            print(nombre)
        except Exception as e:
            print(e)
            print('Pelicula sin titulo')

        try: 
        # estoy extranendo el year pero es una clase que tambien extrae otras cosas,me una litas con otros elememtos
            year = pelicula.xpath('.//div[@class="sc-15ac7568-6 fqJJPW cli-title-metadata"]/span/text()')
            year = year[0]
            print(year)
        except Exception as e:
            print(e)
            print('Pelicula sin year')
        

        try:
        # estoy extranendo el rating pero es una clase que tambien extrae otras cosas,me una litas con otros elememtos
            ratings = pelicula.xpath('.//span[@class="ipc-rating-star--rating"]/text()')
            ratings =ratings[0]
            print (ratings)
        except Exception as e:
            print(e)
            print('pelicula sin rating')

        writer.writerow([i, nombre or "Desconocido", year or "Desconocido", ratings or "N/A"])
    
