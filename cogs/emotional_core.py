import asyncio
import random
import json
import discord
from itertools import cycle
from discord.ext import commands


class Emotions:
    def __init__(self, client):
        self.client = client

    async def on_message(self, message):
        channel = message.channel
        msg = [word.lower() for word in message.content.split()]
        content = message.content.lower()
        data = await self.load_status()
        good_keys = data['status_changing_words']['good']
        bad_keys = data['status_changing_words']['bad']
        good_bot = data['bot']['good']
        bad_bot = data['bot']['bad']
        for word in msg:
            if word in good_keys:
                good = 1
                await self.emotional_level(good)
            if word in bad_keys:
                bad = -1
                await self.emotional_level(bad)
        for value in good_bot:
            if value in content:
                await channel.send(random.choice(data['bot']['good_response']))
        for value in bad_bot:
            if value in content:
                await channel.send(random.choice(data['bot']['bad_response']))

    async def emotional_level(self, value):
        status = await self.load_status()
        if value < 0 and status["status"]["level"] == 0:
            return
        if value > 0 and status["status"]["level"] == 50:
            return
        status["status"]["level"] += value
        print('Artemis emotional level change: {0}'.format(status["status"]["level"]))
        await self.dump_status(status)

    @commands.command()
    async def status(self, ctx):
        data = await self.load_status()
        level = data["status"]["level"]

        if level >= 40:
            await ctx.channel.send(random.choice(data["responses"]["great"]))
            mood = "Great"
        elif level >= 30:
            await ctx.channel.send(random.choice(data["responses"]["good"]))
            mood = "Good"
        elif level >= 20:
            await ctx.channel.send(random.choice(data["responses"]["ok"]))
            mood = 'OK'
        elif level >= 10:
            await ctx.channel.send(random.choice(data["responses"]["bad"]))
            mood = 'Bad'
        else:
            await ctx.channel.send(random.choice(data["responses"]["terrible"]))
            mood = 'Terrible'
        print('Mood: {0:<5} Level: {1}/50'.format(mood, level))
        return mood

    async def change_status(self):
        await self.client.wait_until_ready()
        data = await self.load_status()
        status_response = data['bot']['status_response']
        msg = cycle(status_response)
        while not self.client.is_closed():
            current_status = next(msg)
            await self.client.change_presence(game=discord.Game(name=current_status))
            await asyncio.sleep(60 * 5)

    @staticmethod
    async def load_status():
        with open('files/status.json') as f:
            data = json.load(f)
            return data

    @staticmethod
    async def dump_status(data):
        with open('files/status.json', 'w') as f:
            json.dump(data, f, indent=2)


def setup(client):
    client.add_cog(Emotions(client))
    client.loop.create_task(Emotions(client).change_status())
