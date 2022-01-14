from flask import Flask, redirect, url_for, request, render_template, json

from app import app, client, db
from app.models import Character,Move,Hitbox,Hurtbox,Grab,Throw,CharacterLog

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
    characters = {"characterList": []}
    for character in Character.query.all():
        characters[character.value] = character.serialize(checkIncludesExcludes(request.args.get("include")), checkIncludesExcludes(request.args.get("exclude")))
        characters["characterList"].append(character.value)
    return characters

@app.route('/api/character/<string:character>', methods=["GET"])
def getCharacter(character):
    data= Character.query.get(character).serialize(checkIncludesExcludes(request.args.get("include")), checkIncludesExcludes(request.args.get("exclude")))
    if "ERROR_MESSAGE" in data:
        return data["ERROR_MESSAGE"], data["ERROR_CODE"]
    return data

@app.route('/api/move/<string:move>', methods=["GET"])
def getMove(move):
    return Move.query.get(move).serialize()

@app.route('/api/images/<string:move>', methods=["GET"])
def getImages(move):

    if client == None:
        return "Error requesting AWS S3 Credentials", 400

    myMove = Move.query.get(move).serialize()
    myCharacter = Character.query.get(myMove["character"]).serialize()

    if myMove == None:
        return {"Error": "Invalid Move"}

    if "frame" in request.args:
        resp = client.generate_presigned_url('get_object', Params={'Bucket': 'ultimate-hitboxes', 'Key': "frames/"+myCharacter["number"]+"_"+myMove["character"]+"/"+move+"/"+request.args["frame"]+".png"})
        return resp
    print(request.args)

    start = 1
    end = int(myMove["faf"])

    if "startFrame" in request.args:
        start = int(request.args["startFrame"])
    if "endFrame" in request.args:
        end = int(request.args["endFrame"])
    arr = []
    for i in range(max(1,start), min(int(myMove["faf"])+1, end+1)):
        arr.append(client.generate_presigned_url('get_object', Params={'Bucket': 'ultimate-hitboxes', 'Key': "frames/"+myCharacter["number"]+"_"+myMove["character"]+"/"+move+"/"+str(i)+".png"}))
    urls = {"urls": arr, "imgCount": len(arr)}
    return urls

@app.route('/api/logs/character/<string:character>', methods=["POST"])
def writeCharacterLog(character):
    characterLogSQL=CharacterLog(IP=request.remote_addr,CharacterNum="", CharacterName="",URL="")
    db.session.add(characterLogSQL)
    db.session.commit()
    return {"Message": "Success"}