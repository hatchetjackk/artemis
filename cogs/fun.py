import os
import random
import re
import urllib.request
import urllib.parse
import discord
import requests
from discord.ext.commands import BucketType, CommandNotFound
from artemis import load_json, dump_json
from PyDictionary import PyDictionary
from discord.ext import commands


class Fun:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def playing(self, ctx, *args):
        game_match = ' '.join(args)
        if game_match == 'all':
            games_currently_being_played = [member.game.name for member in ctx.guild.members
                                            if member.game is not None
                                            and member.id != self.client.user.id]
            if len(games_currently_being_played) < 1:
                embed = discord.Embed(title='No one is playing anything!')
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title='Games currently being played'.format(game_match),
                                      description='\n'.join(game for game in games_currently_being_played))
                await ctx.send(embed=embed)
        else:
            members_playing_game = []
            pattern = re.compile(r'' + re.escape(game_match.lower()))
            for member in ctx.guild.members:
                if member.game is not None:
                    matches = pattern.findall(member.game.name.lower())
                    for _ in matches:
                        x = '{} - {}'.format(member.name, member.game.name)
                        if x in members_playing_game:
                            pass
                        else:
                            members_playing_game.append(x)
            if len(members_playing_game) < 1:
                embed = discord.Embed(title='No members are playing "{}"'.format(game_match))
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title='Members currently playing "{}"'.format(game_match),
                                      description='\n'.join(member for member in members_playing_game))
                await ctx.send(embed=embed)

    @commands.command()
    async def sudo(self, ctx, *, cmd: str):
        if 'rm -rf .' == cmd:
            await ctx.send('Deletin--')
            return
        if 'make me a sandwhich' == cmd:
            await ctx.send('Yeah, I\'ll get right on that...')
            return
        await ctx.send('Sudo go f*ck yourself.')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(':ping_pong: Pong')

    @commands.command()
    async def lennie(self, ctx):
        await ctx.send('( ͡° ͜ʖ ͡°)')

    @commands.command()
    async def roll(self, ctx, dice: str):
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception as e:
            print(e)
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

    @commands.command(aliases=['g'])
    async def google(self, ctx, *, search: str):
        r = requests.get('http://www.google.com/search?q="{}"&btnI'.format(search))
        await ctx.send(r.url)

    @commands.group()
    async def rochembed(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @rochembed.group()
    async def qizard(self, ctx):
        directory = 'pictures/'
        pictures = [file for file in os.listdir('pictures/')]
        pic = directory + random.choice(pictures)
        await ctx.send(file=discord.File(pic))

    @staticmethod
    async def on_message(message):
        channel = message.channel
        msg = message.content
        if msg.startswith('r/'):
            reddit_search = 'https://reddit.com/' + msg
            await channel.send(reddit_search)
        if msg == '(╯°□°）╯︵ ┻━┻' or msg == '(∩⩺ロ⩹)⊃━☆ﾟ.* ︵ ┻━┻':
            table_fix = ['┬─┬ ノ( ゜-゜ノ)', '┬─┬ ノ( ⩺ロ⩹ノ)']
            await channel.send(random.choice(table_fix))

    @commands.command(aliases=['health'])
    @commands.cooldown(rate=1, per=3, type=BucketType.user)
    async def hp(self, ctx, *, target: str):
        embed = discord.Embed()
        data = await load_json('users')
        pattern = re.compile(r'' + re.escape(target.lower()))
        for member in ctx.guild.members:
            member_name = await self.member_name(member)
            matches = pattern.finditer(member_name.lower())
            for _ in matches:
                mid = str(member.id)
                embed.add_field(name=member_name,
                                value='{}/{} HP'.format(data[mid]['hp'], data[mid]['max hp']))
                embed.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=embed)

    @staticmethod
    async def member_name(member):
        # grab author nick
        member_name = member.nick
        if member_name is None:
            member_name = member.name
        return member_name

    @commands.command()
    async def rps(self, ctx, choice: str):
        rps = ['rock', 'paper', 'scissors']
        lose = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}
        win = {'paper': 'rock', 'rock': 'scissors', 'scissors': 'paper'}

        # check for valid entry
        if choice not in rps:
            await ctx.send('You have to pick rock, paper, or scissors.')

        bot_choice = random.choice(rps)
        # check choice against bot
        if bot_choice == choice:
            await ctx.send('Artemis chose {0}! It\'s a tie!'.format(bot_choice))
            print('{0} played rock, paper, scissors and tied with Artemis.'.format(ctx.author.name))
        if choice == lose.get(bot_choice):
            await ctx.send('Artemis chose {0}! You lost!'.format(bot_choice))
            data = await load_json('users')
            data[str(ctx.author.id)]['hp'] -= 1
            await ctx.send('{} took 1 HP of damage...'.format(ctx.author.name))
            print('{0} played rock, paper, scissors and lost to Artemis.'.format(ctx.author.name))
            await dump_json('users', data)
        if choice == win.get(bot_choice):
            await ctx.send('Artemis chose {0}! You win!'.format(bot_choice))
            print('{0} played rock, paper, scissors and beat Artemis!'.format(ctx.author.name))

    @commands.command(aliases=['yt'])
    @commands.cooldown(rate=1, per=30, type=BucketType.user)
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
    @hp.error
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
