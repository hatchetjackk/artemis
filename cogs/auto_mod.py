import discord
import sqlite3
from artemis import load_db
from discord.ext import commands


class Automod(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.color_alert = discord.Color.orange()
        self.color_info = discord.Color.dark_blue()

    async def spam_detection(self):
        # todo add spam detection
        pass

    @staticmethod
    async def guild_blacklist():
        conn, c = await load_db()
        c.execute("SELECT guild FROM auto_mod_blacklist")
        blacklist = [guild[0] for guild in c.fetchall()]
        return blacklist

    @commands.command()
    async def roles(self, ctx):
        roles = ['`{}`'.format(value.name) for value in ctx.guild.roles if value.name != '@everyone']
        fmt = [ctx.guild.name, '\n'.join(roles)]
        embed = await self.msg(color=self.color_info,
                               title='Roles',
                               thumb_url=ctx.guild.icon_url,
                               msg='The roles for {0} include:\n{1}'.format(*fmt)
                               )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        conn, c = await load_db()
        c.execute("SELECT autorole, thumbnail FROM guilds WHERE id = (:id)", {'id': member.guild.id})
        autorole_id, thumbnail_url = c.fetchone()[0]
        autorole = None
        try:
            if autorole_id is not None:
                autorole = discord.utils.get(member.guild.roles, id=autorole_id)
                await member.add_roles(autorole)

            spam_channel_id = await self.get_spam_channel(member.guild.id)
            if spam_channel_id is not None:
                channel = member.guild.get_channel(spam_channel_id)
                embed = await self.msg(color=self.color_alert,
                                       thumb_url=member.avatar_url,
                                       title='A New User Has Joined the Server',
                                       msg='{0.name} joined {0.guild}.'.format(member)
                                       )
                await channel.send(embed=embed)
                embed = await self.msg(color=self.color_alert,
                                       thumb_url=member.avatar_url,
                                       title='Autorole Assigned',
                                       msg='{0} was assigned the role {1}'.format(member.name, autorole.name)
                                       )
                await channel.send(embed=embed)
            general_channel = discord.utils.get(member.guild.channels, name='general')
            guild_blacklist = await self.guild_blacklist()
            if member.guild.name not in guild_blacklist:
                await general_channel.send('Welcome to {0.guild.name}, {0.name}!'.format(member))
        except sqlite3.OperationalError as e:
            print('An error occurred with the database: {}'.format(e))
        except Exception as e:
            print('An error occurred when attempting to give {0.name} an autorole: {1}'.format(member, e))
            raise

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        spam_channel_id = await self.get_spam_channel(member.guild.id)
        if spam_channel_id is not None:
            msg = '{0.name} has left {0.guild}.'.format(member)
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name='A Member has Left', value=msg, inline=False)
            spam_channel = member.guild.get_channel(spam_channel_id)
            await spam_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        try:
            blacklist = await self.guild_blacklist()
            if before.guild.name in blacklist or before.author.bot or 'http' in before.content:
                return
            if before.content == '':
                return
            spam_channel_id = await self.get_spam_channel(before.guild.id)
            if spam_channel_id is not None:
                embed = discord.Embed(title='{0} edited a message'.format(after.author.name),
                                      description='in channel {0.mention}.'.format(after.channel),
                                      color=discord.Color.blue())
                embed.set_thumbnail(url=after.author.avatar_url)
                embed.add_field(name='Before', value=before.content, inline=False)
                embed.add_field(name='After', value=after.content, inline=False)
                channel = before.guild.get_channel(spam_channel_id)
                await channel.send(embed=embed)
        except Exception as e:
            print(e)
            raise

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        msg = '{0.author.name}\'s message was deleted:\n' \
              '**Channel**: {0.channel.mention}\n' \
              '**Content**: {0.content}'

        spam_channel_id = await self.get_spam_channel(message.guild.id)
        if spam_channel_id is not None:
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name='Alert', value=msg.format(message))
            channel = message.guild.get_channel(spam_channel_id)
            await channel.send(embed=embed)

    @staticmethod
    async def msg(color=discord.Color.dark_grey(), title='Alert', thumb_url=None, msg=None):
        embed = discord.Embed(color=color)
        if thumb_url is not None:
            embed.set_thumbnail(url=thumb_url)
        embed.add_field(name=title, value=msg, inline=False)
        return embed

    @staticmethod
    async def get_spam_channel(guild_id):
        conn, c = await load_db()
        c.execute("SELECT spam FROM guilds WHERE id = (:id)", {'id': guild_id})
        spam_channel_id = c.fetchone()[0]
        return spam_channel_id

    @commands.Cog.listener()
    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = ':sob: You\'ve triggered a cool down. Please try again in {} sec.'.format(
                int(error.retry_after))
            await ctx.send(msg)
        if isinstance(error, commands.CheckFailure):
            msg = 'You do not have permission to run this command.'
            await ctx.send(msg)


def setup(client):
    client.add_cog(Automod(client))
