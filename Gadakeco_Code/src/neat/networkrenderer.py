import pygame
import random

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
    pygame.draw.rect(surface, (128, 128, 128, 128), (0, 0, 100 * TILESIZE, 18 * TILESIZE))#27 *TILESIZE
    #draw a rectangle with the color (128, 128, 128, 128), postion(0, 0) and size(27 * TILESIZE, 18 * TILESIZE)
    # draw minimap
    for y in range(18):
        for x in range(27):
            if values[y * 27 + x] != 0:
                color = colors[values[y * 27 + x]]
                surface.fill(color, (TILESIZE * x, TILESIZE * y, TILESIZE, TILESIZE))
                pygame.draw.rect(surface, (0, 0, 0), (TILESIZE * x, TILESIZE * y, TILESIZE, TILESIZE), 1)
                #the last parameter 1 means width=1 and used for line thickness

    # Zeichnen Sie hier das Netzwerk auf das Surface.
    

    # TODO node_dict 只存在hidden_nodes 的位置，input_nodes 和output_nodes 的位置在画线的时候也是需要的？ 
    node_dict={}
    #save in form of {"node_name":(x.node, y.node)}
    possible_position=[(x,y) for x in range(28,60) for y in range(0,18)]
    #save all left position in Surface

    for node in network.genome.nodes["hidden_nodes"]:
        if node.node_name in node_dict:
            continue
        else:
            position=random.choice(possible_position)
            possible_position.remove(position)
            node_dict[node.node_name]=position
    #refresh the node_dict and possible_position
    for _ in node_dict:
        x=node_dict[_][0]
        y=node_dict[_][1]
        surface.fill(colors[1], (TILESIZE * x, TILESIZE * y, TILESIZE, TILESIZE))
        pygame.draw.rect(surface, (0, 0, 0), (TILESIZE * x, TILESIZE * y, TILESIZE, TILESIZE), 1)

    connection_dict={}

    for key_connection, values_connection in network.genome.connection.items():
        if values_connection==1:
            connection_dict[key_connection]=(0, 201, 87)
        elif values_connection==-1:
            connection_dict[key_connection]=(255, 0, 0)
        else:
            connection_dict[key_connection]=(255,255,0)
    
    for nodes, color_line in connection_dict.items():
        pygame.draw.line(surface, color_line, node_dict[nodes[0].node_name], node_dict[nodes[1].node_name], 1)


        









   






