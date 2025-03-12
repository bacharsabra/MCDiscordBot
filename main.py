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
tree = discord.app_commands.CommandTree(client)

last_status = False

async def check_server_status():
    global last_status
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    check_interval = 30 # change to 60

    while not client.is_closed():
        try:
            print(f"🔄 Checking server: {MC_SERVER}:{MC_PORT}")
            server = JavaServer.lookup(f"{MC_SERVER}:{MC_PORT}")
            status = server.status()
            online = status.version.protocol == 769
            if online:
                print("✅ Server is ONLINE")
                if last_status is False:
                    await channel.send(f"💡 Dar lserver! {status.players.online}/{status.players.max} players online.") #add @everyone later
                    check_interval = 60
            else:
                print("❌ Server is OFFLINE")
                if last_status is True:
                    check_interval = 5
                else:
                    check_interval = 30
        except Exception as e:
            online = False
            print(f"❌ No connection: {e}")
            check_interval = 30

        last_status = online

        await asyncio.sleep(check_interval)

@tree.command(name="mcstatus", description="Check if the server is online")
async def mcstatus_command(interaction: discord.Interaction):
    try:
        server = JavaServer.lookup(f"{MC_SERVER}:{MC_PORT}")
        status = server.status()
        online = status.version.protocol == 769
        if online:
            response = f"✅ **Online**\n👥 Players: {status.players.online}/{status.players.max}"
        else:
            response = "⛔ **Offline**"
    except Exception:
            response = "⚠️ **Server is currently loading or unavailable.**"
    await interaction.response.send_message(response)

@tree.command(name="mcplayers", description="List all players online")
async def mcplayers_command(interaction: discord.Interaction):
    try:
        server = JavaServer.lookup(f"{MC_SERVER}:{MC_PORT}")
        status = server.status()
        online = status.version.protocol == 769
        if online:
            if status.players.online > 0:
                players = "\n".join(status.players.sample)
                response = f"👥 **Players online**\n{players}"
            else:
                response = "🚪 **No players online**"
        else:
            response = "⛔ **Server is offline.**"
    except Exception:
        response = "⚠️ **Server is currently loading or unavailable.**"
    await interaction.response.send_message(response)

@client.event
async def on_ready():
    await tree.sync()
    client.get_channel(CHANNEL_ID)
    client.loop.create_task(check_server_status())

client.run(TOKEN)
