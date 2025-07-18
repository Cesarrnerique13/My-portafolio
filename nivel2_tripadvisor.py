from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from itemloaders.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess

class Hotel(Item):
    nombre = Field()
    score = Field()
    descripcion = Field()
    amenities = Field()

class TripAdvisor(CrawlSpider):
    name = "Hoteles"

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    allowed_domains = ['tripadvisor.com']

    start_urls = ['https://www.tripadvisor.com/Hotels-g303845-Guayaquil_Guayas_Province-Hotels.html']

    download_delay = 2

    rules = (
        Rule(
            LinkExtractor(
                allow=r'/Hotel_Review-'
                ), follow=True, callback='parse_hotel' 
        ),
    )

    def quitardolar(self, texto):
        return texto.replace("$","")

    def parse_hotel(self,response):
        sel = Selector(response)
        item = ItemLoader(Hotel(), sel)
        item.add_xpath('nombre','//h1[@id="HEADING"]/text()')
        item.add_xpath('score', 
                       '//div[@class="biGQs _P hzzSG LSyRd"]/text()',
                       MapCompose(self.quitardolar))
        item.add_xpath('amenities','//div[contains(@data-test-target, "amenity_text")]/text()')
        item.add_xpath('descripcion', '//div[@class="biGQs _P pZUbB AWdfh"]/text()',
                       MapCompose(lambda i: i.replace("\n", "").replace('\r', '')))
        yield item.load_item()

if __name__ == '__main__':
    process = CrawlerProcess({
        'FEED_FORMAT':'csv',
        "FEED_URI": "hoteles.csv"
    }
    )
    process.crawl(TripAdvisor)
    process.start()