import scrapy
from ..items import DuocItem
from datetime import datetime
import re
import requests
class NguoiDuaTinSpider(scrapy.Spider):
	name = 'nguoiduatin'
	allowed_domains = ['nguoiduatin.vn']
	def __init__(self,config=None, *args, **kwargs):
		super(NguoiDuaTinSpider, self).__init__(*args, **kwargs)
		self.items_crawled = 0
		self.last_date = config["last_date"]

		self.article_url_query = config['article_url_query']
		self.title_query = config['title_query']
		self.timeCreatePostOrigin_query = config['timeCreatePostOrigin_query']
		self.author_query = config['author_query']
		self.content_query =config['content_query']
		self.summary_query = config['summary_query']
		self.content_html_query = config['content_html_query']
		self.summary_html_query = config['summary_html_query']

		self.origin_domain = 'https://www.nguoiduatin.vn'
		self.start_urls = ['https://www.nguoiduatin.vn/tag-ajax/34687/layout/desktop/page/1']
		self.current_page = 1
	def parse(self, response):
		data = response.json().get('html', '')
		if data:
			selector = scrapy.selector.Selector(text=data)
			article_links = selector.css(self.article_url_query)
			for link in article_links:
				href = link.attrib['href']
				print(href)
				yield scrapy.Request(self.origin_domain + href, callback=self.parse_article)
			if len(article_links)>0:
				print('current_page',self.current_page)
				next_page = self.current_page +1
				next_page_link = response.url.replace(f"page/{self.current_page}",f"page/{next_page}")
				self.current_page = next_page
				yield scrapy.Request(next_page_link, callback=self.parse)
			else:
				print("No more article links to follow. Stopping the spider.")
				self.crawler.engine.close_spider(self, 'No more articles to scrape')
	def formatString(self, text):
		if isinstance(text, list):  # Check if text is a list
			text = ' '.join(text)
		if text is not None :
			text = text.replace('\r\n','')
			text = text.replace('\n','')
			text = "".join(text.rstrip().lstrip())
		cleaned_text = re.sub(r'[^a-zA-Z0-9À-ỹ\s.,!?]', ' ', str(text))
		cleaned_string = re.sub(r'\s{2,}', ' ', cleaned_text)
		
		return cleaned_string
	def parse_article(self, response):
		# Extract information from the news article page
		title = response.css(self.title_query+'::text').get()
		title = self.formatString(title)
		timeCreatePostOrigin = response.css(self.timeCreatePostOrigin_query+'::text').get()
		try:
			date_portion = timeCreatePostOrigin.split(',')[1].split('|')[0].strip()
			datetime_object = datetime.strptime(date_portion, '%d/%m/%Y')
			timeCreatePostOrigin = datetime_object.strftime('%Y/%m/%d')
		except Exception as e: 
			print('Do Not convert to datetime')
			print(e)
		author = response.css(self.author_query+'::text').get()
		author = self.formatString(author)

		summary = response.css(self.summary_query+'::text').get()
		summary = self.formatString(summary)
		summary_html =  response.css(self.summary_html_query).get()

		content = response.css(self.content_query+' ::text').getall()
		content = self.formatString(content)
		content_html = response.css(self.content_html_query).get()

		item = DuocItem(
			title=title,
			timeCreatePostOrigin=timeCreatePostOrigin,
			author = author,
			summary=summary,
			content=content,
			summary_html = summary_html,
			content_html = content_html,
			urlPageCrawl= 'nguoiduatin',
			url=response.url
		)
		if title == '' or title ==None or content =='' or content == None :
			yield None
		else :
			yield item
