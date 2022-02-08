from app import db
import datetime
from sqlalchemy import func

def includeExclude(fields, data, includes,excludes):
    if includes and excludes:
        return {"ERROR_MESSAGE": "Can not use both 'include' and 'exclude' options", "ERROR_CODE": 400}

    if includes:
        for field in fields:
            if field not in includes:
                data.pop(field)
    elif excludes:
        for field in fields:
            if field in excludes:
                data.pop(field)

    return data

class Character(db.Model):
    value=db.Column(db.String(80), primary_key=True)
    name=db.Column(db.String(80))
    series=db.Column(db.String(80))
    number = db.Column(db.String(80))
    version = db.Column(db.String(80))
    id = db.Column(db.Integer)
    completed = db.Column(db.Boolean)
    moves = db.relationship('Move', backref="Character", lazy=True)
    logs=db.relationship('CharacterLog', backref="Character",lazy=True)

    def __repr__(self):
        return self.name

    def serialize(self, includes, excludes):

        fields = ["value", "name", "series", "number", "version", "id", "completed", "moves"]
        
        moves = []
        for move in self.moves:
            moves.append(move.getValue())

        data = { 
            "value": self.value,
            "name": self.name,
            "series": self.series,
            "number": self.number,
            "version": self.version,
            "id": self.id,
            "completed": self.completed,
            "moves": moves
        }
        
        return includeExclude(fields,data,includes,excludes)
    def serialize_extra_move_data(self):
        moves = []
        for move in self.moves:
            moveObj = {"name": move.getName(), "value": move.getValue(), "completed": move.getCompleted()}
            moves.append(moveObj)

        data = { 
            "value": self.value,
            "name": self.name,
            "series": self.series,
            "number": self.number,
            "version": self.version,
            "id": self.id,
            "completed": self.completed,
            "moves": moves
        }
        
        return data


class Move(db.Model):
    value=db.Column(db.String(80), primary_key=True)
    name=db.Column(db.String(80))
    character=db.Column(db.String(80), db.ForeignKey('character.value'))
    frames=db.Column(db.Integer)
    faf=db.Column(db.Integer)
    notes=db.Column(db.String(200))
    completed=db.Column(db.Boolean)
    hitboxes=db.relationship('Hitbox', backref="Move", lazy=True)
    hurtboxes=db.relationship('Hurtbox', backref="Move", lazy=True)
    grabs=db.relationship('Grab', backref="Move", lazy=True)
    throws=db.relationship('Throw', backref="Move", lazy=True)
    logs=db.relationship('MoveLog', backref="Move",lazy=True)

    #def __repr__(self):
    #    return self.name

    def serialize(self):

        moveData = { 
            "value": self.value,
            "name": self.name,
            "character": self.character,
            "frames": self.frames,
            "faf": self.faf,
            "notes": self.notes,
            "completed": self.completed,
            "hitboxes": [hitbox.serialize() for hitbox in self.hitboxes],
            "hurtboxes": [hurtbox.serialize() for hurtbox in self.hurtboxes],
            "grabs": [grab.serialize() for grab in self.grabs],
            "throws": [throw.serialize() for throw in self.throws]
        }

        dataTypes = ["hitboxes", "hurtboxes", "grabs", "throws"]
        for type in dataTypes:
            if len(moveData[type]) == 0:
                moveData.pop(type, None)
        return moveData
        
    def getValue(self):
        return self.value
    def getName(self):
        return self.name
    def getCompleted(self):
        return self.completed

class Hitbox(db.Model):
    value=db.Column(db.String(80), primary_key=True)
    move=db.Column(db.String(80), db.ForeignKey('move.value'))
    color=db.Column(db.String(80))
    notes=db.Column(db.String(200))
    data=db.Column(db.JSON)
    frames=db.Column(db.JSON)

    def serialize(self):
        return {
            "value": self.value,
            "move": self.move,
            "data": self.data,
            "frames": self.frames["frames"],
            "color": self.color,
            "notes": self.notes
        }

class Grab(db.Model):
    value=db.Column(db.String(80), primary_key=True)
    move=db.Column(db.String(80), db.ForeignKey('move.value'))
    color=db.Column(db.String(80))
    notes=db.Column(db.String(200))
    data=db.Column(db.JSON)
    frames=db.Column(db.JSON)

    def serialize(self):
        return {
            "value": self.value,
            "move": self.move,
            "data": self.data,
            "frames": self.frames["frames"],
            "color": self.color,
            "notes": self.notes
        }

class Throw(db.Model):
    value=db.Column(db.String(80), primary_key=True)
    move=db.Column(db.String(80), db.ForeignKey('move.value'))
    color=db.Column(db.String(80))
    notes=db.Column(db.String(200))
    data=db.Column(db.JSON)
    frames=db.Column(db.JSON)

    def serialize(self):
        return {
            "value": self.value,
            "move": self.move,
            "data": self.data,
            "frames": self.frames["frames"],
            "color": self.color,
            "notes": self.notes
        }

class Hurtbox(db.Model):
    value=db.Column(db.String(80), primary_key=True)
    move=db.Column(db.String(80), db.ForeignKey('move.value'))
    color=db.Column(db.String(80))
    notes=db.Column(db.String(200))
    bone=db.Column(db.String(200))
    frames=db.Column(db.JSON)
    hp=db.Column(db.String(80))
    type=db.Column(db.String(80))

    def serialize(self):
        return {
            "value": self.value,
            "move": self.move,
            "bone": self.bone,
            "hp": self.hp,
            "type": self.type,
            "frames": self.frames["frames"],
            "color": self.color,
            "notes": self.notes
        }

class CharacterLog(db.Model):
    ID = db.Column(db.Integer, primary_key=True,autoincrement=True)
    DateTime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    IP = db.Column(db.String(80))
    CharacterName = db.Column(db.String(80), db.ForeignKey('character.value'))
    URL = db.Column(db.String(80))

class MoveLog(db.Model):
    ID = db.Column(db.Integer, primary_key=True,autoincrement=True)
    DateTime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    IP = db.Column(db.String(80))
    MoveName = db.Column(db.String(80), db.ForeignKey('move.value'))
    URL = db.Column(db.String(80))



class User(db.Model):
    id = db.Column(db.Integer,autoincrement=True, primary_key=True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(80), unique=True)
    hashed_password = db.Column(db.String(256))
    apikey = db.Column(db.String(20), unique=True)
    usertype = db.Column(db.String(20))
    active = db.Column(db.Boolean, default=True)
    authenticated=db.Column(db.Boolean, default=False)
    logs=db.relationship('Log', backref="user",lazy=True)

    def __repr__(self):
        return self.username

    def verify_password(self, password):
        return sha256_crypt.verify(password, self.hashed_password)
    
    def is_active(self):
        return self.active

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.authenticated

    def get_user_by_username_or_email(value):
        return User.query.filter((func.lower(User.email) == value.lower()) | (func.lower(User.username) == value.lower())).first()
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    datetime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    ip = db.Column(db.String(80))
    url = db.Column(db.String(80))
    username = db.Column(db.String(80), db.ForeignKey('user.username'))


class Confirmation(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    confirmation_code=db.Column(db.String(16))
    email = db.Column(db.String(80))
    sent_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    confirmed_on = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)