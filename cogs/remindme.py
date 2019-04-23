import asyncio
from datetime import datetime

from dateutil.relativedelta import relativedelta
from discord.ext import commands
import cogs.utilities as utilities


class RemindMe(commands.Cog):
    def __init__(self, client):
        self.client = client

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


def setup(client):
    remind = RemindMe(client)
    client.add_cog(remind)
    client.loop.create_task(remind.check_reminders())
