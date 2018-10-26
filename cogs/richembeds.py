import json
import discord
from discord import Color, Embed
from discord.ext import commands


class RichEmbed:

    def __init__(self, client):
        self.client = client
        self.client_color = Color.red()
        self.color_dict = {
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

    @commands.group(aliases=['colours', 'color', 'colour'])
    async def colors(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = Embed(colors=Color.blue())
            for key, value in self.color_dict.items():
                color_num = str(hash(value[0]))
                embed.add_field(name=value[1], value=color_num)
            embed.add_field(name='\u200b',
                            value='Try ``colors full`` for embed examples.\n'
                                  '**WARNING**: This will blow up your DMs!')
            await ctx.author.send(embed=embed)

    @colors.group()
    async def full(self, ctx):
        await ctx.send('*Incoming!* :boom:')
        for key, value in self.color_dict.items():
            color_num = str(hash(value[0]))
            embed = Embed(color=value[0])
            embed.add_field(name=value[1], value=color_num)
            await ctx.author.send(embed=embed)

    @commands.group()
    async def richembed(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invoke `richembed` with `get`, `pasta`, or `example`.')

    @richembed.group(aliases=['wiz', 'w'])
    async def wizard(self, ctx):
        message = ctx.message
        channel = ctx.channel

        footer_text = None
        color = discord.Color.blue()

        def check(m):
            return m.author == message.author and m.channel == channel

        tut_embed = await self.tut_embed('Pick a color for the embed (ie dark_blue):')
        await ctx.send(embed=tut_embed)
        msg = await self.client.wait_for('message', check=check)
        if len(msg.content) == 7:
            color = int(msg.content)
        for key, value in self.color_dict.items():
            if msg.content == value[1]:
                color = value[0]

        tut_embed = await self.tut_embed('Set your title: ')
        await ctx.send(embed=tut_embed)
        msg = await self.client.wait_for('message', check=check)
        title = msg.content

        tut_embed = await self.tut_embed('Set your description. To skip this enter "None": ')
        await ctx.send(embed=tut_embed)
        msg = await self.client.wait_for('message', check=check)
        description = msg.content

        embed = discord.Embed(title=title, color=color)
        if description.lower() != 'none':
            embed = discord.Embed(title=title, description=description, color=color)

        while True:

            tut_embed = await self.tut_embed('Pick an option: field, footer, quit')
            await ctx.send(embed=tut_embed)
            msg = await self.client.wait_for('message', check=check)

            if msg.content == 'quit':
                tut_embed = await self.tut_embed('Generating embed...')
                await ctx.send(embed=tut_embed)
                break

            elif msg.content == 'field':
                tut_embed = await self.tut_embed('Set the field name')
                await ctx.send(embed=tut_embed)
                msg = await self.client.wait_for('message', check=check)
                field_name = msg.content

                tut_embed = await self.tut_embed('Set the field value')
                await ctx.send(embed=tut_embed)
                msg = await self.client.wait_for('message', check=check)
                field_value = msg.content

                tut_embed = await self.tut_embed('Make inline? [yes/no] ')
                await ctx.send(embed=tut_embed)
                msg = await self.client.wait_for('message', check=check)
                inline_format = False
                if msg.content == 'yes':
                    inline_format = True

                embed.add_field(name=field_name, value=field_value, inline=inline_format)

            elif msg.content == 'footer':
                tut_embed = await self.tut_embed('Set the footer text:')
                await ctx.send(embed=tut_embed)
                msg = await self.client.wait_for('message', check=check)
                footer_text = msg.content

        if footer_text is not None:
            embed.set_footer(text=footer_text)
        await ctx.send(embed=embed)

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
            url='http://icons.iconarchive.com/icons/papirus-team/papirus-apps/512/discord-icon.png'
        )
        embed.set_thumbnail(
            url='http://icons.iconarchive.com/icons/papirus-team/papirus-apps/512/discord-icon.png'
        )
        embed.set_author(
            name='Author',
            icon_url='http://icons.iconarchive.com/icons/papirus-team/papirus-apps/512/discord-icon.png'
        )
        embed.add_field(
            name='This is the first field name.',
            value='This is the first field name value.',
            inline=False
        )
        embed.add_field(
            name='This is the second field name.',
            value='This is the second field name value.',
            inline=False
        )
        await ctx.send(embed=embed)

    async def on_message(self, message):
        channel = message.channel
        embed = Embed(color=self.client_color)
        # quick embeds!
        if message.content.startswith('>'):
            lines = message.content.split('\n')
            line1 = lines[0]
            title = line1[1:]
            line2 = ' '.join(lines[1:])
            value = line2[1:].split('\n')
            embed.add_field(name=title, value=' '.join(value), inline=False)
            embed.set_footer(text='Created by {}'.format(message.author.name))
            await message.channel.purge(limit=len(lines))
            await channel.send(embed=embed)

    @staticmethod
    async def tut_embed(description):
        tut_embed = discord.Embed(
            title='Artemis Embed Wizard',
            description=description,
            color=discord.Color.blue())
        return tut_embed

    @staticmethod
    async def on_message_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = ':sob: You\'ve triggered a cool down. Please try again in {} sec.'.format(
                int(error.retry_after))
            await ctx.send(msg)
        if isinstance(error, commands.CheckFailure):
            msg = 'You do not have permission to run this command.'
            await ctx.send(msg)


def setup(client):
    client.add_cog(RichEmbed(client))
