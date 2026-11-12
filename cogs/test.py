import discord
from discord import app_commands
from discord.ext import commands
import database
from checks import geregistreerd

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leeg", description="Testfunctie: zet je saldo op 0")
    @geregistreerd()
    async def leeg(self, interaction: discord.Interaction):
        database.zet_saldo(interaction.user.id, 0)
        await interaction.response.send_message("Je saldo staat nu op 0.", ephemeral=True)

    @app_commands.command(name="delete", description="Verwijder jezelf uit de database")
    @geregistreerd()
    async def delete(self, interaction: discord.Interaction):
        database.verwijder_speler(interaction.user.id)
        await interaction.response.send_message("Je bent verwijderd.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Test(bot))