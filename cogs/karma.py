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

    @commands.command(pass_context=True)
    async def karma(self, ctx):
        """ Check karma points """
        author = ctx.message.author
        message = ctx.message.content.split()
        members = ctx.message.server.members
        # check another user's karma
        for member in members:
            if member.mention in message or member.name.lower() in message:
                with open('files/users.json', 'r') as f:
                    users = json.load(f)
                    if member.id in users:
                        await self.client.send_message(ctx.message.channel,
                                                       '{0} has {1} karma.'.format(member.name,
                                                                                   users[member.id]['karma']))
                        return
        # check author's karma
        with open('files/users.json', 'r') as f:
            users = json.load(f)
            if author.id in users:
                points = users[author.id]['karma']
                await self.client.send_message(ctx.message.channel, 'You have {0} karma.'.format(points))

    @commands.command(pass_context=True)
    async def leaderboard(self, ctx):
        # todo order top 10 users from most to least karma
        embed = discord.Embed(
            title="Karma Leaderboard",
            description="This is a work in progress",
            color=discord.Color.blue()
        )
        with open('files/users.json', 'r') as f:
            users = json.load(f)
            for user in users:
                if str(ctx.message.server) in users[user]['server']:
                    points = users[user]['karma']
                    user = ctx.message.server.get_member(user)
                    embed.add_field(name=user.name, value=points, inline=False)
        await self.client.say(embed=embed)

    async def on_message(self, message):
        """ Generate karma!

        This section of code splits messages into lists. It then parses the lists for user mentions. If it finds a 
        user ID in the message, it will search for other keywords from the karma list to determine if a user is 
        thanking  another user. Because of how mentions work, two variants of the user ID have to be passed to 
        catch all users.
        todo allow multiple users to be mentioned in one line
        """
        responses = [":sparkles: You earned some karma, {0}!",
                     ":sparkles: Cha-ching! You got some karma, {0}!",
                     ":sparkles: What's that? Sounds like that karma train, {0}!",
                     ":sparkles: +1 karma for {0}!"]
        client_responses = ["You're welcome!", "No problem.",
                            "Anytime!", "Sure thing, fellow human!",
                            "*eats karma* Mmm.", 'I try!', 'I do it for the kudos!', ':wink:',
                            'Appreciate it!', 'You got it!', ':smile:', 'Yeet!'
                            ]
        bad_response = ["You can't give yourself karma.",
                        "Let's keep things fair here...",
                        "Looks like karma abuse over here.",
                        "Are you trying to farm karma?!"]

        msg = [word.lower() for word in message.content.split()]
        keywords = ['thanks', 'thank', 'gracias', 'kudos', 'thx', 'appreciate', 'cheers']
        karma_key = [item for item in keywords if item in msg]
        members = message.server.members
        # check that message contains user names and words
        for member in members:
            if member.mention in msg or member.name.lower() in msg:
                # catch if one or more karma keyword has been passed
                # this prevents a bug that allows  a user to pass karma multiple times in one post
                if len(karma_key) > 0:
                    # check if someone is trying to give artemis karma
                    if member.id == self.client.user.id:
                        await self.client.send_message(message.channel, random.choice(client_responses))
                        return
                    # check if someone is trying to give karma for their self
                    if member.id is message.author.id:
                        await self.client.send_message(message.channel,
                                                       random.choice(bad_response).format(message.author.id))
                        return
                    # if karma is going to a user and not artemis
                    with open('files/users.json', 'r') as f:
                        data = json.load(f)

                        data[member.id]['karma'] += 1

                    with open('files/users.json', 'w') as f:
                        json.dump(data, f, indent=2)

                    fmt = random.choice(responses).format(member.name)
                    await self.client.send_message(message.channel, fmt)
                    print("{0} received a karma point from {1}".format(member.name, message.author.name))
                    return


def setup(client):
    client.add_cog(Karma(client))
