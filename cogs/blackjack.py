import random
import discord
from discord import app_commands
from discord.ext import commands
from checks import geregistreerd
from kaartplaatje import maak_tafel

# ---------- Kaartenlogica ----------
def nieuw_deck():
    deck = [(rang, soort) for rang in "A23456789TJQK" for soort in "♠♥♦♣"]
    random.shuffle(deck)
    return deck

def waarde(hand):
    totaal, azen = 0, 0
    for rang, _ in hand:
        if rang == "A":
            totaal += 11
            azen += 1
        elif rang in "TJQK":
            totaal += 10
        else:
            totaal += int(rang)
    while totaal > 21 and azen:
        totaal -= 10
        azen -= 1
    return totaal

class Spel:
    def __init__(self):
        self.deck = nieuw_deck()
        self.speler = [self.deck.pop(), self.deck.pop()]
        self.dealer = [self.deck.pop(), self.deck.pop()]

    def trek(self, hand):
        hand.append(self.deck.pop())

    def dealer_speelt(self):
        while waarde(self.dealer) < 17:
            self.trek(self.dealer)

def uitslag(spel):
    s, d = waarde(spel.speler), waarde(spel.dealer)
    if s > 21:
        return "Bust! Je gaat over 21. Dealer wint.", discord.Color.red()
    if d > 21:
        return "Dealer gaat bust. Je wint!", discord.Color.green()
    if s > d:
        return "Je wint!", discord.Color.green()
    if s < d:
        return "Dealer wint.", discord.Color.red()
    return "Gelijkspel.", discord.Color.light_grey()

# ---------- Het menu (embed + plaatje) ----------
def maak_embed(spel, einde=False):
    if einde:
        tekst, kleur = uitslag(spel)
        embed = discord.Embed(title="Blackjack", description=f"**{tekst}**", color=kleur)
        dealer_waarde = waarde(spel.dealer)
    else:
        embed = discord.Embed(
            title="Blackjack",
            description="Kies `/hit` of `/stand`",
            color=discord.Color.blurple(),
        )
        dealer_waarde = "?"

    embed.add_field(name="Dealer", value=f"Waarde: **{dealer_waarde}**", inline=True)
    embed.add_field(name="Jij", value=f"Waarde: **{waarde(spel.speler)}**", inline=True)
    embed.set_image(url="attachment://tafel.png")

    bestand = maak_tafel(spel.dealer, spel.speler, verberg_dealer=not einde)
    return embed, bestand

# ---------- Commands ----------
class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spellen = {}  # user_id -> lopend Spel

    @app_commands.command(name="start", description="Start een potje blackjack")
    @geregistreerd()
    async def start(self, interaction: discord.Interaction):
        uid = interaction.user.id

        if uid in self.spellen:
            embed, bestand = maak_embed(self.spellen[uid])
            await interaction.response.send_message(
                "Je zit al in een spel!", embed=embed, file=bestand, ephemeral=True
            )
            return

        spel = Spel()

        if waarde(spel.speler) == 21 or waarde(spel.dealer) == 21:
            embed, bestand = maak_embed(spel, einde=True)
            await interaction.response.send_message(embed=embed, file=bestand)
            return

        self.spellen[uid] = spel
        embed, bestand = maak_embed(spel)
        await interaction.response.send_message(embed=embed, file=bestand)

    @app_commands.command(name="hit", description="Pak nog een kaart")
    @geregistreerd()
    async def hit(self, interaction: discord.Interaction):
        uid = interaction.user.id
        spel = self.spellen.get(uid)
        if spel is None:
            await interaction.response.send_message("Je hebt geen spel. Gebruik `/start`.", ephemeral=True)
            return

        spel.trek(spel.speler)
        totaal = waarde(spel.speler)

        if totaal > 21:
            del self.spellen[uid]
            embed, bestand = maak_embed(spel, einde=True)
        elif totaal == 21:
            spel.dealer_speelt()
            del self.spellen[uid]
            embed, bestand = maak_embed(spel, einde=True)
        else:
            embed, bestand = maak_embed(spel)

        await interaction.response.send_message(embed=embed, file=bestand)

    @app_commands.command(name="stand", description="Stop en laat de dealer spelen")
    @geregistreerd()
    async def stand(self, interaction: discord.Interaction):
        uid = interaction.user.id
        spel = self.spellen.get(uid)
        if spel is None:
            await interaction.response.send_message("Je hebt geen spel. Gebruik `/start`.", ephemeral=True)
            return

        spel.dealer_speelt()
        del self.spellen[uid]
        embed, bestand = maak_embed(spel, einde=True)
        await interaction.response.send_message(embed=embed, file=bestand)

async def setup(bot):
    await bot.add_cog(Blackjack(bot))