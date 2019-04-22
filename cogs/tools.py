import asyncio
from discord.ext import commands
import cogs.utilities as utilities


class Tools(commands.Cog):
    def __init__(self, client):
        self.client = client

    def shorten(self, ctx, *, link: str):
        """
        Take a user provided link and return a shortened link
        todo: find an url shortener
        :param ctx:
        :param link:
        :return:
        """
        pass

    def vote(self):
        pass

    def image(self, ctx, subreddit):
        """
        Return a random image from specified subreddit
        :param ctx:
        :param subreddit:
        :return:
        """
        pass


def setup(client):
    tools = Tools(client)
    client.add_cog(tools)
