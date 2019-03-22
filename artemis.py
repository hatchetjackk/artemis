#! /usr/bin/python3
import os
import random
import discord
import json
import logging
import cogs.utilities as utilities
from datetime import datetime
from discord.ext import commands
from discord.ext.commands import CommandNotFound

logging.basicConfig(filename='files/artemis.log', format='%(asctime)s %(message)s', level=logging.INFO)
logging.info('Starting')


# noinspection PyUnusedLocal
async def prefix(bot, message):
    conn, c = await utilities.load_db()
    c.execute("SELECT prefix FROM guilds WHERE id = (:id)", {'id': message.guild.id})
    bot_prefix = c.fetchone()[0]
    return bot_prefix
client = commands.Bot(command_prefix=prefix, case_insensitive=True)
client.remove_command('help')


@client.event
async def on_ready():
    print(f'{"Logged in as":<15} {client.user.name}')
    print(f'{"Client":<15} {client.user.id}')
    print(f'{"Discordpy ver.":<15} {discord.__version__}')
    print('---------------------------------------')
    print(f'[{datetime.now()}] Artemis is online.')
    await utilities.build_db_tables()


@client.event
async def on_resumed():
    print(f'[{datetime.now()}] Artemis is back online.')


# noinspection PyShadowingNames
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        conn, c = await utilities.load_db()
        c.execute("SELECT response FROM bot_responses WHERE message_type = 'error_response'")
        error_response = [value[0] for value in c.fetchall()]
        await utilities.single_embed(
            color=utilities.color_alert,
            title=random.choice(error_response),
            channel=ctx
        )


if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in os.listdir('cogs/') if not f.startswith('_')]:
        try:
            client.load_extension('cogs.' + extension)
        except discord.ClientException:
            # skip cogs without setup functions
            pass
        except Exception as e:
            print(f'[{datetime.now()}] {extension} cannot be loaded: {e}')
    with open('files/credentials.json', 'r') as f:
        credentials = json.load(f)
    client.run(credentials['token'])
