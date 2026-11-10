from io import BytesIO
from pathlib import Path
import discord
from PIL import Image

KAARTEN_MAP = Path(__file__).parent / "assets" / "Cards"
SOORT_NAAM = {"♠": "Spades", "♥": "Hearts", "♦": "Diamonds", "♣": "Clubs"}
RANG_NAAM = {"A": "Ace", "T": "10", "J": "Jack", "Q": "Queen", "K": "King"}  # 2-9 blijven hetzelfde
ACHTERKANT = KAARTEN_MAP / "Back.png"  # pas aan als jullie achterkant anders heet

KAART_HOOGTE = 180   # alle kaarten worden hierop geschaald
RUIMTE = 12          # ruimte tussen kaarten en rijen
RAND = 20
TAFEL_KLEUR = (34, 100, 60, 255)  # groen vilt

def kaart_pad(kaart):
    rang, soort = kaart
    suit = SOORT_NAAM[soort]
    rank = RANG_NAAM.get(rang, rang)
    return KAARTEN_MAP / suit / f"{rank}{suit}.png"

def laad(pad):
    img = Image.open(pad).convert("RGBA")
    breedte = int(img.width * KAART_HOOGTE / img.height)
    return img.resize((breedte, KAART_HOOGTE))

def rij_breedte(plaatjes):
    return sum(p.width for p in plaatjes) + RUIMTE * (len(plaatjes) - 1)

def maak_tafel(dealer, speler, verberg_dealer=True):
    """Geeft een discord.File met de dealer bovenaan en de speler onderaan."""
    dealer_img = []
    for i, kaart in enumerate(dealer):
        if verberg_dealer and i == 1:
            dealer_img.append(laad(ACHTERKANT))
        else:
            dealer_img.append(laad(kaart_pad(kaart)))
    speler_img = [laad(kaart_pad(k)) for k in speler]

    breedte = max(rij_breedte(dealer_img), rij_breedte(speler_img)) + 2 * RAND
    hoogte = 2 * KAART_HOOGTE + RUIMTE * 2 + 2 * RAND
    tafel = Image.new("RGBA", (breedte, hoogte), TAFEL_KLEUR)

    for rij, y in ((dealer_img, RAND), (speler_img, RAND + KAART_HOOGTE + RUIMTE * 2)):
        x = (breedte - rij_breedte(rij)) // 2   # rij centreren
        for kaart in rij:
            tafel.paste(kaart, (x, y), kaart)
            x += kaart.width + RUIMTE

    buffer = BytesIO()
    tafel.save(buffer, format="PNG")
    buffer.seek(0)
    return discord.File(buffer, filename="tafel.png")