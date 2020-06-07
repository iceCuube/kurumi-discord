import discord

def formatspaces(line, maxlength, endchar="", addspace=True):
    length = len(line)
    if length > maxlength:
        line = line[:(maxlength-3)] + "..."
        offset = 1
    else:
        offset = maxlength - length + 1

    line += endchar

    if addspace == True:
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