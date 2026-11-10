import discord
from discord import app_commands
from discord.ext import commands
import database
from checks import geregistreerd

class Account(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="welkom", description="Maak een account aan en krijg 100 tokens")
    async def welkom(self, interaction: discord.Interaction):
        if database.maak_speler(interaction.user.id, interaction.user.name):
            await interaction.response.send_message("Welkom! Je account is aangemaakt en je krijgt 100 tokens.")
        else:
            await interaction.response.send_message("Je hebt al een account.", ephemeral=True)

    @app_commands.command(name="saldo", description="Bekijk je tokens")
    @geregistreerd()
    async def saldo(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Je hebt {database.get_saldo(interaction.user.id)} tokens.", ephemeral=True
        )

    @app_commands.command(name="gratis", description="Krijg 100 tokens als je op 0 staat")
    @geregistreerd()
    async def gratis(self, interaction: discord.Interaction):
        saldo = database.get_saldo(interaction.user.id)
        if saldo > 0:
            await interaction.response.send_message(
                f"Je hebt nog {saldo} tokens. Je kunt alleen gratis tokens krijgen als je op 0 staat.",
                ephemeral=True,
            )
        else:
            database.pas_saldo_aan(interaction.user.id, 100)
            await interaction.response.send_message("Je hebt 100 tokens gekregen!")

async def setup(bot):
    await bot.add_cog(Account(bot))