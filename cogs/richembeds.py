"""
generate embeds with user input
"""
from discord import Color, Embed, Object
import json
from discord.ext import commands


class RichEmbed:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def colors(self, ctx, *args):
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
        if len(args) > 0:
            if args[0] == 'full':
                await ctx.send('*Incoming!* :boom:')
                for key, value in colors.items():
                    color_num = str(hash(value[0]))
                    embed = Embed(color=value[0])
                    embed.add_field(name=value[1], value=color_num)
                    await ctx.author.send(embed=embed)
            return
        embed = Embed(colors=Color.blue())
        for key, value in colors.items():
            color_num = str(hash(value[0]))
            embed.add_field(name=value[1], value=color_num)
        embed.add_field(name='u2oob', value='Try ``colors full`` for embed examples.\n'
                                            '**WARNING**: This will blow up your DMs!')
        await ctx.author.send(embed=embed)

    @commands.command()
    async def richembed(self, ctx, *args):
        try:
            if args[0] == 'get':
                msg = await ctx.get_message(id=args[1])
                e_msg = msg.embeds[0].to_dict()
                await ctx.send(e_msg)
                return
        except IndexError as e:
            print(e)
            await ctx.send('An error occurred. Please review your command and try again.')
            return
        try:
            if args[0] == 'pasta':
                msg = ' '.join(args[1:])

                # format for json
                msg = msg.replace('True', 'true')
                msg = msg.replace('False', 'false')
                msg = msg.replace('None', 'null')
                d = json.loads(msg.replace('\'', ''))

                embed = Embed.from_data(d)
                await ctx.send(embed=embed)
                return
        except Exception as e:
            print(e)
            await ctx.send('An error occurred. Please review your command and try again.')
            raise
        try:
            example = ['example', 'ex']
            if args[0] in example:
                embed = Embed(
                    title='This is the embed\'s title.',
                    description='This is the embed description',
                    color=Color.blue()
                )
                embed.set_footer(text='This is the footer')
                embed.set_image(
                    url='http://vignette1.wikia.nocookie.net/pantheonthelegends/images/d/d2/Artemis.png/revision/latest?cb=20130604072452')
                embed.set_thumbnail(
                    url='http://vignette1.wikia.nocookie.net/pantheonthelegends/images/d/d2/Artemis.png/revision/latest?cb=20130604072452')
                embed.set_author(name='Author',
                                 icon_url='http://vignette1.wikia.nocookie.net/pantheonthelegends/images/d/d2/Artemis.png/revision/latest?cb=20130604072452')
                embed.add_field(name='This is the first field name.', value='This is the first field name\'s value.', inline=False)
                embed.add_field(name='This is the second field name.', value='This is the second field name\'s value.', inline=False)
                await ctx.send(embed=embed)
                await ctx.send(embed.to_dict())
        except IndexError as e:
            print(e)
            await ctx.send('An error occurred. Please review your command and try again.')
            return

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
