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
		
		self.title_query = self.formatQuery(config['title_query'])
		self.timeCreatePostOrigin_query = self.formatQuery(config['timeCreatePostOrigin_query'])
		self.author_query = self.formatQuery(config['author_query'])
		self.content_query = self.formatQuery(config['content_query'])
		self.summary_query = self.formatQuery(config['summary_query'])
		self.content_html_query = self.formatQuery(config['content_html_query'])
		self.summary_html_query = self.formatQuery(config['summary_html_query'])

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
	
	def formatQuery(self, query):
		query = str(query).strip()
		query = query.replace(">"," ")
		query = ' '.join(query.split())
		return query
	
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
	def get_inner_text(element, delimiter="\n"):
		list_result = [str(el).strip() for el in element.css('*::text').getall() if len(str(el).strip())>0]
		print(list_result)
		result = delimiter.join(list_result)
		print(result)
		return result
	
	def parse(self, response):
		print('start')
		print('Using Spash :' ,self.useSplash)
		le = LinkExtractor()
		list_links = le.extract_links(response)
		news_links = [
			link.url for link in list_links if self.should_follow_link(link.url)
		]
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
		for next_page_link in next_page_links:
			if next_page_link not in self.visited_links:
				if self.useSplash:
					yield  SplashRequest(url= next_page_link, callback=self.parse_news, args={"wait": 15})
				else:
					yield scrapy.Request(url=next_page_link, callback=self.parse_news)
		
		title = self.get_inner_text(response.css(self.title_query))
		title = self.formatTitle(title)
		if self.timeCreatePostOrigin_query == '' or self.timeCreatePostOrigin_query ==None:
			timeCreatePostOrigin = ''
			timeCreatePostRaw = ''
		else:
			timeCreatePostRaw = self.get_inner_text(response.css(self.timeCreatePostOrigin_query))
		try :
			timeCreatePostOrigin  = convert_to_custom_format(timeCreatePostRaw)
		except Exception as e: 
			timeCreatePostOrigin = None
			print('Do Not convert to datetime')
			print(e)

		if self.author_query == '' or self.author_query ==None:
			author = self.namePage
		else:
			author = self.get_inner_text(response.css(self.author_query))

		if self.summary_query == '' or self.summary_query ==None:
			summary = ''
			summary_html =''
			
		else:
			summary = self.get_inner_text(response.css(self.summary_query))
			summary_html = response.css(self.summary_html_query).get()
		if self.content_query == '' or self.content_query ==None:
			content = ''
			content_html =''
		else:
			content = self.get_inner_text(response.css(self.content_query))
			content_html = response.css(self.content_html_query).get()
		item = DuocItem(
			title=title,
			timeCreatePostOrigin=timeCreatePostOrigin,
			timeCreatePostRaw = timeCreatePostRaw,
			author = author,
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
