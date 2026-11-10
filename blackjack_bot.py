import os
import sqlite3
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# database 
db = sqlite3.connect('blackjack.db')
db.execute(
    "CREATE TABLE IF NOT EXISTS spelers ("
    "user_id INTEGER PRIMARY KEY, "
    "naam TEXT NOT NULL)"
)
db.commit()

#bot
bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

@bot.tree.command(name="start", description="Registreer jezelf bij de blackjack bot")
async def start(interaction: discord.Interaction):
    cursor = db.execute(
        "INSERT OR IGNORE INTO spelers (user_id, naam) VALUES (?, ?)",
        (interaction.user.id, interaction.user.name),
    )
    db.commit()

    if cursor.rowcount == 1:
        await interaction.response.send_message("Welkom! Je bent nu geregistreerd.")
    else:
        await interaction.response.send_message("Je was al geregistreerd.", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Ingelogd als {bot.user}")

bot.run(os.environ["Token"])