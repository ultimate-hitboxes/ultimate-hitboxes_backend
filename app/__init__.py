from flask import Flask
import boto3
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

try:
    client = boto3.client('s3', aws_access_key_id=os.environ["ACCESSKEY"], aws_secret_access_key=os.environ["SECRETKEY"])
except KeyError:
    client = None

from app import routes