import scrapy
from scrapy import signals
import json
from .utils import pagination_count


class ZlibSpider(scrapy.Spider):
    name = 'zlib'

    headers = {
        'User_Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 RuxitSynthetic/1.0 v8134650122 t38550 ath9b965f92 altpub cvcv=2'
    }

    start_urls = ['https://b-ok.africa/categories']
    custom_settings = {
        'CONCURRENT_REQUEST_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 3
    }
    scraped_books = []

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse, headers=self.headers)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ZlibSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        booksin = json.dumps(self.scraped_books, indent=2) 
        with open('books.json', 'w') as file:
            file.write(booksin)
        
        spider.logger.info('spider closed: %s', self.name)

    def parse(self, response, **kwargs):
        nextpage = response.xpath('(//td)[2]//a/@href').getall()
        del nextpage[0:2]

        for each in nextpage:
            yield response.follow(each, self.sectionparse, headers=self.headers,
                                  cb_kwargs=dict(pagination=True))
            

    def sectionparse(self, response, pagination):
        bookpage = response.xpath('//table//table//table//h3/a/@href').getall()

        for each in bookpage:
            yield response.follow(each, self.bookparse, headers=self.headers)
            

        if pagination:
            s = response.xpath('//script[contains(., "?page=%number%")]/text()').get()
            if s:
                pages_span = pagination_count(s)

                if pages_span:
                    page_links = []
                    for i in range(pages_span)[1:]:
                        page_url = response.url + '?page=' + str(i + 1)
                        page_links.append(page_url)
                    
                    for page in page_links:
                        yield response.follow(page, self.sectionparse, headers=self.headers,
                                              cb_kwargs=dict(pagination=False))

    def bookparse(self, response):

        pages = response.xpath('(//div[@itemscope])[1]//div[contains(@class, "property_pages")]//span/text()')\
                            .getall()
        pages = ', '.join(pages) if pages else pages

        book = {
            'name': response.xpath('(//div[@itemscope])[1]//h1/text()').
                                get().strip(),

            'author': ', '.join(response.xpath('(//div[@itemscope])[1]//i/a/text()').
                                getall()),

            'category': response.xpath('(//div[@itemscope])[1]//div[contains(@class, "property_categories")]//a/text()')
                                    .get().replace('\\\\', '/'),

            'year': response.xpath('(//div[@itemscope])[1]//div[contains(@class, "property_year")]/div[2]/text()')
                                .get(),

            'edition': response.xpath('(//div[@itemscope])[1]//div[contains(@class, "property_edition")]/div[2]/text()')
                                .get(),

            'publisher': response.xpath('(//div[@itemscope])[1]//div[contains(@class, "property_publisher")]/div[2]/text()')
                                .get(),

            'language': response.xpath('(//div[@itemscope])[1]//div[contains(@class, "property_language")]/div[2]/text()')
                                .get(),

            'pages': pages,

            'isbn10': response.xpath('(//div[@itemscope])[1]//div[contains(@class, "property_isbn 10")]/div[2]/text()')
                                .get(),

            'isbn13': response.xpath('(//div[@itemscope])[1]//div[contains(@class, "property_isbn 13")]/div[2]/text()')
                                .get(),

            'series': response.xpath('(//div[@itemscope])[1]//div[contains(@class, "property_series")]/div[2]/text()').get(),
            'file': response.xpath('(//div[@itemscope])[1]//div[contains(@class, "property__file")]/div[2]/text()').get()
        }
        
        self.scraped_books.append(book)

