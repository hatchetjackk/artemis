import asyncio
import discord
from _datetime import datetime
import pytz
import json
import random
from discord.ext import commands

""" All times in events are handled as UTC and then converted to set zone times for local reference """


class Automod:
    def __init__(self, client):
        self.client = client


def setup(client):
    client.add_cog(Automod(client))
