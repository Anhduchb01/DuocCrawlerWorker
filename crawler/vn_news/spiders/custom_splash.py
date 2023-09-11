import scrapy
from ..items import DuocItem
from datetime import datetime
import re
import dateutil.parser
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest
from .convert_date import convert_to_custom_format
class CustomSplashSpider(scrapy.Spider):
	name = 'customSplash'
	def __init__(self,config=None, *args, **kwargs):
		super(CustomSplashSpider, self).__init__(*args, **kwargs)
		self.items_crawled = 0
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
		else :
			return True
	def should_follow_link(self, link):
		if(self.check_correct_rules(link) and self.check_incorrect_rules(link) and self.check_visited_rules(link)):
			return True
		else:
			return False
	
	def start_requests(self):
		for url in self.start_urls:
			print('start request',url)
			yield SplashRequest(
                url,
                endpoint="render.html",
                args={"wait": 10,"expand":1,"timeout":90},
                callback=self.parse,
            )
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
			yield  SplashRequest(url= link, callback=self.parse, args={"wait": 10,"expand":1,"timeout":90})
		title = response.css(self.title_query+'::text').get()
		title = self.formatString(title)
		if self.timeCreatePostOrigin_query == '' or self.timeCreatePostOrigin_query ==None:
			timeCreatePostOrigin = ''
		else:
			timeCreatePostOrigin = response.css(self.timeCreatePostOrigin_query+'::text').get()
			timeCreatePostOrigin = re.sub(r'\s{2,}', ' ', str(timeCreatePostOrigin))
		try :
			timeCreatePostOrigin  = convert_to_custom_format(timeCreatePostOrigin)
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
			summary = response.css(self.summary_query+'::text').get()
			summary = self.formatString(summary)
			summary_html = response.css(self.summary_html_query).get()
		if self.content_query == '' or self.content_query ==None:
			content = ''
			content_html =''
		else:
			content = response.css(self.content_query+' ::text').getall()
			content = self.formatString(content)
			content_html = response.css(self.content_html_query).get()
		item = DuocItem(
			title=title,
			timeCreatePostOrigin=timeCreatePostOrigin,
			author = self.namePage,
			summary=summary,
			content=content,
			summary_html=summary_html,
			content_html = content_html,
			urlPageCrawl= self.namePage,
			url=response.url
		)
		if title == '' or title ==None or content =='' or content == None :
			yield None
		else :
			yield item


	
	