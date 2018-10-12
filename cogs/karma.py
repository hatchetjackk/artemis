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
        user = ctx.message.author.id
        target = ctx.message.author
        message = ctx.message.content.split()
        members = [member for member in ctx.message.server.members]
        # check another user's karma
        for member in members:
            if member.mention in message:
                target = member.name
                user = member.id
                with open('files/users.json', 'r') as f:
                    users = json.load(f)
                    if user in users:
                        points = users[user]['karma']
                        await self.client.send_message(ctx.message.channel, '{0} has {1} karma.'.format(target, points))
                        return
        # check message author's karma
        with open('files/users.json', 'r') as f:
            users = json.load(f)
            if user in users:
                points = users[user]['karma']
                await self.client.send_message(ctx.message.channel, 'You have {1} karma.'.format(target, points))

    async def generate_karma(self, message):
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
        client_responses = ["You're welcome!",
                            "No problem.",
                            "Anytime!",
                            "Sure thing, fellow human!",
                            "*eats karma* Mmm."]
        bad_response = ["You can't give yourself karma.",
                        "Let's keep things fair here...",
                        "Looks like karma abuse over here.",
                        "Are you trying to farm karma?!"]

        message_word_list = [word.lower() for word in message.content.split()]
        keywords = ['thanks', 'thank', 'gracias', 'kudos', 'thx', 'appreciate', 'cheers']
        karma_key = [item for item in keywords if item in message_word_list]
        user_list = [member for member in message.server.members]
        # check that message contains user names and words
        for user in user_list:
            if user.mention in message_word_list:
                # catch if one or more karma keyword has been passed
                # this prevents a bug that allows  a user to pass karma multiple times in one post
                if len(karma_key) > 0:
                    # check if someone is trying to give artemis karma
                    if user.id is self.client.user.id:
                        await self.client.send_message(message.channel, random.choice(client_responses))
                        return
                    # check if someone is trying to give karma for their self
                    if user.id is message.author.id:
                        await self.client.send_message(message.channel,
                                                       random.choice(bad_response).format(message.author.id))
                        return
                    # if karma is going to a user and not artemis
                    with open('files/users.json', 'r') as f:
                        users = json.load(f)
                    await self.add_karma(users, user)

                    with open('files/users.json', 'w') as f:
                        json.dump(users, f, indent=2)

                    fmt = random.choice(responses).format(user.name)
                    await self.client.send_message(message.channel, fmt)
                    print("{0} received a karma point from {1}".format(user.name, message.author.name))
                    return

    @staticmethod
    async def add_karma(users, user):
        users[user.id]['karma'] += 1

    @staticmethod
    async def username_formatter(username):
        user1 = '<@!{0}>'.format(username)
        user2 = '<@{0}>'.format(username)
        return user1, user2

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

    @commands.command(pass_context=True)
    async def karma_test(self, ctx):
        # owner only
        if ctx.message.author.id == "193416878717140992":
            await self.client.wait_until_ready()
            for x in range(30):
                await self.client.send_message(discord.Object(id="477966302871289866"), "thanks <@193416878717140992>")
                await self.client.send_message(discord.Object(id="477966302871289866"), "thanks <@355055661303988225>")


def setup(client):
    client.add_cog(Karma(client))
