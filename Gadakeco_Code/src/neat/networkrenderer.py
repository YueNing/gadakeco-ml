import pygame

TILESIZE = 10


def render_network(surface, network, values):
    """
    Zeichnet die Minimap und den Netzwerkgraphen 
    
    Argumente:
        surface: ein pygame.Surface der Groesse 750 x 180 Pixel.
                 Darauf soll der Graph und die Minimap gezeichnet werden.
        network: das eigen implementierte Netzwerk (in network.py), dessen Graph gezeichnet werden soll.
        values: eine Liste von 27x18 = 486 Werten, welche die aktuelle diskrete Spielsituation darstellen
                die Werte haben folgende Bedeutung:
                 1 steht fuer begehbaren Block
                -1 steht fuer einen Gegner
                 0 leerer Raum
                Die Spielfigur befindet sich immer ca. bei der Position (10, 9) und (10, 10).
    """
    colors = {1: (255, 255, 255), -1: (255, 0, 0)}
    # draw slightly gray background for the minimap
    pygame.draw.rect(surface, (128, 128, 128, 128), (0, 0, 27 * TILESIZE, 18 * TILESIZE))
    # draw minimap
    for y in range(18):
        for x in range(27):
            if values[y * 27 + x] != 0:
                color = colors[values[y * 27 + x]]
                surface.fill(color, (TILESIZE * x, TILESIZE * y, TILESIZE, TILESIZE))
                pygame.draw.rect(surface, (0, 0, 0), (TILESIZE * x, TILESIZE * y, TILESIZE, TILESIZE), 1)

    # Zeichnen Sie hier das Netzwerk auf das Surface.
