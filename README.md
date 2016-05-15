# RePort Bot

The RePort Bot scrapes textual content from ePortfolio pages and automatically returns analyis of these pages that coheres around the concept of "rhetorical velocity." 

This repository hosts working code and sample outputs. However, this code is tailored to scrape content from the site [ryan-omizo.com](https://ryan-omizo.com). CSS and XPath selectors will vary across ePortfolios, so the links to [ryan-omizo.com](https://ryan-omizo.com) found in the RePort Bot spider and the `div` selectors used in ePortfolio.py will need to modified for use on other sites. 

##Procedure: Dependences
In order to run RePort Bot, you will need to install the following Python packages to your computer or virtual environment:
```python
pip
Scrapy==1.1.0rc3
beautifulsoup4==4.3.2
bleach==1.4
lxml==3.4.1
nltk==2.0.4
numpy==1.8.0
pyOpenSSL==0.15.1
python-dateutil==2.2
pyzmq==14.3.1
requests==2.7.0
requests-oauthlib==0.5.0
```
The RePort Bot's web scrapy engine runs on [scrapy](http://scrapy.org/). You may use the [scrapy documentation](http://doc.scrapy.org/en/latest/intro/tutorial.html) to extend the RePort Bot to include features such as link following.

## Procedure: Customize
To customize the RePort Bot's scraper, open `crawler.py.` `crawler.py` contains the nuts and bolts of the scraper in the `class PortfolioSpider`. 

```python
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
```


Notice all the domains and URLs that contain references to [ryan-omizo.com](https://ryan-omizo.com). Replace these domains and URLs the the site of your choice. For example:

```python
def start_requests(self):
        yield scrapy.Request('http://ryan-omizo.com/', self.parse)
        
def start_requests(self):
        yield scrapy.Request('http://yourePortfolio.com/', self.parse)
```
        
Once you have adjusted the URLs to match the site of your choice, you will need to dig around that site's HTML structure using the Inspector in Firefox or Chrome. Look for the elements that contain the main content of each page. You will then use the name of that structural container in `def parse(self, response)` function. The spider will target for extraction whatever HTML container element you specify. For [ryan-omizo.com](https://ryan-omizo.com), the `div class entry-content` frames in-page content. 

##Procedure: Use
Once you have modified the settings of the `crawler.py`, you can run the RePort Bot from your shell or Python interpreter. Because the functionality of the RePort Bot is distributed across several Python files, you will be tasked with manually implementing key points of the pipeline. 

1. Clone the RV respository to your computer.
2. Enter the `spider` directory (`RV > portfolio > portfolio spider') in the RV repository.
3. In Terminal or command line tools, enter the following command:
`scrapy crawl portfolio -o items.json`
This will activate the screen scraping program by calling `scrapy.` The results of the scrape will be saved in `items.json.`
4. Import `ePortfolio.py` by running:
```python
import ePortfolio
from ePortfolio import *
```
5. Analyze the scraped data and generate the h-index report with the following command:
`make_report('items.json')`
This will generate a `report.html` file that can be read in a browser. To see a sample, visit [RePort Bot Report](http://rmomizo.github.io/RePort_Bot/report)



        
        
