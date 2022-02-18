from flask import Flask, flash, redirect, url_for, request, render_template

from app import app, client, db
from app.models import Character,Move,CharacterLog, Log, User, Confirmation
from app.get_images import get_images

def checkIncludesExcludes(includeExclude):
    if not includeExclude:
        return includeExclude
    else:
        return includeExclude.split(",")


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

    try:
        moveData = Move.query.get(move).serialize()
    except AttributeError:
        return f'{move} is not a valid move', 404
        
    if "include" in request.args and "exclude" in request.args:
        return "Can not use both 'include' and 'exclude' options", 400

    if request.args.get("images"):
        moveData["imgData"] = get_images(client, move, request)
    writeLog(request)
    return moveData



@app.route('/api/images/<string:move>', methods=["GET"])
def getImages(move):

    if client == None:
        return "Error requesting AWS S3 Credentials", 400

    obj = get_images(client, move, request)
    writeLog(request)
    return obj

def writeLog(request):
    print("here")
    user=User.query.filter(User.apikey==request.headers.get('API-Key')).first()

    if(not user):
        log = Log(ip=request.remote_addr, url=request.url)
    else:
        log = Log(ip=request.remote_addr, url=request.url, username=user.username)
    
    writeToDB([log])

def writeToDB(SQL):
    for statement in SQL:
        db.session.add(statement)
    db.session.commit()