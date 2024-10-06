import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import functools
import math


def lcm(a, b):
    return abs(a * b) // math.gcd(a, b)

def lcm_of_list(numbers):
    return functools.reduce(lcm, numbers)


def check_different(G, path):

    different = False
    nodes = dict(G.nodes)
    first = nodes[path[0][0]]["_type"]
    for edge in path:
        if(nodes[edge[0]]["_type"] != first):
            different = True
        if(nodes[edge[1]]["_type"] != first):
            different = True
    
    return different
        

def find_type(a_node):

    if(a_node.find("CPU") != -1):
        return "CPU"

    elif(a_node.find("SM") != -1):
        return "SM"

    elif(a_node.find("CE") != -1):
        return "CE"

    else:
        print("Error code 1: Weird Type is Seen During Suspension Dictionary Generation, exiting..")
        exit(1)


def return_intermediate_nodes_in_path(path):

    intermediate = []
    for i in range(1, len(path)):
        intermediate.append(path[i][0])

    return intermediate

def get_cmin_sum_intermediates(G, intermediates):

    nodes = G.nodes(data=True)
    _sum = 0
    for intermediate in intermediates:
        _sum = _sum + nodes[intermediate]["_cmin"]
    
    return _sum
    
def get_cmax_sum_intermediates(G, intermediates):

    nodes = G.nodes(data=True)
    _sum = 0
    for intermediate in intermediates:
        _sum = _sum + nodes[intermediate]["_cmax"]
    
    return _sum

def return_path_cmin_sum(G, path):

    _sum = 0
    for node in path:
        _sum = _sum + G.nodes(data=True)[node]['_cmin'] 

    return _sum

def return_path_cmax_sum(G, path):

    _sum = 0
    for node in path:
        _sum = _sum + G.nodes(data=True)[node]['_cmax'] 

    return _sum
        
def minimum_extra_jitter_from_paths(G, paths):

    my_min = 2**20
    for path in paths:
        _sum = return_path_cmin_sum(G, path)
        if(my_min > _sum):
            my_min = _sum

    return my_min

def maximum_extra_jitter_from_paths(G, paths):

    my_max = 0

    for path in paths:
        _sum = return_path_cmax_sum(G, path)
        if(my_max < _sum):
            my_max = _sum

    return my_max
    
def return_path_with_maximum_suspension_first_iter(G, suspension):

    my_max = 0
    my_min = 2**20
    for path in suspension['paths']:
        intermediates = return_intermediate_nodes_in_path(path)
        cmin_sum = get_cmin_sum_intermediates(G, intermediates)
        cmax_sum = get_cmax_sum_intermediates(G, intermediates)

        if my_min > cmin_sum:
            my_min = cmin_sum
        if my_max < cmax_sum:
            my_max = cmax_sum
    
    return my_min, my_max
    

##Currently, assumes one CPU type root, therefore multiple roots are not implemented
def find_roots_in_DAG(DAG):

    root_nodes = []
    nodes = list(DAG.nodes())

    for node in nodes:
        if(DAG.in_degree(node) == 0):
            root_nodes.append(node)

    if(len(root_nodes) > 1):
        print("Error code 3: Currently does not support multiple roots in task DAG, exiting..")
        exit(1)

    return root_nodes
    

def visualize_bfs_w_depth(G):
    # Ensure the graph is not empty
    if len(G.nodes()) == 0:
        print("Graph is empty!")
        return
    
    # Select a valid start node
    start_node = next(iter(G.nodes()))
    print("Starting BFS from node:", start_node)
    
    # Perform BFS and track node depths
    bfs_edges = list(nx.bfs_edges(G, start_node))
    
    # Create a dictionary to store the depth of each node
    depth_dict = {start_node: 0}
    for parent, child in bfs_edges:
        depth_dict[child] = depth_dict[parent] + 1
    
    # Group nodes by their depth
    depth_levels = defaultdict(list)
    for node, depth in depth_dict.items():
        depth_levels[depth].append(node)
    
    # Create a position dictionary to store the layout positions
    pos = {}
    y_spacing = -0.5  # Vertical spacing between levels
    x_spacing = 1  # Horizontal spacing between nodes at the same level
    
    for depth, nodes_at_depth in depth_levels.items():
        x = 0  # Reset horizontal position for each depth level
        for node in nodes_at_depth:
            pos[node] = (x, y_spacing * depth)  # Assign position (x, y) based on depth
            x += x_spacing  # Space nodes horizontally

    color_map = []
    for node in G.nodes(data=True):
        print(node)
        if node[1]['_type'] == 'CPU':
            color_map.append('blue')
        elif node[1]['_type'] == 'SM':
            color_map.append('green')
        elif node[1]['_type'] == 'CE':
            color_map.append('red')
            
    # Draw the graph using the custom BFS layout
    nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=500, font_size=10)
    plt.show()

    


