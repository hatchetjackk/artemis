"""
Mod module for administrator commands
"""
import discord
from discord.ext import commands


class Mod:
    extensions = []

    def __init__(self, client):
        self.client = client

    # async def on_message_delete(self, message):
    #     await self.client.send_message(message.channel, "Message deleted.")

    @commands.command(pass_context=True)
    async def test(self, ctx):
        # owner only
        if ctx.message.author.id == "193416878717140992":
            counter = 0
            tmp = await self.client.send_message(ctx.message.channel, "Calculating messages...")
            async for log in self.client.logs_from(ctx.message.channel, limit=100):
                if log.author == ctx.message.author:
                    counter += 1
            await self.client.edit_message(tmp, "You have {0} messages.".format(counter))
        else:
            await self.client.say("You do not have permission to do that.")
            return

    @commands.command(pass_context=True)
    async def load(self, ctx, extension):
        # owner only
        if ctx.message.author.id == "193416878717140992":
            try:
                self.client.load_extension(extension)
            except Exception as error:
                print('{0} cannot be loaded [{1}]'.format(extension, error))
                return
        else:
            await self.client.say("You do not have permission to do that.")
            return
        spam = ['botspam']
        d = discord.Client
        channels = d.client.get_all_channels()
        for channel in channels:
            ch = channel.name
            if ch in spam:
                # pass
                await self.client.say(ctx.channel.message, '{0} loaded.'.format(extension))

    @commands.command(pass_context=True)
    async def unload(self, ctx, extension):
        # owner only
        if ctx.message.author.id == "193416878717140992":
            try:
                self.client.load_extension(extension)
            except Exception as error:
                print('{0} cannot be unloaded [{1}]'.format(extension, error))
                return
        else:
            await self.client.say("You do not have permission to do that.")
            return
        spam = ['botspam']
        d = discord.Client
        channels = d.client.get_all_channels()
        for channel in channels:
            ch = channel.name
            if ch in spam:
                # pass
                await self.client.say(ctx.channel.message, '{0} unloaded.'.format(extension))


    @commands.command(pass_context=True)
    # mods
    async def clear(self, ctx, amount=2):
        mod = '495187511698784257'
        if mod or "193416878717140992" in [role.id for role in ctx.message.author.roles]:
            channel = ctx.message.channel
            messages = []
            async for message in self.client.logs_from(channel, limit=int(amount)):
                messages.append(message)
            await self.client.delete_messages(messages)
        else:
            await self.client.say("You do not have permission to do that.")

    @commands.command(pass_context=True)
    # mods
    async def displayembed(self, ctx):
        mod = '495187511698784257'
        if mod or "193416878717140992" in [role.id for role in ctx.message.author.roles]:
            # hex colors
            # int(767,a76, 16)
            embed = discord.Embed(
                title="Title",
                description="Description",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Footer")
            embed.set_image(url="http://promoboxx.com/compare/images/broken_robot.png")
            embed.set_thumbnail(url="http://promoboxx.com/compare/images/broken_robot.png")
            embed.set_author(name="Author Name", icon_url="http://promoboxx.com/compare/images/broken_robot.png")
            embed.add_field(name="Field Name", value="Field Value", inline=False)
            await self.client.say(embed=embed)
        else:
            await self.client.say("You do not have permission to do that.")


def setup(client):
    client.add_cog(Mod(client))
