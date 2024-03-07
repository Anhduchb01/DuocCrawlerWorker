# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
from datetime import datetime
import dateutil.parser

from datetime import datetime
class VnNewsPipeline:
	def process_item(self, item, spider):
		return item

class MongoPipeline(object):
	def __init__(self, mongo_uri, mongo_db):
		self.mongo_uri = mongo_uri
		self.mongo_db = mongo_db

	@classmethod
	def from_crawler(cls, crawler):
		return cls(
			mongo_uri=crawler.settings.get('MONGO_URI'),
			mongo_db=crawler.settings.get('MONGO_DB')
		)
	def open_spider(self, spider):
		print('Start crawling! ',spider.namePage)
		self.client = pymongo.MongoClient(self.mongo_uri)
		self.db = self.client[self.mongo_db]
		self.db.crawlers.update_one({'addressPage': spider.namePage,'industry':spider.industry}, {'$set': {'increasePost': 0}})
		print(self.db.crawlers.find_one({'addressPage': spider.namePage,'industry':spider.industry}))

	def process_item(self, item, spider):
		name = item.__class__.__name__
		saveToCollection = spider.saveToCollection
		industry = spider.industry
		title = dict(item).get('title')
		url = dict(item).get('url')
		urlPageCrawl = dict(item).get('urlPageCrawl')
		timeCreatePostOrigin = dict(item).get('timeCreatePostOrigin')
		check_exits = self.db[saveToCollection].find_one({'url': url,'industry':industry})
		check_exits1 = self.db[saveToCollection].find_one({'title': title,'urlPageCrawl':urlPageCrawl,'industry':industry})
		
		try:
			if len(title.split()) >= 3 :
				current_datetime = datetime.now()
				current_datetime = current_datetime.strftime("%Y/%m/%d")
				dict_item = dict(item)
				if timeCreatePostOrigin is not None and timeCreatePostOrigin != "":
					if timeCreatePostOrigin > current_datetime:
						self.db.crawlers.update_one({'addressPage': spider.namePage,'industry':industry}, {'$set': {'wrong_date': True}})
						original_date = datetime.strptime(timeCreatePostOrigin, "%Y/%m/%d")
						new_date = original_date.strftime("%Y/%d/%m")
						dict_item['timeCreatePostOrigin'] = new_date
						print('url wrong date',original_date,url)
				if not check_exits and not check_exits1:
					print('Add new item to MongoDB',title)
					self.db[saveToCollection].insert_one(dict_item)	
					curren_crawler = self.db.crawlers.find_one({'addressPage': spider.namePage,'industry':industry})
					self.db.crawlers.update_one({'addressPage': spider.namePage,'industry':industry}, {'$set': {'increasePost': int(curren_crawler['increasePost'])+1}})

				# else :
				# 	print('Update item to MongoDB',title)
				# 	self.db[saveToCollection].update_one({'url': url}, {'$set': dict_item})
			else :
				print('len of split title and content < 3',title)
				print('URL',url)
		except Exception as e:
			print(f'Error in process_item: {str(e)}')
		
		return item
	def spider_error(self, failure, response, spider):
		print('Error crawling! ',spider.namePage)
		error = failure.getTraceback()
		curren_crawler = self.db.crawlers.find_one({'addressPage': spider.namePage,'industry':spider.industry})
		time_crawl_page = datetime.now().strftime("%Y/%m/%d")
		self.db.crawlers.update_one({'addressPage': spider.namePage,'industry':spider.industry}, {'$set': {'statusPageCrawl': 'Error','dateLastCrawler':time_crawl_page,'sumPost':int(curren_crawler['sumPost'])+int(curren_crawler['increasePost'])}})
		self.save_logger_crawler(spider.namePage,spider.industry,"Error",error)
		print('Update status Error for crawler ',spider.namePage)
		self.client.close()

	def close_spider(self, spider):
		
		
		print('Finished crawling! ',spider.namePage)
		curren_crawler = self.db.crawlers.find_one({'addressPage': spider.namePage,'industry':spider.industry})
		# if curren_crawler['wrong_date'] == True:
		# 	print('Start Loop convert date correct day month')
		# 	post_not_correct = self.db.posts.find({'urlPageCrawl': spider.namePage})
		# 	for post in post_not_correct:
		# 		old_date = post["timeCreatePostOrigin"]
		# 		original_date = datetime.strptime(old_date, "%Y/%m/%d")
		# 		new_date = original_date.strftime("%Y/%d/%m")
		# 		if new_date is not None:
		# 			# Update the document with the new date
		# 			self.db.posts.update_one(
		# 				{"_id": post["_id"]},
		# 				{"$set": {"timeCreatePostOrigin": new_date,"correct_date_day_month":True}}
		# 			)
		time_crawl_page = datetime.now().strftime("%Y/%m/%d")
		self.db.crawlers.update_one({'addressPage': spider.namePage,'industry':spider.industry}, {'$set': {'statusPageCrawl': 'Success','dateLastCrawler':time_crawl_page,'sumPost':int(curren_crawler['sumPost'])+int(curren_crawler['increasePost'])}})
		self.save_logger_crawler(spider.namePage,spider.industry,"Success","")
		print('Update status success for crawler ',spider.namePage)
		self.client.close()
	def save_logger_crawler(self,page,industry,action,message):
		time_crawl_page = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
		string_message = ""

		if action == "Create":
			string_message = "Create Crawler"
		elif action == "Success":
			string_message = "Crawler Success"
		elif action == "Error":
			string_message = message.replace(r"['\"()]", '')

		log_entry = {
			'action': action,
			'page': page,
			'industry':industry,
			'message': string_message,
			'timelog': time_crawl_page
		}
		self.db.logcrawlers.insert_one(log_entry)
