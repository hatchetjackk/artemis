import discord
from artemis import load_db
from discord.ext import commands


class Automod(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def spam_detection(self):
        # todo add spam detection
        pass

    @staticmethod
    async def automod_blacklist():
        conn, c = await load_db()
        c.execute("SELECT guild FROM auto_mod_blacklist")
        blacklist = [guild[0] for guild in c.fetchall()]
        return blacklist

    @commands.command()
    async def roles(self, ctx):
        roles = [value.name for value in ctx.guild.roles if value.name != '@everyone']
        embed = await self.msg('The roles for {} include\n{}'.format(ctx.guild.name, '\n'.join(roles)))
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        conn, c = await load_db()
        c.execute("SELECT autorole FROM guilds WHERE id = (:id)", {'id': member.guild.id})
        autorole = c.fetchone()[0]
        try:
            if autorole is not None:
                role = discord.utils.get(member.guild.roles, id=autorole)
                await member.add_roles(role)
            else:
                role = None
            spam_channel_id = await self.get_spam_channel(member.guild.id)
            if spam_channel_id is not None:
                msg1 = '{0.name} joined {1}.'.format(member, member.guild)
                msg2 = '{0} was assigned the autorole {1}'.format(member.name, role)
                embed = discord.Embed(color=discord.Color.blue())
                embed.set_thumbnail(url=member.avatar_url)
                embed.add_field(name='Alert', value=msg1, inline=False)
                embed.add_field(name='Alert', value=msg2, inline=False)
                channel = member.guild.get_channel(spam_channel_id)
                await channel.send(embed=embed)
            general_chat = discord.utils.get(member.guild.channels, name='general')
            blacklist = await self.automod_blacklist()
            if member.guild.name not in blacklist:
                await general_chat.send('Welcome to {}, {}!'.format(member.guild.name, member.name))
        except Exception as e:
            print('An error occurred when attempting to give {} the autorole: {}'.format(member.name, e))

    async def on_member_remove(self, member):
        spam_channel_id = await self.get_spam_channel(member.guild.id)
        if spam_channel_id is not None:
            msg = '{0.name} has left {1}.'.format(member, member.guild)
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name='Alert', value=msg, inline=False)
            channel = member.guild.get_channel(spam_channel_id)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        try:
            blacklist = await self.automod_blacklist()
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
    async def msg(msg):
        embed = discord.Embed()
        embed.add_field(name='Watch out!',
                        value=msg,
                        inline=False)
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
