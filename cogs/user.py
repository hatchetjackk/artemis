import discord
import random
import urllib.request
import urllib.parse
import re
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

    @commands.command(pass_context=True)
    async def card(self, ctx):
        """ draw a random card from a deck """
        card = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 'Ace', 'King', 'Queen', 'Jack']
        style = ['Spades', 'Hearts', 'Clubs', 'Diamonds']

        rcard = random.choice(card)
        rstyle = random.choice(style)

        fmt = 'You drew the {0} of {1}!'
        if ctx.message.author.id == '193416878717140992':
            card = ['Ace']
            style = ['Hearts']
            rcard = random.choice(card)
            rstyle = random.choice(style)
            if rcard == 'Ace':
                if rstyle == 'Spades':
                    await self.spades(ctx)
                if rstyle == 'Diamonds':
                    await self.diamonds(ctx)
                if rstyle == 'Clubs':
                    await self.clubs(ctx)
                if rstyle == 'Hearts':
                    await self.hearts(ctx)
                return
        await self.client.send_message(ctx.message.channel, fmt.format(rcard, rstyle))
        print('{0} drew the {1} of {2}.'.format(ctx.message.author.name, rcard, rstyle))

    async def spades(self, ctx):
        await self.client.send_message(ctx.message.channel, '***IT\'S THE ACE OF SPADES! THE ACE OF SPADES!!!***')

    async def diamonds(self, ctx):
        """ Move user to the Sparkle, Sparkle role """
        await self.client.send_message(ctx.message.channel, ':sparkles: *Sparkle, Sparkle! *:sparkles: ')
        await discord.Client.add_roles(self.client, ctx.message.author, discord.utils.get(ctx.message.server.roles, name='Sparkle, Sparkle!'))

    async def clubs(self, ctx):
        """ send a channel invite to the user then kick them! """
        d = discord.Client
        await self.client.send_message(ctx.message.channel, 'You\'ve activated my trap card!')

        # send invite link before kick
        link = await self.client.create_invite(destination=ctx.message.channel)
        fmt = 'You activated my trap card!\n{0}'.format(link)
        await self.client.send_message(ctx.message.author, fmt)

        # don't kick the owner
        if ctx.message.author.id == '193416878717140992':
            await self.client.send_message(ctx.message.channel, 'I can\'t kick the owner!')
            return
        # kick!
        await d.kick(self.client, member=ctx.message.author)

    async def hearts(self, ctx):
        # todo fix member call
        await self.client.send_message(ctx.message.channel, ':sparkling_heart: :kissing_heart: :two_hearts: ')
        await self.client.change_nickname(ctx.message.author, '💖_{0}_💖'.format(discord.utils.get(ctx.message.server.members, name='testie')))
        # await discord.Client.change_nickname(self.client, ctx.message.author, nickname='💖 {0} 💖'.format(ctx.message.author.name))


def setup(client):
    client.add_cog(User(client))
