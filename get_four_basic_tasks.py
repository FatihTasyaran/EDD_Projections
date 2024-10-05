import networkx as nx



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

    G1.add_node('CE_1', _type='SM', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=45, _p=1, _q=1)
    G1.add_node('CE_2', _type='SM', _cmin=2, _cmax=3, _amin=0, _amax=0, _d=65, _p=1, _q=1)

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

    G2.add_node('CE_1', _type='SM', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=45, _p=1, _q=1)
    G2.add_node('CE_2', _type='SM', _cmin=1, _cmax=2, _amin=0, _amax=0, _d=60, _p=1, _q=1)

    G2.add_edge('CPU_1', 'SM_1', susp_min=0, susp_max=0)
    G2.add_edge('SM_1', 'CPU_2', susp_min=0, susp_max=0)
    G2.add_edge('CPU_2', 'CE_1', susp_min=0, susp_max=0)
    G2.add_edge('CE_1', 'CPU_3', susp_min=0, susp_max=0)
    G2.add_edge('CPU_3', 'SM_2', susp_min=0, susp_max=0)
    G2.add_edge('SM_2', 'CPU_4', susp_min=0, susp_max=0)
    G2.add_edge('CPU_4', 'CE_2', susp_min=0, susp_max=0)
    G2.add_edge('CE_2', 'CPU_5', susp_min=0, susp_max=0)

    return G1, G2
