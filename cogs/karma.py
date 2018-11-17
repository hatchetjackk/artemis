import discord
import random
import json
import time
from collections import OrderedDict
from artemis import load_json, dump_json
from discord.ext import commands


class Karma:
    def __init__(self, client):
        self.client = client
        self.karma_blacklist = ['Knights of Karma']

    @commands.command()
    async def karma(self, ctx):
        if ctx.guild.name in self.karma_blacklist:
            return
        author = ctx.author
        aid = str(author.id)
        message = ctx.message.content.split()
        members = ctx.guild.members

        users = await load_json('users')

        # check another user's karma
        for member in members:
            mid = str(member.id)
            if member.mention in message or member.name.lower() in message:
                if mid in users:
                    if 'karma' not in users[mid]:
                        users[mid]['karma'] = 0
                        await dump_json('users', users)
                    await ctx.send('{0} has {1} karma.'.format(member.name, users[mid]['karma']))
                    return

        # check author's karma
        if aid in users:
            if 'karma' not in users[aid]:
                users[aid]['karma'] = 0
            points = users[aid]['karma']
            await ctx.send('You have {0} karma.'.format(points))
        else:
            await ctx.send('{} not found.'.format(author.name))

    @commands.command()
    async def leaderboard(self, ctx):
        guild = ctx.guild
        data = await load_json('users')
        leaderboard = {}
        for user in data:
            if str(guild.id) in data[user]['guild']:
                if 'karma' not in data[user]:
                    data[user]['karma'] = 0
                    await dump_json('users', data)
                points = data[user]['karma']
                user = guild.get_member(int(user))
                if user.nick is not None:
                    leaderboard[user.nick] = points
                else:
                    leaderboard[user.name] = points
        sorted_karma = OrderedDict(reversed(sorted(leaderboard.items(), key=lambda x: x[1])))
        counter = 1
        karma_leaderboard = []
        for key, value in sorted_karma.items():
            karma_leaderboard.append('{}: {} - {} points'.format(counter, key, value))
            counter += 1
        embed = discord.Embed(
            title="Karma Leaderboard",
            color=discord.Color.blue(),
            description='\n'.join(karma_leaderboard[:10])
        )
        await ctx.send(embed=embed)

        print(karma_leaderboard)

        # embed.add_field(name=user.name, value=points, inline=False)
        # await ctx.send(embed=embed)

    async def on_message(self, message):
        """ Generate karma!

        This section of code splits messages into lists. It then parses the lists for user mentions. If it finds a
        user ID in the message, it will search for other keywords from the karma list to determine if a user is
        thanking  another user. Because of how mentions work, two variants of the user ID have to be passed to
        catch all users.
        todo allow multiple users to be mentioned in one line
        """
        if message.guild.name in self.karma_blacklist:
            return
        karma_responses = await load_json('status')
        data = await load_json('users')

        # ignore the bot
        author = message.author
        if author.id == self.client.user.id:
            return

        msg = [word.lower() for word in message.content.split()]
        keywords = ['thanks', 'thank', 'gracias', 'kudos', 'thx', 'appreciate', 'cheers']
        karma_key = [item for item in keywords if item in msg]

        # check that message contains user names and words
        for member in message.guild.members:
            mid = str(member.id)
            if member.mention in msg or member.name.lower() in msg:
                # catch if one or more karma keyword has been passed
                # this prevents a bug that allows  a user to pass karma multiple times in one post
                if len(karma_key) > 0:
                    if 'last_karma_give' not in data[str(author.id)]:
                        pass
                    else:
                        last_karma_give = data[str(author.id)]['last_karma_give']
                        remaining_time = int(time.time() - last_karma_give)
                        time_limit = 60 * 3
                        if remaining_time < time_limit:
                            msg = 'You must wait {0} seconds to give karma again.'.format(time_limit - remaining_time)
                            await message.channel.send(msg)
                            return
                    # check if someone is trying to give artemis karma
                    if member.id == self.client.user.id:
                        await message.channel.send(random.choice(karma_responses['karma_responses']['client_response']))
                    # check if someone is trying to give karma for their self
                    elif member.id is author.id:
                        await message.channel.send(
                            random.choice(karma_responses['karma_responses']['bad_response']).format(message.author.id))
                    # if karma is going to a user and not artemis or the author
                    else:
                        if 'karma' not in data[mid]:
                            data[mid]['karma'] = 0
                        data[mid]['karma'] += 1
                        data[str(author.id)]['last_karma_give'] = time.time()
                        await dump_json('users', data)
                        fmt = random.choice(karma_responses['karma_responses']['good_response']).format(member.name)
                        await message.channel.send(fmt)
                        print("{0} received a karma point from {1}".format(member.name, message.author.name))


def setup(client):
    client.add_cog(Karma(client))
