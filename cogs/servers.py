import sqlite3

from discord.ext import commands

import cogs.utilities as utilities


class Servers(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        for channel in guild.channels:
            if channel.name.lower() == 'general':
                await utilities.single_embed(
                    color=utilities.color_alert,
                    title=f'Artemis has joined {guild.name}!',
                    description='Guild owner: Please use `@artemis config` to begin setup.',
                    channel=channel
                )
        conn, c = await utilities.load_db()
        with conn:
            try:
                c.execute("INSERT INTO guilds VALUES (:id, :guild, :mod_role, :autorole, :prefix, :spam, :thumbnail)",
                          {'id': guild.id, 'guild': guild.name, 'mod_role': None,
                           'autorole': None, 'prefix': '!', 'spam': None, 'thumbnail': None})
                print(f'Artemis has joined the {guild.name} guild!')
            except sqlite3.DatabaseError as e:
                print(f'An error occurred when Artemis joined {guild.name}: {e}')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        print(f'Artemis has been removed from {guild.name}.')

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        conn, c = await utilities.load_db()
        if before.name != after.name:
            with conn:
                c.execute("SELECT mod_role, autorole, prefix, spam, thumbnail FROM guilds WHERE id = (:id)",
                          {'id': before.id})
                mod_role, autorole, prefix, spam, thumbnail = c.fetchall()[0]
                try:
                    c.execute(
                        "REPLACE INTO guilds VALUES (:id, :guild, :mod_role, :autorole, :prefix, :spam, :thumbnail)",
                        {'id': before.id, 'guild': after.name, 'mod_role': mod_role, 'autorole': autorole,
                         'prefix': prefix, 'spam': spam, 'thumbnail': thumbnail}
                    )
                    print(f'The {before.name} guild changed its name to {after.name}.')
                except sqlite3.Error as e:
                    print(f'An error occurred on guild update: {e}')

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
                        print(f'{name} ({uid}) cleaned from {ctx.guild.name}.')
                    except Exception as e:
                        print(f'An error occurred when attempting to clean the database: {e}')


def setup(client):
    client.add_cog(Servers(client))
