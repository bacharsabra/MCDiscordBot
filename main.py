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


def get_server_status():
    try:
        server = JavaServer.lookup(f"{MC_SERVER}:{MC_PORT}")
        status = server.status()
        online = status.version.protocol == 769
        return status, online
    except Exception as e:
        print(f"❌ No connection: {e}")
        return None, False


async def check_server_status():
    global last_status
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    check_interval = 20

    while not client.is_closed():
        status, online = get_server_status()
        if online:
            print("✅ Server is ONLINE")
            if last_status is False:
                await channel.send(
                    f"💡 Dar lserver! {status.players.online}/{status.players.max} players online. @everyone"
                )
        else:
            print("❌ Server is OFFLINE")
            check_interval = 5 if last_status else 20

        last_status = online
        await asyncio.sleep(check_interval)


@tree.command(name="mcstatus", description="Check if the server is online")
async def mcstatus_command(interaction: discord.Interaction):
    online = get_server_status()
    if online:
        response = "✅ **Online**"
    elif not online:
        response = "⛔ **Offline**"
    else:
        response = "⚠️ **Server is currently loading or unavailable.**"
    await interaction.response.send_message(response)


@tree.command(name="mcplayers", description="List all players online")
async def mcplayers_command(interaction: discord.Interaction):
    status, online = get_server_status()
    if online:
        if status.players.online > 0 and status.players.sample:
            players = "\n".join([player.name for player in status.players.sample])
            response = f"👥 **Currently playing:**\n{players}"
        else:
            response = "🚪 **No players online**"
    elif not online:
        response = "⛔ **Server is offline.**"
    else:
        response = "⚠️ **Server is currently loading or unavailable.**"
    await interaction.response.send_message(response)


@client.event
async def on_ready():
    await tree.sync()
    client.loop.create_task(check_server_status())


client.run(TOKEN)
