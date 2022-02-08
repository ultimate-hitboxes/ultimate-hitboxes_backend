from app import db
import json
from app.models import Character, Move, Hitbox,Grab,Throw,Hurtbox,CharacterLog,MoveLog, Log, User;
import random

db.reflect()
db.drop_all()

db.create_all()

dataFile=open('./data/characterData.json')
data = json.load(dataFile)

for character in data["characters"]:
    charSQL = Character(value=character["value"], name=character["name"],series=character["series"],number=character["number"],version=character["version"],id=character["id"],completed=character["completed"])
    db.session.add(charSQL)

    characterDataFile = open('./data/' + character["number"] + "_" + character["value"] + ".json")
    characterData = json.load(characterDataFile)

    for i in range(0, random.randint(0,1000)):
        characterLogSQL=CharacterLog(IP="localhost",CharacterName=character["value"],URL="/api/character/"+character["value"])
        #db.session.add(characterLogSQL)


    for move in characterData["moves"]:
        for i in range(0, random.randint(0,100)):
            moveLogSQL=MoveLog(IP="localhost", MoveName=move["value"], URL="/api/move/"+move["value"])
            #db.session.add(moveLogSQL)

        if "complete" not in move:
            complete = True
        else:
            complete = False
        moveSQL = Move(value=move["value"], name=move["name"], character=character["value"],faf=move["faf"],frames=move["frames"],notes=move.get("notes"), completed=complete)
        db.session.add(moveSQL)


        if "hitboxes" in move:
            for i in range(0, len(move["hitboxes"])):
                if i<10:
                    index = "00"+str(i)
                elif i<100:
                    index = "0"+str(i)
                else:
                    index=str(i)

                hitbox = move["hitboxes"][i]
                notes=hitbox["notes"]
                color=hitbox["color"]
                frames={"frames": hitbox["frames"]}

                hitbox.pop("notes")
                hitbox.pop("color")
                hitbox.pop("frames")

                hitboxSQL=Hitbox(value=move["value"]+"-hitbox"+index,move=move["value"],color=color,notes=notes,frames=frames,data=hitbox)
                db.session.add(hitboxSQL)
        if "grabs" in move:
            for i in range(0, len(move["grabs"])):
                if i<10:
                    index = "00"+str(i)
                elif i<100:
                    index = "0"+str(i)
                else:
                    index=str(i)

                grab = move["grabs"][i]
                notes=grab["notes"]
                color=grab["color"]
                frames={"frames": grab["frames"]}

                grab.pop("notes")
                grab.pop("color")
                grab.pop("frames")

                grabSQL=Grab(value=move["value"]+"-grab"+index,move=move["value"],color=color,notes=notes,frames=frames,data=grab)
                db.session.add(grabSQL)
        if "throws" in move:
            for i in range(0, len(move["throws"])):
                if i<10:
                    index = "00"+str(i)
                elif i<100:
                    index = "0"+str(i)
                else:
                    index=str(i)

                throw = move["throws"][i]
                notes=throw["notes"]
                color=throw["color"]
                frames={"frames": throw["frames"]}

                throw.pop("notes")
                throw.pop("color")
                throw.pop("frames")

                throwSQL=Throw(value=move["value"]+"-throw"+index,move=move["value"],color=color,notes=notes,frames=frames,data=throw)
                db.session.add(throwSQL)

        if "hurtboxes" in move:
            for i in range(0, len(move["hurtboxes"])):
                if i<10:
                    index = "00"+str(i)
                elif i<100:
                    index = "0"+str(i)
                else:
                    index=str(i)

                hurtbox = move["hurtboxes"][i]

                hurtboxSQL=Hurtbox(value=move["value"]+"-hurtbox"+index,move=move["value"],color=hurtbox["color"],notes=notes,bone=hurtbox["bone"],frames={"frames": hurtbox["frames"]},hp=hurtbox["hp"],type=hurtbox["type"])
                db.session.add(hurtboxSQL)

#commit changes
db.session.commit()
