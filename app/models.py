from app import db

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

    def serialize(self):
        return { 
            "value": self.value,
            "name": self.name,
            "series": self.series,
            "number": self.number,
            "version": self.version,
            "id": self.id,
            "completed": self.completed
        }


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

    def serialize(self):
        return { 
            "value": self.value,
            "name": self.name,
            "character": self.character,
            "frames": self.frames,
            "faf": self.faf,
            "notes": self.notes
        }

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