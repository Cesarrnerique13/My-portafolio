from scrapy.item import Item
from scrapy.item import Field
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose
from scrapy.crawler import CrawlerProcess

class Article(Item):
    title = Field()
    content = Field()

class Review(Item):
    title= Field()
    rating = Field()

class Video(Item):
    title = Field()
    date_of_publication = Field()

class IgnCrawler(CrawlSpider):
    name = 'ign'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'CLOSESPIDER_PAGECOUNT': 100,
        'FEED_EXPORT_FIELDS': ['title', 'rating', 'date_of_publication', 'content'], # Ordena los campos exportados en el archivo de salida (ej: CSV, JSON)
        'FEED_EXPORT_ENCODING': 'utf-8' # Para que se muestren bien los caracteres especiales (ej. acentos)
    }

    allowed_domains = ['latam.ign.com']

    start_urls = ['https://latam.ign.com/se/?model=article&q=ps5']

    download_delay = 3

    rules = (
    # Horizontalidad por tipo de informacion (No tiene callback ya que aqui no voy a extraer datos)
        Rule(
            LinkExtractor(
                allow=r'model='
            ), follow=True
            
        ),
        # Horizontalidad por paginacion  => No tiene callback ya que aqui no voy a extraer datos
        Rule(
            LinkExtractor(
                allow=r'=&page=\d+',

            ), follow=True

            
        ),
        # Una regla para cada tipo de informacion donde ire verticalmente
        # Cada una tiene su propia funcion parse que extraera los items dependiendo de la estructura del HTML donde esta cada tipo de item
        # Reviews
        Rule(
            LinkExtractor(
                allow=r'/review/',
                deny=r'utm_source=recirc', # Parametro deny para evitar URLs repetidas que en este caso especial de IGN son por los parametros (https://www.udemy.com/instructor/communication/qa/15832180/detail?course=2861742)
            ), follow=True,callback='parse_reviews'
        ),
        # Video
        Rule(
            LinkExtractor(
                allow=r'/video/'
            ), follow=True, callback='parse_video'
        ),
        # Article 
        Rule(
            LinkExtractor(
                allow=r'/news/'
            ), follow=True, callback='parse_news'
        ),
    )


    def parse_review(self,response):
        item = ItemLoader(Review(), response)
        item.add_xpath('title', '//div[@class="article-headline"]/h1/text()')
        item.add_xpath('rating','//span[@class="side-wrapper side-wrapper hexagon-content"]/div/text()')
        yield item.load_item()

    def parse_video(self,response):
         item = ItemLoader(Video(),response)
         item.add_xpath('title', '//h1/text()')
         item.add_xpath('date_of_publication', '//span[@class="publish-date"]/text()')
         yield item.load_item()

    def parse_news(self,response):
        item = ItemLoader(Article(),response)
        item.add_xpath('title', '//h1/text()')
        item.add_xpath('content','//div[@id="id_text"]//*/text()')
        yield item.load_item()

if __name__ == "__main__":
    process = CrawlerProcess({
        'FEED_FORMAT': 'json',
        'FEED_URI': 'ign.json'
    }
    )
    process.crawl(IgnCrawler)
    process.start()