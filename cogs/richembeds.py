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

    @commands.command(pass_context=True)
    async def embedwiz(self, ctx):
        await self.client.send_message(ctx.message.channel, 'This command is not ready.')
        return
        # author = ctx.message.author
        #
        # embed = discord.Embed(title='Embed Wizard', color=discord.Color.blue())
        # embed.set_thumbnail(url=self.client.user.avatar_url)
        # embed.add_field(name="Welcome to the embed wizard.",
        #                 value='Please follow the prompts to create a custom embed.')
        # embed.add_field(name="Timeout.",
        #                 value='Please be aware that the timeout is set for 60 seconds.')
        # await self.client.send_message(ctx.message.channel, embed=embed)
        # await asyncio.sleep(3)
        #
        # # set title
        # embed = discord.Embed(title='Your Title Goes Here', color=discord.Color.blue())
        # await self.client.send_message(ctx.message.channel, embed=embed)
        # await self.client.send_message(ctx.message.channel, 'What do you want your title to be?')
        # title = await self.client.wait_for_message(author=author, timeout=60)
        # title = title.clean_content
        # # clear entries
        #
        # # display title embed
        # embed = discord.Embed(title=title, color=discord.Color.blue())
        # await self.client.send_message(ctx.message.channel, embed=embed)
        # while True:
        #     await self.client.send_message(ctx.message.channel,
        #                                    '```'
        #                                    'What color do you want to use? Please choose a number:\n'
        #                                    '[1] Teal, [2] Dark Teal, [3] Green, [4] Dark Green\n'
        #                                    '[5] Blue, [6] Dark Blue, [7] Purple, [8] Dark Purple\n'
        #                                    '[9] Magenta, [10] Dark Magenta, [11] Gold, [12] Dark Gold\n'
        #                                    '[13] Orange, [14] Dark Orange, [15] Red, [16] Dark Red\n'
        #                                    '[17] Lighter Grey, [18] Dark Grey, [19] Light Grey, [20] Darker Grey\n'
        #                                    '```')
        #     num = await self.client.wait_for_message(author=author, timeout=60)
        #     num = int(num.clean_content)
        #     colors = {
        #         1: discord.Color.teal(), 2: discord.Color.dark_teal(), 3: discord.Color.green(), 4: discord.Color.dark_green(),
        #         5: discord.Color.blue(), 6: discord.Color.dark_blue(), 7: discord.Color.purple(), 8: discord.Color.dark_purple(),
        #         9: discord.Color.magenta(), 10: discord.Color.dark_magenta(), 11: discord.Color.gold(), 12: discord.Color.dark_gold(),
        #         13: discord.Color.orange(), 14: discord.Color.dark_orange(), 15: discord.Color.red(), 16: discord.Color.dark_red(),
        #         17: discord.Color.lighter_grey(), 18: discord.Color.dark_grey(), 19: discord.Color.light_grey(), 20: discord.Color.darker_grey()
        #     }
        #     if num in colors:
        #         color = colors[num]
        #         break
        #     else:
        #         await self.client.send_message(ctx.message.channel, '{} is not a valid entry.'.format(num))
        #
        # # thumbnail? [1] server avatar [2] user avatar [3] artemis avatar [4] custom url
        # embed = discord.Embed(title=title, color=color)
        # await self.client.send_message(ctx.message.channel, embed=embed)
        # await self.client.send_message(ctx.message.channel, 'Choose a thumbnail.')
        # while True:
        #     await self.client.send_message(ctx.message.channel,
        #                                    '```'
        #                                    'What color do you want to use? Please choose a number:\n'
        #                                    '[1] Server Avatar\n'
        #                                    '[2] Author Avatar\n'
        #                                    '[3] Artemis\'s Avatar\n'
        #                                    '[4] Custom URL\n'
        #                                    '[5] None'
        #                                    '```')
        #     num = await self.client.wait_for_message(author=author, timeout=60)
        #     num = int(num.clean_content)
        #     thumbs = {
        #         1: ctx.message.server.icon_url,
        #         2: ctx.message.author.avatar_url,
        #         3: self.client.user.avatar_url,
        #         4: await self.choose_thumb(author),
        #         5: None
        #     }
        #     if num in thumbs:
        #         thumb = thumbs[num]
        #         break
        #     else:
        #         await self.client.send_message(ctx.message.channel, '{} is not a valid entry.'.format(num))
        # # clear entries
        #
        # # fields
        # embed = discord.Embed(title=title, color=color)
        # embed.set_thumbnail(url=thumb)
        # await self.client.send_message(ctx.message.channel, embed=embed)
        # # add thumbnail embed, delete previous entries and display current information
        # # while loop for fields
        # # add at least one field
        # # example input, name='test input' value='test input'
        # # add field to a list of fields
        # # do you want to add another field? y/n
        # # no breaks the loops
        # # add footer
        # pass

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
