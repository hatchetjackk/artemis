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
        coin = random.randint(1, 2)
        if coin == 1:
            await self.client.send_message(ctx.message.channel, 'Heads!')
        if coin == 2:
            await self.client.send_message(ctx.message.channel, 'Tails!')

    @commands.command()
    async def google(self):
        pass

    @commands.command(pass_context=True)
    async def rps(self, ctx, index: str):
        rps = {1: 'rock', 2: 'paper', 3: 'scissors'}
        num = random.randint(1, 3)
        bot_choice = rps.get(num)
        user_choice = index
        # check for valid entry
        if user_choice not in rps.get:
            self.client.send_message(ctx.message.channel, 'Invalid choice.')
            return
        # check choice against bot
        if bot_choice == 'rock' and user_choice == 'rock' or bot_choice == 'paper' and user_choice == 'paper' or bot_choice == 'scissors' and user_choice == 'scissors':
            self.client.send_message(ctx.message.channel, 'It\'s a tie!!')
        if bot_choice == 'rock' and user_choice == 'paper' or bot_choice == 'paper' and user_choice == 'scissors' or bot_choice == 'scissors' and user_choice == 'rock':
            self.client.send_message(ctx.message.channel, 'You win!')
        if bot_choice == 'rock' and user_choice == 'scissors' or bot_choice == 'paper' and user_choice == 'rock' or bot_choice == 'scissors' and user_choice == 'paper':
            self.client.send_message(ctx.message.channel, 'You lost!')

    @commands.command()
    async def server(self):
        pass

    @commands.command()
    async def whois(self):
        pass


def setup(client):
    client.add_cog(User(client))
