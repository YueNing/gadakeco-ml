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
    pygame.draw.rect(surface, (128, 128, 128, 128), (0, 0, 27 * TILESIZE, 18 * TILESIZE))#27 *TILESIZE
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
 
    node_dict={}
    #save in form of {"node_name":(x.node, y.node)}
    possible_position=[(x*TILESIZE,y*TILESIZE) for x in range(28,60) for y in range(0,18)]
    #choose the position of hidden_nodes randomly and save the rest possible positions
    for node in network.genome.hidden_nodes_dict:
            position=random.choice(possible_position)
            possible_position.remove(position)
            node_dict[node]=position
    #choose the position of output_nodes
    y_output_node=4
    for output_node in network.genome.output_nodes_dict:
        node_dict[output_node]=(65*TILESIZE, y_output_node*TILESIZE)
        y_output_node+=5
    #print nodes in screen
    for _ in node_dict:
        x=node_dict[_][0]
        y=node_dict[_][1]
        surface.fill(colors[1], (x, y, TILESIZE, TILESIZE))
        pygame.draw.rect(surface, (0, 0, 0), (x, y, TILESIZE, TILESIZE), 1)
    for y in range(18):
        for x in range(27):
            node_dict[f"in_{y * 27 + x}"]=[x*TILESIZE,y*TILESIZE]
    
    connection_dict={}
    line_colors={1:(0, 201, 87),-1:(255, 0, 0),0:(255,255,0)}
    #merge two dictionaries into one dictionary
    hidden_output_nodes = {**network.genome.hidden_nodes_dict, **network.genome.output_nodes_dict}
    #generate a dict in form of {"node_name":[("input_node.node_name", color),(),()]}
    for node in hidden_output_nodes:
        connection_dict[node]=[]
        for link in hidden_output_nodes[node].links:
            # import pdb; pdb.set_trace()
            if link[0].node_type=="input":
                pygame.draw.rect(surface, line_colors[1], (node_dict[link[0].node_name][0], node_dict[link[0].node_name][1], TILESIZE, TILESIZE), 1)
            if link[1]==1:
                connection_dict[node].append((link[0].node_name,line_colors[1]))
            elif link[1]==-1:
                connection_dict[node].append((link[0].node_name,line_colors[-1]))
            else:
                connection_dict[node].append((link[0].node_name,line_colors[0]))
    #print connections in screen
    for node in connection_dict:
        for i in range(len(connection_dict[node])):
            pygame.draw.line(surface, connection_dict[node][i][1], (node_dict[connection_dict[node][i][0]][0]+TILESIZE/2, node_dict[connection_dict[node][i][0]][1]+TILESIZE/2),\
            (node_dict[node][0]+TILESIZE/2, node_dict[node][1]+TILESIZE/2), 1)

        # if node==1:
        #     connection_dict[key_connection]=(0, 201, 87)
        # elif values_connection==-1:
        #     connection_dict[key_connection]=(255, 0, 0)
        # else:
        #     connection_dict[key_connection]=(255,255,0)
    # import pdb; pdb.set_trace()