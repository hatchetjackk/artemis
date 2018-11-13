import asyncio
import random
import re
from discord import Embed, Color
from discord.ext.commands import BucketType, CommandNotFound
from artemis import load_json, dump_json
from discord.ext import commands


class Arena:
    def __init__(self, client):
        self.client = client
        self.artemis_is_vulnerable = False
        self.raid_is_active = False
        self.duel_is_active = False

        self.user_attack = Color.teal()
        self.enemy_attack = Color.dark_red()
        self.enemy_miss = Color.light_grey()
        self.defend_color = Color.dark_magenta()
        self.win_the_fight = Color.gold()
        self.lose_the_fight = Color.dark_purple()
        self.use_item = Color.green()
        self.revive_user = Color.dark_gold()
        self.rpg_info = Color.blue()
        self.error = Color.orange()

    @commands.command()
    async def raid(self, ctx):
        if self.raid_is_active:
            await ctx.send('A raid is already active!')
            return
        self.raid_is_active = True

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
                embed_msg = '{0} joined the fight!'.format(author_name)
                await self.send_embed(channel=channel, msg=embed_msg, color=self.rpg_info)
                fighters.append(msg.author)
            if 'stop' in msg.content:
                embed_msg = 'The raid was stopped.'
                await self.send_embed(channel=channel, msg=embed_msg, color=self.rpg_info)
                self.raid_is_active = False
                return
            if 'start' in msg.content:
                if len(fighters) < 1:
                    embed_msg = 'You cannot start a raid without fighters!'
                    await self.send_embed(channel=channel, msg=embed_msg, color=self.rpg_info)
                else:
                    fighter_has_nick = [fighter.nick for fighter in fighters if fighter.nick is not None]
                    fighter_no_nick = [fighter.name for fighter in fighters if fighter.nick is None]
                    fighter_merge = fighter_has_nick + fighter_no_nick
                    embed_msg = '**The fight begins!**\nFighters: {}'.format(', '.join(
                        fighter for fighter in fighter_merge)
                    )
                    await self.send_embed(channel=channel, msg=embed_msg, color=self.rpg_info)
                    break
        print('A raid has started!')
        self.artemis_is_vulnerable = True

        while True:
            data = await load_json('users')
            raid_boss_hp = data[str(client.user.id)]['hp']
            all_players_alive = all(data[str(fighter.id)]['hp'] > 0 for fighter in fighters)

            if raid_boss_hp > 0 and all_players_alive:
                await asyncio.sleep(10)

                artemis_attack = random.randint(1, 20)
                crit = random.randint(1, 20)
                if crit == 1:
                    embed_msg = 'Artemis laughs maniacally.'
                    await self.send_embed(channel=channel, msg=embed_msg, color=self.enemy_miss)
                    continue
                if crit == 2:
                    embed_msg = 'Artemis stares deeply into your soul.'
                    await self.send_embed(channel=channel, msg=embed_msg, color=self.enemy_miss)
                    continue
                if crit == 20:
                    artemis_attack *= 2
                    embed_msg = '*Artemis draws energy from the surrounding area for a* **powered up** *attack!*'
                await self.send_embed(channel=channel, msg=embed_msg, color=self.enemy_attack)
                if crit == 10:
                    embed_msg = '*Artemis ate something* **strange** *and regained some health!*'
                    await self.send_embed(channel=channel, msg=embed_msg, color=self.use_item)
                    data[str(client.user.id)]['hp'] += 50
                    await dump_json('users', data)
                    continue

                adjectives = ['a savage', 'a brutal', 'a deadly', 'a god-like',
                              'an unseen', 'a terrifying', 'an ungodly']
                verbs = ['kick', 'blast', 'punch', 'hook', 'uppercut', 'magical beam',
                         'laser attack', 'counter', 'beatdown', 'knee to the gut', 'body slam']

                while True:
                    fighter = random.choice(fighters)
                    fighter_hp = data[str(fighter.id)]['hp']
                    if fighter_hp > 0:
                        break

                fighter_name = await self.member_name(fighter)
                msg = 'Artemis attacks {} with {} {}! :dagger:'.format(fighter_name,
                                                                       random.choice(adjectives),
                                                                       random.choice(verbs))
                data[str(fighter.id)]['hp'] -= artemis_attack
                fighter_hp = data[str(fighter.id)]['hp']
                await dump_json('users', data)
                damage = '{0} lost {1} HP!'.format(fighter_name, artemis_attack)
                remaining = '{}/{} HP'.format(fighter_hp, 100)
                fmt = '{}\n{}'.format(damage, remaining)

                embed = Embed(description='{}\n{}'.format(msg, fmt),
                              color=self.enemy_attack)
                await ctx.send(embed=embed)

                if fighter_hp <= 0:
                    embed = Embed(description='{} has lost consciousness! :dizzy:'.format(fighter_name),
                                  color=self.enemy_attack)
                    await ctx.send(embed=embed)

                raid_boss_hp = data[str(client.user.id)]['hp']
                all_players_alive = all(data[str(fighter.id)]['hp'] > 0 for fighter in fighters)
                if raid_boss_hp <= 0 or not all_players_alive:
                    break
            else:
                break
        data[str(client.user.id)]['hp'] = 200
        await dump_json('users', data)

        msg = 'You defeated Artemis! :sparkles: '
        color = self.win_the_fight
        if not all_players_alive:
            msg = 'You were defeated! :skull: '
            color = self.lose_the_fight
        embed = Embed(description=msg,
                      color=color)
        await ctx.send(embed=embed)
        self.artemis_is_vulnerable = False
        self.raid_is_active = False
        print('A raid has ended!')

    @commands.command()
    async def duel(self, ctx, *, target: str):
        # fight another member one on one
        if len(target) < 3:
            await ctx.send('Please use at least 3 characters when choosing your target.')
            return
        fighters = [ctx.author]
        author_name = await self.member_name(ctx.author)
        pattern = re.compile(r'' + re.escape(target.lower()))
        for member in ctx.guild.members:
            member_name = await self.member_name(member)
            matches = [match for match in pattern.finditer(member_name.lower())]
            for match in matches:
                def check(m):
                    return m.author == member and m.channel == ctx.channel
                bad_duels = [ctx.author, self.client.user]
                if member in bad_duels:
                    embed = Embed(description='You cannot duel {}.'.format(member_name),
                                  color=self.error)
                    await ctx.send(embed=embed)
                    return

                embed = Embed(description='{}, {} has challenged you to a duel! \n'
                                          'To accept, enter `accept` or else enter `deny`.'.format(member.mention, author_name))
                await ctx.send(embed=embed, delete_after=30)

                msg = await self.client.wait_for('message', check=check, timeout=30)
                if 'deny' in msg.content:
                    target_name = await self.member_name(msg.author)
                    embed = Embed(
                        title='{} denied the fight!'.format(target_name),
                        color=self.rpg_info)
                    await ctx.send(embed=embed, delete_after=5)
                    return

                if 'accept' in msg.content:
                    target_name = await self.member_name(msg.author)
                    embed = Embed(
                        title='{} accepted the fight!'.format(target_name),
                        color=self.rpg_info)
                    await ctx.send(embed=embed, delete_after=5)
                    fighters.append(msg.author)
        if len(fighters) > 1:
            embed = Embed(description='The fight begins!\n'
                                      'A fighter\'s speed is based on their equipped weight. Light fighters take action more often!')
            await ctx.send(embed=embed, delete_after=5)
        print(fighters)

        rpg = await load_json('rpg')
        turn_counter = 0
        self.duel_is_active = True
        while True:
            print(1)
            users = await load_json('users')
            print(2)
            all_players_alive = all(users[str(fighter.id)]['hp'] > 0 for fighter in fighters)
            print(3)
            if all_players_alive:
                for fighter in fighters:
                    print(4)

                    def check(m):
                        return m.author == fighter and m.channel == ctx.channel

                    print(5)

                    fighter_name = await self.member_name(fighter)
                    equipped_weapon = users[str(fighter.id)]['equipped']['weapon']
                    equipped_armor = users[str(fighter.id)]['equipped']['armor']
                    weapon_weight = 0
                    armor_weight = 0
                    for wep_type, wep in rpg['weapons'].items():
                        if equipped_weapon in wep:
                            weapon_weight = rpg['weapons'][wep_type][equipped_weapon]['weight']
                    for arm_type, arm in rpg['armor'].items():
                        if equipped_armor in arm:
                            armor_weight = rpg['armor'][arm_type][equipped_armor]['weight']
                    equipped_weight = weapon_weight + armor_weight
                    if equipped_weight == 0:
                        equipped_weight = 1

                    if equipped_weight % turn_counter == 0:
                        fighter_turn = Embed(title='{}\'s turn!'.format(fighter_name))
                        await ctx.send(embed=fighter_turn)
                        while True:
                            action = await self.client.wait_for('message', check=check, timeout=60)
                            attacks = ['hit', 'kick', 'punch', 'jab', 'headbutt', 'slap', 'stomp', 'atk',
                                       'shoot', 'poke', 'strike']
                            if any(attacks) in action.content:
                                break
                            elif 'use' in action.content:
                                break
                            else:
                                await ctx.send('Attacks and Items will use your turn')
                turn_counter += 1
            else:
                await ctx.send('The fight is over!')
                break

    async def fight(self, ctx):
        # fight a monster solo or with a party
        pass

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
        rolls, limit, weapon = await self.get_member_weapon(author)
        user_attack, roll_results = await self.calculate_attack_power(dice=rolls, sides=limit)
        msg, user_attack_with_critical = await self.critical_check(user_attack, author_name)

        # if target is artemis
        embed = await self.is_target_artemis(guild, target, user_attack_with_critical)
        if embed is not None:
            await ctx.send(embed=embed)
            return

        # if target is a member
        embed = await self.is_target_member(ctx, author, guild, target, user_attack_with_critical, msg)
        if embed is not None:
            await ctx.send(embed=embed)

    @commands.command()
    async def use(self, ctx, item: str, target: str):
        rpg = await load_json('rpg')
        if item in rpg['items']['potions']:
            await self.item_is_potion(ctx, item, target)

        if item in rpg['items']['bombs']:
            pass

    async def item_is_potion(self, ctx, item, target):
        client = self.client
        author = ctx.author
        guild = ctx.guild
        rpg = await load_json('rpg')
        data = await load_json('users')
        if item == 'smelling salts':
            if data[str(author.id)]['inventory'][item] > 0:
                pattern = re.compile(r'' + re.escape(target.lower()))
                for member in guild.members:
                    member_name = await self.member_name(member)
                    matches = pattern.finditer(member_name.lower())
                    for match in matches:
                        target_id = str(member.id)
                        if target_id == str(client.user.id):
                            embed = Embed(title='{} cannot be revived this way.'.format(client.user.name),
                                          color=self.error)
                            await ctx.send(embed=embed)
                        elif data[target_id]['hp'] <= 0:
                            data[target_id]['hp'] = data[target_id]['max hp']
                            data[str(author.id)]['inventory'][item] -= 1
                            if data[str(author.id)]['inventory'][item] == 0:
                                data[str(author.id)]['inventory'].pop(item, None)
                            embed = Embed(
                                description='{} woke up! :scream: '.format(member_name),
                                color=self.revive_user)
                            await ctx.send(embed=embed)
                            await dump_json('users', data)
                        else:
                            embed = Embed(description='{} is not unconscious!'.format(member_name),
                                          color=self.error)
                            await ctx.send(embed=embed)
            else:
                embed = Embed(description='You don\'t have any more smelling salts.',
                              color=self.error)
                await ctx.send(embed=embed, delete_after=3)

        elif data[str(author.id)]['inventory'][item] > 0:
            pattern = re.compile(r'' + re.escape(target.lower()))
            for member in guild.members:
                member_name = await self.member_name(member)
                matches = pattern.finditer(member_name.lower())
                for match in matches:
                    mid = str(member.id)
                    if mid == str(client.user.id):
                        embed = Embed(title='{} cannot be healed this way.'.format(client.user.name),
                                      color=self.error)
                        await ctx.send(embed=embed)
                        return
                    elif data[mid]['hp'] > 0:
                        rolls, limit, modifier = rpg['items']['potions'][item]['effect']
                        hp_gained = sum([random.randint(1, limit) for roll in range(rolls)]) + modifier
                        data[mid]['hp'] += hp_gained
                        if data[mid]['hp'] > data[mid]['max hp']:
                            data[mid]['hp'] = data[mid]['max hp']
                        data[str(author.id)]['inventory'][item] -= 1
                        if data[str(author.id)]['inventory'][item] == 0:
                            data[str(author.id)]['inventory'].pop(item, None)
                        embed = Embed(
                            description='{} recovered {} HP! :sparkling_heart:'.format(member_name, hp_gained),
                            color=self.use_item)
                        await ctx.send(embed=embed)
                        await dump_json('users', data)
                        return
                    else:
                        embed = Embed(description='{} cannot be revived with a potion.'.format(member_name),
                                      color=self.error)
                        await ctx.send(embed=embed)
                        return
        else:
            embed = Embed(description='You don\'t have any {}s in your inventory!'.format(item),
                          color=self.error)
            await ctx.send(embed=embed)

    @staticmethod
    async def member_name(member):
        # grab author nick
        member_name = member.nick
        if member_name is None:
            member_name = member.name
        return member_name

    async def is_member_exhausted(self, member):
        data = await load_json('users')
        if data[str(member.id)]['hp'] <= 0:
            embed = Embed(title='You are too exhausted to attack!',
                          color=self.lose_the_fight)
            return embed
        return None

    async def is_target_artemis(self, guild, target, roll):
        data = await load_json('users')
        pattern = re.compile(r'' + re.escape(target.lower()))
        for member in guild.members:
            member_name = await self.member_name(member)
            matches = pattern.finditer(member_name.lower())
            for match in matches:
                if member.id == self.client.user.id:
                    if self.artemis_is_vulnerable is False:
                        artemis_react = ['Artemis effortlessly evades the attack.',
                                         'Artemis brushes off the attack.',
                                         'Artemis ignores the attack.']
                        embed = Embed(title=random.choice(artemis_react),
                                      color=self.enemy_miss)
                        return embed
                    data[str(self.client.user.id)]['hp'] -= roll
                    await dump_json('users', data)
                return None

    async def is_target_member(self, ctx, author, guild, target, roll, msg):
        if not self.duel_is_active:
            embed = Embed(description='You cannot attack another person outside of a duel.',
                          color=self.error)
            await ctx.send(embed=embed)
            return
        data = await load_json('users')
        pattern = re.compile(r'' + re.escape(target.lower()))
        for member in guild.members:
            member_name = await self.member_name(member)
            if member.mention == target:
                mid = str(member.id)
                if roll == 0:
                    embed = Embed(description=msg,
                                  color=self.user_attack)
                    return embed
                if data[mid]['hp'] <= 0:
                    data[mid]['hp'] -= roll
                    damage = '{} took {} points of damage!'.format(member_name, roll)
                    unconscious = '{} is already unconscious! :dizzy: '.format(member_name)
                    embed = Embed(description='{}\n{}'.format(damage, unconscious),
                                  color=self.user_attack)
                    await dump_json('users', data)
                    return embed

                data[mid]['hp'] -= roll
                await dump_json('users', data)
                if data[mid]['hp'] <= 0:
                    damage = '{} took {} points of damage!'.format(member_name, roll)
                    unconscious = '{} has lost consciousness! :dizzy: '.format(member_name)
                    embed = Embed(description='{}\n{}'.format(damage, unconscious),
                                  color=self.user_attack)
                    exp = data[mid]['level'] * 10
                    await self.character_level(ctx, author, exp)
                    await dump_json('users', data)
                    return embed
                else:
                    damage = '{} took {} points of damage!'.format(member_name, roll)
                    hp_left = '{} has {}/{} HP left!'.format(member_name, data[mid]['hp'], data[mid]['max hp'])
                    embed = Embed(description='{}\n{}\n{}'.format(msg, damage, hp_left),
                                  color=self.user_attack)
                    exp = data[mid]['level'] * 5
                    await self.character_level(ctx, author, exp)
                    await dump_json('users', data)
                    return embed
            matches = pattern.finditer(member_name.lower())
            for match in matches:
                mid = str(member.id)
                if roll == 0:
                    embed = Embed(description=msg,
                                  color=self.user_attack)
                    return embed
                if data[mid]['hp'] <= 0:
                    data[mid]['hp'] -= roll
                    damage = '{} took {} points of damage!'.format(member_name, roll)
                    unconscious = '{} is already unconscious! :dizzy: '.format(member_name)
                    embed = Embed(description='{}\n{}'.format(damage, unconscious),
                                  color=self.user_attack)
                    await dump_json('users', data)
                    return embed
                data[mid]['hp'] -= roll
                await dump_json('users', data)
                if data[mid]['hp'] <= 0:
                    damage = '{} took {} points of damage!'.format(member_name, roll)
                    unconscious = '{} has lost consciousness! :dizzy: '.format(member_name)
                    embed = Embed(description='{}\n{}'.format(damage, unconscious),
                                  color=self.user_attack)
                    exp = data[mid]['level'] * 10
                    await self.character_level(ctx, author, exp)
                    return embed
                else:
                    damage = '{} took {} points of damage!'.format(member_name, roll)
                    hp_left = '{} has {}/{} HP left!'.format(member_name, data[mid]['hp'], data[mid]['max hp'])
                    embed = Embed(description='{}\n{}\n{}'.format(msg, damage, hp_left),
                                  color=self.user_attack)
                    exp = data[mid]['level'] * 5
                    await self.character_level(ctx, author, exp)
                    return embed
        return None

    @staticmethod
    async def critical_check(user_attack, author_name):
        critical = random.randint(1, 20)
        if critical == 1:
            msg = '{} missed!'.format(author_name)
            user_attack *= 0
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

    @staticmethod
    async def get_member_weapon(member):
        mid = str(member.id)
        user_data = await load_json('users')
        rpg_data = await load_json('rpg')

        weapon = user_data[mid]['equipped']['weapon']
        if weapon is None:
            return 1, 4, weapon
        for key, value in rpg_data['weapons'].items():
            if weapon in value:
                rolls = value[weapon]['rolls']
                limit = value[weapon]['limit']
                return rolls, limit, weapon

    @staticmethod
    async def character_level(ctx, member, exp_gain):
        # give experience to a member after defeating a monster or member
        data = await load_json('users')
        data[str(member.id)]['exp'] = data[str(member.id)]['exp'] + int(exp_gain)
        experience = int(data[str(member.id)]['exp'])
        lvl_start = data[str(member.id)]['level']
        lvl_end = int(experience ** (1/4))
        await dump_json('users', data)

        if lvl_start < lvl_end:
            hp_gain = random.randint(5, 10) + 2
            data[str(member.id)]['max hp'] += hp_gain
            level_up = Embed(description=':arrow_up: {0} reached level {1}!\n'
                                         '{0} gained {2} HP!'.format(member.name, lvl_end, hp_gain))
            await ctx.send(embed=level_up)
            data[str(member.id)]['level'] = lvl_end
            await dump_json('users', data)

    @staticmethod
    async def send_embed(channel, msg, color):
        embed = Embed(
            description=msg,
            color=color)
        await channel.send(embed=embed)

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
