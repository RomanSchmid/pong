import random
import pyglet
from pyglet import gl
from pyglet.window import key

# GLOBALNI KONSTANTY

# Velikost okna v pixelech
SIRKA = 900
VYSKA = 600

VELIKOST_MICE = 20
TLOUSTKA_PALKY = 10
DELKA_PALKY = 100
RYCHLOST = 200 # v pixelech za sekundu
RYCHLOST_PALKY = RYCHLOST * 1.5 # taky v pixelech za sekundu

DELKA_PULICI_CARKY = 20
VELIKOST_FONTU = 42
ODSAZENI_TEXTU = 30

# GLOBALNI PROMENNE

pozice_palek = [VYSKA // 2, VYSKA // 2] # vertikalni pozice dvou palek
pozice_mice = [0, 0] # x,y soradnice micku -- nastavene v reset()
rychlost_mice = [0, 0] # x, y slozky rychlosti micku -- nastavene v reset()
stisknute_klavesy = set() # sada stisknutych klaves
skore = [0, 0] # skore dvou hracu

def nakresli_obdelnik(x1, y1, x2, y2):
    """Nakresli obdelnik na dane souradnice

    Nazorny diagram::

         y2 - +-----+
              |/////|
         y1 - +-----+
              :     :
             x1    x2
    """
    # Volame OpenGL
    gl.glBegin(gl.GL_TRIANGLE_FAN) # zacni kreslit spojene trojuhelniky
    gl.glVertex2f(int(x1), int(y1)) # vrchol A
    gl.glVertex2f(int(x1), int(y2)) # vrchol B
    gl.glVertex2f(int(x2), int(y2)) # vrchol C, nakresli trojuhelnik ABC
    gl.glVertex2f(int(x2), int(y1)) # vrchol D, nakresli trojuhelnik BCD
    gl.glEnd() # ukonci kresleni trojuhelniku

def vykresli():
    """Vykresli stav hry"""
    gl.glClear(gl.GL_COLOR_BUFFER_BIT) # smaz obsah okna (vybarvi na cerno)
    gl.glColor3f(1, 1, 1) # nastav barvu kresleni na bilou

    # Vykresleni micku
    nakresli_obdelnik(
        pozice_mice[0] - VELIKOST_MICE // 2,
        pozice_mice[1] - VELIKOST_MICE // 2,
        pozice_mice[0] + VELIKOST_MICE // 2,
        pozice_mice[1] + VELIKOST_MICE // 2,
    )

    # Vykresleni prvni palky
    nakresli_obdelnik(
        0,
        pozice_palek[0] - DELKA_PALKY // 2,
        TLOUSTKA_PALKY,
        pozice_palek[0] + DELKA_PALKY // 2,
    )

    # Vykresleni druhe palky
    nakresli_obdelnik(
       SIRKA - TLOUSTKA_PALKY,
       pozice_palek[1] - DELKA_PALKY // 2,
       SIRKA,
       pozice_palek[1] + DELKA_PALKY // 2,
    )

    for y in range(DELKA_PULICI_CARKY // 2, VYSKA, DELKA_PULICI_CARKY * 2):
        nakresli_obdelnik(
            SIRKA // 2 - 1,
            y,
            SIRKA // 2 + 1,
            y + DELKA_PULICI_CARKY,
        )

    nakresli_text(
        str(skore[0]),
        x=ODSAZENI_TEXTU,
        y=VYSKA - ODSAZENI_TEXTU - VELIKOST_FONTU,
        pozice_x='left',
    )

    nakresli_text(
        str(skore[1]),
        x=SIRKA - ODSAZENI_TEXTU,
        y=VYSKA - ODSAZENI_TEXTU - VELIKOST_FONTU,
        pozice_x='right',
    )

def nakresli_text(text, x, y, pozice_x):
    """Nakresli dany text na danou pozici

    Argument ``pozice_x`` muze byt "left" nebo "right", udava na kterou stranu
    bude text zarovnany
    """
    napis = pyglet.text.Label(
        text,
        font_size=VELIKOST_FONTU,
        x=x, y=y, anchor_x=pozice_x
    )
    napis.draw()

def stisk_klavesy(symbol, modifikatory):
    if symbol == key.W:
        stisknute_klavesy.add(('nahoru', 0))
    if symbol == key.S:
        stisknute_klavesy.add(('dolu', 0))
    if symbol == key.UP:
        stisknute_klavesy.add(('nahoru', 1))
    if symbol == key.DOWN:
        stisknute_klavesy.add(('dolu', 1))

def pusteni_klavesy(symbol, modifikatory):
    if symbol == key.W:
        stisknute_klavesy.discard(('nahoru', 0))
    if symbol == key.S:
        stisknute_klavesy.discard(('dolu', 0))
    if symbol == key.UP:
        stisknute_klavesy.discard(('nahoru', 1))
    if symbol == key.DOWN:
        stisknute_klavesy.discard(('dolu', 1))

def obnov_stav(dt):
    for cislo_palky in (0, 1):
        # pohyb podle klaves (viz funkce 'stisk_klavesy')
        if ('nahoru', cislo_palky) in stisknute_klavesy:
            pozice_palek[cislo_palky] += RYCHLOST_PALKY * dt
        if ('dolu', cislo_palky) in stisknute_klavesy:
            pozice_palek[cislo_palky] -= RYCHLOST_PALKY * dt

        # dolkni zarazka - kdyz je palka prilis dole, nastavime ji na minimum
        if pozice_palek[cislo_palky] < DELKA_PALKY / 2:
            pozice_palek[cislo_palky] = DELKA_PALKY / 2
        if pozice_palek[cislo_palky] > VYSKA - DELKA_PALKY / 2:
            pozice_palek[cislo_palky] = VYSKA - DELKA_PALKY / 2
    
    pozice_mice[0] += rychlost_mice[0] * dt
    pozice_mice[1] += rychlost_mice[1] * dt

    # Odraz micku od sten
    if pozice_mice[1] < VELIKOST_MICE // 2:
        rychlost_mice[1] = abs(rychlost_mice[1])
    if pozice_mice[1] > VYSKA - VELIKOST_MICE // 2:
        rychlost_mice[1] = -abs(rychlost_mice[1])  

    palka_min = pozice_mice[1] - VELIKOST_MICE / 2 - DELKA_PALKY / 2
    palka_max = pozice_mice[1] + VELIKOST_MICE / 2 + DELKA_PALKY / 2  

    # odrazeni vlevo
    if pozice_mice[0] < TLOUSTKA_PALKY + VELIKOST_MICE / 2:
        if palka_min < pozice_palek[0] < palka_max:
            # palka je na spravnem miste, odrazime micek
            rychlost_mice[0] = abs(rychlost_mice[0])
        else:
            # palka je jinde nez ma byt, hrac prohral
            skore[1] += 1
            reset()
    
    # odrazeni vpravo
    if pozice_mice[0] > SIRKA - (TLOUSTKA_PALKY + VELIKOST_MICE / 2):
        if palka_min < pozice_palek[1] < palka_max:
            rychlost_mice[0] = -abs(rychlost_mice[0])
        else:
            skore[0] += 1
            reset()

def reset():
    pozice_mice[0] = SIRKA // 2
    pozice_mice[1] = VYSKA // 2
    # x-ova rychlost - bud vpravo, nebo vlevo
    if random.randint(0, 1):
        rychlost_mice[0] = RYCHLOST
    else:
        rychlost_mice[0] = -RYCHLOST
    # y-ova rychlost - uplne nahodna
    rychlost_mice[1] = random.uniform(-1, 1) * RYCHLOST

reset()
# Otevreni okna o velikosti hraci plochy
window = pyglet.window.Window(width=SIRKA, height=VYSKA)
window.push_handlers(
    on_draw=vykresli, # na vykresleni okna pouzij funkci 'vykresli'
    on_key_press=stisk_klavesy,
    on_key_release=pusteni_klavesy,                         
)
pyglet.clock.schedule(obnov_stav)
pyglet.app.run() # spusteni hry
