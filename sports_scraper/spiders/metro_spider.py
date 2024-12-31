import scrapy


class MetroSpiderSpider(scrapy.Spider):
    name = "metro_spider"
    allowed_domains = ["metro.co.uk"]
    start_urls = ["https://metro.co.uk/sport/football/"]

    def parse(self, response):
        pass
    

    def parse_details(self, response):
        pass