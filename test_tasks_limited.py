import networkx as nx
import global_definitions

t = global_definitions.TYPES_ALPHA

def return_tasks():

    ##Task 2##
    G2 = nx.DiGraph()
    G2.add_node('CPU_1', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=0, _d=120, _p=2, _q=1)
    G2.add_node('CPU_2', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=0, _d=120, _p=2, _q=1)
    G2.add_node('CPU_3', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=0, _d=120, _p=2, _q=1)

    G2.add_node('SM_1', _type=t["SM"], _cmin=5, _cmax=10, _amin=0, _amax=0, _d=120, _p=2, _q=1)
    G2.add_node('SM_2', _type=t["SM"], _cmin=5, _cmax=10, _amin=0, _amax=0, _d=120, _p=2, _q=1)

    G2.add_edge('CPU_1', 'SM_1', susp_min=0, susp_max=0)
    G2.add_edge('SM_1', 'CPU_2', susp_min=0, susp_max=0)
    G2.add_edge('CPU_2', 'SM_2', susp_min=0, susp_max=0)
    G2.add_edge('SM_2', 'CPU_3', susp_min=0, susp_max=0)


    ##Task 3##
    G3 = nx.DiGraph()
    G3.add_node('CPU_1', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=0, _d=60, _p=2, _q=1)
    G3.add_node('CPU_2', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=0, _d=60, _p=2, _q=1)
    G3.add_node('CPU_3', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=0, _d=60, _p=2, _q=1)

    G3.add_node('CE_1', _type=t["CE"], _cmin=5, _cmax=10, _amin=0, _amax=0, _d=60, _p=2, _q=1)
    G3.add_node('CE_2', _type=t["CE"], _cmin=5, _cmax=10, _amin=0, _amax=0, _d=60, _p=2, _q=1)

    G3.add_edge('CPU_1', 'CE_1', susp_min=0, susp_max=0)
    G3.add_edge('CE_1', 'CPU_2', susp_min=0, susp_max=0)
    G3.add_edge('CPU_2', 'CE_2', susp_min=0, susp_max=0)
    G3.add_edge('CE_2', 'CPU_3', susp_min=0, susp_max=0)
    
    
    return G2, G3
