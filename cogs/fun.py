import random
import re
import urllib.request
import urllib.parse
import discord
import requests
from datetime import datetime
from discord.ext.commands import BucketType, CommandNotFound
from PyDictionary import PyDictionary
from discord.ext import commands


class Fun:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def playing(self, ctx, *, game_match='all'):
        if game_match == 'all':
            games_currently_being_played = [member.game.name for member in ctx.guild.members
                                            if member.game is not None
                                            and member.id != self.client.user.id]
            if len(games_currently_being_played) < 1:
                embed = discord.Embed(title='No one is playing anything!')
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title='Games currently being played'.format(game_match),
                                      description='\n'.join(games_currently_being_played))
                await ctx.send(embed=embed)
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
                embed = discord.Embed(title='No members are playing "{}"'.format(game_match))
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title='Members currently playing "{}"'.format(game_match),
                                      description='\n'.join(members_playing_game))
                await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(':ping_pong: Pong')

    @commands.command()
    async def roll(self, ctx, dice: str):
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception as e:
            print('An error occurred when rolling dice', e)
            await ctx.send('Please use the format "NdN" when rolling dice. Thanks!')
            return
        rolls = [random.randint(1, limit) for _ in range(rolls)]
        result = ', '.join(str(roll) for roll in rolls)
        await ctx.send(result)

    @commands.command(aliases=['hi', 'bonjour', 'hola'])
    async def hello(self, ctx):
        responses = ["Hi, {0.author.mention}!",
                     "Ahoy, {0.author.mention}!",
                     "Hey there, {0.author.mention}!",
                     "*[insert traditional greeting here]*",
                     "*0100100001000101010011000100110001001111*\nAhem, I mean: hello!",
                     "Hello. Fine weather we're having.",
                     "Hello, fellow human!"]
        msg = random.choice(responses).format(ctx.message)
        await ctx.send(msg)

    @commands.command()
    async def define(self, ctx, word: str):
        try:
            dictionary = PyDictionary()
            results = dictionary.meaning(word)
            embed = discord.Embed(title=word.upper(), color=discord.Color.blue())
            for key, definition in results.items():
                definitions = []
                num = 1
                for value in definition:
                    definitions.append(str(num) + ') ' + value)
                    num += 1
                all_def = '\n'.join(definitions)
                embed.add_field(name=key, value=all_def)
            await ctx.send(embed=embed)
        except Exception as e:
            print('[{}] The definition for {} could not be found: {}'.format(datetime.now(), word, e))
            await ctx.send('Sorry, I could not find the definition for {}!'.format(word))

    @commands.command(aliases=['g'])
    async def google(self, ctx, *, search: str):
        r = requests.get('http://www.google.com/search?q="{}"&btnI'.format(search))
        await ctx.send(r.url)

    @staticmethod
    async def on_message(message):
        if message.content.startswith('r/'):
            reddit_search = 'https://reddit.com/' + message.content
            await message.channel.send(reddit_search)

    @commands.command()
    async def rps(self, ctx, choice: str):
        rps = ['rock', 'paper', 'scissors']
        lose = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}
        win = {'paper': 'rock', 'rock': 'scissors', 'scissors': 'paper'}

        if choice not in rps:
            await ctx.send('You have to pick rock, paper, or scissors.')

        bot_choice = random.choice(rps)
        if bot_choice == choice:
            await ctx.send('Artemis chose {0}! It\'s a tie!'.format(bot_choice))
            print('{0} played rock, paper, scissors and tied with Artemis.'.format(ctx.author.name))
        if choice == lose.get(bot_choice):
            await ctx.send('Artemis chose {0}! You lost!'.format(bot_choice))
            print('{0} played rock, paper, scissors and lost to Artemis.'.format(ctx.author.name))
        if choice == win.get(bot_choice):
            await ctx.send('Artemis chose {0}! You win!'.format(bot_choice))
            print('{0} played rock, paper, scissors and beat Artemis!'.format(ctx.author.name))

    @commands.command(aliases=['yt'])
    @commands.cooldown(rate=1, per=15, type=BucketType.user)
    async def youtube(self, ctx, *args):
        query_string = urllib.parse.urlencode({"search_query": ' '.join(args)})
        html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
        search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
        await ctx.send("http://www.youtube.com/watch?v=" + search_results[0])
        print('{0} searched Youtube for "{1}".'.format(ctx.author.name, ' '.join(args)))

    @commands.command()
    async def card(self, ctx):
        """ draw a random card from a deck """
        card = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 'Ace', 'King', 'Queen', 'Jack']
        style = ['Spades', 'Hearts', 'Clubs', 'Diamonds']

        rcard = random.choice(card)
        rstyle = random.choice(style)

        fmt = 'You drew the {0} of {1}!'
        await ctx.send(fmt.format(rcard, rstyle))
        print('{0} drew the {1} of {2}.'.format(ctx.author.name, rcard, rstyle))

    @rps.error
    @youtube.error
    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = 'You\'ve triggered a cool down. Please try again in {} sec.'.format(
                int(error.retry_after))
            await ctx.send(msg)
        if isinstance(error, commands.CheckFailure):
            msg = 'You do not have permission to run this command.'
            await ctx.send(msg)
        if isinstance(error, commands.MissingRequiredArgument):
            msg = 'A critical argument is missing from the command.'
            await ctx.send(msg)
        if isinstance(error, CommandNotFound):
            msg = 'Did you mean to try another command?'
            await ctx.send(msg)


def setup(client):
    client.add_cog(Fun(client))
