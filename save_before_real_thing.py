import networkx as nx
import matplotlib.pyplot as plt


def create_digraph():

    G = nx.DiGraph()

    # Add nodes with a 'type' attribute
    #G.add_node('CPU_1', type='CPU')
    G.add_node('CPU_1', type='CPU')
    G.add_node('CPU_2', type='CPU')
    G.add_node('CPU_3', type='CPU')
    G.add_node('CE_1', type='CE')
    G.add_node('CE_2', type='CE')
    G.add_node('SM_1', type='SM')
    G.add_node('SM_2', type='SM')
    G.add_node('SM_3', type='SM')
    
    

    # Add directed edges between nodes
    #G.add_edge('CPU_1', 'SM_1',w relation='controls')
    

    return G


def visualize_graph(G):


    color_map = []
    for node in G.nodes(data=True):
        if node[1]['type'] == 'CPU':
            color_map.append('blue')
        elif node[1]['type'] == 'SM':
            color_map.append('green')
        elif node[1]['type'] == 'CE':
            color_map.append('red')

    # Draw the graph
    pos = nx.spring_layout(G)  # Positioning layout for better visualization
    nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=2000, font_size=10, font_color='white')
        
    # Add edge labels
    edge_labels = nx.get_edge_attributes(G, 'suspension')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    # Show the plot
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
    visualize_graph(DIG)
    #do_the_compute()
