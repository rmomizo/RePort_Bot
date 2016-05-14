import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from portfolio.items import PortfolioItem
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.spiders import CrawlSpider, Rule
import bleach


class PortfolioSpider(scrapy.Spider):
    name = "portfolio"
    allowed_domains = ["ryan-omizo.com"]

    def start_requests(self):
        yield scrapy.Request('http://ryan-omizo.com/', self.parse)
        yield scrapy.Request('http://ryan-omizo.com/cv-page/', self.parse)
        yield scrapy.Request('http://ryan-omizo.com/research-page/', self.parse)
        yield scrapy.Request('http://ryan-omizo.com/teaching-page/', self.parse)
        yield scrapy.Request('http://ryan-omizo.com/experiments-blog-page/', self.parse)


    def parse(self, response):
        item = PortfolioItem()
        item['start_url'] = response.request.url
        item['title'] = response.xpath('//title/text()').extract()
        item['content'] = response.xpath('//div[@class="entry-content"]').extract()
        item['links'] = response.xpath('//a/@href').extract()

        yield item









