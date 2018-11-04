import asyncio
import random
from discord import Embed, Color
from .rpg import Monsters
from discord.ext.commands import BucketType, CommandNotFound
from artemis import load_json, dump_json
from discord.ext import commands


class Arena:
    def __init__(self, client):
        self.client = client
        self.artemis_is_vulnerable = False

    @commands.command()
    async def test(self, ctx):
        await ctx.send(Monsters.giant_bat())

    @commands.command()
    async def raid(self, ctx):
        client = self.client
        channel = ctx.channel
        fighters = []

        def check(m):
            return m.author != self.client.user and m.channel == channel
        embed = Embed(title='A raid is about to begin!',
                      description='Enter `join` to join the raid, `start` to begin, or `stop` to end!',
                      color=Color.blue())
        await ctx.send(embed=embed)

        while True:
            msg = await client.wait_for('message', check=check)
            if 'join' in msg.content:
                author_name = await self.member_name(msg.author)
                embed = Embed(
                    title='{0} joined the fight!'.format(author_name),
                    color=Color.blue())
                await ctx.send(embed=embed)
                fighters.append(msg.author)
            if 'stop' in msg.content:
                embed = Embed(
                    title='The raid was stopped.',
                    color=Color.blue())
                await ctx.send(embed=embed)
                return
            if 'start' in msg.content:
                if len(fighters) < 1:
                    embed = Embed(description='You cannot start a raid without fighters!')
                    await ctx.send(embed=embed)
                else:
                    fighter_has_nick = [fighter.nick for fighter in fighters if fighter.nick is not None]
                    fighter_no_nick = [fighter.name for fighter in fighters if fighter.nick is None]
                    fighter_merge = fighter_has_nick + fighter_no_nick
                    embed = Embed(title='The fight begins!',
                                  description='Fighters: {}'.format(', '.join(fighter for fighter in fighter_merge)),
                                  color=Color.blue())
                    await ctx.send(embed=embed)
                    break
        print('A raid has started!')
        self.artemis_is_vulnerable = True

        data = await load_json('users')
        while True:
            all_players_alive = all(data[str(fighter.id)]['hp'] > 0 for fighter in fighters)
            # if party and artemis are alive
            if data[str(client.user.id)]['hp'] > 0 and all_players_alive:
                # artemis speed
                await asyncio.sleep(10)

                # artemis attack calculation
                artemis_roll = random.randint(1, 20)
                crit = random.randint(1, 20)
                if crit == 1:
                    # miss
                    embed = Embed(title='Artemis laughs maniacally.', color=Color.dark_red())
                    await ctx.send(embed=embed)
                    continue
                if crit == 20:
                    # critical hit
                    artemis_roll = artemis_roll * 2
                    embed = Embed(
                        description='Artemis draws energy from the surrounding area for a **powered up** attack!',
                        color=Color.dark_red())
                    await ctx.send(embed=embed)
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
                    # if targeted member is not dead
                    target = random.choice(fighters)
                    if data[str(target.id)]['hp'] > 0:
                        break

                target_name = await self.member_name(target)
                msg = 'Artemis attacks {} with {} {}! :dagger:'.format(target_name,
                                                                       random.choice(artemis_adj),
                                                                       random.choice(artemis_attacks))
                # subtract hp from target
                data = await load_json('users')
                data[str(target.id)]['hp'] -= artemis_roll
                await dump_json('users', data)

                damage = '{0} lost {1} HP!\n{0} has {2}/100 HP left!'.format(target_name,
                                                                             artemis_roll,
                                                                             data[str(target.id)]['hp'])

                embed = Embed(description='{}\n{}'.format(msg, damage),
                              color=Color.dark_red())
                await ctx.send(embed=embed)

                if data[str(target.id)]['hp'] <= 0:
                    embed = Embed(description='{} has lost consciousness! :dizzy:'.format(target_name),
                                  color=Color.dark_purple())
                    await ctx.send(embed=embed)
            else:
                break
        msg = 'You defeated Artemis! :sparkles: '
        if not all_players_alive:
            msg = 'You were defeated! :skull: '
        embed = Embed(description=msg,
                      color=Color.dark_magenta())
        await ctx.send(embed=embed)
        self.artemis_is_vulnerable = False
        print('A raid has ended!')

    @commands.command(aliases=['hit', 'kick', 'punch', 'jab', 'headbutt', 'slap', 'stomp', 'atk',
                               'shoot', 'poke', 'strike'])
    @commands.cooldown(rate=1, per=3, type=BucketType.user)
    async def attack(self, ctx, *, target: str):
        client = self.client
        author = ctx.author
        guild = ctx.guild

        # stop artemis from activating herself
        if author.id == client.user.id:
            return
        author_name = await self.member_name(author)
        embed = await self.is_member_exhausted(author)
        if embed is not None:
            await ctx.send(embed=embed)
            return

        # generate attack
        user_attack, roll_results = await self.calculate_attack_power(dice=1, sides=20)
        msg, user_attack = await self.critical_check(ctx, user_attack, author_name)
        if user_attack is None:
            return

        # if target is artemis
        embed = await self.is_target_artemis(target, user_attack)
        if embed is not None:
            await ctx.send(embed=embed)
            return

        # if target is a member
        embed = await self.is_target_member(guild, target, user_attack, msg)
        if embed is not None:
            await ctx.send(embed=embed)

    @commands.group()
    async def cast(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invoke cast with `fire`, `ice`, or `thunder`!')

    @cast.group()
    async def fire(self, ctx, target: str):
        client = self.client
        author = ctx.author
        guild = ctx.guild

        # stop artemis from activating herself
        if author.id == client.user.id:
            return
        author_name = await self.member_name(author)
        embed = await self.is_member_exhausted(author)
        if embed is not None:
            await ctx.send(embed=embed)
            return

        # generate attack
        user_attack, rolls = await self.calculate_attack_power(dice=2, sides=20)
        msg, user_attack = await self.critical_check(ctx, user_attack, author_name)
        if user_attack is None:
            return

        # if target is artemis
        embed = await self.is_target_artemis(target, user_attack)
        if embed is not None:
            await ctx.send(embed=embed)
            return

        # if target is a member
        embed = await self.is_target_member(guild, target, user_attack, msg)
        if embed is not None:
            await ctx.send(embed=embed)

    @cast.group()
    async def ice(self, ctx, target: str):
        attack_power, rolls = await self.calculate_attack_power(dice=2, sides=20)
        await ctx.send('You attack {} with ice for {} HP! :snowflake: '.format(target, sum(attack_power)))

    @cast.group()
    async def thunder(self, ctx, target: str):
        attack_power, rolls = await self.calculate_attack_power(dice=2, sides=20)
        await ctx.send('You attack {} with thunder for {} HP! :zap:'.format(target, sum(attack_power)))

    @cast.group()
    async def soul_stream(self, ctx, target: str):
        attack_power, rolls = await self.calculate_attack_power(dice=2, sides=20)
        await ctx.send('You attack {} with a torrential volley of souls for {} HP! :ghost: '.format(target, sum(attack_power)))

    @commands.group()
    async def heal(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invoke heal with `potion`, `megapotion`, or `revive`!')

    @heal.group()
    @commands.cooldown(rate=1, per=30, type=BucketType.user)
    async def potion(self, ctx, *, target: str):
        client = self.client
        guild = ctx.guild

        data = await load_json('users')
        for member in guild.members:
            mid = str(member.id)
            if target.lower() == client.user.name.lower() or target == client.user.mention:
                embed = Embed(title='{} cannot be healed this way.'.format(client.user.name))
                await ctx.send(embed=embed)
                return

            member_name = member.nick
            if member_name is None:
                member_name = member.name

            if member.mention == target or member_name.lower() == target.lower():
                if data[mid]['hp'] > 0:
                    data[mid]['hp'] += 20
                    if data[mid]['hp'] > 100:
                        data[mid]['hp'] = 100
                    embed = Embed(title='{} recovered 20 HP! :sparkling_heart:'.format(member_name),
                                  color=Color.green())
                    await ctx.send(embed=embed)
                    await dump_json('users', data)
                    return
                else:
                    embed = Embed(title='{} cannot be revived with a potion.'.format(member_name),
                                  color=Color.green())
                    await ctx.send(embed=embed)
                    return
        embed = Embed(title='You fumbled your potion!',
                      color=Color.green())
        await ctx.send(embed=embed)

    @heal.group(aliases=['mega-potion'])
    @commands.cooldown(rate=1, per=60*3, type=BucketType.user)
    async def megapotion(self, ctx, *, target: str):
        client = self.client
        guild = ctx.guild

        data = await load_json('users')
        for member in guild.members:
            mid = str(member.id)
            if target.lower() == client.user.name.lower() or target == client.user.mention:
                embed = Embed(title='{} cannot be healed this way.'.format(client.user.name))
                await ctx.send(embed=embed)
                return

            member_name = await self.member_name(member)
            if member.mention == target or member_name.lower() == target.lower():
                if data[mid]['hp'] > 0:
                    data[mid]['hp'] = 100
                    await dump_json('users', data)
                    embed = Embed(title='{} is fully healed! :sparkling_heart: '.format(member_name),
                                  color=Color.green())
                    await ctx.send(embed=embed)
                    return
                else:
                    embed = Embed(title='{} cannot be revived with a potion.'.format(member_name),
                                  color=Color.green())
                    await ctx.send(embed=embed)
                    return
        embed = Embed(title='You fumbled your megapotion!',
                      color=Color.green())
        await ctx.send(embed=embed)

    @heal.group()
    @commands.cooldown(rate=1, per=60 * 5, type=BucketType.user)
    async def revive(self, ctx, *, target: str):
        client = self.client
        data = await load_json('users')
        for member in ctx.guild.members:
            mid = str(member.id)
            if target.lower() == client.user.name.lower() or target == client.user.mention:
                embed = Embed(title='{} cannot be healed this way.'.format(client.user.name))
                await ctx.send(embed=embed)
                return

            member_name = member.nick
            if member_name is None:
                member_name = member.name

            if member.mention == target or member_name.lower() == target.lower():
                if data[mid]['hp'] <= 0:
                    data[mid]['hp'] = 100
                    embed = Embed(title='{} has been revived!'.format(member_name),
                                  color=Color.green())
                    await ctx.send(embed=embed)
                    await dump_json('users', data)
                    return
                else:
                    embed = Embed(title='{} is not unconscious.'.format(member_name),
                                  color=Color.green())
                    await ctx.send(embed=embed)
                    return
        embed = Embed(title='You fumbled your revive!',
                      color=Color.green())
        await ctx.send(embed=embed)

    @staticmethod
    async def member_name(member):
        # grab author nick
        member_name = member.nick
        if member_name is None:
            member_name = member.name
        return member_name

    @staticmethod
    async def is_member_exhausted(member):
        data = await load_json('users')
        if data[str(member.id)]['hp'] <= 0:
            embed = Embed(title='You are too exhausted to attack!',
                          color=Color.orange())
            return embed
        return None

    async def is_target_artemis(self, target, roll):
        data = await load_json('users')
        if target.lower() == self.client.user.name.lower() or target == self.client.user.mention:
            if self.artemis_is_vulnerable is False:
                artemis_react = ['Artemis effortlessly evades the attack.',
                                 'Artemis brushes off the attack.',
                                 'Artemis ignores the attack.']
                embed = Embed(title=random.choice(artemis_react),
                              color=Color.dark_red())
                return embed
            data[str(self.client.user.id)]['hp'] -= roll
            await dump_json('users', data)
        return None

    async def is_target_member(self, guild, target, roll, msg):
        data = await load_json('users')
        for member in guild.members:
            member_name = await self.member_name(member)
            if member.mention == target or member_name.lower() == target.lower():
                mid = str(member.id)
                data[mid]['hp'] -= roll
                if data[mid]['hp'] <= 0:
                    embed = Embed(description='{} has lost consciousness! :dizzy: '.format(member.nick),
                                  color=Color.red())
                    await dump_json('users', data)
                    return True, embed
                else:
                    damage = '{} took {} points of damage!'.format(member_name, roll)
                    hp_left = '{} has {}/100 HP left!'.format(member_name, data[mid]['hp'])
                    embed = Embed(description='{}\n{}\n{}'.format(msg, damage, hp_left),
                                  color=Color.dark_blue())
                    await dump_json('users', data)
                    return embed
        return None

    @staticmethod
    async def critical_check(ctx, user_attack, author_name):
        print('crit check')
        critical = random.randint(1, 20)
        if critical == 1:
            msg = '{} missed!'.format(author_name)
            embed = Embed(desciption=msg,
                          color=Color.orange())
            await ctx.send(embed=embed)
            return None, None
        elif critical == 20:
            msg = '{} scored a critical hit! :game_die:'.format(author_name)
            user_attack *= 2
        else:
            msg = '{} hit their target! :dagger:'.format(author_name)
            user_attack *= 1
        return msg, user_attack

    @staticmethod
    async def calculate_attack_power(dice, sides):
        rolls = [random.randint(1, sides) for roll in range(dice)]
        total = sum(rolls)
        return total, rolls

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
