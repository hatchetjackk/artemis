import discord
import random
from discord.ext import commands


class Emotions:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def status(self):
        pass


def setup(client):
    client.add_cog(Emotions(client))
