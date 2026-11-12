import os
import sqlite3
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# database 
db = sqlite3.connect('test.db')
db.execute(
    "CREATE TABLE IF NOT EXISTS spelers ("
    "user_id INTEGER PRIMARY KEY, "
    "naam TEXT NOT NULL)"
)
db.commit()

#Find root of specific card
def getCardRoot(rank, suit):
    stringRank = str(rank)
    return discord.File("assets/Cards/"+ suit + "/" + stringRank + suit +".png")

#bot
bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

@bot.tree.command(
    name="picture",
)
async def picture(interaction: discord.Interaction):

    file = getCardRoot(9, "Diamonds")

    await interaction.response.send_message(
        file=file
    )

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"logged in as {bot.user}")

bot.run(os.environ["Token"])