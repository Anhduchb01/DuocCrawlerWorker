
from flask import Flask, request, jsonify ,Blueprint ,current_app
from apscheduler.schedulers.background import BackgroundScheduler
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from datetime import datetime
from crawler.vn_news.spiders.cafebiz_duoc import CafebizDuocSpider
from crawler.vn_news.spiders.cafef_duoc import CafefDuocSpider
from crawler.vn_news.spiders.nguoiduatin import NguoiDuaTinSpider
from crawler.vn_news.spiders.thanhnien import ThanhNienSpider
from crawler.vn_news.spiders.vnexpress import VnexpressSpider
from crawler.vn_news.spiders.vnpca import VnpcaSpider
from crawler.vn_news.spiders.custom import CustomSpider
from crawler.vn_news.spiders.custom_splash import CustomSplashSpider
from crawler.vn_news.pipelines import MongoPipeline
import json
from celery.result import AsyncResult
import threading
from pymongo import MongoClient
from scrapy import signals
from scrapy.signalmanager import dispatcher
import traceback
import os
from dotenv import load_dotenv
import redis 
from rq import Queue, Connection
from bson.json_util import dumps, loads
load_dotenv()
DB_URL = os.environ.get('DB_URL')
DB_Name = os.environ.get('DB_Name')
SPLASH_URL = os.environ.get('SPLASH_URL')
client = MongoClient(DB_URL)
crawler = Blueprint('crawler', __name__)
import crochet
crochet.setup()
output_data = []
# client = MongoClient("mongodb://crawl02:crawl02123@localhost:27017/?authSource=Duoc")
db = client.Duoc
crawlers_collection = db["crawlers"]
config_crawlers_collection = db["configcrawlers"]
config_default_crawlers_collection = db["configdefaultcrawlers"]
log_crawlers_collection = db["logcrawlers"]
from celery import Celery
import os
DB_URL = os.environ.get('DB_URL')
DB_Name = os.environ.get('DB_Name')
celery = Celery("app", broker=os.environ.get("CELERY_BROKER_URL"),backend=os.environ.get("CELERY_RESULT_BACKEND"))
scheduler = BackgroundScheduler()
scheduler.start()
@crawler.route("/", methods=['GET', 'POST'])
def main():
		return '<h1>API PYTHON CRWALER</h1>'
@crawler.route("/create-crawler", methods=["POST"])
def create_crawler():
	try:
		obj_data_new = request.json["objDataNew"]
		print(obj_data_new)
		address_page = str(obj_data_new["titlePage"]).lower()
		check_crawler_info = db.crawlers.find_one({'addressPage': address_page})
		if check_crawler_info :
			return "NamePage Exist"
		# Create and save the crawler object
		crawler = {
			"addressPage": address_page,
			"URL": obj_data_new["urlPage"],
			"dateLastCrawler": '----/--/--',
			"sumPost": "0",
			"statusPageCrawl": "Off",
			"modePage": "On",
			"increasePost": '0',
			"type": "create"
		}
		crawler_obj = crawlers_collection.insert_one(crawler)
		print(f'Create crawler Ok : {crawler_obj.inserted_id}')


		summary_query_split = obj_data_new["summary_query"].split(' ')
		if summary_query_split and summary_query_split[-1] == "p":
			summary_query_split.pop()

		obj_data_new["summary_query_html"] = ' '.join(summary_query_split)

		content_query_split = obj_data_new["content_query"].split(' ')
		if content_query_split and content_query_split[-1] == "p":
			content_query_split.pop()

		obj_data_new["content_html_query"] = ' '.join(content_query_split)
		config_crawler_obj = {
			"titlePage": obj_data_new["titlePage"],
			"modeSchedule": obj_data_new["modeSchedule"],
			"namePage": address_page,
			"urlPage": obj_data_new["urlPage"],
			"timeSchedule": obj_data_new["timeSchedule"],
			"modeRobotsParser": obj_data_new["modeRobotsParser"],
			"timeOutCrawl": obj_data_new["timeOutCrawl"],
			"numberRetryCrawl": obj_data_new["numberRetryCrawl"],
			"timeDelayCrawl": obj_data_new["timeDelayCrawl"],
			"userAgent": obj_data_new["userAgent"],
			"article_url_query": obj_data_new["article_url_query"],
			"title_query": obj_data_new["title_query"],
			"timeCreatePostOrigin_query": obj_data_new["timeCreatePostOrigin_query"],
			"author_query": obj_data_new["author_query"],
			"content_query": obj_data_new["content_query"],
			"summary_query": obj_data_new["summary_query"],
			"content_html_query": obj_data_new["content_html_query"],
			"summary_html_query": obj_data_new["summary_query_html"],
			"start_urls": obj_data_new["start_urls"],
			"correct_url_contain": obj_data_new["correct_url_contain"],
			"incorrect_url_contain": obj_data_new["incorrect_url_contain"],
			"type": "create",
			"useSplash" : obj_data_new["useSplash"]
		}
		config_crawler_obj_id = config_crawlers_collection.insert_one(config_crawler_obj)
		print(f'Create ConfigCrawler OK : {config_crawler_obj["titlePage"]}')
		config_default_crawler_obj = {
			"titlePage": obj_data_new["titlePage"],
			"article_url_query": obj_data_new["article_url_query"],
			"title_query": obj_data_new["title_query"],
			"timeCreatePostOrigin_query": obj_data_new["timeCreatePostOrigin_query"],
			"author_query": obj_data_new["author_query"],
			"content_query": obj_data_new["content_query"],
			"summary_query": obj_data_new["summary_query"],
			"content_html_query": obj_data_new["content_html_query"],
			"summary_html_query": obj_data_new["summary_query_html"],
			"start_urls": obj_data_new["start_urls"],
			"correct_url_contain": obj_data_new["correct_url_contain"],
			"incorrect_url_contain": obj_data_new["incorrect_url_contain"],
			"type": "create",
			"useSplash" : obj_data_new["useSplash"]
		}

		config_default_crawler_obj_id = config_default_crawlers_collection.insert_one(config_default_crawler_obj)
		print(f'Create configDefaultCrawlerObj OK : {config_default_crawler_obj["titlePage"]}')
		save_logger_crawler(address_page,"Create","")
		return "create success"

	except Exception as err:
		print(err)
		return str(err), 502
@crawler.route("/remove-crawler", methods=["POST"])
def remove_crawler():
	try:
		name_page = request.json["namePage"]
		config_default_crawlers_collection.delete_one({"titlePage": name_page})
		crawlers_collection.delete_one({"addressPage": name_page})
		config_crawlers_collection.delete_one({"namePage": name_page})
		return "remove crawler success"

	except Exception as err:
		print(err)
		return str(err), 502
@crawler.route("/crawler-get-information", methods=["GET"])
def get_crawler_information():
	try:
		crawler_data = list(crawlers_collection.find({}))
		return dumps(crawler_data)

	except Exception as err:
		print(err)
		return str(err), 500
@crawler.route("/get-data-edit-crawl", methods=["GET"])
def get_data_edit_crawl():
	try:
		config_crawler_data = list(config_crawlers_collection.find({}))
		return dumps(config_crawler_data)

	except Exception as err:
		print(err)
		return str(err), 500
@crawler.route("/save-edit-crawl", methods=["POST"])
def save_edit_crawl():
	try:
		obj_data_edit = request.json["objDataEdit"]

		for i in range(len(obj_data_edit["timeSchedule"])):
			obj_data_edit["timeSchedule"][i]["hour"] = obj_data_edit["timeSchedule"][i]["hour"] or []
			if obj_data_edit["timeSchedule"][i]["hour"]:
				obj_data_edit["timeSchedule"][i]["hour"] = list(map(int, obj_data_edit["timeSchedule"][i]["hour"]))

		summary_query_split = obj_data_edit["summary_query"].split(' ')
		if summary_query_split and summary_query_split[-1] == "p":
			summary_query_split.pop()

		obj_data_edit["summary_query_html"] = ' '.join(summary_query_split)

		content_query_split = obj_data_edit["content_query"].split(' ')
		if content_query_split and content_query_split[-1] == "p":
			content_query_split.pop()

		obj_data_edit["content_html_query"] = ' '.join(content_query_split)

		config_crawlers_collection.update_one(
			{"titlePage": obj_data_edit["titlePage"]},
			{
				"$set": {
					"modeSchedule": obj_data_edit["modeSchedule"],
					"timeSchedule": obj_data_edit["timeSchedule"],
					"modePublic": obj_data_edit["modePublic"],
					"modeRobotsParser": obj_data_edit["modeRobotsParser"],
					"timeOutCrawl": obj_data_edit["timeOutCrawl"],
					"numberRetryCrawl": obj_data_edit["numberRetryCrawl"],
					"timeDelayCrawl": obj_data_edit["timeDelayCrawl"],
					"userAgent": obj_data_edit["userAgent"],
					"article_url_query": obj_data_edit["article_url_query"],
					"title_query": obj_data_edit["title_query"],
					"timeCreatePostOrigin_query": obj_data_edit["timeCreatePostOrigin_query"],
					"author_query": obj_data_edit["author_query"],
					"content_query": obj_data_edit["content_query"],
					"summary_query": obj_data_edit["summary_query"],
					"content_html_query": obj_data_edit["content_html_query"],
					"summary_html_query": obj_data_edit["summary_query_html"],
					
				}
			}
		)
		return "success edit config"

	except Exception as err:
		print(err)
		return str(err), 500
@crawler.route("/save-edit-crawl-create", methods=["POST"])
def save_edit_crawl_create():
	try:
		obj_data_edit = request.json["objDataEdit"]

		for i in range(len(obj_data_edit["timeSchedule"])):
			obj_data_edit["timeSchedule"][i]["hour"] = obj_data_edit["timeSchedule"][i]["hour"] or []
			if obj_data_edit["timeSchedule"][i]["hour"]:
				obj_data_edit["timeSchedule"][i]["hour"] = list(map(int, obj_data_edit["timeSchedule"][i]["hour"]))

		summary_query_split = obj_data_edit["summary_query"].split(' ')
		if summary_query_split and summary_query_split[-1] == "p":
			summary_query_split.pop()

		obj_data_edit["summary_html_query"] = ' '.join(summary_query_split)

		content_query_split = obj_data_edit["content_query"].split(' ')
		if content_query_split and content_query_split[-1] == "p":
			content_query_split.pop()

		obj_data_edit["content_html_query"] = ' '.join(content_query_split)
		print('obj_data_edit',obj_data_edit)
		config_crawlers_collection.update_one(
			{"titlePage": obj_data_edit["titlePage"]},
			{
				"$set": {
					"modeSchedule": obj_data_edit["modeSchedule"],
					"timeSchedule": obj_data_edit["timeSchedule"],
					# "modeCookies": obj_data_edit["modeCookies"],
					"modeRobotsParser": obj_data_edit["modeRobotsParser"],
					"timeOutCrawl": int(obj_data_edit["timeOutCrawl"]),
					"numberRetryCrawl": int(obj_data_edit["numberRetryCrawl"]),
					"timeDelayCrawl": int(obj_data_edit["timeDelayCrawl"]),
					"userAgent": obj_data_edit["userAgent"],
					# "cookies": obj_data_edit["cookies"],
					# "httpHeader": obj_data_edit["httpHeader"],
					"article_url_query": obj_data_edit["article_url_query"],
					"title_query": obj_data_edit["title_query"],
					"timeCreatePostOrigin_query": obj_data_edit["timeCreatePostOrigin_query"],
					"author_query": obj_data_edit["author_query"],
					"content_query": obj_data_edit["content_query"],
					"summary_query": obj_data_edit["summary_query"],
					"content_html_query": obj_data_edit["content_html_query"],
					"summary_html_query": obj_data_edit["summary_html_query"],
					"start_urls": obj_data_edit["start_urls"],
					"correct_url_contain": obj_data_edit["correct_url_contain"],
					"incorrect_url_contain": obj_data_edit["incorrect_url_contain"],
					"useSplash": obj_data_edit["useSplash"],
				}
			}
		)
		if obj_data_edit["modeSchedule"] :
			print('Setup Schedule {}'.format(obj_data_edit["titlePage"]))
			configure_scheduler(obj_data_edit["titlePage"])
		else :
			print('Remove Scheduler {}'.format(obj_data_edit["titlePage"]))
			remove_scheduler(obj_data_edit["titlePage"])

		
		return "success edit create config"

	except Exception as err:
		print(err)
		return str(err), 500
@crawler.route("/crawl", methods=['GET', 'POST'])
def crawl():
	data = request.get_json()
	namePage = data['namePage']
	crawler_info = db.crawlers.find_one({'addressPage': namePage})
	if crawler_info['statusPageCrawl'] == 'Pending':
		return  jsonify({"msg":"Crawler is running","namePage":namePage}), 200
	else:
		task = crawl_new.delay(namePage)
		return jsonify({"msg":"excute successfully crawler","namePage":namePage,"task_id": task.id}), 200
@crawler.route("/tasks/<task_id>", methods=["GET"])
def get_status(task_id):
	task_result = AsyncResult(task_id)
	result = {
		"task_id": task_id,
		"task_status": task_result.status,
		"task_result": task_result.result
	}
	return jsonify(result), 200
def run_spider_crawl(spider,config_crawl,addressPage):
	print('config_crawl_crophet',config_crawl)
	setting = get_project_settings()
	setting.update({
		"ITEM_PIPELINES":{MongoPipeline: 400}
	})
	setting.update({
		"MONGO_URI": DB_URL
	})
	setting.update({
		"MONGO_DB": DB_Name
	})
	if config_crawl['timeOutCrawl'] > 0:
		setting.update({
		"DOWNLOAD_TIMEOUT": config_crawl['timeOutCrawl']
		})
	if config_crawl['timeDelayCrawl'] > 0:
		setting.update({
		"DOWNLOAD_DELAY": config_crawl['timeDelayCrawl']
		})
	if config_crawl['numberRetryCrawl'] > 0:
		setting.update({
		"RETRY_TIMES": config_crawl['numberRetryCrawl']
		})
	if config_crawl['userAgent'] != '':
		setting.update({
		"USER_AGENT": config_crawl['userAgent']
		})
	setting.update({
	"DOWNLOAD_TIMEOUT": config_crawl['modeRobotsParser']
	})
	print('START CRAWL')
	if config_crawl['useSplash']:
		print('Config Splash')
		setting.update({
			"SPLASH_URL": SPLASH_URL,
			"SPIDER_MIDDLEWARES": {
				'scrapy_splash.SplashDeduplicateArgsMiddleware': 100
			},
			"COOKIES_ENABLED":True,
			"DUPEFILTER_CLASS": 'scrapy_splash.SplashAwareDupeFilter',
			"HTTPCACHE_STORAGE": 'scrapy_splash.SplashAwareFSCacheStorage',
			"DOWNLOADER_MIDDLEWARES": {
				'scrapy_splash.SplashCookiesMiddleware': 723,
				'scrapy_splash.SplashMiddleware': 725,
				'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
			}
		})
	# else:
	# 	setting.update({
	# 		"SPIDER_MIDDLEWARES": {},
	# 		"DUPEFILTER_CLASS": 'scrapy.dupefilters.RFPDupeFilter',
	# 		"HTTPCACHE_STORAGE": 'scrapy.extensions.httpcache.FilesystemCacheStorage',
	# 		"DOWNLOADER_MIDDLEWARES": {
	# 			"vn_news.middlewares.VnNewsSpiderMiddleware": 543
	# 		}
	# 	})
	print('setting',setting.copy_to_dict())
	crawl_runner = CrawlerRunner(setting)
	eventual = crawl_runner.crawl(
		spider,config = config_crawl)
	
	return eventual 

@celery.task(name='crawl_page')
def crawl_new(namePage):
	crawler_info = db.crawlers.find_one({'addressPage': namePage})
	crawler_config = db.configcrawlers.find_one({'namePage': namePage})
	db.crawlers.update_one({"addressPage": namePage},{"$set": {"statusPageCrawl": "Pending"}})
	type_crawler = crawler_config["type"]
	last_date = crawler_info["dateLastCrawler"]
	title_query = crawler_config["title_query"]
	timeCreatePostOrigin_query = crawler_config["timeCreatePostOrigin_query"]
	author_query = crawler_config["author_query"]
	content_query = crawler_config["content_query"]
	summary_query = crawler_config["summary_query"]
	content_html_query = crawler_config["content_html_query"]
	summary_html_query = crawler_config["summary_html_query"]

	timeOutCrawl = crawler_config["timeOutCrawl"]
	timeDelayCrawl = crawler_config["timeDelayCrawl"]
	numberRetryCrawl = crawler_config["numberRetryCrawl"]
	userAgent = crawler_config["userAgent"]
	modeRobotsParser = crawler_config["modeRobotsParser"]
	useSplash = crawler_config["useSplash"]
	print('type_crawler',type_crawler)
	if type_crawler == 'origin':
		config_crawl = {
			"namePage":namePage,
			"last_date":last_date,
			"article_url_query": crawler_config["article_url_query"],
			"title_query": title_query,
			"timeCreatePostOrigin_query": timeCreatePostOrigin_query,
			"author_query": author_query,
			"content_query": content_query,
			"summary_query": summary_query,
			"content_html_query":content_html_query,
			"summary_html_query":summary_html_query,
			"type_crawler":type_crawler,
			'timeOutCrawl': timeOutCrawl,
			'timeDelayCrawl': timeDelayCrawl,
			'numberRetryCrawl': numberRetryCrawl,
			'userAgent': userAgent,
			'modeRobotsParser': modeRobotsParser,
			'useSplash':useSplash
		}
	else:
		config_crawl = {
			"last_date":last_date,
			"title_query": title_query,
			"timeCreatePostOrigin_query": timeCreatePostOrigin_query,
			"author_query": author_query,
			"content_query": content_query,
			"summary_query": summary_query,
			"content_html_query":content_html_query,
			"summary_html_query":summary_html_query,
			"start_urls":crawler_config["start_urls"],
			"correct_rules":crawler_config["correct_url_contain"],
			"incorrect_rules":crawler_config["incorrect_url_contain"],
			"namePage":namePage,
			"origin_domain":crawler_config["urlPage"],
			"type_crawler":type_crawler,
			'timeOutCrawl': timeOutCrawl,
			'timeDelayCrawl': timeDelayCrawl,
			'numberRetryCrawl': numberRetryCrawl,
			'userAgent': userAgent,
			'modeRobotsParser': modeRobotsParser,
			'useSplash':useSplash

		}
	
	try:
	# Run the crawl
		if namePage == 'cafef':
			run_spider_crawl(CafefDuocSpider,config_crawl,'cafef')
		elif namePage == 'cafebiz':
			run_spider_crawl(CafebizDuocSpider,config_crawl,'cafebiz')
		elif namePage == 'nguoiduatin':
			run_spider_crawl(NguoiDuaTinSpider,config_crawl,'nguoiduatin')
		elif namePage == 'thanhnien':
			run_spider_crawl(ThanhNienSpider,config_crawl,'thanhnien')
		elif namePage == 'vnexpress':
			run_spider_crawl(VnexpressSpider,config_crawl,'vnexpress')
		elif namePage == 'vnpca':
			run_spider_crawl(VnpcaSpider,config_crawl,'vnpca')
		else:
			if useSplash:
				run_spider_crawl(CustomSplashSpider,config_crawl,'customSplash')
			else:
				run_spider_crawl(CustomSpider,config_crawl,'custom')
	except Exception as e:
		msg = f"Error occurred during crawl: {str(traceback.format_exc())}"
		db.crawlers.update_one({"addressPage": namePage},{"$set": {"statusPageCrawl": "Error"}})
		save_logger_crawler(namePage,"Error",msg)
		return str(msg)
def configure_scheduler(namePage):
	crawler_info = config_crawlers_collection.find_one({'namePage': namePage})
	schedule = crawler_info['timeSchedule']  # Replace this with your schedule data
	print('schedule',schedule)
	for entry in schedule:
		for hour in entry['hour']:
			days_of_week = int(entry['day'])
			scheduler.add_job(crawl_new, 'cron', id=f'{namePage}_{entry["day"]}_{hour}', args=[namePage], day_of_week=days_of_week, hour=hour)
def remove_scheduler(namePage):
	jobs_to_remove = [job for job in scheduler.get_jobs() if namePage in job.id]
	for job in jobs_to_remove:
		scheduler.remove_job(job.id)

def save_logger_crawler(page,action,message):
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
		'message': string_message,
		'timelog': time_crawl_page
	}
	log_crawlers_collection.insert_one(log_entry)
