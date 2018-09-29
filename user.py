import discord
import random
import json
from discord.ext import commands


class User:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def afk(self):
        # set status to away with a message to respond to users that mention the afk user
        # return from afk when sending a message
        pass

    @commands.command(pass_context=True)
    async def flipcoin(self, ctx):
        # return heads or tails
        coin = random.randint(1,2)
        if coin == 1:
            self.client.send_message(ctx.message.channel, 'Heads!')
        if coin == 2:
            self.client.send_message(ctx.message.channel, 'Tails!')

    @commands.command()
    async def google(self):
        pass

    @commands.command()
    async def rps(self):
        pass

    @commands.command()
    async def server(self):
        pass

    @commands.command()
    async def whois(self):
        pass


def setup(client):
    client.add_cog(User(client))