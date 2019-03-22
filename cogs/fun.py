import random
import re
import urllib.request
import urllib.parse
import discord
import requests
import cogs.utilities as utilities
from datetime import datetime
from discord.ext.commands import BucketType, CommandNotFound
from PyDictionary import PyDictionary
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group()
    async def fun(self, ctx):
        if ctx.invoked_subcommand is None:
            await utilities.single_embed(
                color=utilities.color_alert,
                title='Try `fun help` for more options.',
                channel=ctx
            )

    @fun.group()
    async def help(self, ctx):
        await utilities.single_embed(
            color=utilities.color_help,
            title='Fun Help',
            channel=ctx,
            description='`playing` View all current statuses\n'
                        '`ping` Check if Artemis is reactive\n'
                        '`roll ndn` Roll n dice\n'
                        '`draw` Draw a random card. High/low anyone?\n'
                        '`hello` Say hi to Artemis\n'
                        '`define [word]` Get a definition\n'
                        '`google [topic]` Retrieve the first link from Google\n'
                        '`r/[subreddit]` Retrieve a subreddit link\n'
                        '`youtube [topic]` Retrieve the first video from YouTube\n'
                        '`rps [rock/paper/scissors]` Play against Artemis'
        )

    @commands.command()
    async def playing(self, ctx, *, game_match='all'):
        if game_match == 'all':
            games_being_played = [member.game.name for member in ctx.guild.members
                                  if member.game is not None
                                  and member.id != self.client.user.id]
            if len(games_being_played) < 1:
                await utilities.single_embed(title='No ones is playing anything!', channel=ctx)
            else:
                await utilities.single_embed(title='Current Games',
                                             description='\n'.join(games_being_played),
                                             channel=ctx)
        else:
            members_playing_game = []
            pattern = re.compile(r'' + re.escape(game_match.lower()))
            for member in ctx.guild.members:
                if member.game is not None:
                    matches = pattern.findall(member.game.name.lower())
                    for _ in matches:
                        game = '{} - {}'.format(member.name, member.game.name)
                        if game in members_playing_game:
                            pass
                        else:
                            members_playing_game.append(game)
            if len(members_playing_game) < 1:
                await utilities.single_embed(title=f'No one is playing {game_match}.', channel=ctx)
            else:
                await utilities.single_embed(title=f'{len(members_playing_game)} members are playing {game_match}.',
                                             description='\n'.join(members_playing_game),
                                             channel=ctx)

    @commands.command()
    async def ping(self, ctx):
        await utilities.single_embed(title=':ping_pong: Pong!', channel=ctx, color=utilities.color_alert)

    @commands.command()
    async def roll(self, ctx, dice: str):
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await utilities.single_embed(title='Please use the format "NdN" when rolling dice. Thanks!', channel=ctx)
            raise
        rolls = [random.randint(1, limit) for _ in range(rolls)]
        result = ', '.join(str(roll) for roll in rolls)
        await utilities.single_embed(title=f'You rolled {result} for a total of {sum(rolls)}!', channel=ctx)

    @commands.command(aliases=['hi', 'bonjour', 'hola'])
    async def hello(self, ctx):
        responses = ["Hi, {0.author.name}!",
                     "Ahoy, {0.author.name}!",
                     "Hey there, {0.author.name}!",
                     "*[insert traditional greeting here]*",
                     "*0100100001000101010011000100110001001111*\nAhem, I mean: hello!",
                     "Hello. Fine weather we're having.",
                     "Hello, fellow human!"]
        msg = random.choice(responses).format(ctx)
        await utilities.single_embed(title=msg, channel=ctx)

    @commands.command()
    async def define(self, ctx, word: str):
        try:
            dictionary = PyDictionary()
            results = dictionary.meaning(word)
            messages = []
            for key, definition in results.items():
                definitions = []
                num = 1
                for value in definition:
                    definitions.append(str(num) + ') ' + value)
                    num += 1
                all_def = '\n'.join(definitions)
                messages.append([key, all_def])
            await utilities.multi_embed(
                title=word.upper(),
                messages=messages,
                channel=ctx
            )
        except Exception as e:
            print('[{}] The definition for {} could not be found: {}'.format(datetime.now(), word, e))
            await utilities.single_embed(
                color=utilities.color_alert,
                title=f'Sorry, I could not find the definition for {word}!',
                channel=ctx
            )

    @commands.command(aliases=['g'])
    async def google(self, ctx, *, search: str):
        r = requests.get(f'http://www.google.com/search?q="{search}"&btnI')
        await ctx.send(r.url)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith('r/'):
            reddit_search = 'https://reddit.com/' + message.content
            await message.channel.send(reddit_search)

    @commands.command()
    async def rps(self, ctx, choice: str):
        rps = ['rock', 'paper', 'scissors']
        lose = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}
        win = {'paper': 'rock', 'rock': 'scissors', 'scissors': 'paper'}

        if choice not in rps:
            await utilities.single_embed(
                color=utilities.color_alert,
                title='You have to pick rock, paper, or scissors.',
                channel=ctx
            )

        bot_choice = random.choice(rps)
        if bot_choice == choice:
            await utilities.single_embed(title=f'Artemis chose {bot_choice}! It\'s a tie!', channel=ctx)
        if choice == lose.get(bot_choice):
            await utilities.single_embed(color=utilities.color_alert, title=f'Artemis chose {bot_choice}! You lost!',
                                         channel=ctx)
        if choice == win.get(bot_choice):
            await utilities.single_embed(color=utilities.color_help, title=f'Artemis chose {bot_choice}! You won!',
                                         channel=ctx)

    @commands.command(aliases=['yt'])
    @commands.cooldown(rate=1, per=15, type=BucketType.user)
    async def youtube(self, ctx, *args):
        query_string = urllib.parse.urlencode({"search_query": ' '.join(args)})
        html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
        search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
        await ctx.send("http://www.youtube.com/watch?v=" + search_results[0])

    @commands.command(aliases=['draw'])
    async def card(self, ctx):
        """ draw a random card from a deck """
        card = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 'Ace', 'King', 'Queen', 'Jack']
        style = ['Spades', 'Hearts', 'Clubs', 'Diamonds']

        rcard = random.choice(card)
        rstyle = random.choice(style)

        await utilities.single_embed(title=f'You drew the {rcard} of {rstyle}!', channel=ctx)

    @rps.error
    @youtube.error
    @commands.Cog.listener()
    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = f'You\'ve triggered a cool down. Please try again in {error.retry_after} sec.'
            await utilities.single_embed(
                color=utilities.color_alert,
                title=msg,
                channel=ctx
            )
        if isinstance(error, commands.CheckFailure):
            await utilities.single_embed(
                color=utilities.color_alert,
                title='You do not have permission to run this command.',
                channel=ctx
            )
        if isinstance(error, commands.MissingRequiredArgument):
            await utilities.single_embed(
                color=utilities.color_alert,
                title='A critical argument is missing from the command.',
                channel=ctx
            )
        if isinstance(error, CommandNotFound):
            await utilities.single_embed(
                color=utilities.color_alert,
                title='Did you mean to try another command?',
                channel=ctx
            )


def setup(client):
    client.add_cog(Fun(client))
