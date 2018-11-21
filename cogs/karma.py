""" Generate karma!

This section of code splits messages into lists. It then parses the lists for user mentions. If it finds a
user ID in the message, it will search for other keywords from the karma list to determine if a user is
thanking  another user. Because of how mentions work, two variants of the user ID have to be passed to
catch all users.
"""

import re
import discord
import random
import time
from collections import OrderedDict
from artemis import load_json, dump_json, load_db
from discord.ext import commands


class Karma:
    def __init__(self, client):
        self.client = client
        self.karma_blacklist = ['Knights of Karma']

    @commands.command()
    async def karma(self, ctx, *args):
        if ctx.guild.name in self.karma_blacklist:
            return
        member_check = ' '.join(args)
        conn = await load_db()
        c = conn.cursor()
        with conn:
            if member_check == '':
                c.execute("SELECT karma FROM members WHERE id = (:id)", {'id': ctx.author.id})
                points = c.fetchone()[0]
                await ctx.send('You have {0} karma.'.format(points))
            else:
                if len(member_check) < 3:
                    await ctx.send('Please search using 3 or more characters.')
                    return
                target_member = ''
                for member in ctx.guild.members:
                    member_name = member.name.lower()
                    if member.nick is not None:
                        member_name = member.nick.lower()
                    if member.mention in member_check:
                        target_member = member
                    else:
                        pattern = re.compile(r'' + re.escape(member_check))
                        matches = pattern.findall(member_name)
                        for _ in matches:
                            target_member = member
                c.execute("SELECT karma FROM members WHERE id = (:id)", {'id': target_member.id})
                points = c.fetchone()[0]
                target_member_name = target_member.name
                if target_member.nick is not None:
                    target_member_name = target_member.nick
                msg = '{0} has {1} karma.'.format(target_member_name, points)
                await ctx.send(msg)

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
            karma_leaderboard.append('{}: {} - {} karma'.format(counter, key, value))
            counter += 1
        embed = discord.Embed(
            title="Karma Leaderboard",
            color=discord.Color.blue(),
            description='\n'.join(karma_leaderboard[:10])
        )
        await ctx.send(embed=embed)

    async def on_message(self, message):
        if message.guild.name in self.karma_blacklist:
            return
        author = message.author
        if author.id == self.client.user.id:
            return

        conn = await load_db()
        c = conn.cursor()

        karma_responses = await load_json('status')
        # data = await load_json('users')

        keywords = ['thanks', 'thank', 'gracias', 'kudos', 'thx', 'appreciate', 'cheers']
        msg = [word.lower() for word in message.content.split() if len(word) >= 3]
        karma_key = [item for item in keywords if item in msg]

        thanked_members = []
        # check that message contains user names and words
        for member in message.guild.members:
            if member.mention in msg:
                if member not in thanked_members:
                    thanked_members.append(member)
            else:
                for word in msg:
                    if len(word) > 3:
                        pattern = re.compile(r'' + re.escape(word))
                        if member.nick is not None:
                            matches = pattern.findall(member.nick.lower())
                        else:
                            matches = pattern.findall(member.name.lower())
                        for _ in matches:
                            if member not in thanked_members:
                                thanked_members.append(member)
        for member in thanked_members:
            # mid = str(member.id)
            # format member name
            member_name = member.name
            if member.nick is not None:
                member_name = member.nick
            if len(karma_key) > 0:
                print(1)
                # check karma cool down
                c.execute("SELECT * FROM members WHERE id = (:id)", {'id': message.author.id})
                member_id, membername, points, last_karma_given = c.fetchone()
                if last_karma_given is None:
                    pass
                else:
                    remaining_time = int(time.time() - last_karma_given)
                    time_limit = 60 * 3
                    if remaining_time < time_limit:
                        msg = 'You must wait {0} seconds to give karma again.'.format(time_limit - remaining_time)
                        await message.channel.send(msg)
                        return
                # check if someone is trying to give artemis karma
                if member.id == self.client.user.id:
                    await message.channel.send(random.choice(karma_responses['karma_responses']['client_response']))
                # check if someone is trying to farm karma
                elif member.id is author.id:
                    msg = random.choice(karma_responses['karma_responses']['bad_response']).format(message.author.id)
                    await message.channel.send(msg)
                # if karma is going to a user and not artemis or the author
                else:
                    with conn:
                        c.execute("SELECT * FROM members WHERE id = (:id)", {'id': member.id})
                        member_id, membername, points, last_karma_given = c.fetchone()
                        last_karma_given = int(time.time())
                        points += 1
                        c.execute("UPDATE members SET karma = (:karma), last_karma_given = (:last_karma_given) WHERE id = (:id)",
                                  {'karma': points, 'last_karma_given': last_karma_given, 'id': member.id})
                        msg = random.choice(karma_responses['karma_responses']['good_response']).format(member_name)
                        await message.channel.send(msg)
                        print("{0} received a karma point from {1}".format(member_name, message.author.name))
                        return


def setup(client):
    client.add_cog(Karma(client))
