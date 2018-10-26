import json
import discord
from discord.ext import commands


class Mod:
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['spam'])
    @commands.has_any_role('mod', 'Moderators', 'moderator', 'moderators')
    async def botspam(self, ctx, *args):
        try:
            guild = ctx.guild
            gid = str(guild.id)

            data = await self.load_json('guilds')
            if len(args) < 1 or len(args) > 1:
                await ctx.send('Please use `spamchannel channel_name`.')
            if args[0] not in [channel.name for channel in ctx.guild.channels]:
                await ctx.send('{} is not a channel.'.format(args[0]))
                return
            spam = discord.utils.get(guild.channels, name=args[0])
            data[gid]['spam'] = spam.id
            await self.dump_json('guilds', data)
            msg = '{0} changed the botspam channel. It is now {1.mention}'.format(ctx.message.author.name, spam)
            await self.spam(ctx, msg)
        except Exception as e:
            print(e)
            raise

    async def spam(self, ctx, message):
        guild = ctx.guild
        gid = str(guild.id)

        data = await self.load_json('guilds')
        if gid in data:
            if data[gid]['spam'] is not None:
                embed = discord.Embed(color=discord.Color.blue())
                embed.add_field(
                    name='Alert',
                    value=message
                )
                channel = self.client.get_channel(data[gid]['spam'])
                await channel.send(embed=embed)

    # owner command
    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension):
        author = ctx.author

        if author.id == "193416878717140992":
            try:
                self.client.load_extension(extension)
            except Exception as error:
                print('{0} cannot be loaded [{1}]'.format(extension, error))
                return
        else:
            await ctx.send("You do not have permission to do that.")
            return
        spam = ['botspam']
        channels = ctx.get_all_channels()
        for channel in channels:
            ch = channel.name
            if ch in spam:
                # pass
                await ctx.send(ctx.channel.message, '{0} loaded.'.format(extension))

    # owner command
    @commands.command()
    async def unload(self, ctx, extension):
        author = ctx.author

        if author.id == "193416878717140992":
            try:
                self.client.load_extension(extension)
            except Exception as error:
                print('{0} cannot be unloaded [{1}]'.format(extension, error))
                return
        else:
            await ctx.send("You do not have permission to do that.")
            return
        spam = ['botspam']
        channels = ctx.get_all_channels()
        for channel in channels:
            ch = channel.name
            if ch in spam:
                # pass
                await ctx.send(ctx.channel.message, '{0} unloaded.'.format(extension))

    @commands.command()
    @commands.is_owner()
    async def prefix(self, ctx, prefix: str):
        # change the prefix for the guild
        guild = ctx.guild
        gid = str(guild.id)
        with open('files/guilds.json') as f:
            data = json.load(f)
        data[gid]['prefix'] = prefix
        with open('files/guilds.json', 'w') as f:
            json.dump(data, f, indent=2)
        await ctx.send('Changed guild prefix to {}'.format(prefix))

    @staticmethod
    async def load_json(f):
        with open('files/{}.json'.format(f)) as g:
            data = json.load(g)
        return data

    @staticmethod
    async def dump_json(f, data):
        with open('files/{}.json'.format(f), 'w') as g:
            json.dump(data, g, indent=2)

    @prefix.error
    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = ':sob: You\'ve triggered a cool down. Please try again in {} sec.'.format(
                int(error.retry_after))
            await ctx.send(msg)
        if isinstance(error, commands.CheckFailure):
            msg = 'You do not have permission to run this command.'
            await ctx.send(msg)


def setup(client):
    client.add_cog(Mod(client))
