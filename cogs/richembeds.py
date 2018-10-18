"""
generate embeds with user input
"""
import discord
import asyncio
from _datetime import datetime
import pytz
import json
import random
from discord.ext import commands


class RichEmbed:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def embedex(self):
        embed = discord.Embed(
            title="Title",
            description="Description",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Footer")
        embed.set_image(url="http://vignette1.wikia.nocookie.net/pantheonthelegends/images/d/d2/Artemis.png/revision/latest?cb=20130604072452")
        embed.set_thumbnail(url="http://vignette1.wikia.nocookie.net/pantheonthelegends/images/d/d2/Artemis.png/revision/latest?cb=20130604072452")
        embed.set_author(name="Author", icon_url="http://vignette1.wikia.nocookie.net/pantheonthelegends/images/d/d2/Artemis.png/revision/latest?cb=20130604072452")
        embed.add_field(name="FieldName", value="FieldValue", inline=False)
        await self.client.say(embed=embed)

    @commands.command(pass_context=True)
    async def colors(self, ctx, *args):
        colors = {
            1: [discord.Color.teal(), 'teal'],
            2: [discord.Color.dark_teal(), 'dark_teal'],
            3: [discord.Color.green(), 'green'],
            4: [discord.Color.dark_green(), 'dark_green'],
            5: [discord.Color.blue(), 'blue'],
            6: [discord.Color.dark_blue(), 'dark_blue'],
            7: [discord.Color.purple(), 'purple'],
            8: [discord.Color.dark_purple(), 'dark_purple'],
            9: [discord.Color.magenta(), 'magenta'],
            10: [discord.Color.dark_magenta(), 'dark_magenta'],
            11: [discord.Color.gold(), 'gold'],
            12: [discord.Color.dark_gold(), 'dark_gold'],
            13: [discord.Color.orange(), 'orange'],
            14: [discord.Color.dark_orange(), 'dark_orange'],
            15: [discord.Color.red(), 'red'],
            16: [discord.Color.dark_red(), 'dark_red'],
            17: [discord.Color.lighter_grey(), 'lighter_grey'],
            18: [discord.Color.dark_grey(), 'grey'],
            19: [discord.Color.light_grey(), 'light_grey'],
            20: [discord.Color.darker_grey(), 'darker_grey']
        }
        if len(args) > 0:
            if args[0] == 'full':
                await self.client.send_message(ctx.message.channel, '*Incoming!* :boom:')
                for key, value in colors.items():
                    embed = discord.Embed(color=value[0])
                    embed.add_field(name=value[1], value=value[0])
                    await self.client.send_message(ctx.message.author, embed=embed)
            return
        embed = discord.Embed(colors=discord.Color.blue())
        for key, value in colors.items():
            embed.add_field(name=value[1], value=value[0])
        embed.add_field(name='u2oob', value='Try ``colors full`` for embed examples.\n'
                                            '**WARNING**: This will blow up your DMs!')
        await self.client.send_message(ctx.message.author, embed=embed)

    @commands.command(pass_context=True)
    async def richembed(self, ctx):
        title, color, fieldvalue, fieldname = None, None, None, None
        embed = discord.Embed(title='Rich Embed Creator', color=discord.Color.blue())
        embed.set_thumbnail(url=self.client.user.avatar_url)
        embed.add_field(name='Format', value='keys: \n'
                                             'title=<title>; color=<color>;\n '
                                             'author=<author>; \n'
                                             'footer=<footer>; \n'
                                             'thumbnail=<url>;\n'
                                             'fieldname=<a field title>; fieldvalue=<some text>; \n\n'
                                             'ex: title=This is a title; color=dark_blue; author=Hatchet Jackk \n'
                                             'Use semicolons ` ; ` to split keys.')
        embed.add_field(name='\u200b', value='Please enter your embed string or enter ``quit`` to exit.')
        await self.client.send_message(ctx.message.channel, embed=embed)
        try:
            richembed = await self.client.wait_for_message(author=ctx.message.author)
            richembed = richembed.clean_content

            if richembed == 'quit':
                await self.client.send_message(ctx.message.channel, 'Quitting Rich Embed Creator.')
                return
            lines = [line.strip() for line in richembed.split(';')]
            for line in lines:
                # get color
                if line.lower().startswith('color='):
                    color = line[6:]
                    verify, color = await self.check_colors(color)
                    if not verify:
                        await self.client.send_message(ctx.message.channel, '{} is not a valid color.')
                # get colour
                if line.lower().startswith('colour='):
                    color = line[7:]
                    verify, color = await self.check_colors(color)
                    if not verify:
                        await self.client.send_message(ctx.message.channel, '{} is not a valid color.')
                # get title
                if line.lower().startswith('title='):
                    title = line[6:]
            embed = discord.Embed(title=title, color=color)
            for line in lines:
                # get author
                if line.lower().startswith('author='):
                    author = line[7:]
                    embed.set_author(name=author)
                # get thumb url
                if line.lower().startswith('thumbnail='):
                    thumbnail = line[10:]
                    embed.set_thumbnail(url=thumbnail)
                # get footer
                if line.lower().startswith('footer='):
                    footer = line[7:]
                    embed.set_footer(text=footer)
            for line in lines:
                # get field
                if line.lower().startswith('fieldname='):
                    fieldname = line[10:]
                if line.lower().startswith('fieldvalue='):
                    fieldvalue = line[11:]
            if fieldname is not None and fieldvalue is not None:
                embed.add_field(name=fieldname, value=fieldvalue)
        except TypeError as e:
            print(e)
            await self.client.send_message(ctx.message.channel, 'Embed string was not properly formatted.\n'
                                                                'Quitting.')
            return

        # delete bot and user input before issuing embed
        messages = []
        async for message in self.client.logs_from(ctx.message.channel, limit=int(3)):
            messages.append(message)
        await self.client.delete_messages(messages)
        await self.client.send_message(ctx.message.channel, embed=embed)

    async def on_message(self, message):
        embed = discord.Embed(color=discord.Color.blue())
        # quickembeds!
        if message.content.startswith('>'):
            lines = message.content.split('\n')
            line1 = lines[0]
            title = line1[1:]
            line2 = ' '.join(lines[1:])
            value = line2[1:]
            embed.add_field(name=title, value=value, inline=False)
            embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            await self.client.send_message(discord.Object(id=message.channel.id), embed=embed)

    async def choose_thumb(self, author):
        thumb = await self.client.wait_for_message(author=author, timeout=60)
        thumb = thumb.clean_content
        return thumb

    async def clear_messages(self, ctx, amount=2):
        mod = '495187511698784257'
        if mod or "193416878717140992" in [role.id for role in ctx.message.author.roles]:
            channel = ctx.message.channel
            messages = []
            async for message in self.client.logs_from(channel, limit=int(amount)):
                messages.append(message)
            await self.client.delete_messages(messages)
        else:
            await self.client.say("You do not have permission to do that.")

    @staticmethod
    async def check_colors(color):
        colors = {
            1: [discord.Color.teal(), 'teal'],
            2: [discord.Color.dark_teal(), 'dark_teal'],
            3: [discord.Color.green(), 'green'],
            4: [discord.Color.dark_green(), 'dark_green'],
            5: [discord.Color.blue(), 'blue'],
            6: [discord.Color.dark_blue(), 'dark_blue'],
            7: [discord.Color.purple(), 'purple'],
            8: [discord.Color.dark_purple(), 'dark_purple'],
            9: [discord.Color.magenta(), 'magenta'],
            10: [discord.Color.dark_magenta(), 'dark_magenta'],
            11: [discord.Color.gold(), 'gold'],
            12: [discord.Color.dark_gold(), 'dark_gold'],
            13: [discord.Color.orange(), 'orange'],
            14: [discord.Color.dark_orange(), 'dark_orange'],
            15: [discord.Color.red(), 'red'],
            16: [discord.Color.dark_red(), 'dark_red'],
            17: [discord.Color.lighter_grey(), 'lighter_grey'],
            18: [discord.Color.dark_grey(), 'grey'],
            19: [discord.Color.light_grey(), 'light_grey'],
            20: [discord.Color.darker_grey(), 'darker_grey']
        }
        for key, value in colors.items():
            if color == value[1]:
                return True, value[0]
        return False


def setup(client):
    client.add_cog(RichEmbed(client))
