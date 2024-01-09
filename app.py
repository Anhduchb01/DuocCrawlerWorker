from flask import Flask
from flask_cors import CORS

import os
from flask_oidc import OpenIDConnect
app = Flask(__name__)
CORS(app)

app.config.update({
    'SECRET_KEY': 'rukU9AevuCZbm9A9wQp1VGesYCmMsIbW',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': 'fcdp',
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post',
    'OIDC_TOKEN_TYPE_HINT': 'access_token'
})

oidc = OpenIDConnect()
oidc.init_app(app)

app.config["CELERY_BROKER_URL"] = os.environ.get("CELERY_BROKER_URL")
app.config["CELERY_RESULT_BACKEND"] =os.environ.get("CELERY_RESULT_BACKEND")
from celery import Celery
celery = Celery("app", broker=os.environ.get("CELERY_BROKER_URL"),backend=os.environ.get("CELERY_RESULT_BACKEND"))
celery.conf.update(app.config)

if __name__ == '__main__':    
	from crawler import crawler_blueprint
	app.register_blueprint(crawler_blueprint)
	app.run(host="0.0.0.0",port=5000,debug=False)