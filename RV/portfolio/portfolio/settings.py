# Scrapy settings for portfolio project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'portfolio'

SPIDER_MODULES = ['portfolio.spiders']
NEWSPIDER_MODULE = 'portfolio.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'portfolio (+http://www.ryan-omizo.com)'
