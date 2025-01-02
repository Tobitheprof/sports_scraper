import scrapy
from sports_scraper.items import SportsScraperItem


class MirrorSpiderSpider(scrapy.Spider):
    name = "mirror_spider"
    allowed_domains = ["www.mirror.co.uk"]
    start_urls = ["https://www.mirror.co.uk/sport/football/"]

    def parse(self, response):
        links = response.css("article.story a::attr(href)").getall()


        for link in links:
            yield scrapy.Request(response.urljoin(link), callback=self.parse_details)

    
    def parse_details(self, response):

        item = SportsScraperItem()

        item['title'] = response.css("h1.lead-content__title::text").get()
        item['url'] = response.url
        item['author'] = response.css("a.publication-theme::text").get()

        item['date'] = response.css("span.time-container::text").get()

        item['body'] = response.css("div p::text").getall()
        item['source'] = "Mirror UK"

        yield item



    


