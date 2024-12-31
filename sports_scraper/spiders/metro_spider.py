import scrapy
from sports_scraper.items import SportsScraperItem


class MetroSpiderSpider(scrapy.Spider):
    name = "metro_spider"
    allowed_domains = ["metro.co.uk"]
    start_urls = ["https://metro.co.uk/sport/football/"]

    def parse(self, response):
        links = response.css("h3.article-card__title a::attr(href)").getall()

        for link in links:
            yield scrapy.Request(response.urljoin(link), callback=self.parse_details)

    def parse_details(self, response):
        item = SportsScraperItem()

        item['title'] = self.clean_text(response.css("h1.article__title::text").get())
        item['url'] = response.url
        item['author'] = self.clean_text(response.css("a.author-name::text").get())

        date_raw = response.css("div.article__date span.article__published *::text").getall()
        item['date'] = self.clean_text(" ".join([text.strip() for text in date_raw if text.strip()]).replace("Published", ""))

        item['body'] = self.clean_body(response.css("div.article__content__inner p::text").getall())
        item['source'] = "Metro UK"

        yield item


    def clean_text(self, text):
        """Clean and normalize text."""
        if text:
            return text.strip()
        return None

    def clean_body(self, paragraphs):
        """Clean and join article body paragraphs."""
        if paragraphs:
            return " ".join([p.strip() for p in paragraphs if p.strip()])
        return None
