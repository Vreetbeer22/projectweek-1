import re
import discord
import database

def _basisnaam(naam):
    return re.sub(r"\s*\[\d+ 🪙\]$", "", naam)

async def update_naam(member):
    saldo = database.get_saldo(member.id)
    if saldo is None or not isinstance(member, discord.Member):
        return
    nieuw = f"{_basisnaam(member.display_name)[:20]} [{saldo} 🪙]"
    try:
        await member.edit(nick=nieuw)
    except discord.Forbidden:
        pass