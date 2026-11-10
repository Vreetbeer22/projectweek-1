import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from checks import Nietgeregistreerd

load_dotenv()

COGS = [
    "cogs.account",
    "cogs.blackjack",
    "cogs.test",        # haal deze regel weg als de bot live gaat
]

class BlackjackBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())

    async def setup_hook(self):
        for cog in COGS:
            await self.load_extension(cog)
        self.tree.error(self.on_tree_error)
        await self.tree.sync()

    async def on_tree_error(self, interaction: discord.Interaction, error):
        if isinstance(error, Nietgeregistreerd):
            await interaction.response.send_message(
                "Je hebt nog geen account. Gebruik eerst `/welkom`.", ephemeral=True
            )
        else:
            raise error

    async def on_ready(self):
        print(f"Ingelogd als {self.user}")

BlackjackBot().run(os.environ["Token"])