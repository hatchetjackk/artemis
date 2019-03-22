import re
import random
import time
import cogs.utilities as utilities
from collections import OrderedDict
from discord.ext import commands


class Karma(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.karma_blacklist = ['Knights of Karma']

    @commands.group()
    async def karma(self, ctx):
        if ctx.guild.name in self.karma_blacklist:
            return
        if ctx.invoked_subcommand is None:
            await utilities.single_embed(
                color=utilities.color_alert,
                title='Try `karma help` for more options.',
                channel=ctx
            )

    @karma.group()
    async def help(self, ctx):
        await utilities.single_embed(
            color=utilities.color_help,
            name='Karma Help',
            value='`karma help` This menu!\n'
                  '`karma check` Check your own Karma\n'
                  '`karma check [user]` Check a member\'s Karma\n'
                  '`karma board` Check top 10 Karma leaders\n'
                  '`thanks [@user]` Give a member Karma\n',
            channel=ctx
        )

    @karma.group()
    async def check(self, ctx, *, member_check=None):
        conn, c = await utilities.load_db()
        if member_check is None:
            c.execute("SELECT id, karma FROM members WHERE id = (:id)", {'id': ctx.author.id})
            member_id, karma = c.fetchone()
            name = ctx.author.nick
            if name is None:
                name = ctx.author.name
            await utilities.single_embed(
                title=f'You have {karma} karma, {name}!',
                channel=ctx,
            )

        if len(member_check) < 3:
            await utilities.single_embed(
                color=utilities.color_alert,
                title=':heart: Karma Error',
                name='An error occurred when checking karma!',
                value='Please search using 3 or more characters.',
                channel=ctx
            )
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
        name = target_member.name
        if target_member.nick is not None:
            name = target_member.nick
        await utilities.single_embed(
            title=f'{name} has {karma} karma!',
            channel=ctx
        )

    @karma.group(aliases=['leaderboards', 'karmaboard', 'board'])
    async def leaderboard(self, ctx):
        conn, c = await utilities.load_db()
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
            if member_identity != 'Artemis':
                leaderboard[member_identity] = karma
        sorted_karma = OrderedDict(reversed(sorted(leaderboard.items(), key=lambda x: x[1])))
        counter = 1
        karma_leaderboard = []
        for key, value in sorted_karma.items():
            karma_leaderboard.append(f'{counter}: {key} - **{value}** karma')
            counter += 1
        await utilities.single_embed(
            title='Karma Leaderboard Top 10',
            description='\n'.join(karma_leaderboard[:10]),
            channel=ctx
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if (message.author.id == self.client.user.id
                    or message.author.name == 'Dyno'
                    or message.content.startswith('!')
                    or message.guild.name in self.karma_blacklist):
                return

            karma_keywords = ['thanks', 'thank', 'gracias', 'kudos', 'thx', 'appreciate it', 'cheers']
            msg = [word.lower().replace('.', '') for word in message.content.split()]
            karma_key = [word for word in karma_keywords if word in msg]

            if len(karma_key) > 0:
                thanked_members = [member for member in message.guild.members if member.mention in msg]
                if len(thanked_members) > 0:
                    conn, c = await utilities.load_db()

                    c.execute("SELECT * FROM members WHERE id = (:id)", {'id': message.author.id})
                    member_id, membername, points, last_karma_given = c.fetchone()

                    if last_karma_given is not None:
                        remaining_time = int(time.time() - last_karma_given)
                        time_limit = 60 * 3
                        if remaining_time < time_limit:
                            msg = f'You must wait {time_limit - remaining_time} seconds to give karma again.'
                            await message.channel.send(msg)
                            return

                    for member in thanked_members:
                        member_name = member.name
                        if member.nick is not None:
                            member_name = member.nick

                        # catch artemis karma
                        if member.id == self.client.user.id:
                            c.execute("SELECT response FROM bot_responses WHERE message_type = 'client_karma'")
                            client_karma = c.fetchall()
                            msg = random.choice([response[0] for response in client_karma])
                            await utilities.single_embed(title=msg, channel=message.channel)

                        # catch self karma
                        elif member.id == message.author.id:
                            c.execute("SELECT response FROM bot_responses WHERE message_type = 'bad_karma'")
                            bad_karma = c.fetchall()
                            msg = random.choice([response[0] for response in bad_karma]).format(message.author.id)
                            await utilities.single_embed(
                                title=msg,
                                color=utilities.color_alert,
                                channel=message.channel
                            )

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
                            msg = random.choice([response[0] for response in good_responses]).format(member_name)
                            await utilities.single_embed(title=msg, channel=message.channel)
            await self.client.process_commands(message)
        except Exception as e:
            print(f'An unexpected error occurred when giving karma: {e}')
            raise


def setup(client):
    client.add_cog(Karma(client))
