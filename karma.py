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

    async def on_message(self, message):
        with open('users.json', 'r') as f:
            users = json.load(f)
        members = [member for member in message.server.members]
        for member in members:
            await self.update_data(users, member)

        with open('users.json', 'w') as f:
            json.dump(users, f)

        author = message.author.id
        artemis = self.client.user.id
        # stop the client from looping with itself
        # if message.author == client.user:
        #     return
        # only check messages that do not start with the command
        if not message.content.startswith("!"):

            """ Generate karma!

            This section of code splits messages into lists. It then parses the lists for user mentions. If it finds a 
            user ID in the message, it will search for other keywords from the karma list to determine if a user is 
            thanking  another user. Because of how mentions work, two variants of the user ID have to be passed to 
            catch all users.
            """
            # generate lists
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
                            "Let's keep things fair here {0}...",
                            "Looks like karma abuse over here."]
            # karma_database = read_csv("karma.csv")
            message_word_list = [word.lower() for word in message.content.split()]
            karma_keywords = ["thanks", "thank", "gracias", "kudos", "thx", "appreciate"]
            user_list = [member for member in message.server.members]
            # check that message contains user names and words
            for user in user_list:
                # format user IDs to match mentionable IDs
                (user1, user2) = await self.username_formatter(user.id)

                if user1 in message_word_list:
                    karma_key = [item for item in karma_keywords if item in message_word_list]
                    # catch if one or more karma keyword has been passed
                    # this prevents a bug that allows  a user to pass karma multiple times in one post
                    if len(karma_key) > 0:
                        # check if someone is trying to give artemis karma
                        if user.id == artemis:
                            await self.client.send_message(message.channel, random.choice(client_responses))
                            return
                        # check if someone is trying to give karma for their self
                        if user.id == author:
                            await self.client.send_message(message.channel, random.choice(bad_response).format(author))
                            return
                        # if karma is going to a user and not artemis
                        with open('users.json', 'r') as f:
                            users = json.load(f)
                        await self.add_karma(users, user)
                        with open('users.json', 'w') as f:
                            json.dump(users, f)
                        fmt = random.choice(responses).format(user.mention)
                        await self.client.send_message(message.channel, fmt)
                        print("{0} received a karma point from {1}".format(user, message.author))

                if user2 in message_word_list:
                    karma_keys = [item for item in karma_keywords if item in message_word_list]
                    # catch if one or more karma keyword has been passed
                    # this prevents a bug that allows  a user to pass karma multiple times in one post
                    if len(karma_keys) > 0:
                        if user.id == author:
                            await self.client.send_message(message.channel, random.choice(bad_response))
                            return
                        with open('users.json', 'r') as f:
                            users = json.load(f)
                        await self.add_karma(users, user)
                        with open('users.json', 'w') as f:
                            json.dump(users, f)
                        fmt = random.choice(responses).format(user.mention)
                        await self.client.send_message(message.channel, fmt)
                        print("{0} received a karma point from {1}".format(user, message.author))
            await self.client.process_commands(message)

    @staticmethod
    async def update_data(users, user):
        if user.id not in users:
            users[user.id] = {}
            users[user.id]['karma'] = 0

    @staticmethod
    async def add_karma(users, user):
        users[user.id]['karma'] += 1

    async def username_formatter(self, username):
        user1 = '<@!{0}>'.format(username)
        user2 = '<@{0}>'.format(username)
        return user1, user2


def setup(client):
    client.add_cog(Karma(client))
