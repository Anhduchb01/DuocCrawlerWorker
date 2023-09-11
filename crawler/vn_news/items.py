# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class DuocItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    timeCreatePostOrigin = scrapy.Field()
    summary = scrapy.Field()
    content = scrapy.Field()
    summary_html = scrapy.Field()
    content_html = scrapy.Field()
    urlPageCrawl = scrapy.Field()
    url = scrapy.Field()
class VnNewsItem(scrapy.Item):
    title = scrapy.Field()
    timeCreatePostOrigin = scrapy.Field()
    type = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    content_html = scrapy.Field()
    image_url = scrapy.Field()
    urlPageCrawl = scrapy.Field()
    url = scrapy.Field()
    status = scrapy.Field()
class CafefItem(scrapy.Item):
    pass
class ReportItem(scrapy.Item):
    page = scrapy.Field()
    id_item = scrapy.Field()
    date = scrapy.Field()
    title= scrapy.Field()
    source =scrapy.Field()
    number_CK = scrapy.Field()
    id_pdf = scrapy.Field()