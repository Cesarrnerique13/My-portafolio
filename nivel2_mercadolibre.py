from scrapy.item import Item
from scrapy.item import Field
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from itemloaders.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess

class Articulo(Item):
    titulo = Field()    
    precio_usdt= Field()
    descripcion = Field()

class MercadoLibre(CrawlSpider):
    name = 'MercadoLibreSpider'

    custom_settings = {
        "USER_AGENT":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "CLOSESPIDER_PAGECOUNT" : 20
    }

    allowed_domains = ['listado.mercadolibre.com.ve', 'articulo.mercadolibre.com.ve']

    start_urls = ['https://listado.mercadolibre.com.ve/perros?sb=all_mercadolibre#D[A:perros]']

    download_delay = 1

    rules = (
        # paginacion
        Rule( LinkExtractor(
            allow=r'_NoIndex_True'
        ), follow=True

        ),
        # detalle de los productos 
        Rule(
            LinkExtractor(
                allow=r'/MLV-'
            ), follow=True, callback="parse_item"
        ),
    )

    def limpiar_texto(self,texto):
        nuevo_texto= texto.replace('\n',' ').replace('\r',' ').replace('\t',' ').strip()
        return nuevo_texto

    def parse_item(self,response):
        item = ItemLoader(Articulo(), response)
        item.add_xpath('titulo', '//h1/text()',MapCompose(self.limpiar_texto))
        item.add_xpath('precio_usdt', '//span[@class="andes-money-amount__fraction"]/text()')
        item.add_xpath('descripcion', '//div[@class="ui-pdp-description"]/p/text()',
                       MapCompose(self.limpiar_texto))
        yield item.load_item()

    
if __name__ == "__main__":
    process = CrawlerProcess({
        "FEED_FORMAT":"csv",
        "FEED_URI": "articulo.csv"
    })

    process.crawl(MercadoLibre)
    process.start()