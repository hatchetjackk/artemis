import discord
import random
import json
from emotional_core import Emotions
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
    async def flip(self, ctx):
        # return heads or tails
        choice = ['Heads!', 'Tails!']
        coin = random.choice(choice)
        await self.client.send_message(ctx.message.channel, coin)

    @commands.command()
    async def google(self):
        pass

    @commands.command(pass_context=True)
    async def rps(self, ctx, index: str):
        rps = ['rock', 'paper', 'scissors']
        lose = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}
        win = {'paper': 'rock', 'rock': 'scissors', 'scissors': 'paper'}
        bot_choice = random.choice(rps)
        user_choice = index
        # check for valid entry
        if user_choice not in rps:
            await self.client.send_message(ctx.message.channel, 'That\'s not a valid choice.')
            return
        # check choice against bot
        if bot_choice == user_choice:
            await self.client.send_message(ctx.message.channel, 'Artemis chose {0}! It\'s a tie!'.format(bot_choice))
        if user_choice == lose.get(bot_choice):
            await self.client.send_message(ctx.message.channel, 'Artemis chose {0}! You lost!'.format(bot_choice))
        if user_choice == win.get(bot_choice):
            await self.client.send_message(ctx.message.channel, 'Artemis chose {0}! You win!'.format(bot_choice))

    @commands.command(pass_context=True)
    async def server(self, ctx):
        # e = Emotions(self.client)
        # start = time.time() in artemis.py
        # uptime = time.time() - start
        # server_id = server id
        # mood = e.status
        # thumbnail = 'https://cdn0.iconfinder.com/data/icons/cosmo-medicine/40/eye_6-512.png'
        # embed
        # embed = discord.Embed(
        #     color=discord.Color.blue()
        # )
        # embed.set_author(name="Artemis", icon_url=thumbnail)
        # embed.add_field(name="Uptime", value=uptime, inline=False)
        # embed.add_field(name="Server ID", value=server_id, inline=False)
        # embed.add_field(name="Mood", value=mood, inline=False)
        # await self.client.say(embed=embed)
        await self.client.send_message(ctx.message.channel, 'This command is not ready yet.')

    @commands.command(pass_context=True)
    async def whois(self, ctx):
        # read message for user or part of a username
        # joined_discord = check when joined discord
        # joined_server = check when joined server
        # user_avatar = grab user avatar
        # roles = grab roles from list
        # make embed
        # add joined_discord
        # add joined_server
        # add user_avatar
        # add roles
        # send to channel
        await self.client.send_message(ctx.message.channel, 'This command is not ready yet.')


def setup(client):
    client.add_cog(User(client))
