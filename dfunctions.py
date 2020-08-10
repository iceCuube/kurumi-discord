import discord
import json 

def formatspaces(line, maxlength, endchar="", replacelast=True, addspace=True, reverse=False):
    length = len(line)
    if length > maxlength:
        if replacelast:
            line = line[:(maxlength-3)] + "..."
        else:
            line = line[:(maxlength)]
        offset = 0
    else:
        offset = maxlength - length

    line += endchar

    if addspace:
        if reverse:
            line = (' ' * offset) + line
        else:
            line += (' ' * offset)

    return line

def generatesimpleembed(title, desc, footer=None, colour=discord.Colour.red()):
    embedinfo = discord.Embed(
                title = title,
                description = desc,
                colour = colour
                )

    if footer != None:
        embedinfo.set_footer(text=footer)

    return embedinfo

def savejson(dictionary, name):
    try:
        jsonfile = open(name, "w")
    except Exception as error:
        print("File cannot be opened for writing!")
        print(error)
        return False

    jsondump = json.dumps(dictionary, indent=4)

    jsonfile.write(jsondump)
    jsonfile.close()

    return True

def loadjson(name):
    try:
        jsonfile = open(name, "r")
    except:
        print("File cannot be openend for writing!")
        return None

    return json.load(jsonfile)