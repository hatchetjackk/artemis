import json
from discord.ext import commands


class Mod:
    def __init__(self, client):
        self.client = client

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

    @prefix.error
    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = ':sob: You\'ve triggered a cool down. Please try again in {} sec.'.format(
                int(error.retry_after))
            await ctx.send(msg)
        if isinstance(error, commands.CheckFailure):
            msg = 'You do not have permission to run this command.'
            await ctx.send(msg)

    # async def artemis(self, ctx):
    #     # talk about the bot


def setup(client):
    client.add_cog(Mod(client))
