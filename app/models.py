from app import db
import datetime

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

    def serialize(self):
        moves = []
        for move in self.moves:
            moves.append(move.getValue())
        return { 
            "value": self.value,
            "name": self.name,
            "series": self.series,
            "number": self.number,
            "version": self.version,
            "id": self.id,
            "completed": self.completed,
            "moves": moves
        }


class Move(db.Model):
    value=db.Column(db.String(80), primary_key=True)
    name=db.Column(db.String(80))
    character=db.Column(db.String(80), db.ForeignKey('character.value'))
    frames=db.Column(db.Integer)
    faf=db.Column(db.Integer)
    notes=db.Column(db.String(200))
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
            "hitboxes": [hitbox.serialize() for hitbox in self.hitboxes],
            "hurtboxes": [hurtbox.serialize() for hurtbox in self.hurtboxes],
            "grabs": [grab.serialize() for grab in self.grabs],
            "throws": [throw.serialize() for throw in self.throws]
        }

        return moveData
        
    def getValue(self):
        return self.value

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
            "frames": self.frames,
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
            "frames": self.frames,
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
            "frames": self.frames,
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
            "frames": self.frames,
            "color": self.color,
            "notes": self.notes
        }

class CharacterLog(db.Model):
    ID = db.Column(db.Integer, primary_key=True,autoincrement=True)
    DateTime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    IP = db.Column(db.String(80))
    CharacterNum = db.Column(db.String(80))
    CharacterName = db.Column(db.String(80), db.ForeignKey('character.value'))
    URL = db.Column(db.String(80))

class MoveLog(db.Model):
    ID = db.Column(db.Integer, primary_key=True,autoincrement=True)
    DateTime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    IP = db.Column(db.String(80))
    CharacterNum = db.Column(db.String(80))
    CharacterName = db.Column(db.String(80))
    MoveName = db.Column(db.String(80), db.ForeignKey('move.value'))
    URL = db.Column(db.String(80))