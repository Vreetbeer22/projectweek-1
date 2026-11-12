import discord
from discord import app_commands
from discord.ext import commands

COMMANDS = {
    "Account": [
        ("/welkom", "Maak een account aan en krijg 100 tokens"),
        ("/saldo", "Bekijk hoeveel tokens je hebt"),
        ("/gratis", "Krijg 100 tokens als je op 0 staat"),
    ],
    "Blackjack": [
        ("/start inzet", "Start een potje met een inzet van 1 tot 1000 tokens"),
        ("/hit", "Pak nog een kaart"),
        ("/stand", "Stop en laat de dealer spelen"),
    ],
}

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Laat alle commands zien")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Blackjack bot",
            description="Hier zijn alle commands:",
            color=discord.Color.blurple(),
        )
        for categorie, regels in COMMANDS.items():
            tekst = "\n".join(f"`{naam}`: {uitleg}" for naam, uitleg in regels)
            embed.add_field(name=categorie, value=tekst, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Help(bot))