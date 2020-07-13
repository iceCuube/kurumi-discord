import discord
from discord.ext import commands

import dfunctions

numberemojitoint = {
    "1️⃣": 1,
    "2️⃣": 2,
    "3️⃣": 3,
    "4️⃣": 4,
    "5️⃣": 5,
    "6️⃣": 6,
    "7️⃣": 7,
    "8️⃣": 8,
    "9️⃣": 9,
}

class TTCBoard:
    def __init__(self, xmember, omember):
        self.board = [
                '-','-','-',
                '-','-','-',
                '-','-','-'
                ]

        self.xmember = xmember
        self.omember = omember

    def __returnwinner(self, slot):
        if slot == 'X':
            return self.xmember
        return self.omember

    def checkforwinner(self):
        # check each row from left to right
        for i in range(0,3):
            if self.board[i*3] != '-' and self.board[i*3] == self.board[i*3+1] and self.board[i*3+1] == self.board[i*3+2]:
                return self.__returnwinner(self.board[i*3])

        # check each row from top to bottom
        for i in range(0,3):
            if self.board[i] != '-' and self.board[i] == self.board[i+3] and self.board[i+3] == self.board[i+6]:
                return self.__returnwinner(self.board[i])

        #check for diagonal
        if self.board[0] != '-' and self.board[0] == self.board[4] and self.board[4] == self.board[8]:
            return self.__returnwinner(self.board[0])

        if self.board[2] != '-' and self.board[2] == self.board[4] and self.board[4] == self.board[6]:
            return self.__returnwinner(self.board[2])

        # check if tie
        if '-' not in self.board:
            return False

        return None

    def placemarker(self, character, position):
        position -= 1
        if not (position >= 0 and position <= 8):
            return False

        if self.board[position] != '-':
            return False

        self.board[position] = character
        return True
    
    def show(self):
        text = ""

        for j in range(0,3):
            text += "| "

            for i in range(0,3):
                text += self.board[i+(j*3)] + " | "

            text += "\n"

        return text

    def clear(self):
        for i in range(0,9):
            self.board[i] = '-'
        return

class ttt(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.challenger = None
        self.challenged = None
        self.turn = None
        self.board = None
        self.boardmessage = None
        self.gamestart = False

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.client.user.id: # ignore own reactions
            return

        if self.gamestart == False: # ignore if game hasnt started
            return

        channel = self.client.get_channel(payload.channel_id) # get channel object
        message = await channel.fetch_message(payload.message_id) # get message object

        if self.boardmessage.id != message.id: # check if the message received by the payload is the board
            return

        if str(payload.emoji) not in numberemojitoint.keys(): # check if the reaction is one of the number emojis. ignore if not
            return

        if self.turn != payload.member:
            return

        if self.turn == self.challenger:
            if not self.board.placemarker("X", numberemojitoint[str(payload.emoji)]):
                return
            colour = discord.Colour.blue()
            self.turn = self.challenged
        elif self.turn == self.challenged:
            if not self.board.placemarker("O", numberemojitoint[str(payload.emoji)]):
                return
            self.turn = self.challenger
            colour = discord.Colour.orange()

        # check who has won
        boardwinner = self.board.checkforwinner()
        if boardwinner == None: # if there is still an extra spot
            await self.boardmessage.edit(embed=dfunctions.generatesimpleembed("It's " + self.turn.display_name + "'s turn!", "```\n" + self.board.show() + "\n```", colour=colour))
        else:
            if boardwinner == False: # if its a tie
                await self.boardmessage.edit(embed=dfunctions.generatesimpleembed("looks like it's a tie :/", "```\n" + self.board.show() + "\n```"))
            else: # if there is a winner
                await self.boardmessage.edit(embed=dfunctions.generatesimpleembed(boardwinner.display_name + " has won!", "```\n" + self.board.show() + "\n```", colour=colour))

            self.challenger = None
            self.challenged = None
            self.turn = None
            self.board = None
            self.boardmessage = None
            self.gamestart = False
        return

    @commands.command()
    async def tictactoe(self, ctx, opponent: discord.Member):
        if self.gamestart == True:
            await ctx.send("please wait")
            return

        if opponent == None:
            await ctx.send("i cant find that user :/")
            return

        if opponent == ctx.author:
            await ctx.send("you cant play with yourself!")
            return

        if ctx.author.bot == True:
            await ctx.send("you cant play with a bot!")
            return

        self.challenger = ctx.author
        self.challenged = opponent

        await ctx.send(ctx.author.display_name + " wants to play Tic Tac Toe with " + opponent.display_name + "\n" + opponent.display_name + ", type u&accept to accept or u&decline to decline")
        return

    @commands.command()
    async def tttaccept(self, ctx):
        if self.challenger == None:
            await ctx.send("no one asked")
            return

        if self.challenged != ctx.author:
            await ctx.send("no")
            return

        self.gamestart = True
        self.turn = self.challenger
        self.board = TTCBoard(self.challenger, self.challenged)
        
        await ctx.send("okayy!")
        self.boardmessage = await ctx.send(embed=dfunctions.generatesimpleembed("It's " + self.turn.display_name + "'s turn!", "```\n" + self.board.show() + "\n```"))
        for emoji in sorted(numberemojitoint.keys()):
            await self.boardmessage.add_reaction(emoji)
        return

    @commands.command()
    async def tttdecline(self, ctx):
        if self.challenger == None:
            await ctx.send("no one asked")
            return

        if self.challenged != ctx.author:
            await ctx.send("no")
            return

        self.challenger = None
        self.challenger = None
        await ctx.send("alright")
        return

def setup(client):
    client.add_cog(ttt(client))