import discord
import random
import urllib.request
import urllib.parse
import re
from discord.ext import commands
from datetime import datetime, timedelta


class User:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def afk(self):
        # set status to away with a message to respond to users that mention the afk user
        # return from afk when sending a message
        pass

    @commands.command()
    async def flip(self, ctx):
        # return heads or tails
        choice = ['Heads!', 'Tails!']
        coin = random.choice(choice)
        print('{0} flipped a coin.'.format(ctx.author.name))
        await ctx.send(coin)

    @commands.command()
    async def google(self):
        # pull the first link from a google search (ie feeling lucky)
        pass

    @commands.command()
    async def image(self):
        # pull the first image from a google search
        pass

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

    @commands.command()
    async def whois(self, ctx, *args):
        try:
            user = ctx.guild.get_member_named(' '.join(args).replace('@', ''))
            members_lower_case = [member.name.lower() for member in ctx.guild.members]
            for member in ctx.guild.members:
                if member.mention in ' '.join(args):
                    user = member
            embed = discord.Embed(title=user.name, color=discord.Color.blue())
            embed.set_thumbnail(url=user.avatar_url)
            created = user.created_at.strftime('%H:%M UTC - %B %d, %Y')
            # calculate lifetime as a user
            lifetime = datetime.utcnow() - user.created_at
            days = lifetime.days
            years, days = divmod(days, 365)
            hours, remainder = divmod(lifetime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            embed.add_field(name='User Since',
                            value='{} \n'
                                  'Lifetime: {} years, {} days, {} minutes, {} seconds'.format(created, years, days, hours, minutes, seconds),
                            inline=False)

            joined = user.joined_at.strftime('%H:%M UTC - %B %d, %Y')
            lifetime = datetime.utcnow() - user.joined_at
            days = lifetime.days
            years, days = divmod(days, 365)
            hours, remainder = divmod(lifetime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            embed.add_field(name='Joined',
                            value='{} \n'
                                  'Lifetime: {} years, {} days, {} minutes, {} seconds'.format(joined, years, days, hours, minutes, seconds),
                            inline=False)

            role_list = [role.name for role in user.roles if role.name != '@everyone']
            embed.add_field(name='Roles',
                            value=', '.join(role_list))
            await ctx.send(embed=embed)
        except AttributeError as e:
            print(e)
            await ctx.send('User not found. Double check your spelling.')

    @commands.command()
    async def yt(self, ctx, *args):
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
        if ctx.author.id == '193416878717140992':
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
        await ctx.send(fmt.format(rcard, rstyle))
        print('{0} drew the {1} of {2}.'.format(ctx.author.name, rcard, rstyle))

    @staticmethod
    async def spades(ctx):
        await ctx.send('***IT\'S THE ACE OF SPADES! THE ACE OF SPADES!!!***')

    async def diamonds(self, ctx):
        """ Move user to the Sparkle, Sparkle role """
        await ctx.send(':sparkles: *Sparkle, Sparkle! *:sparkles: ')
        await discord.Member.add_roles(
            self.client,
            ctx.author,
            discord.utils.get(
                ctx.guild.roles,
                name='Sparkle, Sparkle!')
        )

    async def clubs(self, ctx):
        """ send a channel invite to the user then kick them! """
        await ctx.send('You\'ve activated my trap card!')

        # send invite link before kick
        link = await self.client.create_invite(destination=ctx.channel)
        fmt = 'You activated my trap card!\n{0}'.format(link)
        await ctx.author.send(fmt)

        # don't kick the owner
        if ctx.author.id == '193416878717140992':
            await ctx.send('I can\'t kick the owner!')
            return
        # kick!
        await discord.Member.kick(self.client, member=ctx.author)

    async def hearts(self, ctx):
        # todo fix member call
        await ctx.send(':sparkling_heart: :kissing_heart: :two_hearts: ')
        await self.client.change_nickname(
            ctx.author, '💖_{0}_💖'.format(
                discord.utils.get(
                    ctx.guild.members,
                    name='testie')
            )
        )
        # await discord.Client.change_nickname(self.client, ctx.author, nickname='💖 {0} 💖'.format(ctx.author.name))


def setup(client):
    client.add_cog(User(client))
