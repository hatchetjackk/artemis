"""
generate embeds with user input
"""
from discord import Color, Embed, Object
import json
from discord.ext import commands


class RichEmbed:
    color_dict = {
        1: [Color.teal(), 'teal'],
        2: [Color.dark_teal(), 'dark_teal'],
        3: [Color.green(), 'green'],
        4: [Color.dark_green(), 'dark_green'],
        5: [Color.blue(), 'blue'],
        6: [Color.dark_blue(), 'dark_blue'],
        7: [Color.purple(), 'purple'],
        8: [Color.dark_purple(), 'dark_purple'],
        9: [Color.magenta(), 'magenta'],
        10: [Color.dark_magenta(), 'dark_magenta'],
        11: [Color.gold(), 'gold'],
        12: [Color.dark_gold(), 'dark_gold'],
        13: [Color.orange(), 'orange'],
        14: [Color.dark_orange(), 'dark_orange'],
        15: [Color.red(), 'red'],
        16: [Color.dark_red(), 'dark_red'],
        17: [Color.lighter_grey(), 'lighter_grey'],
        18: [Color.dark_grey(), 'grey'],
        19: [Color.light_grey(), 'light_grey'],
        20: [Color.darker_grey(), 'darker_grey']
    }

    def __init__(self, client):
        self.client = client

    @commands.group()
    async def colors(self, ctx):
        colors = RichEmbed.color_dict
        if ctx.invoked_subcommand is None:
            embed = Embed(colors=Color.blue())
            for key, value in colors.items():
                color_num = str(hash(value[0]))
                embed.add_field(name=value[1], value=color_num)
            embed.add_field(name='u2oob', value='Try ``colors full`` for embed examples.\n'
                                                '**WARNING**: This will blow up your DMs!')
            await ctx.author.send(embed=embed)

    @colors.group()
    async def full(self, ctx):
        colors = RichEmbed.color_dict
        await ctx.send('*Incoming!* :boom:')

        for key, value in colors.items():
            color_num = str(hash(value[0]))
            embed = Embed(color=value[0])
            embed.add_field(name=value[1], value=color_num)
            await ctx.author.send(embed=embed)

    @commands.group()
    async def richembed(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invoke `richembed` with `get`, `pasta`, or `example`.')

    @richembed.group()
    async def get(self, ctx, *args):
        msg = await ctx.get_message(id=args[0])
        e_msg = msg.embeds[0].to_dict()
        await ctx.send(e_msg)

    @richembed.group()
    async def pasta(self, ctx, *args):
        msg = ' '.join(args)
        # format for json
        msg = msg.replace('True', 'true')
        msg = msg.replace('False', 'false')
        msg = msg.replace('None', 'null')
        msg = msg.replace('\'', '"')
        d = json.loads(msg)
        embed = Embed.from_data(d)
        await ctx.send(embed=embed)

    @richembed.group()
    async def example(self, ctx):
        embed = Embed(
            title='This is the embed title.',
            description='This is the embed description',
            color=Color.blue()
        )
        embed.set_footer(
            text='This is the footer.'
        )
        embed.set_image(
            url='http://icons.iconarchive.com/icons/papirus-team/papirus-apps/512/discord-icon.png')
        embed.set_thumbnail(
            url='http://icons.iconarchive.com/icons/papirus-team/papirus-apps/512/discord-icon.png')
        embed.set_author(
            name='Author',
            icon_url='http://icons.iconarchive.com/icons/papirus-team/papirus-apps/512/discord-icon.png')
        embed.add_field(
            name='This is the first field name.',
            value='This is the first field name value.',
            inline=False)
        embed.add_field(
            name='This is the second field name.',
            value='This is the second field name value.',
            inline=False)
        embed_dict = embed.to_dict()
        await ctx.send(embed=embed)
        await ctx.send(embed_dict)

    async def on_message(self, message):
        embed = Embed(color=Color.blue())
        # quickembeds!
        if message.content.startswith('>'):
            lines = message.content.split('\n')
            line1 = lines[0]
            title = line1[1:]
            line2 = ' '.join(lines[1:])
            value = line2[1:]
            embed.add_field(name=title, value=value, inline=False)
            embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            await self.client.send_message(Object(id=message.channel.id), embed=embed)

    async def choose_thumb(self, author):
        thumb = await self.client.wait_for(author=author, timeout=60)
        thumb = thumb.clean_content
        return thumb

    async def clear_messages(self, ctx, amount=2):
        mod = '495187511698784257'
        if mod or '193416878717140992' in [role.id for role in ctx.author.roles]:
            messages = []
            async for message in self.client.logs_from(ctx.channel, limit=int(amount)):
                messages.append(message)
            await self.client.delete_messages(messages)
        else:
            await ctx.send('You do not have permission to do that.')

    @staticmethod
    async def check_colors(color):
        colors = {
            1: [Color.teal(), 'teal'],
            2: [Color.dark_teal(), 'dark_teal'],
            3: [Color.green(), 'green'],
            4: [Color.dark_green(), 'dark_green'],
            5: [Color.blue(), 'blue'],
            6: [Color.dark_blue(), 'dark_blue'],
            7: [Color.purple(), 'purple'],
            8: [Color.dark_purple(), 'dark_purple'],
            9: [Color.magenta(), 'magenta'],
            10: [Color.dark_magenta(), 'dark_magenta'],
            11: [Color.gold(), 'gold'],
            12: [Color.dark_gold(), 'dark_gold'],
            13: [Color.orange(), 'orange'],
            14: [Color.dark_orange(), 'dark_orange'],
            15: [Color.red(), 'red'],
            16: [Color.dark_red(), 'dark_red'],
            17: [Color.lighter_grey(), 'lighter_grey'],
            18: [Color.dark_grey(), 'grey'],
            19: [Color.light_grey(), 'light_grey'],
            20: [Color.darker_grey(), 'darker_grey']
        }
        for key, value in colors.items():
            if color == value[1]:
                return True, value[0]
        return False


def setup(client):
    client.add_cog(RichEmbed(client))
