import os
import random
import discord
from PyDictionary import PyDictionary
from discord.ext import commands


class Fun:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):

        await ctx.send(':ping_pong: Pong')

    @commands.command()
    async def lennie(self, ctx):
        await ctx.send('( ͡° ͜ʖ ͡°)')

    @commands.command()
    async def roll(self, ctx, dice: str):
        try:
            rolls, limit = map(int, dice.split('d'))
            print(rolls, limit)
        except Exception as e:
            print(e)
            await ctx.send('Please use the format "NdN" when rolling dice. Thanks!')
            return
        result = ', '.join(str(random.randint(1, limit)) for value in range(rolls))
        await ctx.send(result)

    @commands.command()
    async def hello(self, ctx):
        responses = ["Hi, {0.author.mention}!",
                     "Ahoy, {0.author.mention}!",
                     "Hey there, {0.author.mention}!",
                     "*[insert traditional greeting here]*",
                     "*0100100001000101010011000100110001001111*\nAhem, I mean: hello!",
                     "Hello. Fine weather we're having.",
                     "Hello, fellow human!"]
        msg = random.choice(responses).format(ctx.message)
        await ctx.send(msg)

    @commands.command()
    async def define(self, ctx, word: str):
        dictionary = PyDictionary()
        results = dictionary.meaning(word)
        embed = discord.Embed(title=word.upper(), color=discord.Color.blue())
        for key, definition in results.items():
            definitions = []
            num = 1
            for value in definition:
                definitions.append(str(num) + ') ' + value)
                num += 1
            all_def = '\n'.join(definitions)
            embed.add_field(name=key, value=all_def)
        await ctx.send(embed=embed)

    @commands.group()
    async def rochembed(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @rochembed.group()
    async def qizard(self, ctx):
        directory = 'pictures/'
        pictures = [file for file in os.listdir('pictures/')]
        pic = directory + random.choice(pictures)
        await ctx.send(file=discord.File(pic))

    @staticmethod
    async def on_message(message):
        channel = message.channel
        msg = message.content
        if msg.startswith('r/'):
            reddit_search = 'https://reddit.com/' + msg
            await channel.send(reddit_search)


def setup(client):
    client.add_cog(Fun(client))
