import sqlite3

import discord
from discord.ext import commands

import cogs.utilities as utilities


class Automod(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def spam_detection(self):
        # todo add spam detection
        pass

    @staticmethod
    async def guild_blacklist():
        conn, c = await utilities.load_db()
        c.execute("SELECT guild FROM auto_mod_blacklist")
        blacklist = [guild[0] for guild in c.fetchall()]
        return blacklist

    @commands.command()
    async def roles(self, ctx):
        roles = [f'`{value.name}`' for value in ctx.guild.roles if value.name != '@everyone']
        fmt = [ctx.guild.name, '\n'.join(roles)]
        await utilities.single_embed(
            thumb_url=ctx.guild.icon_url,
            name='**Roles**',
            value='The roles for {0} include:\n{1}'.format(*fmt),
            channel=ctx
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        conn, c = await utilities.load_db()
        c.execute("SELECT autorole, thumbnail FROM guilds WHERE gid = (:gid)", {'gid': member.guild.id})
        autorole_id, thumbnail_url = c.fetchone()
        autorole = None
        try:
            if autorole_id is not None:
                autorole = discord.utils.get(member.guild.roles, id=autorole_id)
                await member.add_roles(autorole)

            await utilities.alert_embed(
                thumb_url=member.avatar_url,
                name='**A New User Has Joined the Server**',
                value='{0.name} joined {0.guild}.'.format(member),
                obj=member
            )
            await utilities.alert_embed(
                thumb_url=member.avatar_url,
                name='**Autorole Assigned**',
                value=f'{member.name} was assigned the role {autorole.name}',
                obj=member
            )
            quarantine = discord.utils.get(member.guild.channels, name='quarantine')
            if quarantine is not None:
                guild_blacklist = await self.guild_blacklist()
                if member.guild.name not in guild_blacklist:
                    await utilities.single_embed(
                        title='Welcome to {0.guild.name}, {0.name}!'
                              ' Please make sure you check the #welcome channel. '
                              'If you believe you are supposed to be a member and not a guest, '
                              'ping a mod!'.format(member),
                        channel=quarantine
                    )
            general_channel = discord.utils.get(member.guild.channels, name='general')
            guild_blacklist = await self.guild_blacklist()
            if member.guild.name not in guild_blacklist:
                await utilities.single_embed(
                    title='Welcome to {0.guild.name}, {0.name}! '
                          'Please make sure you read the welcome channel!'.format(member),
                    channel=general_channel
                )
        except sqlite3.OperationalError as e:
            print(f'An error occurred with the database: {e}')
        except Exception as e:
            print(f'An error occurred when attempting to give {member.name} an autorole: {e}')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            await utilities.alert_embed(
                name='**A Member Has Left**',
                thumb_url=member.avatar_url,
                value='{0.name} has left {0.guild}.'.format(member),
                obj=member
            )
        except Exception as e:
            print(f'An error occurred when removing a user: {e}')
            raise

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        try:
            guild_blacklist = await self.guild_blacklist()
            if (before.guild.name in guild_blacklist
                    or before.author.bot
                    or 'http' in before.content
                    or before.content == ''):
                return
            spam_channel_id = await utilities.get_spam_channel(before.guild.id)
            if spam_channel_id is not None:
                spam_channel = before.guild.get_channel(spam_channel_id)
                await utilities.single_embed(
                    thumb_url=after.author.avatar_url,
                    name=f'{after.author.name} edited a message',
                    value=f'**Channel**: {before.channel.mention}\n'
                          f'**Before**: {before.content}\n'
                          f'**After**: {after.content}',
                    channel=spam_channel
                )
        except Exception as e:
            await utilities.alert_embed(
                name='An error occurred when parsing an edited message',
                value=e
            )

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        await utilities.alert_embed(
            thumb_url=message.author.avatar_url,
            name=f'{message.author.name}\'s message was deleted',
            value='**Channel**: {0.channel.mention}\n'
                  '**Content**: {0.content}'.format(message),
            obj=message
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.client.user.id:
            return
        if message.content == '@artemis config':
            await utilities.new_guild_config(message, self.client)

    @commands.Cog.listener()
    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = f':sob: You\'ve triggered a cool down. Please try again in {int(error.retry_after)} sec.'
            await ctx.send(msg)
        if isinstance(error, commands.CheckFailure):
            msg = 'You do not have permission to run this command.'
            await ctx.send(msg)


def setup(client):
    client.add_cog(Automod(client))
