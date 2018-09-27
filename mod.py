"""
Mod module for administrator commands
"""
import discord
from discord.ext import commands


class Mod:
    extensions = []

    def __init__(self, client):
        self.client = client

    async def on_message_delete(self, message):
        await self.client.send_message(message.channel, "Message deleted.")

    @commands.command()
    async def load(self, extension):
        try:
            self.client.load_extension(extension)
        except Exception as error:
            print('{0} cannot be loaded [{1}]'.format(extension, error))

    @commands.command()
    async def unload(self, extension):
        try:
            self.client.load_extension(extension)
        except Exception as error:
            print('{0} cannot be loaded [{1}]'.format(extension, error))

    @commands.command(pass_context=True)
    async def clear(self, ctx, amount=2):
        channel = ctx.message.channel
        messages = []
        async for message in self.client.logs_from(channel, limit=int(amount)):
            messages.append(message)
        await self.client.delete_messages(messages)

    @commands.command()
    async def displayembed(self):
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


def setup(client):
    client.add_cog(Mod(client))
