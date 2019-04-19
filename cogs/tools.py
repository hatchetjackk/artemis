import asyncio

import cogs.utilities as utilities
from discord.ext import commands
from datetime import datetime


class Tools(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group()
    async def remindme(self, ctx):
        """
        Get user input for simple user reminders
        :param ctx: the message object
        :return:
        """
        if ctx.invoked_subcommand is None:
            def check(m):
                return m.author == ctx.message.author and m.channel == ctx.channel
            conn, c = await utilities.load_db()
            d = datetime.today()

            try:
                # get reminder message
                await utilities.single_embed(
                    name='Reminder',
                    value='What do you want to be reminded of?',
                    channel=ctx
                )
                msg = await self.client.wait_for('message', check=check)
                reminder_contents = msg.content
                await ctx.channel.purge(limit=3)

                # get reminder date
                await utilities.single_embed(
                    name='Reminder',
                    value='When do you want to be reminded?\n'
                          '(example: 3 days, 2 months, 1 year)',
                    channel=ctx
                )
                msg = await self.client.wait_for('message', check=check)
                reminder_date = msg.content
                await ctx.channel.purge(limit=2)

                num_value, date_value = reminder_date.split()
                # ensure that date_value matches keys in the dictionary
                if date_value[-1:] != 's':
                    date_value += 's'
                date_dict = {'days': d.day, 'months': d.month, 'years': d.year}
                date_dict[date_value] += int(num_value)

                with conn:
                    c.execute("INSERT INTO reminders VALUES(:uid, :message, :month, :day, :year, :clock, :id)",
                              {'uid': ctx.author.id,
                               'message': reminder_contents,
                               'month': date_dict['months'],
                               'day': date_dict['days'],
                               'year': date_dict['years'],
                               'clock': f'{d.hour}:{d.minute}',
                               'id': None
                               })
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
                uid, msg, month, day, year, clock, key = reminder
                hour, minute = clock.split(':')
                value = f'[*key: {key}*], {datetime(year, month, day, int(hour), int(minute))}'
                messages.append([msg, value])
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
                name='An unexpected error occurred when trying to show reminders!', value=e, channel=ctx, delete_after=5
            )

    @remindme.group(aliases=['remove', 'del', 'rem'])
    async def delete(self, ctx, key: int=None):
        conn, c = await utilities.load_db()
        if key is not None:
            try:
                with conn:
                    c.execute("DELETE FROM reminders WHERE id = (:id)", {'id': key})
                await utilities.single_embed(
                    title='Reminder deleted!',
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
            d = datetime.now()
            conn, c = await utilities.load_db()
            c.execute("SELECT * FROM reminders")
            reminders = c.fetchall()
            for reminder in reminders:
                uid, message, month, day, year, time, key = reminder
                hour, minute = time.split(':')
                try:
                    new_datetime_object = datetime(year, month, day, int(hour), int(minute))
                    timedelta = new_datetime_object - d

                    if timedelta.total_seconds() < 60:
                        # notify the user
                        member = self.client.get_user(uid)
                        await utilities.single_embed(
                            name='Reminder!',
                            value=f'You told me to remind you about this.\n"{message}"',
                            channel=member
                        )
                        # remove the notification
                        with conn:
                            c.execute("DELETE FROM reminders WHERE id = (:id)", {'id': key})
                except Exception as e:
                    await utilities.alert_embed(
                        name='An error occurred when checking reminders.', value=e
                    )
            await asyncio.sleep(5)

    def shorten(self, ctx, *, link: str):
        """
        Take a user provided link and return a shortened link
        todo: find an url shortener
        :param ctx:
        :param link:
        :return:
        """
        pass

    def vote(self):
        pass

    def image(self, ctx, subreddit):
        """
        Return a random image from specified subreddit
        :param ctx:
        :param subreddit:
        :return:
        """
        pass


def setup(client):
    tools = Tools(client)
    client.add_cog(tools)
    client.loop.create_task(tools.check_reminders())

