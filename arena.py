import discord
import random
import json
from karma import Karma
from discord.ext import commands


class Arena:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def start(self, ctx):
        author = ctx.message.author
        members = ctx.message.server.members
        channel = ctx.message.channel.name
        if channel != 'arena':
            arena = discord.utils.get(self.client.get_all_channels(), name='arena')
            await self.client.send_message(ctx.message.channel,
                                           'Sorry. Combat can only happen in the {0}!'.format(arena.mention))
            return

        # pick combatant one
        await self.client.send_message(ctx.message.channel, 'Pick the first combatant:')
        user_one = await self.client.wait_for_message(author=author, timeout=30)
        print('split', user_one.content.split())
        user_one = user_one.content.split()
        user_one = user_one[0]

        for member in members:
            if member in user_one.content.split():
                pass
        # check if user in members
        for member in members:
            # format user IDs to match mentionable IDs
            if user1 not in user_one.content:
                print('one', user1)
                await self.client.send_message(ctx.message.channel, '{0} is not a member of this server.'.format(user_one.content))
                return
            if user2 not in user_one.content:
                print(user2)
                await self.client.send_message(ctx.message.channel, '{0} is not a member of this server.'.format(user_one.content))
                return
        await self.client.send_message(ctx.message.channel, 'Pick the second combatant:')

        user_two = self.client.wait_for_message(author=author, timeout=30)
        if user_two.id not in members:
            await self.client.send_message(ctx.message.channel, '{0} is not a member of this server.'.format(user_two))
            return

        await self.client.send_message(ctx.message.channel, 'Choose max HP:')
        hp = self.client.wait_for_message(author=author, timeout=30)

        await self.client.send_message(ctx.message.channel, 'Lastly, choose attack power from 1 to 10:')
        atk_power = self.client.wait_for_message(author=author, timeout=30)

        fighter_one = self.fighter(user_one, hp)
        fighter_two = self.fighter(user_two, hp)
        # start combat
        self.combat(ctx, fighter_one, fighter_two, atk_power)

    @staticmethod
    async def fighter(user, hp):
        fighter = {'Combatant': user,
                   'HP': hp}
        return fighter

    async def combat(self, ctx, fighter_one, fighter_two, atk_power):
        # randomly choose the first to go
        await self.client.send_message(ctx.message.channel, 'Choosing which fighter goes first at random!')
        first = random.choice(fighter_one, fighter_two)
        if first == fighter_two:
            second = fighter_two
        else:
            second = fighter_one
        await self.client.send_message(ctx.message.channel, '{0} goes first!\n'
                                                           'Attack with !attack <custom input>'.format(first))

        # begin attack loop
        while True:
            # first attacks
            await self.client.send_message(ctx.message.channel, 'Go, {0}!'.format(first))
            attack = self.client.wait_for_message(author=fighter_one, timeout=30)
            if attack.message.content[:6] == '!attack':
                attack = self.roll(atk_power)
                second = second['HP'] - attack
                # break if mortal blow was dealt
                if second['HP'] < 1:
                    break
            else:
                await ctx.client.send_message(ctx.message.channel, 'You waited to long and lost your chance!')

            # second attacks
            await self.client.send_message(ctx.message.channel, 'Go, {0}!'.format(second))
            attack = self.client.wait_for_message(author=fighter_one, timeout=30)
            if attack.message.content[:6] == '!attack':
                attack = self.roll(atk_power)
                first = first['HP'] - attack
                # break if mortal blow was dealt
                if first['HP'] < 1:
                    break
            else:
                await self.client.send_message(ctx.message.channel, 'You waited to long and lost your chance!')

    @staticmethod
    async def roll(atk_power):
        # roll first die for miss/hit/critical
        multiplier = random.randint(1, 20)

        # miss
        if multiplier < 2:
            multiplier = 0

        # light attack
        if 1 < multiplier < 3:
            multiplier = .5

        # normal attack
        if 2 < multiplier < 20:
            multiplier = 1

        # critical hit
        if multiplier == 20:
            multiplier = 1.5

        # calculate attack
        attack = ((random.randint(1, 10) * multiplier) for value in atk_power)
        return attack


def setup(client):
    client.add_cog(Arena(client))
