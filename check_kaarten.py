from kaartplaatje import kaart_pad, ACHTERKANT

ontbreekt = []
for rang in "A23456789TJQK":
    for soort in "♠♥♦♣":
        pad = kaart_pad((rang, soort))
        if not pad.exists():
            ontbreekt.append(pad)
if not ACHTERKANT.exists():
    ontbreekt.append(ACHTERKANT)

print("Alles is aanwezig!" if not ontbreekt else "Ontbreekt:")
for pad in ontbreekt:
    print(" ", pad)