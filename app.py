from flask import Flask, redirect, url_for, request, render_template
import json
import boto3
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


try:
    client = boto3.client('s3', aws_access_key_id=os.environ["ACCESSKEY"], aws_secret_access_key=os.environ["SECRETKEY"])
except KeyError:
    client = None

class Character(db.Model):
    value=db.Column(db.String(80), primary_key=True)
    name=db.Column(db.String(80))
    series=db.Column(db.String(80))
    number = db.Column(db.String(80))
    version = db.Column(db.String(80))
    id = db.Column(db.Integer)
    completed = db.Column(db.Boolean)
    moves = db.relationship('Move', backref="Character", lazy=True)

    def __repr__(self):
        return self.name

class Move(db.Model):
    value=db.Column(db.String(80), primary_key=True)
    name=db.Column(db.String(80))
    character=db.Column(db.String(80), db.ForeignKey('character.value'))
    frames=db.Column(db.Integer)
    faf=db.Column(db.Integer)
    notes=db.Column(db.String(200))
    hitboxes=db.relationship('Hitbox', backref="Move", lazy=True)

    def __repr__(self):
        return self.name

class Hitbox(db.Model):
    value=db.Column(db.String(80), primary_key=True)
    move=db.Column(db.String(80), db.ForeignKey('move.value'))
    color=db.Column(db.String(80))
    notes=db.Column(db.String(200))
    data=db.Column(db.JSON)
    frames=db.Column(db.JSON)

class Grab(db.Model):
    value=db.Column(db.String(80), primary_key=True)
    move=db.Column(db.String(80), db.ForeignKey('move.value'))
    color=db.Column(db.String(80))
    notes=db.Column(db.String(200))
    data=db.Column(db.JSON)
    frames=db.Column(db.JSON)

class Throw(db.Model):
    value=db.Column(db.String(80), primary_key=True)
    move=db.Column(db.String(80), db.ForeignKey('move.value'))
    color=db.Column(db.String(80))
    notes=db.Column(db.String(200))
    data=db.Column(db.JSON)
    frames=db.Column(db.JSON)

class Hurtbox(db.Model):
    value=db.Column(db.String(80), primary_key=True)
    move=db.Column(db.String(80), db.ForeignKey('move.value'))
    color=db.Column(db.String(80))
    notes=db.Column(db.String(200))
    bone=db.Column(db.String(200))
    frames=db.Column(db.JSON)
    hp=db.Column(db.String(80))
    type=db.Column(db.String(80))

#db.create_all()
def getCharacterFile(character):
    
    try:
        dataFile=open('./data/'+character+'.json')
        data = json.load(dataFile)
        return data
    except FileNotFoundError:
        return {"Error": "Invalid Character"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/characterData', methods=["GET"])
def characterData():
    dataFile = open('./data/characterData.json')
    data = json.load(dataFile)
    return data

@app.route('/api/data/<string:character>', methods=["GET"])
def getCharacter(character):
    return getCharacterFile(character)

@app.route('/data/<string:character>/<string:move>', methods=["GET"])
def getMove(character, move):
    
    data = getCharacterFile(character)

    myMove = None
    for dataMove in data["moves"]:
        if dataMove["value"] == move:
            myMove = dataMove
            break

    return myMove

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
    
    


if __name__ == "__main__":
    if os.environ["Environment"] == "DEVELOPMENT":
        app.run(debug=True, port=5080)
    elif os.environ["Environment"] == "PRODUCTION":
        app.run(port=5443)
    else:
        print("No Environment set")
    