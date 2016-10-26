import discord
import asyncio
import random
import championgg
import api

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

    elif message.content.startswith('!r_winrate'):
        role = message.content.split(" ", 1)[1]

        # TODO: actually look up winrates
        yield from client.send_message(message.channel,
                                       championgg.role_lookup(role))

    elif message.content.startswith('!in_game'):
        summoner = message.content.split(" ", 1)[1]

        yield from client.send_message(message.channel,
                                       "Looking up game data for summoner {}...".format(summoner))
        # TODO: actually look up in game info


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
