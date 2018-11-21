from artemis import load_db
from discord.ext import commands


class User:
    def __init__(self, client):
        self.client = client

    async def on_member_join(self, member):
        await self.create_user(member)

    async def on_message(self, message):
        if message.author.id == self.client.user.id:
            return
        if not message.content.startswith('!'):
            await self.update_users(message)

    @staticmethod
    async def update_users(message):
        # add: levels, exp, alignment, race, description, hp, char inventory, char equipped
        conn = await load_db()
        c = conn.cursor()
        try:
            with conn:
                c.execute(
                    """CREATE TABLE IF NOT EXISTS members (
                        id INTEGER, 
                        member_name TEXT, 
                        karma INTEGER,
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
                        spam INTEGER
                        )"""
                )
        except Exception as e:
            # print(e)
            pass

        for member in message.guild.members:
            try:
                with conn:
                    c.execute("INSERT INTO members VALUES (:id, :member_name, :karma)",
                              {'id': member.id, 'member_name': member.name, 'karma': 0})
            except Exception as e:
                # print(e)
                pass
            try:
                with conn:
                    c.execute("INSERT INTO guild_members VALUES (:id, :guild, :member_id, :member_name, :member_nick)",
                              {'id': message.guild.id, 'guild': message.guild.name, 'member_id': member.id,
                               'member_name': member.name, 'member_nick': member.nick})
            except Exception as e:
                # print(e)
                pass
            try:
                with conn:
                    c.execute("INSERT INTO guilds VALUES (:id, :guild, :mod_role, :autorole, :prefix, :spam)",
                              {'id': message.guild.id, 'guild': message.guild.name, 'mod_role': None,
                               'autorole': None, 'prefix': '!', 'spam': None})
            except Exception as e:
                # print(e)
                pass

    @staticmethod
    async def create_user(member):
        # add: levels, exp, alignment, race, description, hp, char inventory, char equipped
        conn = await load_db()
        c = conn.cursor()
        with conn:
            try:
                with conn:
                    c.execute("INSERT INTO members VALUES (:id, :member_name, :karma)",
                              {'id': member.id, 'member_name': member.name, 'karma': 0})
            except Exception as e:
                print(e)
                pass
            try:
                with conn:
                    c.execute("INSERT INTO guilds VALUES (:id, :guild, :member_id, :member_name, :member_nick)",
                              {'id': member.guild.id, 'guild': member.guild.name, 'member_id': member.id,
                               'member_name': member.name, 'member_nick': member.nick})
            except Exception as e:
                print(e)
                pass

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
