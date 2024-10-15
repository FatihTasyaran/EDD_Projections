import networkx as nx
import global_definitions

t = global_definitions.TYPES_ALPHA

def return_tasks():

    ####################################
    ##Task 1##
    ##While reading tasks/jobs from input file, can implement this as t[type] + _ +counter
    G1 = nx.DiGraph()
    G1.add_node('CPU_1', _type=t["CPU"], _cmin=1, _cmax=5, _amin=0, _amax=5, _d=350, _p=1, _q=1)
    G1.add_node('CPU_2', _type=t["CPU"], _cmin=1, _cmax=5, _amin=0, _amax=0, _d=350, _p=1, _q=1)
    G1.add_node('CPU_3', _type=t["CPU"], _cmin=5, _cmax=10, _amin=0, _amax=0, _d=350, _p=1, _q=1)
    G1.add_node('CPU_4', _type=t["CPU"], _cmin=1, _cmax=5, _amin=0, _amax=0, _d=350, _p=1, _q=1)
    G1.add_node('CPU_5', _type=t["CPU"], _cmin=1, _cmax=5, _amin=0, _amax=0, _d=350, _p=1, _q=1)
    G1.add_node('CPU_6', _type=t["CPU"], _cmin=1, _cmax=5, _amin=0, _amax=0, _d=350, _p=1, _q=1)
    G1.add_node('CPU_7', _type=t["CPU"], _cmin=1, _cmax=5, _amin=0, _amax=0, _d=350, _p=1, _q=1)
    G1.add_node('CPU_8', _type=t["CPU"], _cmin=1, _cmax=5, _amin=0, _amax=0, _d=350, _p=1, _q=1)

    G1.add_node('SM_1', _type=t["SM"], _cmin=5, _cmax=10, _amin=0, _amax=0, _d=350, _p=1, _q=1)
    G1.add_node('SM_2', _type=t["SM"], _cmin=5, _cmax=10, _amin=0, _amax=0, _d=350, _p=1, _q=1)
    
    G1.add_node('CE_1', _type=t["CE"], _cmin=5, _cmax=10, _amin=0, _amax=0, _d=350, _p=1, _q=1)
    G1.add_node('CE_2', _type=t["CE"], _cmin=5, _cmax=10, _amin=0, _amax=0, _d=350, _p=1, _q=1)


    G1.add_edge('CPU_1', 'CPU_2', susp_min=0, susp_max=0)
    G1.add_edge('CPU_2', 'SM_1', susp_min=0, susp_max=0)
    G1.add_edge('CPU_2', 'CE_1', susp_min=0, susp_max=0)
    G1.add_edge('CPU_2', 'CPU_3', susp_min=0, susp_max=0)
    G1.add_edge('SM_1', 'CPU_4', susp_min=0, susp_max=0)
    G1.add_edge('CE_1', 'CPU_4', susp_min=0, susp_max=0)
    G1.add_edge('CPU_3', 'CPU_4', susp_min=0, susp_max=0)
    G1.add_edge('CPU_4', 'CPU_5', susp_min=0, susp_max=0)
    G1.add_edge('CPU_5', 'SM_2', susp_min=0, susp_max=0)
    G1.add_edge('CPU_5', 'CE_2', susp_min=0, susp_max=0)
    G1.add_edge('CPU_5', 'CPU_6', susp_min=0, susp_max=0)
    G1.add_edge('SM_2', 'CPU_7', susp_min=0, susp_max=0)
    G1.add_edge('CE_2', 'CPU_7', susp_min=0, susp_max=0)
    G1.add_edge('CPU_6', 'CPU_7', susp_min=0, susp_max=0)
    G1.add_edge('CPU_7', 'CPU_8', susp_min=0, susp_max=0)


    ##Task 2##
    G2 = nx.DiGraph()
    G2.add_node('CPU_1', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=5, _d=120, _p=2, _q=1)
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
    G3.add_node('CPU_1', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=5, _d=60, _p=2, _q=1)
    G3.add_node('CPU_2', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=0, _d=60, _p=2, _q=1)
    G3.add_node('CPU_3', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=0, _d=60, _p=2, _q=1)

    G3.add_node('CE_1', _type=t["CE"], _cmin=5, _cmax=10, _amin=0, _amax=0, _d=60, _p=2, _q=1)
    G3.add_node('CE_2', _type=t["CE"], _cmin=5, _cmax=10, _amin=0, _amax=0, _d=60, _p=2, _q=1)

    G3.add_edge('CPU_1', 'CE_1', susp_min=0, susp_max=0)
    G3.add_edge('CE_1', 'CPU_2', susp_min=0, susp_max=0)
    G3.add_edge('CPU_2', 'CE_2', susp_min=0, susp_max=0)
    G3.add_edge('CE_2', 'CPU_3', susp_min=0, susp_max=0)
    

    ##Task4##
    G4 = nx.DiGraph()
    G4.add_node('CPU_1', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=5, _d=90, _p=2, _q=1)
    G4.add_node('CPU_2', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=0, _d=90, _p=2, _q=1)
    G4.add_node('CPU_3', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=0, _d=90, _p=2, _q=1)
    G4.add_node('CPU_4', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=0, _d=90, _p=2, _q=1)
    G4.add_node('CPU_5', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=0, _d=90, _p=2, _q=1)

    G4.add_node('CE_1', _type=t["CE"], _cmin=1, _cmax=3, _amin=0, _amax=0, _d=90, _p=2, _q=1)
    G4.add_node('CE_2', _type=t["CE"], _cmin=1, _cmax=3, _amin=0, _amax=0, _d=90, _p=2, _q=1)

    G4.add_node('SM_1', _type=t["SM"], _cmin=1, _cmax=5, _amin=0, _amax=0, _d=90, _p=2, _q=1)
    G4.add_node('SM_2', _type=t["SM"], _cmin=1, _cmax=5, _amin=0, _amax=0, _d=90, _p=2, _q=1)


    G4.add_edge('CPU_1', 'CE_1', susp_min=0, susp_max=0)
    G4.add_edge('CE_1', 'CPU_2', susp_min=0, susp_max=0)
    G4.add_edge('CPU_2', 'SM_1', susp_min=0, susp_max=0)
    G4.add_edge('SM_1', 'CPU_3', susp_min=0, susp_max=0)
    G4.add_edge('CPU_3', 'CE_2', susp_min=0, susp_max=0)
    G4.add_edge('CE_2', 'CPU_4', susp_min=0, susp_max=0)
    G4.add_edge('CPU_4', 'SM_2', susp_min=0, susp_max=0)
    G4.add_edge('SM_2', 'CPU_5', susp_min=0, susp_max=0)


    ##Task5##
    G5 = nx.DiGraph()
    G5.add_node('CPU_1', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=5, _d=160, _p=2, _q=1)
    G5.add_node('CPU_2', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=0, _d=160, _p=2, _q=1)
    G5.add_node('CPU_3', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=0, _d=160, _p=2, _q=1)
    G5.add_node('CPU_4', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=0, _d=160, _p=2, _q=1)
    G5.add_node('CPU_5', _type=t["CPU"], _cmin=1, _cmax=1, _amin=0, _amax=0, _d=160, _p=2, _q=1)

    G5.add_node('CE_1', _type=t["CE"], _cmin=1, _cmax=3, _amin=0, _amax=0, _d=160, _p=2, _q=1)
    G5.add_node('CE_2', _type=t["CE"], _cmin=1, _cmax=3, _amin=0, _amax=0, _d=160, _p=2, _q=1)

    G5.add_node('SM_1', _type=t["SM"], _cmin=1, _cmax=5, _amin=0, _amax=0, _d=160, _p=2, _q=1)
    G5.add_node('SM_2', _type=t["SM"], _cmin=1, _cmax=5, _amin=0, _amax=0, _d=160, _p=2, _q=1)


    G5.add_edge('CPU_1', 'CE_1', susp_min=0, susp_max=0)
    G5.add_edge('CE_1', 'CPU_2', susp_min=0, susp_max=0)
    G5.add_edge('CPU_2', 'SM_1', susp_min=0, susp_max=0)
    G5.add_edge('SM_1', 'CPU_3', susp_min=0, susp_max=0)
    G5.add_edge('CPU_3', 'CE_2', susp_min=0, susp_max=0)
    G5.add_edge('CE_2', 'CPU_4', susp_min=0, susp_max=0)
    G5.add_edge('CPU_4', 'SM_2', susp_min=0, susp_max=0)
    G5.add_edge('SM_2', 'CPU_5', susp_min=0, susp_max=0)
    
    return G1, G2, G3, G4, G5
