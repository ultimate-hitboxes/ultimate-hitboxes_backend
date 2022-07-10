from app.models import Character,Move

def get_images(client, move, request):

    #query = Move.query.join(Character, Move.character==Character.value).add_columns(Character.number, Move.faf, Move.value, Move.character).filter(Move.value==move).all()
    #print(query.serialize())

    #Get the data for the move
    myMove = Move.query.get(move)

    if myMove == None:
        return f'{move} is not a valid move', 404

    #Get the data for the character
    myCharacter = Character.query.get(myMove.character)

    ids = ""
    if request.args.get("ids") and request.args.get("ids").lower() == "true" and myMove.has_ids:
        ids="ids/"

    #If Requesting one frame
    if "frame" in request.args:
        resp = client.generate_presigned_url('get_object', Params={'Bucket': 'ultimate-hitboxes', 'Key': f'frames/{ids}{myCharacter.number}_{myMove.character}/{move}/{request.args["frame"]}.png'})
        return resp

    start = 1
    end = int(myMove.faf)

    if "startFrame" in request.args:
        start = int(request.args["startFrame"])
    if "endFrame" in request.args:
        end = int(request.args["endFrame"])

    if start > end:
        return f'startFrame {start} cannot be greater than endFrame {end}', 400
    obj={"urls": [],"frames": [], }
    for i in range(max(1,start), min(int(myMove.faf)+1, end+1)):
        obj["frames"].append(i)
        obj["urls"].append(client.generate_presigned_url('get_object', Params={'Bucket': 'ultimate-hitboxes', 'Key': f'frames/{ids}{myCharacter.number}_{myMove.character}/{move}/{str(i)}.png'}))
    obj["imgCount"] = len(obj["frames"])

    return obj