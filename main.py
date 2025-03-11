import discord
import os
import asyncio
from mcstatus import JavaServer
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
MC_SERVER = os.getenv("MC_SERVER")
MC_PORT = int(os.getenv("MC_PORT"))

# Create bot instance
intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_status = False

async def check_server_status():
    global last_status
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        try:
            server = JavaServer.lookup(f"{MC_SERVER}:{MC_PORT}")
            status = server.status()
            if status.version.protocol == 762:
                online = True
            else:
                online = False
        except Exception as e:
            online = False
            print(f"Error checking server status: {e}")

        if online and last_status is False:
            await channel.send(f"💡 Dar lserver! {status.players.online}/{status.players.max} players online.")
            last_status = True
        elif not online:
            last_status = False

        await asyncio.sleep(30)


@client.event
async def on_ready():
    client.get_channel(CHANNEL_ID)
    client.loop.create_task(check_server_status())

client.run(TOKEN)
