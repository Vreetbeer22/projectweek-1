import discord
from discord import app_commands
import database

class Nietgeregistreerd(app_commands.CheckFailure):
    pass

def geregistreerd():
    async def check(interaction: discord.Interaction):
        if not database.bestaat(interaction.user.id):
            raise Nietgeregistreerd()
        return True
    return app_commands.check(check)