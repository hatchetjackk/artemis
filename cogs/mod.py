"""
Mod module for administrator commands
"""
import discord
import json
from discord.ext import commands


class Mod:
    def __init__(self, client):
        self.client = client

    # owner command
    @commands.command()
    async def log(self, ctx):
        author = ctx.author
        channel = ctx.channel

        if author.id == "193416878717140992":
            counter = 0
            tmp = await ctx.send("Calculating messages...")
            async for log in self.client.logs_from(channel, limit=100):
                if log.author == author:
                    counter += 1
            await self.client.edit_message(tmp, "You have {0} messages.".format(counter))
        else:
            await ctx.send("You do not have permission to do that.")
            return

    # owner command
    @commands.command()
    async def test(self, ctx):
        author = ctx.author
        channel = ctx.channel
        guild = ctx.guild

        if author.id == '193416878717140992':
            print('author', author)
            print('channel', channel)
            print('guild', guild)
            print('member', discord.Object(id='496516622903803905'))
            # for role in guild.roles:
            #     print('role', role)
            print('roles', discord.utils.get(guild.roles, name='Sparkle!, Sparkle!'))
            # print('role', discord.utils.get(name='Sparkle!'))
            # print('role', guild.roles(name='Sparkle!'))
            print('dchannel', str(channel))

    # owner command
    # @commands.command()
    # async def load(self, ctx, extension):
    #     author = ctx.author
    #
    #     if author.id == "193416878717140992":
    #         try:
    #             self.client.load_extension(extension)
    #         except Exception as error:
    #             print('{0} cannot be loaded [{1}]'.format(extension, error))
    #             return
    #     else:
    #         await ctx.send("You do not have permission to do that.")
    #         return
    #     spam = ['botspam']
    #     channels = ctx.get_all_channels()
    #     for channel in channels:
    #         ch = channel.name
    #         if ch in spam:
    #             # pass
    #             await ctx.send(ctx.channel.message, '{0} loaded.'.format(extension))

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

    # mod command
    @commands.command()
    async def clear(self, ctx, amount=2):
        author = ctx.author
        channel = ctx.channel

        mod = '495187511698784257'
        if mod or "193416878717140992" in [role.id for role in author.roles]:
            messages = []
            async for message in self.client.logs_from(channel, limit=int(amount)):
                messages.append(message)
            await self.client.delete_messages(messages)
        else:
            await ctx.send("You do not have permission to do that.")

    # mod command
    @commands.command()
    async def displayembed(self, ctx):
        author = ctx.author

        mod = '495187511698784257'
        if mod or "193416878717140992" in [role.id for role in author.roles]:
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
            await ctx.send(embed=embed)
        else:
            await ctx.send("You do not have permission to do that.")

    # owner command
    @commands.command()
    async def prefix(self, ctx, arg):
        author = ctx.author

        if '193416878717140992' in [role.id for role in author.roles]:
            with open('bot.json', 'r') as f:
                bot = json.load(f)
            bot['artemis']['prefix'] = arg
            with open('bot.json', 'w') as f:
                json.dump(bot, f)
        else:
            await ctx.send("You do not have permission to do that.")


def setup(client):
    client.add_cog(Mod(client))
