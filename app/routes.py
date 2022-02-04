from flask import Flask, redirect, url_for, request, render_template, json
from passlib.hash import sha256_crypt
from itsdangerous.url_safe import URLSafeTimedSerializer

import secrets
import math, os

import random

import smtplib, ssl

from app import app, client, db
from app.models import Character,Move,CharacterLog,MoveLog, Log, APIUser
from app.get_images import get_images

import smtplib, ssl

def send_confirmation_email(receiver_email):
    context = ssl.create_default_context()
    port=465
    sender_email="ultimatehitboxes@gmail.com"
    password=os.environ.get("EMAIL_PW")
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, "message")

def generate_key():
    generated_key = secrets.token_urlsafe(32)
    print(generated_key)
    return generated_key

def generate_confirmation_code():
    string = '0123456789'
    confirmation_code = ""
    length = len(string)
    for i in range(6) :
        confirmation_code += string[math.floor(random.random() * length)]
 
    return confirmation_code

def hash_password(password):
    return sha256_crypt.encrypt(password)

def checkIncludesExcludes(includeExclude):
    if not includeExclude:
        return includeExclude
    else:
        return includeExclude.split(",")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        print(request.form)
        userSQL=APIUser(username=request.form["username"], email=request.form["email"],hashed_password=sha256_crypt.encrypt(request.form["password"]), apikey=generate_key(), usertype="user")
        
        writeToDB(userSQL)
        send_confirmation_email(request.form["email"])
    return render_template('register.html')

@app.route('/confirmation', methods=["GET"])
def confirmation():
    code=generate_confirmation_code()
    return {"code":code}

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        dbUser = APIUser.query.get(request.form["username"])
        if sha256_crypt.verify(request.form["password"], dbUser.hashed_password):
            print("Verified")
        else:
            print("Invalid PW")
        return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/api/character/all', methods=["GET"])
def characterData():

    if("include" in request.args and "exclude" in request.args):
        return "Can not use both 'include' and 'exclude' options", 400

    characters = {}
    for character in Character.query.all():
        characters[character.value] = character.serialize(checkIncludesExcludes(request.args.get("include")), checkIncludesExcludes(request.args.get("exclude")))
        characters[character.value]["count"] = CharacterLog.query.filter(CharacterLog.CharacterName==character.value).count()

    writeLog(request)
    return characters

@app.route('/api/character/<string:character>', methods=["GET"])
def getCharacter(character):
    dbChar = Character.query.get(character)
    try:
        if request.args.get("extra"):
            data= dbChar.serialize_extra_move_data()
        else:
            data= dbChar.serialize(checkIncludesExcludes(request.args.get("include")), checkIncludesExcludes(request.args.get("exclude")))
    except AttributeError:
        return f'{character} is not a valid character', 404
    if "ERROR_MESSAGE" in data:
        return data["ERROR_MESSAGE"], data["ERROR_CODE"]

    writeLog(request)
    return data

@app.route('/api/move/<string:move>', methods=["GET"])
def getMove(move):

    moveObj = Move.query.get(move)
    if not moveObj:
        return f'{move} is not a valid move', 404
    if "include" in request.args and "exclude" in request.args:
        return "Can not use both 'include' and 'exclude' options", 400

    writeLog(request)
    return moveObj.serialize()



@app.route('/api/images/<string:move>', methods=["GET"])
def getImages(move):

    if client == None:
        return "Error requesting AWS S3 Credentials", 400

    obj = get_images(client, move, request)
    writeLog(request)
    return obj

def writeLog(request):
    user=APIUser.query.filter(APIUser.apikey==request.headers['API-Key']).first()

    if(not user):
        log = Log(ip=request.remote_addr, url=request.url)
    else:
        log = Log(ip=request.remote_addr, url=request.url, username=user.username)
    
    writeToDB(log)

def writeCharacterLog(request, character):
    
    characterLogSQL=CharacterLog(IP=request.remote_addr, CharacterName=character.value,URL=request.url)
    writeToDB(characterLogSQL)

def writeMoveLog(request, move):
    moveLogSQL=MoveLog(IP=request.remote_addr, MoveName=move.value,URL=request.url)
    writeToDB(moveLogSQL)

def writeToDB(SQL):
    db.session.add(SQL)
    db.session.commit()