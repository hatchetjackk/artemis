import sqlite3
from discord.ext import commands

import cogs.utilities as utilities


class Users(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['user'])
    async def user_data(self, ctx, user=None):
        """
        Mention @member to return data about that user. If no user is passed, return data about the author
        :param ctx:
        :param user: the username to check
        :return:
        """
        if user is None:
            user = ctx.author

        for member in ctx.guild.members:
            if member.mention == user:
                user = member

        conc, c = await utilities.load_db()
        c.execute("SELECT uid, karma FROM members WHERE uid = (:uid)", {'uid': user.id})
        uid, karma = c.fetchall()[0]

        await utilities.single_embed(
            channel=ctx,
            title='User Info',
            thumb_url=user.avatar_url,
            name=user.name,
            value=f'**Nickname**: {user.nick}\n'
            f'**Karma**: {karma}\n'
            f'**User ID**: {user.id}\n'
            f'**Joined Discord**: {user.created_at}\n'
            f'**Joined {user.guild.name}**: {user.joined_at}\n'
            f'**Roles**: {", ".join([role.name for role in user.roles if role.name != "@everyone"])}'
        )

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
                c.execute("INSERT INTO members VALUES (:uid, :name, :karma, :last_karma)", {
                    'uid': member.id,
                    'name': member.name,
                    'karma': 0,
                    'last_karma': None
                })
            except sqlite3.Error:
                pass

            try:
                c.execute("INSERT INTO guild_members VALUES (:gid, :guild, :uid, :user, :nick)", {
                    'gid': member.guild.id,
                    'guild': member.guild.name,
                    'uid': member.id,
                    'user': member.name,
                    'nick': member.nick
                })
                await utilities.alert_embed(
                    title=f'{member.name} has joined {member.guild.name}.'
                )
            except sqlite3.Error as e:
                print(f'An error occurred when joining {member} to {member.guild}: {e}')
                pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        conn, c = await utilities.load_db()
        with conn:
            try:
                c.execute("DELETE FROM guild_members WHERE gid = (:gid) and uid = (:uid)", {
                    'gid': member.guild.id,
                    'uid': member.id
                })
            except sqlite3.DatabaseError as e:
                print(f'An error occurred when removing {member.name} from {member.guild.name}: {e}')
                pass

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        conn, c = await utilities.load_db()
        if before.name != after.name or before.nick != after.nick:
            with conn:
                c.execute("SELECT karma, last_karma FROM members WHERE uid = (:uid)", {
                    'uid': before.id
                })
                karma, last_karma = c.fetchall()[0]
                try:
                    c.execute("REPLACE INTO members VALUES (:uid, :name, :karma, :last_karma)", {
                        'uid': before.id,
                        'name': after.name,
                        'karma': karma,
                        'last_karma': last_karma
                    })
                except sqlite3.Error as e:
                    print(f'An error occurred when updating {before.member}: {e}')

                try:
                    c.execute("REPLACE INTO guild_members VALUES (:gid, :guild, :uid, :user, :nick)", {
                        'gid': before.guild.id,
                        'guild': before.guild.name,
                        'uid': before.id,
                        'user': after.name,
                        'nick': after.nick
                    })
                    await utilities.alert_embed(
                        title=f'{before.name}/{before.nick} has changed to {after.name}/{after.nick}.'
                    )
                except sqlite3.Error as e:
                    print(f'An error occurred when updating {before.member}: {e}')

    @commands.command()
    @commands.is_owner()
    async def force_user_update(self, ctx):
        conn, c = await utilities.load_db()
        c.execute("SELECT uid FROM guild_members WHERE gid = (:gid)", {'gid': ctx.guild.id})
        guild_members = [mem[0] for mem in c.fetchall()]
        for member in ctx.guild.members:
            if member.id not in guild_members:
                with conn:
                    try:
                        c.execute("INSERT INTO members VALUES (:uid, :name, :karma, :last_karma)", {
                            'uid': member.id,
                            'name': member.name,
                            'karma': 0,
                            'last_karma': None
                        })
                    except Exception as e:
                        print(f'An error occurred when adding {member} to the database using force_user_update: {e}')
                    try:
                        c.execute("INSERT INTO guild_members VALUES (:gid, :guild, :uid, :user, :nick)", {
                            'gid': member.guild.id,
                            'guild': member.guild.name,
                            'uid': member.id,
                            'user': member.name,
                            'nick': member.nick
                        })
                        print(f'Successfully added {member.name} to MEMBERS and GUILD_MEMBERS.')
                    except Exception as e:
                        print(f'An error occurred when adding {member} to the database using force_user_update: {e}')
                await utilities.single_embed(
                    title=f'{member.name} added to \'members\' and {ctx.guild.name}\'s database.',
                    channel=ctx
                )


def setup(client):
    client.add_cog(Users(client))
