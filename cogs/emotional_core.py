import asyncio
import random
import discord
from artemis import load_json, dump_json
from itertools import cycle
from discord.ext import commands


class Emotions:
    def __init__(self, client):
        self.client = client

    async def on_message(self, message):
        channel = message.channel
        msg = [word.lower() for word in message.content.split()]
        content = message.content.lower()
        data = await load_json('status')
        good_keys = data['status_changing_words']['good']
        bad_keys = data['status_changing_words']['bad']
        good_bot = data['bot']['good']
        bad_bot = data['bot']['bad']
        good_morning = ['good morning', 'morning guys', 'morning, guys', 'morning artie',
                        'good morning, artie', 'good morning, Artemis',
                        'good morning, Artie', 'morning artemis', 'good morning, arty',
                        'good morning arty']
        morning_response = ['Good morning!', 'Good morning, {}!'.format(message.author.name)]
        trigger = False
        for word in msg:
            if word in good_keys:
                trigger = True
                await self.emotional_level(1)
            if word in bad_keys:
                trigger = True
                await self.emotional_level(-1)
        for value in good_morning:
            if value in content and message.author.id != self.client.user.id:
                # trigger = True
                await channel.send(random.choice(morning_response))
                return
        for value in good_bot:
            if value in content:
                trigger = True

                def check(m):
                    return m.author == message.author and m.channel == channel

                neg_responses = ['not u', 'jk', 'just kidding', 'not you', 'nevermind',
                                 'nvm']
                await channel.send(random.choice(data['bot']['good_response']))
                msg = await self.client.wait_for('message', check=check)
                if msg.content in neg_responses:
                    await channel.send(random.choice(data['bot']['bad_response']))
                    bad = -1
                    await self.emotional_level(bad)
        for value in bad_bot:
            if value in content:
                trigger = True
                await channel.send(random.choice(data['bot']['bad_response']))
        if ('artemis' in content or 'artie' in content) and trigger is False:
            random_response = ['Hm?', 'Yes?', 'Someone call me?', 'You rang?',
                               'Did you need something?']
            await channel.send(random.choice(random_response))

    @staticmethod
    async def emotional_level(value):
        data = await load_json('status')
        if value < 0 and data["status"]["level"] == 0:
            return
        if value > 0 and data["status"]["level"] == 50:
            return
        data["status"]["level"] += value
        print('Artemis emotional level change: {0}'.format(data["status"]["level"]))
        await dump_json('status', data)

    @commands.command()
    async def status(self, ctx):
        data = await load_json('status')
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
        data = await load_json('status')
        status_response = data['bot']['status_response']
        msg = cycle(status_response)
        while not self.client.is_closed():
            current_status = next(msg)
            await self.client.change_presence(game=discord.Game(name=current_status))
            await asyncio.sleep(60 * 5)


def setup(client):
    client.add_cog(Emotions(client))
    client.loop.create_task(Emotions(client).change_status())
