import discord
import random
import json
from discord.ext import commands


class User:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def afk(self):
        pass

    @commands.command()
    async def afk_set(self):
        pass

    @commands.command()
    async def afk_ignore(self):
        pass

    @commands.command()
    async def flipcoin(self):
        pass

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