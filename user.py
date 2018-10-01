import discord
import random
import json
import urllib.request
import urllib.parse
import re
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
        print('{0} flipped a coin.'.format(ctx.message.author.name))
        await self.client.send_message(ctx.message.channel, coin)

    @commands.command()
    async def google(self):
        pass

    @commands.command(pass_context=True)
    async def rps(self, ctx, *args):
        print(' '.join(args))
        rps = ['rock', 'paper', 'scissors']
        lose = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}
        win = {'paper': 'rock', 'rock': 'scissors', 'scissors': 'paper'}

        # check for valid entry
        if len(args) < 1:
            await self.client.send_message(ctx.message.channel, 'You didn\'t say what you picked!')
            return
        if len(args) > 1:
            await self.client.send_message(ctx.message.channel,
                                           "It's Rock, Paper, Scissors not Rock, Paper, \"*Whateverthehellyouwant*.\" :joy:")
            return
        if args[0] not in rps:
            await self.client.send_message(ctx.message.channel, 'That\'s not a valid choice.')
            return

        bot_choice = random.choice(rps)
        user_choice = args[0]
        # check choice against bot
        if bot_choice == user_choice:
            await self.client.send_message(ctx.message.channel, 'Artemis chose {0}! It\'s a tie!'.format(bot_choice))
            print('{0} played rock, paper, scissors and tied with Artemis.'.format(ctx.message.author.name))
        if user_choice == lose.get(bot_choice):
            await self.client.send_message(ctx.message.channel, 'Artemis chose {0}! You lost!'.format(bot_choice))
            print('{0} played rock, paper, scissors and lost to Artemis.'.format(ctx.message.author.name))
        if user_choice == win.get(bot_choice):
            await self.client.send_message(ctx.message.channel, 'Artemis chose {0}! You win!'.format(bot_choice))
            print('{0} played rock, paper, scissors and beat Artemis!'.format(ctx.message.author.name))

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
        print('{0} tried to use the server command.'.format(ctx.message.author.name))

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
        print('{0} tried to use the whois command.'.format(ctx.message.author.name))

    @commands.command(pass_context=True)
    async def yt(self, ctx, *args):
        query_string = urllib.parse.urlencode({"search_query": ' '.join(args)})
        html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
        search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())

        await self.client.send_message(ctx.message.channel, "http://www.youtube.com/watch?v=" + search_results[0])
        print('{0} searched Youtube for "{1}".'.format(ctx.message.author.name, ' '.join(args)))


def setup(client):
    client.add_cog(User(client))
