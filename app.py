from flask import Flask
from flask_cors import CORS
from crawler import crawler
import os
app = Flask(__name__)
CORS(app)
app.config["CELERY_BROKER_URL"] = os.environ.get("CELERY_BROKER_URL")
app.config["CELERY_RESULT_BACKEND"] =os.environ.get("CELERY_RESULT_BACKEND")
from celery import Celery
celery = Celery("app", broker=os.environ.get("CELERY_BROKER_URL"),backend=os.environ.get("CELERY_RESULT_BACKEND"))
celery.conf.update(app.config)
app.register_blueprint(crawler)
if __name__ == '__main__':    
	app.run(host="0.0.0.0",port=5000,debug=True)