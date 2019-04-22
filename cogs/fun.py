import asyncio
import random
import re
import urllib.parse
import urllib.request
from datetime import datetime

import requests
from PyDictionary import PyDictionary
from dateutil.relativedelta import relativedelta
from discord.ext import commands
from discord.ext.commands import BucketType, CommandNotFound

import cogs.utilities as utilities


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group()
    async def fun(self, ctx):
        if ctx.invoked_subcommand is None:
            await utilities.single_embed(
                color=utilities.color_alert,
                title='Try `fun help` for more options.',
                channel=ctx
            )

    @fun.group()
    async def help(self, ctx):
        await utilities.single_embed(
            color=utilities.color_help,
            title='Fun Help',
            channel=ctx,
            description='`fun help` This menu!\n'
                        '`playing` View all current statuses\n'
                        '`ping` Check if Artemis is reactive\n'
                        '`roll ndn [modifier]` Roll n number of dice +- modifier\n'
                        '`draw` Draw a random card. High/low anyone?\n'
                        '`hello` Say hi to Artemis\n'
                        '`define word` Get a definition\n'
                        '`google topic` Retrieve the first link from Google\n'
                        '`r/subreddit` Retrieve a subreddit link\n'
                        '`youtube topic` Retrieve the first video from YouTube\n'
                        '`rps rock/paper/scissors` Play against Artemis\n'
                        '`remindme` Create a reminder that will be sent to your DM.'
        )

    @commands.group()
    async def remindme(self, ctx):
        if ctx.invoked_subcommand is None:
            def check(m):
                return m.author == ctx.message.author and m.channel == ctx.channel

            conn, c = await utilities.load_db()

            try:
                # get reminder message
                await utilities.single_embed(
                    name='Reminder',
                    value='What do you want to be reminded of? Enter `cancel` to quit.',
                    channel=ctx
                )
                msg = await self.client.wait_for('message', check=check)
                reminder_contents = msg.content
                await ctx.channel.purge(limit=3)
                if reminder_contents.lower().strip() == 'cancel':
                    await utilities.single_embed(name='Reminder', value='Cancelling...', channel=ctx, delete_after=3)
                    return

                # get reminder date
                await utilities.single_embed(
                    name='Reminder',
                    value='When do you want to be reminded?\n'
                          'You can use <num> <time> formats such as `3 days` or `1 month` or `5 years` etc.',
                    channel=ctx
                )
                msg = await self.client.wait_for('message', check=check)
                reminder_date = msg.content
                await ctx.channel.purge(limit=2)

                num_value, date_value = reminder_date.strip().split()
                num_value = int(num_value)
                if date_value[-1:] != 's':
                    date_value += 's'
                if date_value == 'days':
                    date_object = datetime.now() + relativedelta(days=+num_value)
                elif date_value == 'months':
                    date_object = datetime.now() + relativedelta(months=+num_value)
                elif date_value == 'years':
                    date_object = datetime.now() + relativedelta(years=+num_value)
                else:
                    await utilities.err_embed(
                        title='A date object was not properly set. Please check `remindme help`.',
                        channel=ctx,
                        delete_after=5
                    )
                    return
                with conn:
                    c.execute("INSERT INTO reminders VALUES(:uid, :message, :id, :date_object)",
                              {'id': None,
                               'uid': ctx.author.id,
                               'message': reminder_contents,
                               'date_object': date_object})

                await utilities.single_embed(
                    name='Reminder Set',
                    value=f'I will remind you about `{reminder_contents}` in `{reminder_date}`!',
                    channel=ctx
                )
            except Exception as e:
                await utilities.err_embed(
                    name='An unexpected error occurred when adding a reminder!', value=e, channel=ctx, delete_after=5
                )

    @remindme.group()
    async def help(self, ctx):
        await utilities.single_embed(
            color=utilities.color_help,
            title='RemindMe Help',
            channel=ctx,
            description='`remindme help` This menu!\n'
                        'Remind me is a simple reminder function. It prompts the user for a message and time. '
                        'Eligible time formats include days, months, and years. Once the date is reached, Artemis '
                        'will send a DM to the user reminding them of the message.\n\n'
                        '`remindme show` Send all current reminders via DM\n'
                        '`remindme del <key>` Delete a reminder based on it\'s key integer.'
        )

    @remindme.group()
    async def show(self, ctx):
        conn, c = await utilities.load_db()
        c.execute("SELECT * FROM reminders WHERE uid = (:uid)", {'uid': ctx.author.id})
        reminders = c.fetchall()
        messages = []
        try:
            for reminder in reminders:
                uid, message, key, date_object = reminder
                value = f'Remind at: {date_object}\n' \
                    f'*Key: {key}*'
                messages.append([message, value])
            await utilities.multi_embed(
                title='Reminders',
                channel=ctx.author,
                messages=messages
            )
            await utilities.single_embed(
                title='A private message has been sent to your inbox!',
                channel=ctx
            )
        except Exception as e:
            await utilities.err_embed(
                name='An unexpected error occurred when trying to show reminders!',
                value=e,
                channel=ctx,
                delete_after=5
            )

    @remindme.group(aliases=['remove', 'del', 'rem'])
    async def delete(self, ctx, key: int = None):
        """

        :param ctx:
        :param key: Reminders are stored with a unique key. To delete a reminder, the appropriate key needs to be used.
        :return:
        """
        conn, c = await utilities.load_db()
        if key is not None:
            try:
                with conn:
                    c.execute("DELETE FROM reminders WHERE id = (:id) AND uid = (:uid)",
                              {'id': key, 'uid': ctx.author.id})
                await utilities.single_embed(
                    name='Reminder deleted!',
                    value='Note that the function completed without errors. If this completed but your reminder \n'
                          'still remains, please notify the bot owner.',
                    channel=ctx,
                    delete_after=5
                )
            except Exception as e:
                await utilities.err_embed(
                    name='An error occurred when attempting to remove a reminder.',
                    value=e,
                    channel=ctx
                )

    async def check_reminders(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            conn, c = await utilities.load_db()
            c.execute("SELECT * FROM reminders")
            reminders = c.fetchall()
            for reminder in reminders:
                uid, message, key, datetime_object = reminder
                try:
                    # if total time left is less than 60 seconds, notify and delete
                    delta = datetime_object - datetime.now()
                    if delta.total_seconds() < 60:
                        member = self.client.get_user(uid)
                        await utilities.single_embed(
                            name='Reminder!',
                            value=f'You told me to remind you about this.\n"{message}"',
                            channel=member
                        )
                        with conn:
                            c.execute("DELETE FROM reminders WHERE id = (:id)", {'id': key})
                except Exception as e:
                    await utilities.alert_embed(name='An error occurred when checking reminders.', value=e)
            await asyncio.sleep(30)

    @commands.command()
    async def playing(self, ctx, *, game_match='all'):
        if game_match == 'all':
            games_being_played = [member.game.name for member in ctx.guild.members
                                  if member.game is not None
                                  and member.id != self.client.user.id]
            if len(games_being_played) < 1:
                await utilities.single_embed(title='No ones is playing anything!', channel=ctx)
            else:
                await utilities.single_embed(title='Current Games',
                                             description='\n'.join(games_being_played),
                                             channel=ctx)
        else:
            members_playing_game = []
            pattern = re.compile(r'' + re.escape(game_match.lower()))
            for member in ctx.guild.members:
                if member.game is not None:
                    matches = pattern.findall(member.game.name.lower())
                    for _ in matches:
                        game = '{0.name} - {0.game.name}'.format(member)
                        if game in members_playing_game:
                            pass
                        else:
                            members_playing_game.append(game)
            if len(members_playing_game) < 1:
                await utilities.single_embed(title=f'No one is playing {game_match}.', channel=ctx)
            else:
                await utilities.single_embed(title=f'{len(members_playing_game)} members are playing {game_match}.',
                                             description='\n'.join(members_playing_game),
                                             channel=ctx)

    @commands.command()
    async def ping(self, ctx):
        print('pong')
        await utilities.single_embed(title=':ping_pong: Pong!', channel=ctx, color=utilities.color_alert)

    @commands.command()
    async def roll(self, ctx, dice: str, modifier: int = 0):
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await utilities.single_embed(title='Please use the format "NdN" when rolling dice. Thanks!', channel=ctx)
            raise
        rolls = [random.randint(1, limit) for _ in range(rolls)]
        result = ', '.join(str(roll) for roll in rolls)
        msg = f'You rolled {result} for a total of **{sum(rolls)}**!'
        if modifier is not 0:
            string_mod = modifier
            if modifier > 0:
                string_mod = f'+{modifier}'
            msg = f'You rolled {result} ({string_mod}) for a total of **{sum(rolls) + modifier}**!'
        await utilities.single_embed(
            title=msg,
            channel=ctx
        )

    @commands.command(aliases=['hi', 'bonjour', 'hola'])
    async def hello(self, ctx):
        responses = ["Hi, {0.author.name}!",
                     "Ahoy, {0.author.name}!",
                     "Hey there, {0.author.name}!",
                     "*[insert traditional greeting here]*",
                     "*0100100001000101010011000100110001001111*\nAhem, I mean: hello!",
                     "Hello. Fine weather we're having.",
                     "Hello, fellow human!"]
        msg = random.choice(responses).format(ctx)
        await utilities.single_embed(title=msg, channel=ctx)

    @commands.command()
    async def define(self, ctx, word: str):
        try:
            dictionary = PyDictionary()
            results = dictionary.meaning(word)
            messages = []
            for key, definition in results.items():
                definitions = []
                num = 1
                for value in definition:
                    definitions.append(str(num) + ') ' + value)
                    num += 1
                all_def = '\n'.join(definitions)
                messages.append([key, all_def])
            await utilities.multi_embed(
                title=word.upper(),
                messages=messages,
                channel=ctx
            )
        except Exception as e:
            print('[{}] The definition for {} could not be found: {}'.format(datetime.now(), word, e))
            await utilities.single_embed(
                color=utilities.color_alert,
                title=f'Sorry, I could not find the definition for {word}!',
                channel=ctx
            )

    @commands.command(aliases=['g'])
    async def google(self, ctx, *, search: str):
        r = requests.get(f'http://www.google.com/search?q="{search}"&btnI')
        await ctx.send(r.url)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith('r/'):
            reddit_search = 'https://reddit.com/' + message.content
            await message.channel.send(reddit_search)

    @commands.command()
    async def rps(self, ctx, choice: str):
        rps = ['rock', 'paper', 'scissors']
        win = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}
        lose = {'paper': 'rock', 'rock': 'scissors', 'scissors': 'paper'}

        if choice not in rps:
            await utilities.single_embed(
                color=utilities.color_alert,
                title='You have to pick rock, paper, or scissors.',
                channel=ctx
            )

        bot_choice = random.choice(rps)
        if bot_choice == choice:
            await utilities.single_embed(title=f'Artemis chose {bot_choice}! It\'s a tie!', channel=ctx)
        if choice == lose.get(bot_choice):
            await utilities.single_embed(color=utilities.color_alert, title=f'Artemis chose {bot_choice}! You lost!',
                                         channel=ctx)
        if choice == win.get(bot_choice):
            await utilities.single_embed(color=utilities.color_help, title=f'Artemis chose {bot_choice}! You won!',
                                         channel=ctx)

    @commands.command(aliases=['yt'])
    @commands.cooldown(rate=1, per=15, type=BucketType.user)
    async def youtube(self, ctx, *args):
        query_string = urllib.parse.urlencode({"search_query": ' '.join(args)})
        html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
        search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
        await ctx.send("http://www.youtube.com/watch?v=" + search_results[0])

    @commands.command(aliases=['draw'])
    async def card(self, ctx):
        """ draw a random card from a deck """
        card = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 'Ace', 'King', 'Queen', 'Jack']
        style = ['Spades', 'Hearts', 'Clubs', 'Diamonds']

        rcard = random.choice(card)
        rstyle = random.choice(style)

        await utilities.single_embed(title=f'You drew the {rcard} of {rstyle}!', channel=ctx)

    @rps.error
    @youtube.error
    @commands.Cog.listener()
    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = f'You\'ve triggered a cool down. Please try again in {error.retry_after} sec.'
            await utilities.single_embed(
                color=utilities.color_alert,
                title=msg,
                channel=ctx
            )
        if isinstance(error, commands.CheckFailure):
            await utilities.single_embed(
                color=utilities.color_alert,
                title='You do not have permission to run this command.',
                channel=ctx
            )
        if isinstance(error, commands.MissingRequiredArgument):
            await utilities.single_embed(
                color=utilities.color_alert,
                title='A critical argument is missing from the command.',
                channel=ctx
            )
        if isinstance(error, CommandNotFound):
            await utilities.single_embed(
                color=utilities.color_alert,
                title='Did you mean to try another command?',
                channel=ctx
            )


def setup(client):
    fun = Fun(client)
    client.add_cog(fun)
    client.loop.create_task(fun.check_reminders())
