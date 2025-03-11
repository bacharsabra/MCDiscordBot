import discord
import os
import asyncio
import requests
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
            print(f"🔄 Checking server: {MC_SERVER}:{MC_PORT}")
            response = requests.get(f"https://api.mcsrvstat.us/2/{MC_SERVER}")
            data = response.json()
            online = data.get("online", False)
            print("✅ Server is ONLINE")
        except Exception as e:
            online = False
            print(f"❌ Server is OFFLINE. Error: {e}")

        if online and last_status is False:
            await channel.send("💡 Dar lserver!")
            last_status = True
        elif not online:
            last_status = False

        await asyncio.sleep(30)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("❌ ERROR: Channel not found! Check CHANNEL_ID and bot permissions.")
    else:
        print("✅ Bot is ready and monitoring the server!")

    # Check server status
    client.loop.create_task(check_server_status())

client.run(TOKEN)
