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
from artemis import load_db
from discord.ext import commands


class Karma:
    def __init__(self, client):
        self.client = client
        self.karma_blacklist = ['Knights of Karma']

    @commands.command()
    async def karma(self, ctx, *, member_check=None):
        if ctx.guild.name in self.karma_blacklist:
            return
        conn, c = await load_db()
        if member_check is None:
            c.execute("SELECT id, karma FROM members WHERE id = (:id)", {'id': ctx.author.id})
            member_id, karma = c.fetchone()
            await ctx.send('You have {0} karma.'.format(karma))
        else:
            if len(member_check) < 3:
                await ctx.send('Please search using 3 or more characters.')
                return
            target_member = ''
            for member_object in ctx.guild.members:
                member_name = member_object.name.lower()
                if member_object.nick is not None:
                    member_name = member_object.nick.lower()
                if member_object.mention in member_check:
                    target_member = member_object
                else:
                    pattern = re.compile(r'' + re.escape(member_check))
                    matches = pattern.findall(member_name)
                    for _ in matches:
                        target_member = member_object
            c.execute("SELECT id, karma FROM members WHERE id = (:id)", {'id': target_member.id})
            member_id, karma = c.fetchone()
            target_member_name = target_member.name
            if target_member.nick is not None:
                target_member_name = target_member.nick
            msg = '{0} has {1} karma.'.format(target_member_name, karma)
            await ctx.send(msg)

    @commands.command(aliases=['leaderboards'])
    async def leaderboard(self, ctx):
        conn, c = await load_db()
        leaderboard = {}
        c.execute("SELECT * FROM guild_members WHERE id = (:id)", {'id': ctx.guild.id})
        guild_members = c.fetchall()
        for member in guild_members:
            guild_id, guild, member_id, member_name, member_nick = member
            c.execute("SELECT member_name, karma FROM members WHERE id = (:id)", {'id': member_id})
            member_name, karma = c.fetchone()
            member_identity = member_nick
            if member_identity is None:
                member_identity = member_name
            leaderboard[member_identity] = karma
        sorted_karma = OrderedDict(reversed(sorted(leaderboard.items(), key=lambda x: x[1])))
        counter = 1
        karma_leaderboard = []
        for key, value in sorted_karma.items():
            karma_leaderboard.append('{}: {} - {} karma'.format(counter, key, value))
            counter += 1
        embed = discord.Embed(title="Karma Leaderboard",
                              color=discord.Color.blue(),
                              description='\n'.join(karma_leaderboard[:10]))
        await ctx.send(embed=embed)
        print('Leaderboard displayed by {} in {}.'.format(ctx.message.author, ctx.guild.name))

    async def on_message(self, message):
        if message.author.id == self.client.user.id:
            return
        if message.content.startswith('!'):
            return
        try:
            if message.guild.name in self.karma_blacklist:
                return
        except Exception as e:
            print('An issue occurred when detecting a guild name in a message: {}'.format(e))
            raise

        conn, c = await load_db()
        keywords = ['thanks', 'thank', 'gracias', 'kudos', 'thx', 'appreciate', 'cheers']
        msg = [word.lower() for word in message.content.split()]
        karma_key = [item for item in keywords if item in msg]

        thanked_members = []
        for member in message.guild.members:
            if member.mention in msg:
                if member not in thanked_members:
                    thanked_members.append(member)
        # check last karma timer
        try:
            c.execute("SELECT * FROM members WHERE id = (:id)", {'id': message.author.id})
            member_id, membername, points, last_karma_given = c.fetchone()
            if last_karma_given is None:
                pass
            else:
                remaining_time = int(time.time() - last_karma_given)
                time_limit = 60 * 3
                if remaining_time < time_limit and len(thanked_members) > 0 and len(karma_key) > 0:
                    msg = 'You must wait {0} seconds to give karma again.'.format(time_limit - remaining_time)
                    await message.channel.send(msg)
                    return
        except TypeError as e:
            print(e)
            pass

        for member in thanked_members:
            member_name = member.name
            if member.nick is not None:
                member_name = member.nick
            if len(karma_key) > 0:
                # check if someone is trying to give artemis karma
                if member.id == self.client.user.id:
                    c.execute("SELECT response FROM bot_responses WHERE message_type = 'client_karma'")
                    client_karma = c.fetchall()
                    msg = random.choice([resp[0] for resp in client_karma])
                    await message.channel.send(msg)
                # check if someone is trying to farm karma
                elif member.id is message.author.id:
                    c.execute("SELECT response FROM bot_responses WHERE message_type = 'bad_karma'")
                    bad_karma = c.fetchall()
                    msg = random.choice([resp[0] for resp in bad_karma]).format(message.author.id)
                    await message.channel.send(msg)
                # if karma is going to a user and not artemis or the author
                else:
                    c.execute("SELECT * FROM members WHERE id = (:id)", {'id': member.id})
                    member_id, membername, points, last_karma_given = c.fetchone()
                    last_karma_given = int(time.time())
                    points += 1
                    with conn:
                        c.execute("UPDATE members SET karma = (:karma) WHERE id = (:id)",
                                  {'karma': points, 'id': member.id})
                        c.execute("UPDATE members SET last_karma_given = (:last_karma_given) WHERE id = (:id)",
                                  {'last_karma_given': last_karma_given, 'id': message.author.id})
                    c.execute("SELECT response FROM bot_responses WHERE message_type = 'good_karma'")
                    good_responses = c.fetchall()
                    msg = random.choice([resp[0] for resp in good_responses]).format(member_name)
                    await message.channel.send(msg)
                    print("{0} received a karma point from {1}".format(member_name, message.author.name))


def setup(client):
    client.add_cog(Karma(client))
