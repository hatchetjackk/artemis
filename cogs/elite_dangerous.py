import requests
import json
import aiohttp
import asyncio
from discord import Embed, Color
from math import sqrt
from discord.ext import commands


class EliteDangerous:
    def __init__(self, client):
        self.client = client

    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    @commands.command()
    async def dist(self, ctx, system1, system2):
        system1_url = 'http://www.edsm.net/api-v1/system?sysname=' + system1 + '&coords=1'
        system2_url = 'http://www.edsm.net/api-v1/system?sysname=' + system2 + '&coords=1'
        system1_request = requests.get(system1_url)
        system1_json = json.loads(system1_request.text)

        system2_request = requests.get(system2_url)
        system2_json = json.loads(system2_request.text)

        system1_name = system1_json['name']
        x1 = system1_json['coords']['x']
        y1 = system1_json['coords']['y']
        z1 = system1_json['coords']['z']

        system2_name = system2_json['name']
        x2 = system2_json['coords']['x']
        y2 = system2_json['coords']['y']
        z2 = system2_json['coords']['z']

        x = x2 - x1
        y = y2 - y1
        z = z2 - z1

        distance = sqrt(x**2 + y**2 + z**2)
        distance = round(distance * 100) / 100

        embed = Embed(description='{} <:arrows:511235174374178816> {}: {} LY'.format(system1_name, system2_name, distance),
                      color=Color.blue())
        await ctx.send(embed=embed)
        pass


def setup(client):
    client.add_cog(EliteDangerous(client))
