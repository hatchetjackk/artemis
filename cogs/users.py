import sqlite3

from discord.ext import commands

import cogs.utilities as utilities


class Users(commands.Cogs):
    def __init__(self, client):
        self.client = client

    def xp(self):
        pass

    def level(self):
        pass

    def reputation(self):
        pass

    def credits(self):
        pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        conn, c = await utilities.load_db()
        with conn:
            try:
                c.execute("INSERT INTO members VALUES (:id, :member_name, :karma, :last_karma_given)",
                          {'id': member.id, 'member_name': member.name, 'karma': 0, 'last_karma_given': None})
            except sqlite3.Error:
                pass
            try:
                c.execute("INSERT INTO guild_members VALUES (:id, :guild, :member_id, :member_name, :member_nick)",
                          {'id': member.guild.id, 'guild': member.guild.name, 'member_id': member.id,
                           'member_name': member.name, 'member_nick': member.nick})
            except sqlite3.Error as e:
                print(f'An error occurred when joining {member} to {member.guild}: {e}')
                raise

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        conn, c = await utilities.load_db()
        with conn:
            try:
                c.execute("DELETE FROM guild_members WHERE id = (:id) and member_id = (:member_id)",
                          {'id': member.guild.id, 'member_id': member.id})
            except sqlite3.DatabaseError as e:
                print(f'An error occurred when removing {member.name} from {member.guild.name}: {e}')
                raise

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        conn, c = await utilities.load_db()
        if before.name != after.name or before.nick != after.nick:
            with conn:
                c.execute("SELECT karma, last_karma_given FROM members WHERE id = (:id)",
                          {'id': before.id})
                karma, last_karma = c.fetchall()[0]
                try:
                    c.execute("REPLACE INTO members VALUES (:id, :member_name, :karma, :last_karma_given)",
                              {'id': before.id, 'member_name': after.name, 'karma': karma,
                               'last_karma_given': last_karma})
                except sqlite3.Error as e:
                    print(f'An error occurred when updating {before.member}: {e}')

                try:
                    c.execute("REPLACE INTO guild_members VALUES (:id, :guild, :member_id, :member_name, :member_nick)",
                              {'id': before.guild.id, 'guild': before.guild.name, 'member_id': before.id,
                               'member_name': after.name, 'member_nick': after.nick})
                    print('({0.guild.name}) {0.name}/{0.nick} has changed to {1.name}/{1.nick}.'.format(before, after))
                except sqlite3.Error as e:
                    print(f'An error occurred when updating {before.member}: {e}')

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
    client.add_cog(Users(client))
