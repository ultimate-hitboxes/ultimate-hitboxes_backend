from flask import Flask, redirect, url_for, request, render_template, json

from app import app, client, db
from app.models import Character,Move,CharacterLog,MoveLog

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
    return Move.query.get(move).serialize()

@app.route('/api/images/<string:move>', methods=["GET"])
def getImages(move):

    if client == None:
        return "Error requesting AWS S3 Credentials", 400

    myMove = Move.query.get(move).serialize()
    myCharacter = Character.query.get(myMove["character"]).serialize(None, None)

    if myMove == None:
        return {"Error": "Invalid Move"}

    if "frame" in request.args:
        resp = client.generate_presigned_url('get_object', Params={'Bucket': 'ultimate-hitboxes', 'Key': "frames/"+myCharacter["number"]+"_"+myMove["character"]+"/"+move+"/"+request.args["frame"]+".png"})
        return resp

    start = 1
    end = int(myMove["faf"])

    if "startFrame" in request.args:
        start = int(request.args["startFrame"])
    if "endFrame" in request.args:
        end = int(request.args["endFrame"])

    if start > end:
        return f'startFrame {start} cannot be greater than endFrame {end}', 400
    obj={"urls": [],"frames": [], }
    for i in range(max(1,start), min(int(myMove["faf"])+1, end+1)):
        obj["frames"].append(i)
        obj["urls"].append(client.generate_presigned_url('get_object', Params={'Bucket': 'ultimate-hitboxes', 'Key': f'frames/{myCharacter["number"]}_{myMove["character"]}/{move}/{str(i)}.png'}))
    obj["imgCount"] = len(obj["frames"])
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