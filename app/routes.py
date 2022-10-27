import os

from flask import request

from app import app, client, db
from app.models import Character,Move, Log, User,CharacterPopularity
from app.get_images import get_images
from sqlalchemy import func
from app.populate import startup

def checkIncludesExcludes(includeExclude):
    if not includeExclude:
        return includeExclude
    else:
        return includeExclude.split(",")


@app.route('/api/character/all', methods=["GET"])
def characterData():

    response = {}
    if("include" in request.args and "exclude" in request.args):
        return "Can not use both 'include' and 'exclude' options", 400

    print("here")
    user=User.query.filter(User.apikey==request.headers.get('API-Key')).first()
    if user:
        objs = db.session.query(Character,CharacterPopularity).join(CharacterPopularity).filter(CharacterPopularity.username==user.username).all()
        for obj in objs:
            response[obj.Character.value] = obj.Character.serializeAll(checkIncludesExcludes(request.args.get("include")), checkIncludesExcludes(request.args.get("exclude")))
            response[obj.Character.value]["count"] = obj.CharacterPopularity.count
    else:
        
        for character in Character.query.all():
            response[character.value] = character.serializeAll(checkIncludesExcludes(request.args.get("include")), checkIncludesExcludes(request.args.get("exclude")))

    writeLog(request, '/api/character/all', None)
    return response

@app.route('/api/character/<string:character>', methods=["GET"])
def getCharacter(character):
    dbChar = Character.query.get(character.lower())
    try:
        if request.args.get("extra"):
            data=dbChar.serialize_extra_move_data()
        else:
            data=dbChar.serialize(checkIncludesExcludes(request.args.get("include")), checkIncludesExcludes(request.args.get("exclude")))
    except AttributeError:
        return f'{character} is not a valid character', 404
    if "ERROR_MESSAGE" in data:
        return data["ERROR_MESSAGE"], data["ERROR_CODE"]

    writeLog(request, '/api/character/', character)

    if request.headers.get('API-Key'):
        updatePopularity(request, character)

    return data

@app.route('/api/move/<string:move>', methods=["GET"])
def getMove(move):

    try:
        moveData=Move.query.filter(func.lower(Move.value) == func.lower(move)).first().serialize()
    except AttributeError:
        return f'{move} is not a valid move', 404

    if "include" in request.args and "exclude" in request.args:
        return "Can not use both 'include' and 'exclude' options", 400

    if request.args.get("images"):
        moveData["imgData"] = get_images(client, move, request)
    writeLog(request, '/api/move/', move)
    return moveData



@app.route('/api/images/<string:move>', methods=["GET"])
def getImages(move):

    if client == None:
        return "Error requesting AWS S3 Credentials", 400

    obj = get_images(client, move, request)
    writeLog(request, '/api/images/', move)
    return obj

def writeLog(request, endpoint, resource):

    user=User.query.filter(User.apikey==request.headers.get('API-Key')).first()

    if not request.remote_addr:
        return

    if(not user):
        log = Log(ip=request.remote_addr, endpoint=endpoint, resource=resource)
    else:
        log = Log(ip=request.remote_addr, endpoint=endpoint, resource=resource, username=user.username)
    
    writeToDB([log])

def updatePopularity(request, resource):

    #Figure out the User
    user=User.query.filter(User.apikey==request.headers.get('API-Key')).first()

    #This user does not exist, return
    if not user:
        return

    #Find the entry to update
    entry = db.session.query(CharacterPopularity).filter(CharacterPopularity.value==resource, CharacterPopularity.username==user.username).first()

    #Entry exists, increment count by one
    if entry:
        entry.count += 1

    #Entry does not exist, add an entry for that user/resource combination, set count to 1
    else:
        log = CharacterPopularity(value=resource, username=user.username, count=1)
        db.session.add(log)

    #Commit changes to Database
    db.session.commit()

def writeToDB(SQL):
    for statement in SQL:
        db.session.add(statement)
    db.session.commit()

@app.route('/api/db', methods=["GET"])
def getDb():
    if os.environ.get("FLASK_ENV") == "production":
        return "Access Denied", 403
    startup()
    return {}