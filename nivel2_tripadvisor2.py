from scrapy.item import Item
from scrapy.item import Field
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from itemloaders.processors import MapCompose
from scrapy.crawler import CrawlerProcess

class Opinion(Item):
    title = Field()
    rating = Field()
    content = Field()
    author = Field()
    hotel = Field()

class TrapAdvisor(CrawlSpider):
    name = 'TrapAdvisor'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'CLOSESPIDER_PAGECOUNT': 100,
        'FEED_EXPORT_FIELDS': ['title', 'rating', 'content','hotel'],
        'FEED_EXPORT_ENCODING': 'utf-8'
    }

    allowed_domains = ['tripadvisor.com']

    download_delay = 1

    start_urls = ['https://www.tripadvisor.com/Hotels-g303845-Guayaquil_Guayas_Province-Hotels.html']

    rules = (
        # Horizontalidad (paginacion) de hoteles
        Rule(
            LinkExtractor(
                allow=r'-oa\d+-'
            ),follow=True
        ),
        # Detalles de hoteles (Verticalidad)
        Rule(
            LinkExtractor(
                allow=r'/Hotel_Review-',
                restrict_xpaths=['//div[@data-automation="hotel-card-title"]/a'] # Evita obtener URLs repetidas reduciendo el espectro de busqueda de las URLs a solamente un contenedor especifico dentro de un XPATH
            ), follow=True
        ),
        # Paginacion de opiniones dentro de un hotel
        Rule(
            LinkExtractor(
                allow=r'-or\d+-'
            ), follow=True
        ),
        #Detalles de perfil de usuario 
        Rule(
            LinkExtractor(
                allow=r'Profile',
                restrict_xpaths=['//div[@data-test-target="reviews-tab"]']
            ), follow=True, callback='parse_opinion'
        ),
    )

    def parse_opinion(self, response):
        sel = Selector(response)
        opinions = sel.xpath('//div[@id="content"]/div/div')
        author = sel.xpath('//h1/span/text()').get()
        for opinion in opinions:
            item = ItemLoader(Opinion(), opinion)
            item.add_xpath('title', './/div[@class="AzIrY b _a VrCoN"]/text()')
            #item.add_xpath('rating', './/div[contains(@class, "ui_card section")]//a/div/span[contains(@class, "ui_bubble_rating")]/@class',
                          # MapCompose(lambda i: i.split('_')[-1])) # ya no funciona
            item.add_xpath('content', './/q/text()')
            item.add_value('author', author)
            item.add_xpath('hotel',
                           './/div[contains(@class, "ui_card section")]//div[@title]/text()')  # div[@title] => divs que contengan el atributo title
            yield item.load_item()

if __name__ == "__main__":
    process = CrawlerProcess({
                    'FEED_FORMAT': 'csv',
                    'FEED_URI':'tripadivisor.csv'

                })

    process.crawl(TrapAdvisor)
    process.start()