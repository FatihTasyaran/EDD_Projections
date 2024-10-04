import networkx as nx
import matplotlib.pyplot as plt
import math
from collections import defaultdict
import get_four_basic_tasks

def create_digraph():

    G = nx.DiGraph()

    # Add nodes with a 'type' attribute, there will be other attributes: a, c, q, etc.
    #G.add_node('CPU_1', type='CPU')
    #G.add_node('CPU_1', _type='CPU', _wcet = 3, _bcet = 5) ##How to add other specs
    G.add_node('CPU_1', _type='CPU', _cmin=3, _cmax=5, _amin=0, _amax=5, _d=15, _p=1, _q=1) 
    G.add_node('CPU_2', _type='CPU', _cmin=3, _cmax=8, _amin=10, _amax=11, _d=24, _p=1, _q=3)
    G.add_node('CPU_3', _type='CPU', _cmin=4, _cmax=5, _amin=13, _amax=16, _d=25, _p=1, _q=1)
    G.add_node('CPU_4', _type='CPU', _cmin=4, _cmax=5, _amin=13, _amax=16, _d=25, _p=1, _q=1)
    G.add_node('CPU_5', _type='CPU', _cmin=2, _cmax=6, _amin=19, _amax=20, _d=31, _p=1, _q=1)
    G.add_node('CPU_6', _type='CPU', _cmin=2, _cmax=10, _amin=23, _amax=25, _d=37, _p=1, _q=1)
    G.add_node('CPU_7', _type='CPU', _cmin=1, _cmax=10, _amin=28, _amax=33, _d=44, _p=1, _q=3)
    G.add_node('CPU_8', _type='CPU', _cmin=4, _cmax=7, _amin=36, _amax=39, _d=51, _p=1, _q=2)
    G.add_node('CPU_9', _type='CPU', _cmin=3, _cmax=7, _amin=42, _amax=44, _d=56, _p=1, _q=1)
    G.add_node('CPU_10', _type='CPU', _cmin=1, _cmax=10, _amin=47, _amax=51, _d=66, _p=1, _q=2)
    G.add_node('CPU_11', _type='CPU', _cmin=3, _cmax=6, _amin=54, _amax=59, _d=70, _p=1, _q=1)
    
    G.add_node('CE_1', _type='CE', _cmin=3, _cmax=4, _amin=2, _amax=6, _d=12, _p=1, _q=3)
    G.add_node('CE_2', _type='CE', _cmin=1, _cmax=3, _amin=9, _amax=13, _d=19, _p=1, _q=1)
    G.add_node('CE_3', _type='CE', _cmin=3, _cmax=5, _amin=16, _amax=19, _d=30, _p=1, _q=3)
    G.add_node('CE_4', _type='CE', _cmin=2, _cmax=3, _amin=23, _amax=26, _d=35, _p=1, _q=2)
    
    G.add_node('SM_1', _type='SM', _cmin=1, _cmax=4, _amin=1, _amax=4, _d=14, _p=1, _q=2)
    G.add_node('SM_2', _type='SM', _cmin=2, _cmax=5, _amin=6, _amax=7, _d=19, _p=1, _q=3)
    G.add_node('SM_3', _type='SM', _cmin=4, _cmax=6, _amin=10, _amax=13, _d=25, _p=2, _q=1)
    G.add_node('SM_4', _type='SM', _cmin=1, _cmax=8, _amin=16, _amax=19, _d=32, _p=3, _q=2)
    G.add_node('SM_5', _type='SM', _cmin=3, _cmax=7, _amin=22, _amax=24, _d=38, _p=2, _q=3)
    
    

    # Add directed edges between nodes
    #G.add_edge('CPU_1', 'SM_1', relation='controls')

    G.add_edge('CPU_1', 'CE_1', relation='1', susp_min = 0, susp_max = 0) #1
    G.add_edge('CE_1', 'CPU_2', relation='2', susp_min = 0, susp_max = 0) #2

    G.add_edge('CPU_2', 'SM_1', relation='3', susp_min = 0, susp_max = 0) #3
    G.add_edge('SM_1', 'SM_2', relation='4', susp_min = 0, susp_max = 0) #4
    G.add_edge('SM_2', 'SM_3', relation='5', susp_min = 0, susp_max = 0) #5
    G.add_edge('SM_3', 'CPU_7', relation='6', susp_min = 0, susp_max = 0) #6

    G.add_edge('CPU_2', 'CPU_3', relation='15', susp_min = 0, susp_max = 0) #15
    
    G.add_edge('CPU_3', 'CPU_4', relation='16', susp_min = 0, susp_max = 0) #16
    G.add_edge('CPU_4', 'CPU_6', relation='20', susp_min = 0, susp_max = 0) #20

    G.add_edge('CPU_3', 'CPU_5', relation='17', susp_min = 0, susp_max = 0) #17
    G.add_edge('CPU_5', 'CPU_6', relation='21', susp_min = 0, susp_max = 0) #21

    G.add_edge('CPU_3', 'SM_4', relation='18', susp_min = 0, susp_max = 0) #18
    G.add_edge('SM_4', 'CPU_6', relation='19', susp_min = 0, susp_max = 0) #19

    G.add_edge('CPU_6', 'CPU_7', relation='22', susp_min = 0, susp_max = 0) #22

    G.add_edge('CPU_7', 'CE_2', relation='7', susp_min = 0, susp_max = 0) #7
    G.add_edge('CE_2', 'CPU_8', relation='8', susp_min = 0, susp_max = 0) #8

    G.add_edge('CPU_8', 'CE_3', relation='9', susp_min = 0, susp_max = 0) #9
    G.add_edge('CE_3', 'CPU_9', relation='10', susp_min = 0, susp_max = 0) #10

    G.add_edge('CPU_9', 'SM_5', relation='11', susp_min = 0, susp_max = 0) #11
    G.add_edge('SM_5', 'CPU_10', relation='12', susp_min = 0, susp_max = 0) #12

    G.add_edge('CPU_10', 'CE_4', relation='13', susp_min = 0, susp_max = 0) #13
    G.add_edge('CE_4', 'CPU_11', relation='14', susp_min = 0, susp_max = 0) #14
    
    
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

#It's iterative, recursive would be so much more better
def paths(G):

    nodes = list(G.nodes(data=True))
    paths = []
    for _node in nodes:
        for _iter in nodes:
            if(_node[1]['_type'] == _iter[1]['_type'] and _node[0] != _iter[0]):
                #print("1:", _node, "2:", _iter)
                ##Change this with bfs with incremental depth later
                '''
                all_paths = list(nx.all_simple_paths(G, source=_node[0], target=_iter[0]))
                if(len(all_paths) != 0):
                    print("len:", len(all_paths))
                    for path in all_paths:
                        print(path)
                '''
                bfs = list(nx.dfs_tree(G, source=_node[0], depth_limit=2))
                print("node:", _node[0], bfs)

def recursive_paths_first(G):

    nodes = list(G.nodes(data=True))
    #print(nodes)
    for node in nodes:
        out_edges = G.out_edges(nbunch = node[0])
        in_edges = G.in_edges(nbunch = node[0]) ##This will be needed later
        print("node:", node, "out_edges:", G.out_edges(nbunch = node[0]))
        print("node:", node, "in_edges:", G.in_edges(nbunch = node[0]))

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

##Start is the node where search is started, source and destination define an edge
def recursive_search(G, node_start, node_source, node_destination, path, all_paths):
    path.append((node_source, node_destination))
    nodes = dict(G.nodes)
    ##All conditions satisfied, FOUND
    if(nodes[node_destination]["_type"] == nodes[node_start]["_type"] and check_different(G, path)):
        all_paths.append(list(path))
        ##Start with consecutively same types, SKIP
    elif(not check_different(G, path) and len(path) == 2):
        path.pop()
        return
    ##Same types exist but there are other, 
    elif(nodes[node_source]["_type"] == nodes[node_destination]["_type"] and not check_different(G, path)):
        path.pop()
        return
    else:
        new_out_edges = G.out_edges(nbunch = node_destination)
        temp = node_source
        node_source = node_destination
        for edge in new_out_edges:
            node_destination = edge[1]
            recursive_search(G, node_start, node_source, node_destination, path, all_paths)

    path.pop()

def recursive_paths(G):

    nodes = dict(G.nodes(data=True))
    all_suspensions = []
    for node in nodes:
        out_edges = G.out_edges(nbunch = node) 
        for edge in out_edges:
            path = []
            all_paths = []
            recursive_search(G, node, node, edge[1], path, all_paths)
            all_suspensions.extend(all_paths)
    #print("all suspensions:")
    #for suspension in all_suspensions:
        #print(suspension)
    return all_suspensions

        

def find_type(a_node):

    if(a_node.find("CPU") != -1):
        return "CPU"

    elif(a_node.find("SM") != -1):
        return "SM"

    elif(a_node.find("CE") != -1):
        return "CE"

    else:
        return "Error code 1: Weird Type is Seen During Suspension Dictionary Generation"

def return_intermediate_nodes_in_path(path):

    intermediate = []
    for i in range(1, len(path)):
        intermediate.append(path[i][0])

    return intermediate

def get_cmin_sum_intermediates(G, intermediates):

    nodes = G.nodes(data=True)
    sum = 0
    for intermediate in intermediates:
        sum = sum + nodes[intermediate]["_cmin"]
    
    return sum
    
def get_cmax_sum_intermediates(G, intermediates):

    nodes = G.nodes(data=True)
    sum = 0
    for intermediate in intermediates:
        sum = sum + nodes[intermediate]["_cmax"]
    
    return sum
    
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
    
def generate_cpu_projection(G, suspensions_dict):

    cpu_projection = nx.DiGraph()
    all_nodes = dict(G.nodes(data=True))
    all_edges = G.edges(data=True)
    access_nodes = G.nodes(data=True)
    
    for node in all_nodes:
        if(access_nodes[node]["_type"] == "CPU"):
            node_data = G.nodes[node]
            cpu_projection.add_node(node, **node_data)

    print("##############################")
    print("CPU Projection All Nodes")
    nodes = cpu_projection.nodes(data=True)
    for node in nodes:
        print(node)
    print("##############################")

    ###############################################
    ##Add related edges here

    ##Edges that remains the same, source and target same type
    for edge in all_edges:
        #print("edge:", edge, "type:", type(edge), edge[0], edge[1], edge[2])
        source_type = find_type(edge[0])
        target_type = find_type(edge[1])
        if(source_type == "CPU" and target_type == "CPU"):
            cpu_projection.add_edge(edge[0], edge[1], susp_min = 0, susp_max = 0)

            
    ##Add suspension edges
    for key in suspensions_dict:
        
        suspension = suspensions_dict[key]
        if(suspension['type'] == "CPU"):
            min_susp, max_susp = return_path_with_maximum_suspension_first_iter(G, suspension)
            cpu_projection.add_edge(suspension['source_node'], suspension['target_node'], susp_min = min_susp, susp_max = max_susp)
    ###############################################

    print("##############################")
    print("CPU Projection All Edges")
    edges = cpu_projection.edges(data=True)
    for edge in edges:
        print(edge)
    print("##############################")
    return cpu_projection

def create_suspensions_dict(all_suspensions):

    suspensions_dict = {}
    enum = 1
    for suspension in all_suspensions: ##Enumerating manually here
        print("Suspension:", suspension)
        len_suspend = len(suspension)
        source_node = suspension[0][0]
        target_node = suspension[len_suspend - 1][1]
        
        exist = False
        for key in suspensions_dict:
            if(suspensions_dict[key]['source_node'] == source_node and suspensions_dict[key]['target_node'] == target_node):
                exist = True
                suspensions_dict[key]['paths'].append(suspension)

        if(not exist):
            new_key = str(enum)
            suspensions_dict[new_key] = {}
            suspensions_dict[new_key]['source_node'] = source_node
            suspensions_dict[new_key]['target_node'] = target_node
            suspensions_dict[new_key]['type'] = find_type(source_node)
            suspensions_dict[new_key]['paths'] = []
            suspensions_dict[new_key]['paths'].append(suspension)
            enum = enum + 1

    return suspensions_dict

        
##Here we assume for now: sink and source are always CPU nodes. And after the first iteration first step, we are using response times.    
if __name__ == "__main__":

    DIG = create_digraph()
    #reverse_DIG = DIG.reverse()
    all_suspensions = recursive_paths(DIG)

    print("##############################")
    print("all suspensions:")
    for suspension in all_suspensions:
        print(suspension)
    print("##############################")

    print("##############################")
    print("suspensions dict iter:")
    suspensions_dict = create_suspensions_dict(all_suspensions)
    for key in suspensions_dict:
        print(key, suspensions_dict[key])
    print("##############################")
        
    
    print("##############################")
    print("all nodes:")
    all_nodes = dict(DIG.nodes(data=True))
    for node in all_nodes:
        print(node, DIG.nodes()[node])
    print("##############################")
    
    print("##############################")
    print("all edges:")
    all_edges = DIG.edges(data=True)
    for edge in all_edges:
        print(edge)
    print("##############################")
    
    cpu_projection = generate_cpu_projection(DIG, suspensions_dict)
    
