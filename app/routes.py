from flask import Flask, redirect, url_for, request, render_template, json
from app import app, client, db
from app.models import Character,Move,Hitbox,Hurtbox,Grab,Throw,CharacterLog

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/characterData', methods=["GET"])
def characterData():
    return Character.query.all()

@app.route('/api/character/<string:character>', methods=["GET"])
def getCharacter(character):
    return Character.query.get(character).serialize()

@app.route('/api/move/<string:move>', methods=["GET"])
def getMove(move):
    return Move.query.get(move).serialize()

@app.route('/api/images/<string:move>', methods=["GET"])
def getImages(move):

    if client == None:
        return {"Error": "Error requesting S3 Credentials"}

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