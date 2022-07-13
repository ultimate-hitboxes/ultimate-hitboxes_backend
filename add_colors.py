import os
import json

id_colors = [
	"#FF0000",
	"#C759FF",
	"#FFC7C7",
	"#C7B400",
	"#FF7800",
	"#00FFD6",
	"#C700FF",
	"#604986",
	"#999999"
]

def characterFile(fullPath):
    file = open(fullPath)
    data = json.load(file)
    file.close()

    for move in data["moves"]:

        if move.get("hitboxes"):
            for hitbox in move.get("hitboxes"):
                if hitbox.get("id"):
                    try:
                        hitbox["id_color"] = id_colors[int(hitbox["id"])]
                    except:
                        print(move["value"])
                elif hitbox.get("color"):
                    print(move["value"])
                    hitbox["id_color"] = hitbox["color"]
    with open(fullPath, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


        

def main():
    directory = "data"

    for filename in os.listdir(directory):
        fullPath = os.path.join(directory, filename)

        if os.path.isfile(fullPath) and filename[0].isdigit():
            characterFile(fullPath)

main()