import scrapy
from ..items import DuocItem
from datetime import datetime
import re
class VnexpressSpider(scrapy.Spider):
	name = 'vnexpress'
	allowed_domains = ['vnexpress.net']

	def __init__(self,config=None, *args, **kwargs):
		super(VnexpressSpider, self).__init__(*args, **kwargs)
		self.namePage = 'vnexpress'
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

		self.origin_domain = 'https://vnexpress.net/'
		# self.start_urls = ['https://vnexpress.net/tag/duoc-pham-756653','https://vnexpress.net/tag/nha-thuoc-100130']
		self.start_urls = config['start_urls']
		print('start_url',self.start_urls)
		self.current_page = 1
		self.saveToCollection = config['saveToCollection']
		self.industry = config['industry']
	def parse(self, response):
		# Extract news article URLs from the page
		article_links = response.css(self.article_url_query+'::attr(href)').getall()
		# Follow each article URL and parse the article page
		for link in article_links:
			yield scrapy.Request(link, callback=self.parse_article)

		# Increment the page number and follow the next page
		if response.url == 'https://vnexpress.net/tag/duoc-pham-756653' or response.url == 'https://vnexpress.net/tag/nha-thuoc-100130':
			next_page_link = response.url + f"-p2"
			yield scrapy.Request(next_page_link, callback=self.parse)
		else: 
			if len(article_links)>0:
				self.current_page = int(response.url.split('-p')[-1])
				print('current_page',self.current_page)
				next_page = self.current_page + 1
				next_page_link = response.url.replace(f"-p{self.current_page}", f"-p{next_page}")
				yield scrapy.Request(next_page_link, callback=self.parse)
			# else:
			# 	print("No more article links to follow. Stopping the spider.")
			# 	self.crawler.engine.close_spider(self, 'No more articles to scrape')
	def formatStringContent(self, text):
		if isinstance(text, list):
			text = '\n'.join(text)
		return text
	def formatTitle(self, text):
		try :
			text = re.sub(r'\s{2,}', ' ', text)
		except Exception as e:
			print('formatTitle')
			print(e)
		return text
	def parse_article(self, response):
		# Extract information from the news article page
		title = response.css(self.title_query+'::text').get()
		title = self.formatTitle(title)
		
		timeCreatePostOrigin = response.css(self.timeCreatePostOrigin_query+'::text').get()
		
		try:
			date_portion = timeCreatePostOrigin.split(',')[1].strip()
			datetime_object = datetime.strptime(date_portion, '%d/%m/%Y')
			timeCreatePostOrigin = datetime_object.strftime('%Y/%m/%d')
		except Exception as e: 
				print('Do Not convert to datetime')
				timeCreatePostOrigin = timeCreatePostOrigin
				print(e)
		author = response.css(self.author_query+'::text').get()
		if author == None or author == "":
			author = response.css('p.Normal[style="text-align:right;"] strong::text').get()
			if author == None or author == "":
				author = response.css('p.Normal[style="text-align:right;"] em::text').get()
				if author == None or author == "":
					author = response.css('p.Normal[style="text-align:right;"]').get()
		
		# summary = response.css(self.summary_query+'::text').get()
		# summary = self.formatString(summary)
		# summary_html = response.css(self.summary_html_query).get()

		content = response.css(self.content_query+' ::text').getall()
		content = self.formatStringContent(content)
		content_html = response.css(self.content_html_query).get()
		print(title)
		# Create a CafefItem instance containing the information
		item = DuocItem(
			title=title,
			timeCreatePostOrigin=timeCreatePostOrigin,
			author = author,
			summary='',
			content=content,
			summary_html= '',
			content_html= content_html,
			urlPageCrawl= 'vnexpress',
			url=response.url,
			industry=self.industry,
			status='0'
		)
		if title == '' or title ==None or content =='' or content == None :
			yield None
		else :
			yield item
