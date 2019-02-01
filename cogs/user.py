import sqlite3
from datetime import datetime
from artemis import load_db
from discord.ext import commands


class User:
    def __init__(self, client):
        self.client = client

    @staticmethod
    async def on_member_join(member):
        conn, c = await load_db()
        try:
            with conn:
                c.execute("INSERT INTO members VALUES (:id, :member_name, :karma)",
                          {'id': member.id, 'member_name': member.name, 'karma': 0})
        except Exception as e:
            print('[{}] An error occurred when creating a users: {}'.format(datetime.now(), e))
            raise
        try:
            with conn:
                c.execute("INSERT INTO guilds VALUES (:id, :guild, :member_id, :member_name, :member_nick)",
                          {'id': member.guild.id, 'guild': member.guild.name, 'member_id': member.id,
                           'member_name': member.name, 'member_nick': member.nick})
        except Exception as e:
            print('[{}] An error occurred when adding a user to a guild: {}'.format(datetime.now(), e))
            raise

    @staticmethod
    async def on_member_remove(member):
        conn, c = await load_db()
        try:
            with conn:
                c.execute("DELETE FROM guild_members WHERE id = (:id) and member_id = (:member_id)",
                          {'id': member.guild.id, 'member_id': member.id})
                print('[{}] {} has been removed from from {}.'.format(datetime.now(), member.name, member.guild.name))
        except sqlite3.DatabaseError as e:
            print('[{}] An error occurred when removing {} from {}: {}'.format(datetime.now(), member.name, member.guild.name, e))
            raise

    async def on_message(self, message):
        if message.author.id == self.client.user.id:
            return
        if not message.content.startswith('!'):
            await self.update_database(message)

    @staticmethod
    async def update_database(message):
        conn, c = await load_db()
        try:
            with conn:
                c.execute(
                    """CREATE TABLE IF NOT EXISTS members (
                        id INTEGER,
                        member_name TEXT,
                        karma INTEGER,
                        last_karma_given INTEGER
                        UNIQUE(id, member_name)
                        )"""
                )
                c.execute(
                    """CREATE TABLE IF NOT EXISTS guild_members (
                        id INTEGER,
                        guild TEXT,
                        member_id INTEGER,
                        member_name TEXT,
                        member_nick TEXT,
                        UNIQUE(id, guild, member_id)
                        )"""
                )
                c.execute(
                    """CREATE TABLE IF NOT EXISTS guilds (
                        id INTEGER UNIQUE,
                        guild TEXT,
                        mod_role TEXT,
                        autorole TEXT
                        prefix TEXT,
                        spam INTEGER,
                        thumbnail TEXT
                        )"""
                )
        except sqlite3.DatabaseError:
            pass

        for member in message.guild.members:
            # enter data for new members
            try:
                with conn:
                    c.execute("INSERT INTO members VALUES (:id, :member_name, :karma, :last_karma_given)",
                              {'id': member.id, 'member_name': member.name, 'karma': 0, 'last_karma_given': None})
            # if member already exists, check for member_name change
            except sqlite3.IntegrityError:
                with conn:
                    c.execute("SELECT member_name, karma, last_karma_given FROM members WHERE id = (:id)", {'id': member.id})
                    member_name, karma, last_karma = c.fetchall()[0]
                    if member.name != member_name:
                        c.execute("REPLACE INTO members VALUES (:id, :member_name, :karma, :last_karma_given)",
                                  {'id': member.id, 'member_name': member.name, 'karma': karma, 'last_karma_given': last_karma})

            # enter data for a new member associated with their guild
            try:
                with conn:
                    c.execute("INSERT INTO guild_members VALUES (:id, :guild, :member_id, :member_name, :member_nick)",
                              {'id': message.guild.id, 'guild': message.guild.name, 'member_id': member.id,
                               'member_name': member.name, 'member_nick': member.nick})
            # if guild member already exists, check to see if the member_name or member_nick has changed
            except sqlite3.IntegrityError:
                with conn:
                    c.execute("SELECT guild, member_id, member_name, member_nick FROM guild_members WHERE id = (:id) and member_id = (:member_id)",
                              {'id': message.guild.id, 'member_id': member.id})
                    guild_name, member_id, member_name, member_nick = c.fetchall()[0]
                    if member_name != member.name:
                        c.execute("REPLACE INTO guild_members VALUES (:id, :guild, :member_id, :member_name, :member_nick)",
                                  {'id': message.guild.id, 'guild': message.guild.name, 'member_id': member.id,
                                   'member_name': member.name, 'member_nick': member.nick})
                        print('[{}] {} changed their name to {}.'.format(datetime.now(), member_name, member.name))
                    if member_nick != member.nick:
                        c.execute("REPLACE INTO guild_members VALUES (:id, :guild, :member_id, :member_name, :member_nick)",
                                  {'id': message.guild.id, 'guild': message.guild.name, 'member_id': member.id,
                                   'member_name': member.name, 'member_nick': member.nick})
                        print('[{}] {} changed their nickname to {}.'.format(datetime.now(), member_nick, member.nick))

            # enter data for a new guild
            try:
                with conn:
                    c.execute("INSERT INTO guilds VALUES (:id, :guild, :mod_role, :autorole, :prefix, :spam, :thumbnail)",
                              {'id': message.guild.id, 'guild': message.guild.name, 'mod_role': None,
                               'autorole': None, 'prefix': '!', 'spam': None, 'thumbnail': None})
            # if guild id already exists, check if guild name has changed
            except sqlite3.IntegrityError:
                with conn:
                    c.execute("SELECT guild, mod_role, autorole, prefix, spam, thumbnail FROM guilds WHERE id = (:id)",
                              {'id': message.guild.id})
                    guild_name, mod_role, autorole, prefix, spam, thumbnail = c.fetchall()[0]
                    if message.guild.name != guild_name:
                        c.execute("REPLACE INTO guilds VALUES (:id, :guild, :mod_role, :autorole, :prefix, :spam, :thumbnail)",
                                  {'id': message.guild.id, 'guild': message.guild.name, 'mod_role': mod_role,
                                   'autorole': autorole, 'prefix': prefix, 'spam': spam, 'thumbnail': thumbnail})
                        print('[{}] The {} guild changed its name to {}.'.format(datetime.now(), guild_name, message.guild.name))

    @commands.command()
    @commands.is_owner()
    async def clean_database(self, ctx):
        conn, c = await load_db()
        # for member in ctx.guild.members:
        with conn:
            c.execute("SELECT member_id, member_name FROM guild_members WHERE id = (:id)", {'id': ctx.guild.id})
            db_member_ids = c.fetchall()
            current_guild_ids = [member.id for member in ctx.guild.members]
            for user in db_member_ids:
                if user[0] not in current_guild_ids:
                    try:
                        c.execute("DELETE FROM guild_members WHERE id = (:id) and member_id = (:member_id)",
                                  {'id': ctx.guild.id, 'member_id': user[0]})
                        print('[{}] {} ({}) cleaned from {}.'.format(datetime.now(), user[1], user[0], ctx.guild.name))
                    except Exception:
                        raise

    @staticmethod
    async def on_message_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = ':sob: You\'ve triggered a cool down. Please try again in {} sec.'.format(
                int(error.retry_after))
            await ctx.send(msg)
        if isinstance(error, commands.CheckFailure):
            msg = 'You do not have permission to run this command.'
            await ctx.send(msg)


def setup(client):
    client.add_cog(User(client))
