import sqlite3
import cogs.utilities as utilities
from datetime import datetime
from discord.ext import commands


class Database(commands.Cog):
    def __init__(self, client):
        self.client = client

    @staticmethod
    @commands.Cog.listener()
    async def on_member_join(member):
        conn, c = await utilities.load_db()
        try:
            with conn:
                c.execute("INSERT INTO members VALUES (:id, :member_name, :karma, :last_karma_given)",
                          {'id': member.id, 'member_name': member.name, 'karma': 0, 'last_karma_given': None})
        except Exception as e:
            fmt = (datetime.now(), member.name, e)
            print('[{}] An error occurred when importing {} into the members database: {}'.format(*fmt))
            raise
        try:
            with conn:
                c.execute("INSERT INTO guild_members VALUES (:id, :guild, :member_id, :member_name, :member_nick)",
                          {'id': member.guild.id, 'guild': member.guild.name, 'member_id': member.id,
                           'member_name': member.name, 'member_nick': member.nick})
        except Exception as e:
            fmt = (datetime.now(), member.name, member.guild.name, e)
            print('[{}] An error occurred when adding {} to {}: {}'.format(*fmt))
            raise

    @staticmethod
    @commands.Cog.listener()
    async def on_member_remove(member):
        conn, c = await utilities.load_db()
        try:
            with conn:
                c.execute("DELETE FROM guild_members WHERE id = (:id) and member_id = (:member_id)",
                          {'id': member.guild.id, 'member_id': member.id})
                print('[{0}] {1.name} has been removed from from {1.guild.name}.'.format(datetime.now(), member))
        except sqlite3.DatabaseError as e:
            fmt = (datetime.now(), member.name, member.guild.name, e)
            print('[{}] An error occurred when removing {} from {}: {}'.format(*fmt))
            raise

    @staticmethod
    @commands.Cog.listener()
    async def on_member_update(before, after):
        conn, c = await utilities.load_db()
        try:
            if before.name != after.name or before.nick != after.nick:
                with conn:
                    c.execute("SELECT karma, last_karma_given FROM members WHERE id = (:id)",
                              {'id': before.id})
                    karma, last_karma = c.fetchall()[0]
                    c.execute("REPLACE INTO members VALUES (:id, :member_name, :karma, :last_karma_given)",
                              {'id': before.id, 'member_name': after.name, 'karma': karma,
                               'last_karma_given': last_karma})
                    c.execute("REPLACE INTO guild_members VALUES (:id, :guild, :member_id, :member_name, :member_nick)",
                              {'id': before.guild.id, 'guild': before.guild.name, 'member_id': before.id,
                               'member_name': after.name, 'member_nick': after.nick})
                    fmt = (datetime.now(), before.guild.name, before.name, before.nick, after.name, after.nick)
                    print('[{}] (Guild: {}) {}/{} has changed to {}/{}.'.format(*fmt))
        except Exception as e:
            print(f'An error occurred when updating {before.name}in the database: {e}')

    @staticmethod
    @commands.Cog.listener()
    async def on_guild_join(guild):
        # get channels
        # find general
        # ask for !Artemis init
        # begin initialization
        conn, c = await utilities.load_db()
        try:
            with conn:
                c.execute("INSERT INTO guilds VALUES (:id, :guild, :mod_role, :autorole, :prefix, :spam, :thumbnail)",
                          {'id': guild.id, 'guild': guild.name, 'mod_role': None,
                           'autorole': None, 'prefix': '!', 'spam': None, 'thumbnail': None})
                print(f'[{datetime.now()}] Artemis has joined the {guild.name} guild!')
        except sqlite3.DatabaseError as e:
            print(f'An error occurred when Artemis joined {guild.name}: {e}')

    @staticmethod
    @commands.Cog.listener()
    async def on_guild_remove(guild):
        print(f'[{datetime.now()}] Artemis has been removed from {guild.name}.')

    @staticmethod
    @commands.Cog.listener()
    async def on_guild_update(before, after):
        conn, c = await utilities.load_db()
        if before.name != after.name:
            with conn:
                c.execute("SELECT mod_role, autorole, prefix, spam, thumbnail FROM guilds WHERE id = (:id)",
                          {'id': before.id})
                mod_role, autorole, prefix, spam, thumbnail = c.fetchall()[0]
                c.execute(
                    "REPLACE INTO guilds VALUES (:id, :guild, :mod_role, :autorole, :prefix, :spam, :thumbnail)",
                    {'id': before.id, 'guild': after.name, 'mod_role': mod_role, 'autorole': autorole, 'prefix': prefix,
                     'spam': spam, 'thumbnail': thumbnail})
                print(f'[{datetime.now()}] The {before.name} guild changed its name to {after.name}.')

    @commands.command()
    @commands.is_owner()
    async def clean_database(self, ctx):
        conn, c = await utilities.load_db()
        with conn:
            c.execute("SELECT member_id, member_name FROM guild_members WHERE id = (:id)", {'id': ctx.guild.id})
            db_member_ids = c.fetchall()
            current_guild_ids = [member.id for member in ctx.guild.members]
            for user in db_member_ids:
                uid, name = user
                if uid not in current_guild_ids:
                    try:
                        c.execute("DELETE FROM guild_members WHERE id = (:id) and member_id = (:member_id)",
                                  {'id': ctx.guild.id, 'member_id': user[0]})
                        print(f'[{datetime.now()}] {name} ({uid}) cleaned from {ctx.guild.name}.')
                    except Exception as e:
                        print(f'An error occurred when attempting to clean the database: {e}')

    @commands.command()
    @commands.is_owner()
    async def force_user_update(self, ctx):
        conn, c = await utilities.load_db()
        c.execute("SELECT member_id FROM guild_members WHERE id = (:id)", {'id': ctx.guild.id})
        guild_members = [mem[0] for mem in c.fetchall()]
        for member in ctx.guild.members:
            if member.id not in guild_members:
                with conn:
                    try:
                        c.execute("INSERT INTO members VALUES (:id, :member_name, :karma, :last_karma_given)",
                                  {'id': member.id, 'member_name': member.name, 'karma': 0, 'last_karma_given': None})
                    except Exception as e:
                        print(f'An error occurred when adding {member} to the database using force_user_update: {e}')
                    try:
                        c.execute(
                            "INSERT INTO guild_members VALUES (:id, :guild, :member_id, :member_name, :member_nick)",
                            {'id': member.guild.id, 'guild': member.guild.name, 'member_id': member.id,
                             'member_name': member.name, 'member_nick': member.nick})
                        print(f'Successfully added {member.name} to MEMBERS and GUILD_MEMBERS.')
                    except Exception as e:
                        print(f'An error occurred when adding {member} to the database using force_user_update: {e}')


def setup(client):
    client.add_cog(Database(client))
