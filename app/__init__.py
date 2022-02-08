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

#In Development use a local SQL Lite DB
if os.environ.get("ENV") != "prod":
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

#In Production, connect to an AWS MySQL DB through an SSH Tunnel
else:
    tunnel = sshtunnel.SSHTunnelForwarder(
        (os.environ["SSH_SERVER"]), 
        ssh_username=os.environ["SSH_USER"], 
        ssh_pkey=os.environ["SSH_KEY"], 
        remote_bind_address=(os.environ["PROD_DB_HOST"], 3306)
    )
    tunnel.start()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@127.0.0.1:{}/ultimate_hitboxes'.format(os.environ["PROD_DB_USER"],os.environ["PROD_DB_PW"], tunnel.local_bind_port)

#Set up access to the database through SQL Alchemy
db = SQLAlchemy(app)

#Establish access to the S3 Bucket
try:
    client = boto3.client('s3', aws_access_key_id=os.environ["ACCESSKEYID"], aws_secret_access_key=os.environ["SECRETACCESSKEY"])
except KeyError:
    client = None

from app import routes