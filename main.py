import discord
import asyncio
import random
import lol_commands
import api
import time
client = discord.Client()


@client.event
@asyncio.coroutine
def on_message(message):
    # bot should not reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!guess'):
        yield from client.send_message(message.channel, 'Guess a number between 1 and 10')

        def guess_check(m):
            return m.content.isdigit()

        guess = yield from client.wait_for_message(timeout=5.0, author=message.author, check=guess_check)
        answer = random.randint(1, 10)
        if guess is None:
            msg = "You took too long! The answer was {}."
            yield from client.send_message(message.channel, msg.format(answer))
            return

        if int(guess.content) == answer:
            yield from client.send_message(message.channel, "You're right!")
        else:
            yield from client.send_message(message.channel, "Nope! It was {}.".format(answer))

    elif message.content.startswith('!r_winrate') or message.content.startswith('!wr') or message.content.startswith('!winrate'):
        try:
            role = message.content.split(" ", 1)[1]
        except IndexError:
            yield from client.send_message(message.channel,
                                           "Error with input! See !help for more info.")
            return

        yield from client.send_message(message.channel,
                                       lol_commands.role_lookup(role))

    elif message.content.startswith('!banrate') or message.content.startswith('!br'):
        yield from client.send_message(message.channel,
                                       lol_commands.bans_lookup())

    elif message.content.startswith('!ranked'):
        try:
            summoner = message.content.split(" ", 1)[1]
        except IndexError:
            yield from client.send_message(message.channel,
                                           "Error with input! See !help for more info.")
            return

        yield from client.send_message(message.channel,
                                       "Looking up ranked data for {}...".format(summoner))

        info = lol_commands.summoner_lookup(summoner)
        summoner_info = ""
        if isinstance(info, tuple):
            summoner_info = \
                '''
                {} is in {} {} ({} LP), with a record of {}-{} ({:.3g}%).
                '''.format(summoner, info[0], info[1], info[2], info[3], info[4], info[5])


        yield from client.send_message(message.channel,
                                       summoner_info if summoner_info else info)

    elif message.content.startswith('!ingame'):
        try:
            summoner = message.content.split(" ", 1)[1]
        except IndexError:
            yield from client.send_message(message.channel,
                                           "Error with input! See !help for more info.")
            return

        yield from client.send_message(message.channel,
                                       "Looking up in-game data for {}...".format(summoner))
        yield from client.send_message(message.channel,
                                       lol_commands.game_lookup(summoner))

    elif message.content.startswith("!coinflip") or message.content.startswith("!flip")\
            or message.content.startswith("!coin"):
        flip = random.randint(0,1)
        msg = "It's {}!"
        if flip:
            yield from client.send_message(message.channel,
                                           msg.format("heads"))
        else:
            yield from client.send_message(message.channel,
                                           msg.format("tails"))

    elif message.content.startswith("!monkey"):
        #TODO: only check members that are in current server
        monkeys = [x for x in client.get_all_members()]
        index = random.randrange(0, len(monkeys))
        mention = monkeys[index].mention
        yield from client.send_message(message.channel, "{} is a boosted :monkey:!".format(mention))

    elif message.content.startswith("!help"):
        help_msg = \
        '''
        Commands:
        !coinflip or !coin or !flip - flips a coin
        !guess - plays a guessing game
        !r_winrate [role] or !wr [role] or !winrate [role] - finds champs with highest winrate for role
        !banrate or !br - finds champs with highest banrate
        !ranked [summoner] - shows summoner's ranked info.
        !ingame [summoner] - shows summoner's current game
        !help - show this message
        '''

        yield from client.send_message(message.channel,
                                       help_msg)





@client.event
@asyncio.coroutine
def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("-----")




try:
    client.run(api.DISCORD_TOKEN)
except discord.LoginFailure:
    print("Could not log in.")
