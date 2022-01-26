from asyncio.windows_events import NULL
from app import db
import json
from app.models import Character, Move, Hitbox,Grab,Throw,Hurtbox,CharacterLog,MoveLog;
import random


def evaluate(data):
    if data == "":
        return NULL
    if data == "true":
        return True
    elif data == "false":
        return False
    elif data == "lua_void":
        return NULL
    else:
        try:
            return int(data)
        except ValueError:
            try:
                return float(data)
            except ValueError:
                return data


dataFile=open('./data/characterData.json')
data = json.load(dataFile)

for character in data["characters"]:

    characterDataFile = open('./data/' + character["number"] + "_" + character["value"] + ".json")
    characterData = json.load(characterDataFile)

    for move in characterData["moves"]:

        if "hitboxes" in move:
            for hitbox in move["hitboxes"]:
                for field in hitbox:
                    if field != "color" and field != "frames" and field != "notes":
                        hitbox[field] = evaluate(hitbox[field])
        if "grabs" in move:
            for grab in move["grabs"]:
                for field in grab:
                    if field != "color" and field != "frames" and field != "notes":
                        grab[field] = evaluate(grab[field])
        if "throws" in move:
            for throw in move["throws"]:
                for field in throw:
                    if field != "color" and field != "frames" and field != "notes":
                        throw[field] = evaluate(throw[field])

        if "hurtboxes" in move:
            for hurtbox in move["hurtboxes"]:
                for field in hurtbox:
                    if field != "color" and field != "frames" and field != "notes":
                        hurtbox[field] = evaluate(hurtbox[field])

    with open('./newData/' + character["number"] + "_" + character["value"] + ".json", 'w') as outfile:
        json.dump(characterData, outfile, indent=4)

    print(character["value"])