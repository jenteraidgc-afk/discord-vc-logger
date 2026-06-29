import discord
import json
import os
import gspread
from datetime import datetime

# Load secrets from environment
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

TRIGGER = "For VC"

# Connect to Google Sheet
def get_sheet():
    creds = json.loads(GOOGLE_CREDENTIALS)
    gc = gspread.service_account_from_dict(creds)
    return gc.open_by_key(SPREADSHEET_ID).sheet1

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Bot online as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    lines = [line.strip() for line in message.content.splitlines() if line.strip()]

    # Check if starts with trigger and has all 6 lines
    if len(lines) == 6 and lines[0] == TRIGGER:
        player_name = lines[1]
        level = lines[2]
        game_id = lines[3]
        contact = lines[4]
        number = lines[5]

        # Validate Game ID starts with AS
        if not game_id.upper().startswith("AS"):
            await message.channel.send("❌ Error: Player Game ID must start with **AS**.")
            return

        # Timestamp = exact time message was sent
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [timestamp, player_name, level, game_id, contact, number]

        try:
            sheet = get_sheet()
            # Add headers only once
            if not sheet.acell("A1").value:
                sheet.append_row([
                    "Date / Time",
                    "Player's Name",
                    "Level",
                    "Player Game Id",
                    "Contact way",
                    "Number"
                ])
            # Send data
            sheet.append_row(row)
            await message.channel.send(
                f"✅ Saved successfully!\n"
                f"🕒 {timestamp}\n👤 {player_name}\n🎮 {game_id}"
            )
        except Exception as e:
            print("Error:", e)
            await message.channel.send("⚠️ Failed to save. Please try again.")

    elif len(lines) > 0 and lines[0] == TRIGGER:
        await message.channel.send(
            "❌ Incomplete format! Send exactly like this:\n```\nFor VC\nPlayer's Name\nLevel\nASxxxxxx\nContact Way\nNumber\n```"
        )

client.run(DISCORD_TOKEN)
