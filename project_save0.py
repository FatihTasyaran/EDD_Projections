import networkx as nx
import matplotlib.pyplot as plt
import math
from collections import defaultdict

def create_digraph():

    G = nx.DiGraph()

    # Add nodes with a 'type' attribute
    #G.add_node('CPU_1', type='CPU')
    G.add_node('CPU_1', type='CPU')
    G.add_node('CPU_2', type='CPU')
    G.add_node('CPU_3', type='CPU')
    G.add_node('CPU_4', type='CPU')
    G.add_node('CPU_5', type='CPU')
    G.add_node('CPU_6', type='CPU')
    G.add_node('CPU_7', type='CPU')
    G.add_node('CPU_8', type='CPU')
    G.add_node('CE_1', type='CE')
    G.add_node('CE_2', type='CE')
    G.add_node('SM_1', type='SM')
    G.add_node('SM_2', type='SM')
    G.add_node('SM_3', type='SM')
    G.add_node('SM_4', type='SM')
    
    

    # Add directed edges between nodes
    #G.add_edge('CPU_1', 'SM_1', relation='controls')
    G.add_edge('CPU_1', 'CE_1', relation='proceed')
    G.add_edge('CE_1', 'CPU_2', relation='proceed')
    G.add_edge('CPU_2', 'SM_1', relation='proceed')
    G.add_edge('SM_1', 'SM_2', relation='proceed')
    G.add_edge('SM_2', 'SM_3', relation='proceed')
    G.add_edge('SM_3', 'CPU_3', relation='proceed')
    G.add_edge('CPU_3', 'CE_2', relation='proceed')
    G.add_edge('CE_2', 'CPU_4', relation='proceed')
    G.add_edge('CPU_2', 'CPU_5', relation='proceed')
    G.add_edge('CPU_5', 'CPU_6', relation='proceed')
    G.add_edge('CPU_5', 'CPU_7', relation='proceed')
    G.add_edge('CPU_5', 'SM_4', relation='proceed')
    G.add_edge('CPU_6', 'CPU_8', relation='proceed')
    G.add_edge('CPU_7', 'CPU_8', relation='proceed')
    G.add_edge('SM_4', 'CPU_8', relation='proceed')
    G.add_edge('CPU_8', 'CPU_3', relation='proceed')
    return G


def visualize_graph(G):

    
    color_map = []
    for node in G.nodes(data=True):
        print(node)
        if node[1]['type'] == 'CPU':
            color_map.append('blue')
        elif node[1]['type'] == 'SM':
            color_map.append('green')
        elif node[1]['type'] == 'CE':
            color_map.append('red')

    # Draw the graph
    pos = nx.bfs_layout(G, G.nodes()[0])  # Positioning layout for better visualization
    nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=2000, font_size=10, font_color='white')
        
    # Add edge labels
    #edge_labels = nx.get_edge_attributes(G, 'suspension')
    #nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    # Show the plot
    plt.show()


def visualize_bfs(G):
    # Choose a starting node for BFS
    start_node = next(iter(G.nodes()))

    # Perform BFS to get edges in BFS order
    bfs_edges = list(nx.bfs_edges(G, start_node))

    # Create a position dictionary to store the layout positions
    pos = {}
    x, y = 0, 0  # Start position for the root node

    # Manually assign positions based on BFS
    for edge in bfs_edges:
        parent, child = edge
        if parent not in pos:
            pos[parent] = (x, y)
            x += 1  # Move right for each new parent node
    
        # Position child nodes directly below their parent
        pos[child] = (pos[parent][0], pos[parent][1] - 1)

    # Add the start_node if it doesn't have any children
    if start_node not in pos:
        pos[start_node] = (0, 0)

    # Draw the graph using the custom BFS layout
    nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=500, font_size=10)
    plt.show()

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
        if node[1]['type'] == 'CPU':
            color_map.append('blue')
        elif node[1]['type'] == 'SM':
            color_map.append('green')
        elif node[1]['type'] == 'CE':
            color_map.append('red')
            
    # Draw the graph using the custom BFS layout
    nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=500, font_size=10)
    plt.show()
    
'''
def launch_analysis(_exec, _input):

    output = (_exec, _input)
    output = parse_output
    
    return output

def do_the_compute():

    _continue = TRUE
    while(_continue):
        for i in range(1, 3):
            output = launch_analysis(_exec, _input)
            _input = revisit(output, input_l, i)
 '''

if __name__ == "__main__":

    DIG = create_digraph()
    visualize_bfs_w_depth(DIG)
    #do_the_compute()
