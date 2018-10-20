"""
For adding and checking karma
"""

import discord
import random
import json
from discord.ext import commands


class Karma:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def karma(self, ctx):
        author = ctx.author
        aid = str(author.id)
        message = ctx.message.content.split()
        members = ctx.guild.members

        with open('files/users.json', 'r') as f:
            users = json.load(f)

        # check another user's karma
        for member in members:
            mid = str(member.id)
            if member.mention in message or member.name.lower() in message:
                if mid in users:
                    await ctx.send('{0} has {1} karma.'.format(member.name, users[mid]['karma']))
                    return

        # check author's karma
        if aid in users:
            points = users[aid]['karma']
            await ctx.send('You have {0} karma.'.format(points))
        else:
            await ctx.send('{} not found.'.format(author.name))

    @commands.command()
    async def leaderboard(self, ctx):
        # todo order top 10 users from most to least karma
        guild = ctx.guild

        embed = discord.Embed(
            title="Karma Leaderboard",
            description="This is a work in progress",
            color=discord.Color.blue()
        )
        with open('files/users.json', 'r') as f:
            users = json.load(f)
            for user in users:
                if str(guild.id) in users[user]['guild']:
                    points = users[user]['karma']
                    user = guild.get_member(user)
                    embed.add_field(name=user.name, value=points, inline=False)
        await ctx.send(embed=embed)

    async def on_message(self, message):
        """ Generate karma!

        This section of code splits messages into lists. It then parses the lists for user mentions. If it finds a 
        user ID in the message, it will search for other keywords from the karma list to determine if a user is 
        thanking  another user. Because of how mentions work, two variants of the user ID have to be passed to 
        catch all users.
        todo allow multiple users to be mentioned in one line
        """
        with open('files/status.json') as f:
            karma_responses = json.load(f)

        with open('files/users.json', 'r') as f:
            data = json.load(f)

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
                    # check if someone is trying to give artemis karma
                    if member.id == self.client.user.id:
                        await message.send(random.choice(karma_responses['karma_responses']['client_response']))
                        return
                    # check if someone is trying to give karma for their self
                    if member.id is author.id:
                        await message.channel.send(random.choice(karma_responses['karma_responses']['bad_response']).format(message.author.id))
                        return
                    # if karma is going to a user and not artemis
                    data[mid]['karma'] += 1

                    with open('files/users.json', 'w') as f:
                        json.dump(data, f, sort_keys=True, indent=2)

                    fmt = random.choice(karma_responses['karma_responses']['good_response']).format(member.name)
                    await message.channel.send(fmt)
                    print("{0} received a karma point from {1}".format(member.name, message.author.name))
                    return


def setup(client):
    client.add_cog(Karma(client))
