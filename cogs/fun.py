import os
import random
import discord
import requests
from PyDictionary import PyDictionary
from discord.ext import commands


class Fun:
    def __init__(self, client):
        self.client = client

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
        result = ', '.join(str(random.randint(1, limit)) for value in range(rolls))
        await ctx.send(result)

    @commands.command()
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
    async def google(self, ctx, *args):
        search = ' '.join(args)
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

    @commands.command()
    async def rps(self, ctx, *args):
        rps = ['rock', 'paper', 'scissors']
        lose = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}
        win = {'paper': 'rock', 'rock': 'scissors', 'scissors': 'paper'}

        # check for valid entry
        if len(args) < 1:
            await ctx.send('You didn\'t say what you picked!')
            return
        if len(args) > 1:
            await ctx.send(
                "It's Rock, Paper, Scissors not Rock, Paper, \"*Whateverthehellyouwant*.\" :joy:")
            return
        if args[0] not in rps:
            await ctx.send('That\'s not a valid choice.')
            return

        bot_choice = random.choice(rps)
        user_choice = args[0]
        # check choice against bot
        if bot_choice == user_choice:
            await ctx.send('Artemis chose {0}! It\'s a tie!'.format(bot_choice))
            print('{0} played rock, paper, scissors and tied with Artemis.'.format(ctx.author.name))
        if user_choice == lose.get(bot_choice):
            await ctx.send('Artemis chose {0}! You lost!'.format(bot_choice))
            print('{0} played rock, paper, scissors and lost to Artemis.'.format(ctx.author.name))
        if user_choice == win.get(bot_choice):
            await ctx.send('Artemis chose {0}! You win!'.format(bot_choice))
            print('{0} played rock, paper, scissors and beat Artemis!'.format(ctx.author.name))

    @commands.command(aliases=['yt'])
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


def setup(client):
    client.add_cog(Fun(client))
