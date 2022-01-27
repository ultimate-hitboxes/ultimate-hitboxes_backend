from flask import Flask, redirect, url_for, request, render_template, json

from app import app, client, db
from app.models import Character,Move,CharacterLog,MoveLog
from app.get_images import get_images

def checkIncludesExcludes(includeExclude):
    if not includeExclude:
        return includeExclude
    else:
        return includeExclude.split(",")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/character/all', methods=["GET"])
def characterData():

    if("include" in request.args and "exclude" in request.args):
        return "Can not use both 'include' and 'exclude' options", 400

    characters = {"characterList": []}
    for character in Character.query.all():
        characters[character.value] = character.serialize(checkIncludesExcludes(request.args.get("include")), checkIncludesExcludes(request.args.get("exclude")))
        characters["characterList"].append(character.value)
    return characters

@app.route('/api/character/<string:character>', methods=["GET"])
def getCharacter(character):
    dbChar = Character.query.get(character)
    try:
        data= dbChar.serialize(checkIncludesExcludes(request.args.get("include")), checkIncludesExcludes(request.args.get("exclude")))
    except AttributeError:
        return f'{character} is not a valid character', 404
    if "ERROR_MESSAGE" in data:
        return data["ERROR_MESSAGE"], data["ERROR_CODE"]

    writeCharacterLog(request, Character.query.get(character))
    return data

@app.route('/api/move/<string:character>/<string:move>', methods=["GET"])
@app.route('/api/move/<string:move>', methods=["GET"])
def getMove(move):

    moveObj = Move.query.get(move)
    if not moveObj:
        return f'{move} is not a valid move', 404
    if "include" in request.args and "exclude" in request.args:
        return "Can not use both 'include' and 'exclude' options", 400

    writeMoveLog(request, moveObj)
    return moveObj.serialize()

@app.route('/api/images/<string:move>', methods=["GET"])
def getImages(move):

    if client == None:
        return "Error requesting AWS S3 Credentials", 400

    obj = get_images(client, move, request)
    return obj


def writeCharacterLog(request, character):
    characterLogSQL=CharacterLog(IP=request.remote_addr, CharacterName=character.value,URL=request.url)
    writeToDB(characterLogSQL)

def writeMoveLog(request, move):
    moveLogSQL=MoveLog(IP=request.remote_addr, MoveName=move.value,URL=request.url)
    writeToDB(moveLogSQL)

def writeToDB(SQL):
    db.session.add(SQL)
    db.session.commit()