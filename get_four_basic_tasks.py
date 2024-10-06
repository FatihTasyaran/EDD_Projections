import networkx as nx

def create_digraph():

    G = nx.DiGraph()

    # Add nodes with a 'type' attribute, there will be other attributes: a, c, q, etc.
    #G.add_node('CPU_1', type='CPU')
    #G.add_node('CPU_1', _type='CPU', _wcet = 3, _bcet = 5) ##How to add other specs
    G.add_node('CPU_1', _type='CPU', _cmin=3, _cmax=5, _amin=5, _amax=10, _d=15, _p=1, _q=1) 
    G.add_node('CPU_2', _type='CPU', _cmin=3, _cmax=8, _amin=5, _amax=5, _d=24, _p=1, _q=3)
    G.add_node('CPU_3', _type='CPU', _cmin=4, _cmax=5, _amin=5, _amax=5, _d=25, _p=1, _q=1)
    G.add_node('CPU_4', _type='CPU', _cmin=4, _cmax=5, _amin=5, _amax=5, _d=25, _p=1, _q=1)
    G.add_node('CPU_5', _type='CPU', _cmin=2, _cmax=6, _amin=5, _amax=5, _d=31, _p=1, _q=1)
    G.add_node('CPU_6', _type='CPU', _cmin=2, _cmax=10, _amin=5, _amax=5, _d=37, _p=1, _q=1)
    G.add_node('CPU_7', _type='CPU', _cmin=1, _cmax=10, _amin=5, _amax=5, _d=44, _p=1, _q=3)
    G.add_node('CPU_8', _type='CPU', _cmin=4, _cmax=7, _amin=5, _amax=5, _d=51, _p=1, _q=2)
    G.add_node('CPU_9', _type='CPU', _cmin=3, _cmax=7, _amin=5, _amax=5, _d=56, _p=1, _q=1)
    G.add_node('CPU_10', _type='CPU', _cmin=1, _cmax=10, _amin=5, _amax=5, _d=66, _p=1, _q=2)
    G.add_node('CPU_11', _type='CPU', _cmin=3, _cmax=6, _amin=5, _amax=5, _d=70, _p=1, _q=1)
    
    G.add_node('CE_1', _type='CE', _cmin=3, _cmax=4, _amin=5, _amax=5, _d=12, _p=1, _q=3)
    G.add_node('CE_2', _type='CE', _cmin=1, _cmax=3, _amin=5, _amax=5, _d=19, _p=1, _q=1)
    G.add_node('CE_3', _type='CE', _cmin=3, _cmax=5, _amin=5, _amax=5, _d=30, _p=1, _q=3)
    G.add_node('CE_4', _type='CE', _cmin=2, _cmax=3, _amin=5, _amax=5, _d=35, _p=1, _q=2)
    
    G.add_node('SM_1', _type='SM', _cmin=1, _cmax=4, _amin=5, _amax=5, _d=14, _p=1, _q=2)
    G.add_node('SM_2', _type='SM', _cmin=2, _cmax=5, _amin=5, _amax=5, _d=19, _p=1, _q=3)
    G.add_node('SM_3', _type='SM', _cmin=4, _cmax=6, _amin=5, _amax=5, _d=25, _p=2, _q=1)
    G.add_node('SM_4', _type='SM', _cmin=1, _cmax=8, _amin=5, _amax=5, _d=32, _p=3, _q=2)
    G.add_node('SM_5', _type='SM', _cmin=3, _cmax=7, _amin=5, _amax=5, _d=38, _p=2, _q=3)
    
    

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

def return_tasks():

    ####################################
    ##Task 1##
    G1 = nx.DiGraph()
    G1.add_node('CPU_1', _type='CPU', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=30, _p=1, _q=1)
    G1.add_node('CPU_2', _type='CPU', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=34, _p=1, _q=1)
    G1.add_node('CPU_3', _type='CPU', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=45, _p=1, _q=1)
    G1.add_node('CPU_4', _type='CPU', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=55, _p=1, _q=1)
    G1.add_node('CPU_5', _type='CPU', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=65, _p=1, _q=1)

    G1.add_node('SM_1', _type='SM', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=35, _p=1, _q=1)
    G1.add_node('SM_2', _type='SM', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=65, _p=1, _q=1)

    G1.add_node('CE_1', _type='CE', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=45, _p=1, _q=1)
    G1.add_node('CE_2', _type='CE', _cmin=2, _cmax=3, _amin=0, _amax=0, _d=65, _p=1, _q=1)

    G1.add_edge('CPU_1', 'CE_1', susp_min=0, susp_max=0)
    G1.add_edge('CE_1', 'CPU_2', susp_min=0, susp_max=0)
    G1.add_edge('CPU_2', 'SM_1', susp_min=0, susp_max=0)
    G1.add_edge('SM_1', 'CPU_3', susp_min=0, susp_max=0)
    G1.add_edge('CPU_3', 'CE_2', susp_min=0, susp_max=0)
    G1.add_edge('CE_2', 'CPU_4', susp_min=0, susp_max=0)
    G1.add_edge('CPU_4', 'SM_2', susp_min=0, susp_max=0)
    G1.add_edge('SM_2', 'CPU_5', susp_min=0, susp_max=0)
    ####################################

    ####################################
    ##Task 2##
    G2 = nx.DiGraph()
    G2.add_node('CPU_1', _type='CPU', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=28, _p=1, _q=1)
    G2.add_node('CPU_2', _type='CPU', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=32, _p=1, _q=1)
    G2.add_node('CPU_3', _type='CPU', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=42, _p=1, _q=1)
    G2.add_node('CPU_4', _type='CPU', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=50, _p=1, _q=1)
    G2.add_node('CPU_5', _type='CPU', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=75, _p=1, _q=1)

    G2.add_node('SM_1', _type='SM', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=30, _p=1, _q=1)
    G2.add_node('SM_2', _type='SM', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=60, _p=1, _q=1)

    G2.add_node('CE_1', _type='CE', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=45, _p=1, _q=1)
    G2.add_node('CE_2', _type='CE', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=60, _p=1, _q=1)

    G2.add_edge('CPU_1', 'SM_1', susp_min=0, susp_max=0)
    G2.add_edge('SM_1', 'CPU_2', susp_min=0, susp_max=0)
    G2.add_edge('CPU_2', 'CE_1', susp_min=0, susp_max=0)
    G2.add_edge('CE_1', 'CPU_3', susp_min=0, susp_max=0)
    G2.add_edge('CPU_3', 'SM_2', susp_min=0, susp_max=0)
    G2.add_edge('SM_2', 'CPU_4', susp_min=0, susp_max=0)
    G2.add_edge('CPU_4', 'CE_2', susp_min=0, susp_max=0)
    G2.add_edge('CE_2', 'CPU_5', susp_min=0, susp_max=0)

    return G1, G2
