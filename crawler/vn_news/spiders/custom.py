import scrapy
from ..items import DuocItem
from datetime import datetime
import re
import dateutil.parser
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest
from .convert_date import convert_to_custom_format
class CustomSpider(scrapy.Spider):
	name = 'custom'
	def __init__(self,config=None, *args, **kwargs):
		super(CustomSpider, self).__init__(*args, **kwargs)
		self.items_crawled = 0
		print('crawler')
		print('config',config)
		self.last_date = config["last_date"]
		
		self.title_query = config['title_query']
		self.timeCreatePostOrigin_query = config['timeCreatePostOrigin_query']
		self.author_query = config['author_query']
		self.content_query =config['content_query']
		self.summary_query = config['summary_query']
		self.content_html_query = config['content_html_query']
		self.summary_html_query = config['summary_html_query']

		self.origin_domain = config['origin_domain']
		self.start_urls = config['start_urls']
		self.current_page = 1
		self.visited_links = set()  
		self.correct_rules =config['correct_rules']
		self.incorrect_rules = config['incorrect_rules']
		self.namePage = config['namePage']
		self.useSplash = config['useSplash']
		self.saveToCollection = config['saveToCollection']
		self.industry = config['industry']
	def formatStringContent(self, text):
		if isinstance(text, list):
			text = '\n'.join(text)
		return text
	def formatTitle(self, text):
		try :
			text = re.sub(r'\s{2,}', ' ', str(text))
		except Exception as e:
			print('formatTitle')
			print(e)

		return text
	def check_correct_rules(self, link):
		if len(self.correct_rules) > 0:
			for rule in self.correct_rules:
				if rule in link:
					return True
			return False
		else:
			return True

	def check_incorrect_rules(self, link):
		if len(self.incorrect_rules) > 0:
			for rule in self.incorrect_rules:
				if rule in link:
					return False
			return True
		else:
			return True

	def check_visited_rules(self, link):
		if link in self.visited_links:
			return False
		else:
			return True

	def should_follow_link(self, link):
		if (
			self.check_correct_rules(link)
			and self.check_incorrect_rules(link)
			and self.check_visited_rules(link)
		):
			return True
		else:
			return False
	def parse(self, response):
		print('start')
		print('Using Spash :' ,self.useSplash)
		le = LinkExtractor()
		list_links = le.extract_links(response)
		news_links = [
			link.url for link in list_links if self.should_follow_link(link.url)
		]
		print('news_links',news_links)
		for link in news_links:
			self.visited_links.add(link)
			if self.useSplash:
				yield  SplashRequest(url= link, callback=self.parse_news, args={"wait": 15})
			else:
				yield scrapy.Request(url= link, callback=self.parse_news)
	
	def parse_news(self, response):
		le = LinkExtractor()
		list_page_links = le.extract_links(response)
		next_page_links = [
			link.url for link in list_page_links if self.should_follow_link(link.url)
		]
		print('next_page_links',next_page_links)
		for next_page_link in next_page_links:
			if next_page_link not in self.visited_links:
				if self.useSplash:
					yield  SplashRequest(url= next_page_link, callback=self.parse_news, args={"wait": 15})
				else:
					yield scrapy.Request(url=next_page_link, callback=self.parse_news)
		
		# title = response.css('div.news-title h1::text').get()
		title = response.css(self.title_query+' ::text').get()
		title = self.formatTitle(title)
		if self.timeCreatePostOrigin_query == '' or self.timeCreatePostOrigin_query ==None:
			timeCreatePostOrigin = ''
			timeCreatePostRaw = ''
		else:
			timeCreatePostRaw = ' '.join(response.css(self.timeCreatePostOrigin_query+' ::text').getall())
			timeCreatePostRaw = str(timeCreatePostRaw).strip()
			print('timeCreatePostRaw',str(timeCreatePostRaw))

			
		try :
			timeCreatePostOrigin  = convert_to_custom_format(timeCreatePostRaw)
		except Exception as e: 
			timeCreatePostOrigin = None
			print('Do Not convert to datetime')
			print(e)
		# author = response.css(self.author_query+'::text').get()
		# author = author.replace('Theo','')
		# author = re.sub(r'\s{2,}', ' ', str(author))
		if self.summary_query == '' or self.summary_query ==None:
			summary = ''
			summary_html =''
			
		else:
			summary = response.css(self.summary_query+' ::text').get()
			summary = self.formatStringContent(summary)
			summary_html = response.css(self.summary_html_query).get()
		if self.content_query == '' or self.content_query ==None:
			content = ''
			content_html =''
		else:
			content = response.css(self.content_query+' ::text').getall()
			content = self.formatStringContent(content)
			content_html = response.css(self.content_html_query).get()
		item = DuocItem(
			title=title,
			timeCreatePostOrigin=timeCreatePostOrigin,
			timeCreatePostRaw = timeCreatePostRaw,
			author = self.namePage,
			summary=summary,
			content=content,
			summary_html=summary_html,
			content_html = content_html,
			urlPageCrawl= self.namePage,
			url=response.url,
			industry=self.industry,
			status='0'

		)
		if title == '' or title ==None or content =='' or content == None :
			yield None
		else :
			yield item
