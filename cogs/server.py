import sqlite3

from discord.ext import commands

import cogs.utilities as utilities


class Servers(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['guildinfo'])
    async def server_data(self, ctx):
        """
        Return data about the current guild
        :param ctx:
        :return:
        """
        pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """
        Notify that artemis has joined a server and initiate the configuration. Add the guild to Artemis' database.
        :param guild: The guild that artemis has joined
        :return:
        """
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
                c.execute("INSERT INTO guilds VALUES (:gid, :guild, :modrole, :autorole, :prefix, :spam, :thumbnail)", {
                    'gid': guild.id,
                    'guild': guild.name,
                    'modrole': None,
                    'autorole': None,
                    'prefix': '!',
                    'spam': None,
                    'thumbnail': None
                })
                print(f'Artemis has joined the {guild.name} guild!')
            except sqlite3.DatabaseError as e:
                print(f'An error occurred when Artemis joined {guild.name}: {e}')

            for member in guild.members:
                try:
                    c.execute("INSERT INTO guild_members VALUES(:gid, :guild, :uid, :user, :nick)",
                              {'gid': guild.id,
                               'guild': guild.name,
                               'uid': member.id,
                               'user': member.name,
                               'nick': member.nick})
                except Exception as e:
                    await utilities.err_embed(
                        name=f'Could not add {member.name} to the database',
                        value=e
                    )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        print(f'Artemis has been removed from {guild.name}.')

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        """
        Update guild information in the database
        :param before: The data before the guild updated
        :param after: The data after the guild updated
        :return:
        """
        conn, c = await utilities.load_db()
        if before.name != after.name:
            c.execute("SELECT modrole, autorole, prefix, spam, thumbnail FROM guilds WHERE gid = (:gid)",
                      {'gid': before.id})
            modrole, autorole, prefix, spam, thumbnail = c.fetchall()[0]
            with conn:
                try:
                    c.execute(
                        "REPLACE INTO guilds VALUES (:gid, :guild, :modrole, :autorole, :prefix, :spam, :thumbnail)", {
                            'gid': before.id,
                            'guild': after.name,
                            'modrole': modrole,
                            'autorole': autorole,
                            'prefix': prefix,
                            'spam': spam,
                            'thumbnail': thumbnail
                        })
                    print(f'The {before.name} guild changed its name to {after.name}.')
                except sqlite3.Error as e:
                    print(f'An error occurred on guild update: {e}')

    @commands.command()
    @commands.is_owner()
    async def clean_database(self, ctx):
        """
        Completely wipe the database. This cannot be undone!
        :param ctx:
        :return:
        """
        conn, c = await utilities.load_db()
        with conn:
            c.execute("SELECT uid, user FROM guild_members WHERE gid = (:gid)", {'gid': ctx.guild.id})
            db_member_ids = c.fetchall()
            current_guild_ids = [member.id for member in ctx.guild.members]
            for user in db_member_ids:
                uid, name = user
                if uid not in current_guild_ids:
                    try:
                        c.execute("DELETE FROM guild_members WHERE gid = (:gid) and uid = (:uid)",
                                  {'gid': ctx.guild.id, 'uid': user[0]})
                        print(f'{name} ({uid}) cleaned from {ctx.guild.name}.')
                    except Exception as e:
                        print(f'An error occurred when attempting to clean the database: {e}')


def setup(client):
    client.add_cog(Servers(client))
