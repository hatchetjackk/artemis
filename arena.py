import discord
import random
import json
from discord.ext import commands


class Arena:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def start(self, ctx):
        author = ctx.message.author
        members = ctx.message.server.members

        await ctx.client.send_message(ctx.message.channel, 'Pick the first combatant:')
        user_one = ctx.client.wait_for_message(author=author, timeout=30)
        if user_one.id not in members:
            await ctx.client.send_message(ctx.message.channel, '{0} is not a member of this server.'.format(user_one))
            return
        await ctx.client.send_message(ctx.message.channel, 'Pick the second combatant:')

        user_two = ctx.client.wait_for_message(author=author, timeout=30)
        if user_two.id not in members:
            await ctx.client.send_message(ctx.message.channel, '{0} is not a member of this server.'.format(user_two))
            return

        await ctx.client.send_message(ctx.message.channel, 'Choose max HP:')
        hp = ctx.client.wait_for_message(author=author, timeout=30)

        await ctx.client.send_message(ctx.message.channel, 'Lastly, choose attack power from 1 to 10:')
        atk_power = ctx.client.wait_for_message(author=author, timeout=30)

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
        await ctx.client.send_message(ctx.message.channel, 'Choosing which fighter goes first at random!')
        first = random.choice(fighter_one, fighter_two)
        if first == fighter_two:
            second = fighter_two
        else:
            second = fighter_one
        await ctx.client.send_message(ctx.message.channel, '{0} goes first!\n'
                                                           'Attack with !attack <custom input>'.format(first))

        # begin attack loop
        while True:
            # first attacks
            await ctx.client.send_message(ctx.message.channel, 'Go, {0}!'.format(first))
            attack = ctx.client.wait_for_message(author=fighter_one, timeout=30)
            if attack.message.content[:6] == '!attack':
                attack = self.roll(atk_power)
                second = second['HP'] - attack
                # break if mortal blow was dealt
                if second['HP'] < 1:
                    break
            else:
                await ctx.client.send_message(ctx.message.channel, 'You waited to long and lost your chance!')

            # second attacks
            await ctx.client.send_message(ctx.message.channel, 'Go, {0}!'.format(second))
            attack = ctx.client.wait_for_message(author=fighter_one, timeout=30)
            if attack.message.content[:6] == '!attack':
                attack = self.roll(atk_power)
                first = first['HP'] - attack
                # break if mortal blow was dealt
                if first['HP'] < 1:
                    break
            else:
                await ctx.client.send_message(ctx.message.channel, 'You waited to long and lost your chance!')

    async def roll(self, atk_power):
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