import asyncio
import random
import discord
from discord.ext.commands import BucketType, CommandNotFound
from artemis import load_json, dump_json
from discord.ext import commands


class Arena:
    def __init__(self, client):
        self.client = client
        self.artemis_is_vulnerable = False

    @commands.command()
    async def raid(self, ctx):
        message = ctx.message
        channel = ctx.channel
        fighters = []

        def check(m):
            return m.author != self.client.user and m.channel == channel
        embed = discord.Embed(title='A raid is about to begin!',
                              description='Enter `join` to join the raid or `start` to begin!',
                              color=discord.Color.blue())
        await ctx.send(embed=embed)

        while True:
            msg = await self.client.wait_for('message', check=check)
            if 'join' in msg.content:
                author_name = msg.author.nick
                if author_name is None:
                    author_name = msg.author.name
                embed = discord.Embed(
                    title='{0} joined the fight!'.format(author_name),
                    color=discord.Color.blue())
                await ctx.send(embed=embed)
                fighters.append(msg.author)
            if 'start' in msg.content:
                fighter_has_nick = [fighter.nick for fighter in fighters if fighter.nick is not None]
                fighter_no_nick = [fighter.name for fighter in fighters if fighter.nick is None]
                fighter_merge = fighter_has_nick + fighter_no_nick
                embed = discord.Embed(title='The fight begins!',
                                      description='Fighters: {}'.format(', '.join(fighter for fighter in fighter_merge)),
                                      color=discord.Color.blue())
                await ctx.send(embed=embed)
                break
        print('A raid has started!')
        self.artemis_is_vulnerable = True

        data = await load_json('users')
        while True:
            all_players_dead = all(data[str(fighter.id)]['hp'] <= 0 for fighter in fighters)
            if data[str(self.client.user.id)]['hp'] > 0 and not all_players_dead:
                await asyncio.sleep(10)
                artemis_roll = random.randint(1, 20)
                crit = random.randint(1, 20)
                if crit == 1:
                    embed = discord.Embed(title='Artemis laughs maniacally.', color=discord.Color.dark_red())
                    await ctx.send(embed=embed)
                    continue
                if crit == 20:
                    embed = discord.Embed(
                        title='Artemis draws energy from the surrounding area for a **powered up** attack!',
                        color=discord.Color.dark_red())
                    await ctx.send(embed=embed)
                    artemis_roll = artemis_roll * 2
                # if crit == 10:
                #     await ctx.send('*Artemis ate something* **strange** *and regained some health!*')
                #     data[str(self.client.id)]['hp'] += 50
                #     if data[str(self.client.id)]['hp'] > 1000:
                #         data[str(self.client.id)]['hp'] = 1000
                #     # await dump_json('users', data)
                #     continue
                artemis_adj = ['a savage', 'a brutal', 'a deadly', 'a god-like', 'an unseen', 'a terrifying', 'an ungodly']
                artemis_attacks = ['kick', 'blast', 'punch', 'hook', 'uppercut', 'magical beam', 'laser attack',
                                   'counter', 'beatdown', 'knee to the gut', 'body slam']
                while True:
                    target = random.choice(fighters)
                    tid = str(target.id)
                    if data[tid]['hp'] > 0:
                        break

                target_name = target.nick
                if target_name is None:
                    target_name = target.name
                msg = 'Artemis attacks {} with {} {}!'.format(target_name,
                                                              random.choice(artemis_adj),
                                                              random.choice(artemis_attacks))
                data[str(target.id)]['hp'] -= artemis_roll
                await dump_json('users', data)
                damage = '{0} lost {1} HP!\n{0}: {2}/100'.format(target_name, artemis_roll, data[str(target.id)]['hp'])

                embed = discord.Embed(title=msg, description=damage, color=discord.Color.dark_red())
                await ctx.send(embed=embed)

                if data[str(target.id)]['hp'] <= 0:
                    embed = discord.Embed(title='{} has lost consciousness!'.format(target_name), color=discord.Color.dark_purple())
                    await ctx.send(embed=embed)
            else:
                break
        msg = 'You defeated Artemis!'
        if all_players_dead:
            msg = 'You were defeated!'
        embed = discord.Embed(title=msg, color=discord.Color.dark_magenta())
        await ctx.send(embed=embed)
        self.artemis_is_vulnerable = False
        print('A raid has ended!')

    @commands.command(aliases=['hit', 'kick', 'punch', 'jab', 'headbutt', 'slap', 'stomp', 'atk',
                               'shoot', 'poke', 'strike'])
    @commands.cooldown(rate=1, per=5, type=BucketType.user)
    async def attack(self, ctx, target: str):
        author = ctx.author
        if author.id == self.client.user.id:
            return
        data = await load_json('users')
        if data[str(author.id)]['hp'] <= 0:
            await ctx.send('You are too exhausted to attack!')
            return

        roll = random.randint(1, 20)
        crit = random.randint(1, 20)
        if crit == 1:
            if author.nick is not None:
                await ctx.send('{} missed!'.format(author.nick))
            else:
                await ctx.send('{} missed!'.format(author.name))
            return
        elif crit == 20:
            msg = 'Critical hit!'
            roll = roll * 2
        else:
            if author.nick is not None:
                msg = '{} hit their target!'.format(author.nick)
            else:
                msg = '{} hit their target!'.format(author.name)
        # attacking artemis
        if target.lower() == self.client.user.name.lower() or target == self.client.user.mention:
            if self.artemis_is_vulnerable is False:
                artemis_react = ['Artemis effortlessly evades the attack.',
                                 'Artemis brushes off the attack.',
                                 'Artemis ignores the attack.']
                await ctx.send(random.choice(artemis_react))
                return
            data[str(self.client.user.id)]['hp'] -= roll
            await dump_json('users', data)

        # attacking a member
        for member in ctx.guild.members:
            mid = str(member.id)
            if member.nick is not None:
                if member.mention == target or member.name.lower() == target.lower() \
                        or member.nick.lower() == target.lower():
                    data[mid]['hp'] -= roll
                    if data[mid]['hp'] <= 0:
                        await ctx.send('{} has lost consciousness!'.format(member.nick))
                        await dump_json('users', data)

                    else:
                        damage = '{} took {} points of damage!'.format(member.nick, roll)
                        hp_left = '{} has {} HP left!'.format(member.nick, data[mid]['hp'])
                        await ctx.send('{}\n{} {}'.format(msg, damage, hp_left))
                        await dump_json('users', data)
            else:
                if member.mention == target or member.name.lower() == target.lower():
                    data[mid]['hp'] -= roll
                    if data[mid]['hp'] <= 0:
                        await ctx.send('{} has lost consciousness!'.format(member.name))
                        await dump_json('users', data)

                    else:
                        damage = '{} took {} points of damage!'.format(member.name, roll)
                        hp_left = '{} has {} HP left!'.format(member.name, data[mid]['hp'])
                        await ctx.send('{}\n{} {}'.format(msg, damage, hp_left))
                        await dump_json('users', data)

    @commands.group()
    async def heal(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invoke heal with `potion`, `megapotion`, or `revive`!')

    @heal.group()
    @commands.cooldown(rate=1, per=30, type=BucketType.user)
    async def potion(self, ctx, *, target: str):
        data = await load_json('users')
        for member in ctx.guild.members:
            mid = str(member.id)
            # make a dead user unable to heal
            if target.lower() == self.client.user.name.lower() or target == self.client.user.mention:
                await ctx.send('{} cannot be healed this way.'.format(self.client.user.name))
                return
            if member.nick is not None:
                if member.mention == target or member.name.lower() == target.lower() or member.nick.lower() == target.lower():
                    if data[mid]['hp'] > 0:
                        data[mid]['hp'] += 20
                        if data[mid]['hp'] > 100:
                            data[mid]['hp'] = 100
                        await ctx.send('{} has recovered 20 HP!'.format(member.nick))
                        await dump_json('users', data)
                        return
                    else:
                        await ctx.send('{} cannot be revived with a potion.'.format(member.nick))
                        return
            else:
                if member.mention == target or member.name.lower() == target.lower():
                    if data[mid]['hp'] > 0:
                        data[mid]['hp'] += 20
                        if data[mid]['hp'] > 100:
                            data[mid]['hp'] = 100
                        await ctx.send('{} has recovered 20 HP!'.format(member.name))
                        await dump_json('users', data)
                        return
                    else:
                        await ctx.send('{} cannot be revived with a potion.'.format(member.name))
                        return
        await ctx.send('You fumbled your potion!'.format(target))

    @heal.group()
    @commands.cooldown(rate=1, per=60*3, type=BucketType.user)
    async def megapotion(self, ctx, *, target: str):
        data = await load_json('users')
        for member in ctx.guild.members:
            mid = str(member.id)
            # make a dead user unable to heal
            if target.lower() == self.client.user.name.lower() or target == self.client.user.mention:
                await ctx.send('{} cannot be healed this way.'.format(self.client.user.name))
                return
            if member.nick is not None:
                if member.mention == target or member.name.lower() == target.lower() or member.nick.lower() == target.lower():
                    if data[mid]['hp'] > 0:
                        data[mid]['hp'] = 100
                        await ctx.send('{} has been fully healed!'.format(member.nick))
                        await dump_json('users', data)
                        return
                    else:
                        await ctx.send('{} cannot be revived with a potion.'.format(member.nick))
                        return
            else:
                if member.mention == target or member.name.lower() == target.lower():
                    if data[mid]['hp'] > 0:
                        data[mid]['hp'] = 100
                        await ctx.send('{} has been fully healed!'.format(member.name))
                        await dump_json('users', data)
                        return
                    else:
                        await ctx.send('{} cannot be revived with a potion.'.format(member.name))
                        return
        await ctx.send('You fumbled your megapotion!'.format(target))

    @heal.group()
    @commands.cooldown(rate=1, per=60 * 5, type=BucketType.user)
    async def revive(self, ctx, *, target: str):
        data = await load_json('users')
        for member in ctx.guild.members:
            mid = str(member.id)
            # make a dead user unable to heal
            if target.lower() == self.client.user.name.lower() or target == self.client.user.mention:
                await ctx.send('{} cannot be revived this way.'.format(self.client.user.name))
                return
            if member.nick is not None:
                if member.mention == target or member.name.lower() == target.lower() or member.nick.lower() == target.lower():
                    if data[mid]['hp'] <= 0:
                        data[mid]['hp'] = 100
                        await ctx.send('{} has been revived!'.format(member.nick))
                        await dump_json('users', data)
                        return
                    else:
                        await ctx.send('{} is not unconscious.'.format(member.nick))
                        return
            else:
                if member.mention == target or member.name.lower() == target.lower():
                    if data[mid]['hp'] <= 0:
                        data[mid]['hp'] = 100
                        await ctx.send('{} has been revived!'.format(member.name))
                        await dump_json('users', data)
                        return
                    else:
                        await ctx.send('{} is not unconscious.'.format(member.name))
                        return
        await ctx.send('You fumbled your revive!'.format(target))

    @potion.error
    @megapotion.error
    @revive.error
    @attack.error
    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = 'You\'ve triggered a cool down. Please try again in {} sec.'.format(
                int(error.retry_after))
            await ctx.send(msg)
        if isinstance(error, commands.CheckFailure):
            msg = 'You do not have permission to run this command.'
            await ctx.send(msg)
        if isinstance(error, commands.MissingRequiredArgument):
            msg = 'A critical argument is missing from the command.'
            await ctx.send(msg)
        if isinstance(error, CommandNotFound):
            msg = 'Did you mean to try another command?'
            await ctx.send(msg)


def setup(client):
    client.add_cog(Arena(client))
