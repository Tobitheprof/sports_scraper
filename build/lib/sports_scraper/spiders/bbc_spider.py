import scrapy
from sports_scraper.items import SportsScraperItem

class BbcSpiderSpider(scrapy.Spider):
    name = "bbc_spider"
    allowed_domains = ["www.bbc.com"]
    start_urls = ["https://www.bbc.com/sport/football"]

   
    
    def parse(self, response):
        links = response.css("div.ssrcss-bz7v5r-HierachichalCollectionsWrapper a::attr(href)").getall()
        filtered_links = [link for link in links if "/sport/football/article" in link or "/sport/football/live" in link]

        for link in filtered_links:
            yield scrapy.Request(response.urljoin(link), callback=self.parse_article)

    def parse_article(self, response):
        item = SportsScraperItem()

        item['title'] = response.css("h1#main-heading span::text").get()
        item['url'] = response.url
        item['author'] = response.css("div.ssrcss-68pt20-Text-TextContributorName::text").get()

        # Extract and clean the date
        item['date'] = response.css("span.ssrcss-1if1g9v-MetadataText time::text").get()

        item['body'] = response.css("div.ssrcss-7uxr49-RichTextContainer p::text").getall()
        item['source'] = "BBC Football"

        yield item


