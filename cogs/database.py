import sqlite3
from datetime import datetime
from artemis import load_db
from discord.ext import commands


class Database(commands.Cog):
    def __init__(self, client):
        self.client = client

    @staticmethod
    async def on_member_join(member):
        conn, c = await load_db()
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
    async def on_member_remove(member):
        conn, c = await load_db()
        try:
            with conn:
                c.execute("DELETE FROM guild_members WHERE id = (:id) and member_id = (:member_id)",
                          {'id': member.guild.id, 'member_id': member.id})
                print('[{}] {} has been removed from from {}.'.format(datetime.now(), member.name, member.guild.name))
        except sqlite3.DatabaseError as e:
            fmt = (datetime.now(), member.name, member.guild.name, e)
            print('[{}] An error occurred when removing {} from {}: {}'.format(*fmt))
            raise

    @staticmethod
    async def on_member_update(before, after):
        conn, c = await load_db()
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
            print(e)
            raise

    @staticmethod
    async def on_guild_join(guild):
        conn, c = await load_db()
        try:
            with conn:
                c.execute("INSERT INTO guilds VALUES (:id, :guild, :mod_role, :autorole, :prefix, :spam, :thumbnail)",
                          {'id': guild.id, 'guild': guild.name, 'mod_role': None,
                           'autorole': None, 'prefix': '!', 'spam': None, 'thumbnail': None})
                print('[{}] Artemis has joined the {} guild!'.format(datetime.now(), guild.name))
        except sqlite3.DatabaseError:
            raise

    @staticmethod
    async def on_guild_remove(guild):
        print('[{}] Artemis has been removed from {}.'.format(datetime.now(), guild.name))

    @staticmethod
    async def on_guild_update(before, after):
        conn, c = await load_db()
        if before.name != after.name:
            with conn:
                c.execute("SELECT mod_role, autorole, prefix, spam, thumbnail FROM guilds WHERE id = (:id)",
                          {'id': before.id})
                mod_role, autorole, prefix, spam, thumbnail = c.fetchall()[0]
                c.execute(
                    "REPLACE INTO guilds VALUES (:id, :guild, :mod_role, :autorole, :prefix, :spam, :thumbnail)",
                    {'id': before.id, 'guild': after.name, 'mod_role': mod_role, 'autorole': autorole, 'prefix': prefix,
                     'spam': spam, 'thumbnail': thumbnail})
                print('[{}] The {} guild changed its name to {}.'.format(datetime.now(), before.name, after.name))

    @commands.command()
    @commands.is_owner()
    async def clean_database(self, ctx):
        conn, c = await load_db()
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

    @commands.command()
    @commands.is_owner()
    async def force_user_update(self, ctx):
        conn, c = await load_db()
        c.execute("SELECT member_id, member_name FROM guild_members WHERE id = (:id)", {'id': ctx.guild.id})
        guild_members = c.fetchall()
        for member in ctx.guild.members:
            if member.name not in [db_member[1] for db_member in guild_members]:
                with conn:
                    try:
                        c.execute("INSERT INTO members VALUES (:id, :member_name, :karma, :last_karma_given)",
                                  {'id': member.id, 'member_name': member.name, 'karma': 0, 'last_karma_given': None})
                    except Exception:
                        raise
                    try:
                        c.execute("INSERT INTO guild_members "
                                  "VALUES (:id, :guild, :member_id, :member_name, :member_nick)",
                                  {'id': member.guild.id, 'guild': member.guild.name, 'member_id': member.id,
                                   'member_name': member.name, 'member_nick': member.nick})
                        print('Successfully added {} to MEMBERS and GUILD_MEMBERS.'.format(member.name))
                    except Exception:
                        raise


def setup(client):
    client.add_cog(Database(client))
