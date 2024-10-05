import json
import os
import random
import discord

JSON_PATH = "./dinner.json"
Dinner_Dict = {}
start_sign = "~"
CC_red = int(0xE74C3C)
CC_lightblue = int(0x53FAFA)
CC_lightgreen = int(0x33FF33)
CC_darkblue = int(0x3CA1CD)

def load():
    global JSON_PATH
    global Dinner_Dict
    if os.path.isfile(JSON_PATH):
        with open(JSON_PATH, "r") as f:
            Dinner_Dict = json.loads(f.read())
        print(Dinner_Dict)
        #print("Dinner JSON loaded.")
    else:
        print("Dinner JSON no load.")

def item_exist(lst, item):
    for sml_dict in lst:
        if sml_dict["item"] == item:
            return True
    return False

def add(ID, item, weight):
    ID = str(ID)
    global JSON_PATH
    global Dinner_Dict
    if ID not in Dinner_Dict:
        Dinner_Dict[ID] = []
    if item_exist(Dinner_Dict[ID], item):
        return False
    tmp_dict = {"item": item, "weight": weight}
    Dinner_Dict[ID].append(tmp_dict)
    with open(JSON_PATH, "w") as f:
        f.write(json.dumps(Dinner_Dict, indent = 4))
    return True

def query(ID, item=None):
    ID = str(ID)
    global JSON_PATH
    global Dinner_Dict
    if ID not in Dinner_Dict:
        return None
    if item is None:
        lst = []
        for sml_dict in Dinner_Dict[ID]:
            lst.append((sml_dict["item"], sml_dict["weight"]))
        return lst
    else:
        for sml_dict in Dinner_Dict[ID]:
            if sml_dict["item"] == item:
                return [(sml_dict["item"], sml_dict["weight"])]
        return None

def rm(ID, item):
    ID = str(ID)
    global JSON_PATH
    global Dinner_Dict
    if ID not in Dinner_Dict:
        return False
    for i in range(len(Dinner_Dict[ID])):
        if Dinner_Dict[ID][i]["item"] == item:
            del Dinner_Dict[ID][i]
            with open(JSON_PATH, "w") as f:
                f.write(json.dumps(Dinner_Dict, indent = 4))
            return True
    return False


def rand(ID):
    ID = str(ID)
    global JSON_PATH
    global Dinner_Dict
    total = 0.0
    q = query(ID)
    if q is None:
        return None
    for (item, weight) in q:
        total += float(weight)
    print(total)
    total *= random.random()
    print(total)
    for (item, weight) in q:
        total -= float(weight)
        if total <= 0:
            return item
    return None

def help():
    embed_str = "\n**Commands:**\n\n"
    embed_str += "**Usage\:** `{prefix}dinner`\nRandom pick an restaurant from your list.\n\n".format(prefix=start_sign)
    embed_str += "**add\:** `{prefix}dinner add item_name random_prob`\nAdd an item to your dinner list.\n\n".format(prefix=start_sign)
    embed_str += "**list\:** `{prefix}dinner list (item_name)`\nList all items (or specific item) and their probability.\n\n".format(prefix=start_sign)
    embed_str += "**rm\:** `{prefix}dinner rm item_name`\nRemove specified item from your dinner list.\n\n".format(prefix=start_sign)
    embed_str += "**help\:** `{prefix}dinner help`\nShow this help message.\n\n".format(prefix=start_sign)
    embed = discord.Embed(title=":fork_and_knife:  I will have order! 今晚，我想來點...",\
            description=embed_str, colour=discord.Colour(CC_red))
    return embed

def test():
    load()
    add(123, "麥當勞", 0.3)
    add(123, "龍品魚丸店", 0.5)
    add(123, "迷克夏", 0.2)
    add(123, "Macu", 0.5)
    print(query(123))
    print(query(123, "龍品魚丸店"))
    #print(rm(123, "龍品魚丸店"))
    print(rm(123, "Mac"))
    #print(rm(123, "Macu"))
    print(query(123, "龍品魚丸店"))
    print(query(123, "456"))
    print(query(456, "456"))
    for i in range(10):
        print(rand(123))


if __name__ == '__main__':
    test()
