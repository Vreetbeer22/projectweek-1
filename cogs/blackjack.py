import random
import discord
import database
from discord import app_commands
from discord.ext import commands
from checks import geregistreerd
from kaartplaatje import maak_tafel
from profiel import update_naam


#Kaarten en spel met telling
def waarde(hand):
    totaal = 0
    azen = 0
    for rang, soort in hand:
        if rang == "A":
            totaal += 11
            azen += 1
        elif rang in "TJQK":
            totaal += 10
        else:
            totaal += int(rang)
    while totaal > 21 and azen > 0:
        totaal -= 10
        azen -= 1
    return totaal

class Spel:
    def __init__(self, inzet):
        self.inzet = inzet
        self.deck = [(rang, soort) for rang in "A23456789TJQK" for soort in "♠♥♦♣"]
        random.shuffle(self.deck)
        self.speler = [self.deck.pop(), self.deck.pop()]
        self.dealer = [self.deck.pop(), self.deck.pop()]

    def trek(self, hand):
        hand.append(self.deck.pop())

    def dealer_speelt(self):
        while waarde(self.dealer) < 17:
            self.trek(self.dealer)

    def is_blackjack(self, hand):
        return len(hand) == 2 and waarde(hand) == 21

    def resultaat(self):
        s = waarde(self.speler)
        d = waarde(self.dealer)
        if s > 21:
            return "verlies"
        if self.is_blackjack(self.speler) and not self.is_blackjack(self.dealer):
            return "blackjack"
        if d > 21 or s > d:
            return "winst"
        if s < d:
            return "verlies"
        return "gelijk"

# Per resultaat: (tekst, kleur, hoeveel keer je inzet je terugkrijgt)
UITSLAGEN = {
    "blackjack": ("Blackjack! Je wint 3:2", discord.Color.gold(), 2.5),
    "winst": ("Je wint!", discord.Color.green(), 2),
    "verlies": ("Dealer wint.", discord.Color.red(), 0),
    "gelijk": ("Gelijkspel.", discord.Color.light_grey(), 1)
}

# ---------- 2. Het bericht in Discord ----------
def maak_embed(spel, einde):
    if einde:
        tekst, kleur, _ = UITSLAGEN[spel.resultaat()]
        beschrijving = f"**{tekst}**"
        dealer_waarde = waarde(spel.dealer)
    else:
        kleur = discord.Color.blurple()
        beschrijving = "Kies `/hit` of `/stand`"
        dealer_waarde = waarde(spel.dealer[:1])

    embed = discord.Embed(title="Blackjack", description=beschrijving, color=kleur)
    embed.add_field(name="Dealer", value=f"Waarde: **{dealer_waarde}**")
    embed.add_field(name="Jij", value=f"Waarde: **{waarde(spel.speler)}**")
    embed.set_image(url="attachment://tafel.png")
    embed.set_footer(text=f"Inzet: {spel.inzet} tokens")

    plaatje = maak_tafel(spel.dealer, spel.speler, verberg_dealer=not einde)
    return embed, plaatje

# ---------- 3. De commands ----------
class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spellen = {}   # user_id -> het spel waar die speler nu in zit

    async def stuur(self, interaction, spel, einde=False, content=None):
        "Stuurt de tafel naar Discord. Is het spel afgelopen, dan betaalt dit ook uit."
        if einde:
            del self.spellen[interaction.user.id]
            _, _, factor = UITSLAGEN[spel.resultaat()]
            database.pas_saldo_aan(interaction.user.id, int(spel.inzet * factor))
            await update_naam(interaction.user)
            content = f"Potje van **{interaction.user.display_name}**"

        embed, plaatje = maak_embed(spel, einde)
        await interaction.response.send_message(content=content, embed=embed, file=plaatje, ephemeral=not einde)

    async def haal_spel(self, interaction):
        "Zoekt het lopende spel. Zo niet: stuurt een melding en geeft None terug."
        spel = self.spellen.get(interaction.user.id)
        if spel is None:
            await interaction.response.send_message(
                "Je hebt geen spel. Gebruik `/start`.", ephemeral=True
            )
        return spel

    @app_commands.command(name="start", description="Start een potje blackjack")
    @app_commands.describe(inzet="Aantal tokens dat je inzet")
    @geregistreerd()
    async def start(self, interaction: discord.Interaction,
                    inzet: app_commands.Range[int, 1, 1000]):
        uid = interaction.user.id

        if uid in self.spellen:
            await self.stuur(interaction, self.spellen[uid],
                             content="Je zit al in een spel!")
            return

        saldo = database.get_saldo(uid)
        if saldo < inzet:
            await interaction.response.send_message(
                f"Je hebt niet genoeg tokens. Je saldo is {saldo}.", ephemeral=True
            )
            return

        database.pas_saldo_aan(uid, -inzet)
        await update_naam(interaction.user)
        spel = Spel(inzet)
        self.spellen[uid] = spel

        # Heeft iemand meteen 21? Dan is het spel direct afgelopen.
        direct_klaar = waarde(spel.speler) == 21 or waarde(spel.dealer) == 21
        await self.stuur(interaction, spel, einde=direct_klaar)

    @app_commands.command(name="hit", description="Pak nog een kaart")
    @geregistreerd()
    async def hit(self, interaction: discord.Interaction):
        spel = await self.haal_spel(interaction)
        if spel is None:
            return

        spel.trek(spel.speler)
        totaal = waarde(spel.speler)

        if totaal == 21:
            spel.dealer_speelt()
        await self.stuur(interaction, spel, einde=totaal >= 21)

    @app_commands.command(name="stand", description="Stop en laat de dealer spelen")
    @geregistreerd()
    async def stand(self, interaction: discord.Interaction):
        spel = await self.haal_spel(interaction)
        if spel is None:
            return

        spel.dealer_speelt()
        await self.stuur(interaction, spel, einde=True)

async def setup(bot):
    await bot.add_cog(Blackjack(bot))