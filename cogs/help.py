from discord.ext import commands

import cogs.utilities as utilities


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['commands', 'command', 'artemis'])
    async def help(self, ctx):
        conn, c = await utilities.load_db()
        c.execute("SELECT prefix FROM guilds WHERE gid = (:gid)", {'gid': ctx.guild.id})
        prefix = c.fetchone()[0]
        await utilities.single_embed(
            color=utilities.color_help,
            title='Help Menu',
            description=f'Use `{prefix} <command> help` to get help for each command!',
            name='Commands that can use `help`:',
            value='`challonge`\n'
                  '`elite`\n'
                  '`fun` \n'
                  '`karma`\n'
                  '`admin`',
            channel=ctx
        )


def setup(client):
    client.add_cog(Help(client))
