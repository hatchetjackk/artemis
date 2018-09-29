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

    @commands.command()
    async def server(self):
        pass

    @commands.command()
    async def whois(self):
        pass


def setup(client):
    client.add_cog(User(client))
