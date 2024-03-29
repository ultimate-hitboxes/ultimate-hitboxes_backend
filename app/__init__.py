from flask import Flask
from flask_cors import CORS
import boto3
import os
from flask_sqlalchemy import SQLAlchemy
import sshtunnel
from dotenv import load_dotenv

#Create Flask App
app = Flask(__name__)

#load .env environment variables
load_dotenv()

#Prevent CORS Errors
CORS(app)

#Set the Secret Key
app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]

tunnel = sshtunnel.SSHTunnelForwarder(
        (os.environ["SSH_SERVER"]), 
        ssh_username=os.environ["SSH_USER"], 
        ssh_pkey=os.environ["SSH_KEY"], 
        remote_bind_address=(os.environ["PROD_DB_HOST"], 3306)
    )
tunnel.start()

#In Development use a local SQL Lite DB
if os.environ.get("DB_ENV") != "production":
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.environ["DEV_DB_LOCATION"]}\\development.db'
    app.config['SQLALCHEMY_BINDS'] = {
        'db_old': f'mysql://{os.environ["PROD_DB_USER"]}:{os.environ["PROD_DB_PW"]}@127.0.0.1:{tunnel.local_bind_port}/ulthit_logs',
        'ultimate-hitboxes': f'sqlite:///{os.environ["DEV_DB_LOCATION"]}\\development.db',
        'logs': f'sqlite:///{os.environ["DEV_DB_LOCATION"]}\\logs.db',
    }

#In Production, connect to an AWS MySQL DB through an SSH Tunnel
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{os.environ["PROD_DB_USER"]}:{os.environ["PROD_DB_PW"]}@127.0.0.1:{tunnel.local_bind_port}/ultimate-hitboxes'
    app.config['SQLALCHEMY_BINDS'] = {
        'db_old': f'mysql://{os.environ["PROD_DB_USER"]}:{os.environ["PROD_DB_PW"]}@127.0.0.1:{tunnel.local_bind_port}/ulthit_logs',
        'ultimate-hitboxes':  f'mysql://{os.environ["PROD_DB_USER"]}:{os.environ["PROD_DB_PW"]}@127.0.0.1:{tunnel.local_bind_port}/ultimate-hitboxes',
        'logs': f'mysql://{os.environ["PROD_DB_USER"]}:{os.environ["PROD_DB_PW"]}@127.0.0.1:{tunnel.local_bind_port}/logs'
    }

#Set up access to the database through SQL Alchemy
db = SQLAlchemy(app)

#Establish access to the S3 Bucket
try:
    client = boto3.client('s3', aws_access_key_id=os.environ["ACCESSKEYID"], aws_secret_access_key=os.environ["SECRETACCESSKEY"])
except KeyError:
    client = None

from app import routes