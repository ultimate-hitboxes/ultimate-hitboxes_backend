from flask import Flask, redirect, url_for, request, render_template, json
from app import app
from app.models import Character,Move,Hitbox,Hurtbox,Grab,Throw

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
    print(Move.query.get(move))
    return Move.query.get(move).serialize()

@app.route('/api/images/<string:character>/<string:move>', methods=["GET"])
def getImages(character, move):

    if client == None:
        return {"Error": "Error requesting S3 Credentials"}

    data = getCharacterFile(character)

    myMove = None
    for dataMove in data["moves"]:
        if dataMove["value"] == move:
            myMove = dataMove
            break

    if myMove == None:
        return {"Error": "Invalid Move"}

    if "frame" in request.args:
        resp = client.generate_presigned_url('get_object', Params={'Bucket': 'ultimate-hitboxes', 'Key': "frames/"+character+"/"+move+"/"+request.args["frame"]+".png"})
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
        arr.append(client.generate_presigned_url('get_object', Params={'Bucket': 'ultimate-hitboxes', 'Key': "frames/"+character+"/"+move+"/"+str(i)+".png"}))
    urls = {"urls": arr, "imgCount": len(arr)}
    return urls