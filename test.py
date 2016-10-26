import discord
import asyncio

client = discord.Client()

@client.event
@asyncio.coroutine
def on_ready():
    print("logged in as")
    print(client.user.name)
    print(client.user.id)


try:
    client.run("MjQwNjM1ODUyNjAwOTAxNjQy.CvGPow.SGaukWfshdA8W0Z295m1dq7MDKM")
except discord.LoginFailure:
    print("Could not log in.")
