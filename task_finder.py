import csv
import networkx as nx
from networkx.drawing.nx_pydot import write_dot

api_index = {}
api_index_counter = 0
gpu_index = {}
gpu_index_counter = 0


def api_start_loc(_dict_api, start):

    for loc, key in enumerate(api_index):
        if(api_index[key] == start):
            return loc

    return -1


def csv_to_lists(csv_file):
    # Initialize an empty list to store dictionaries
    data_list = []

    # Open the CSV file and read its contents
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Each row is already a dictionary with column headers as keys
            data_list.append(dict(row))

            # Print the resulting list of dictionaries
    return data_list


def print_dict_head(_dict):

    i = 0
    for key in _dict:
        if(i < 20):
            print(key, _dict[key])
            i = i + 1
        
def list_to_dict_api(lists, _type):

    global api_index
    global api_index_counter
    global gpu_index
    global gpu_index_counter
    
    _dict = {}
    for item in lists:
        corr_id = item["CorrID"]
        corr_id_int = int(corr_id)
        _dict[corr_id_int] = {}
        if(_type == "API"):
            api_index[api_index_counter] = corr_id_int
            api_index_counter = api_index_counter + 1
        if(_type == "GPU"):
            gpu_index[gpu_index_counter] = corr_id_int
            gpu_index_counter = gpu_index_counter + 1
        for key in item:
            if(key != "CorrID"):
                if(item[key].isdigit()):
                    _dict[corr_id_int][key] = int(item[key])
                else:
                    _dict[corr_id_int][key] = item[key]
            else:
                _dict[corr_id_int]["CorrID"] = int(item[key]) ##Fixing profiler's different naming here
                    
    return _dict


def list_to_dict_gpu(lists, _type):

    global api_index
    global api_index_counter
    global gpu_index
    global gpu_index_counter
    
    _dict = {}
    for item in lists:
        corr_id = item["CorrId"]
        corr_id_int = int(corr_id)
        _dict[corr_id_int] = {}
        if(_type == "API"):
            api_index[api_index_counter] = corr_id_int
            api_index_counter = api_index_counter + 1
        if(_type == "GPU"):
            gpu_index[gpu_index_counter] = corr_id_int
            gpu_index_counter = gpu_index_counter + 1
        for key in item:
            if(key != "CorrId"):
                if(item[key].isdigit()):
                    _dict[corr_id_int][key] = int(item[key])
                else:
                    _dict[corr_id_int][key] = item[key]
            else:
                _dict[corr_id_int]["CorrID"] = int(item[key]) ##Fixing profiler's different naming here
                    
                    
    return _dict

def find_period_starts(_dict_api, _dict_gpu, first_line):

    for key in first_line:
        if(first_line[key].isdigit()):
            first_line[key] = int(first_line[key])

    #print("first_line:", first_line)
    
    api_start = first_line['API Start (ns)']
    gpu_start = first_line['Kernel Start (ns)']

    api_first_match = -1
    gpu_first_match = -1
    
    for key in _dict_api:
        if(_dict_api[key]['Start (ns)'] == api_start):
            print("First kernel launch corrID:", key)
            api_first_match = key
            break

    for key in _dict_gpu:
        if(_dict_gpu[key]['Start (ns)'] == gpu_start):
            print("First gpu exec corrID:", key)
            break



    return api_first_match


def find_period(_dict_api, first_match, _dict_gpu):


    global api_index

    first_sync = -1
    first_sync_loc = -1
    second_sync = -1
    second_sync_loc = -1
    
    start_loc = api_start_loc(_dict_api, first_match)
    #print("i:", start_loc)
    #print("i:", len(api_index))
    for i in range(len(api_index)):
        if(i > start_loc and _dict_api[api_index[i]]["Name"] == "cudaStreamSynchronize" and first_sync == -1):
            first_sync = api_index[i]
            first_sync_loc = i
            continue
        if(i > start_loc and _dict_api[api_index[i]]["Name"] == "cudaStreamSynchronize" and second_sync == -1):
            second_sync = api_index[i]
            second_sync_loc = i
        if(first_sync != -1 and second_sync != -1):
            break
    
        #print(_dict_api[api_index[i]])


    print("First_sync_loc:", first_sync_loc, "First_sync:", first_sync)
    print("Second_sync_loc:", second_sync_loc, "Second_sync:", second_sync)

    '''
    for i in range(first_sync_loc + 1, second_sync_loc):
        print("##API: ", _dict_api[api_index[i]])
        try:
            print("##GPU:", _dict_gpu[api_index[i]])
        except:
            print("API?")
    '''
            
    return first_sync, first_sync_loc, second_sync, second_sync_loc


def ret_name(_type, counter):

    name = ""

    name = name + _type
    name = name + "_"
    name = name + str(counter)

    
    return name


def generate_dag_new(_dict_api, _dict_gpu, first_sync, first_sync_loc, second_sync, second_sync_loc):

    ##Also need to go from, last synchronize to next copy, this is, other cpu work
    
    DAG = nx.DiGraph()

    _cpu_counter = 1
    _cpu_counter_prev = -1
    _gpu_node_prev = -1
    _gpu_compute_counter = 1
    _gpu_compute_counter_prev = -1
    _gpu_ce_counter = 1
    _gpu_ce_counter_prev = -1
    _gpu_name_prev = -1 ##This is a string, with contrast to others
    _corr_id_to_name = {} ##This maps a cpu node with corr_id
    DAG.add_node("CPU_0", _type="CPU", _cmin=-1, _cmax=-1, amin=-1, amax=-1, _d=-1, p=-1, _q=-1, e_name="Source") ##Adding CPU
    for i in range(first_sync_loc + 1, second_sync_loc+1): ##When like that, - +1 to +1 - it's first mem copy to last sync_loc
        _api_loc = api_index[i]
        _cpu_node =  _dict_api[_api_loc]
        _cpu_node_type = -1 ## 1 normal, 2 synchronize
        _corr_id = _cpu_node["CorrID"]
        _gpu_node = -1

        if(_cpu_node["Name"] == "cudaStreamSynchronize"):
            _cpu_node_type = 2
        else:
            _cpu_node_type = 1

        if(_corr_id in _dict_gpu):
            _gpu_node = _dict_gpu[_corr_id]
            if(_gpu_node["GrdX"] != ''):
                _gpu_node_type = 1
            else:
                _gpu_node_type = 2
        else:
            _gpu_node = -1

            
        ##Scenario 1 is always true, add CPU node and edge from previous CPU if not first node
        CPU_name = ret_name("CPU", _cpu_counter)
        DAG.add_node(CPU_name, _type="CPU", e_name=_cpu_node["Name"].replace(":", "+++")) ##Adding CPU
        print("1 Adding CPU named: ", CPU_name)
        if(_cpu_counter_prev != -1):
            cpu_name_prev = ret_name("CPU", _cpu_counter_prev)
            DAG.add_edge(cpu_name_prev, CPU_name)
        _corr_id_to_name[_corr_id] = CPU_name
        ##Scenario 3, add edge from latest gpu node
        if(_cpu_node_type == 2):
            DAG.add_edge(_gpu_name_prev, CPU_name)
        _cpu_counter_prev = _cpu_counter
        _cpu_counter = _cpu_counter + 1

        if(_gpu_node != -1):
            if(_gpu_node["GrdX"] != ''): ##GPU node is compute(SM) type
                _gpu_node_type = 1
                GPU_name = ret_name("SM", _gpu_compute_counter)
                DAG.add_node(GPU_name, _type="SM", e_name=_gpu_node["Name"].replace(":", "+++")) ##Adding CPU
                if(_gpu_compute_counter_prev != -1 or _gpu_ce_counter_prev != -1):
                    DAG.add_edge(_gpu_name_prev, GPU_name)
                _gpu_compute_counter_prev = _gpu_compute_counter
                _gpu_compute_counter = _gpu_compute_counter + 1
                related_cpu_node = _corr_id_to_name[_corr_id]
                DAG.add_edge(related_cpu_node, GPU_name) ##Every GPU type node is dispatched by CPU
                _gpu_name_prev = GPU_name
            else: ##GPU node is memory(CE) type
                _gpu_node_type = 2
                CE_name= ret_name("CE", _gpu_ce_counter)
                DAG.add_node(CE_name, _type="CE", e_name=_gpu_node["Name"].replace(":", "+++")) ##Adding CPU
                if(_gpu_compute_counter_prev != -1 or _gpu_ce_counter_prev != -1):
                    DAG.add_edge(_gpu_name_prev, CE_name)
                _gpu_ce_counter_prev = _gpu_ce_counter
                _gpu_ce_counter = _gpu_ce_counter + 1
                related_cpu_node = _corr_id_to_name[_corr_id]
                DAG.add_edge(related_cpu_node, CE_name) ##Every GPU type node is dispatched by CPU
                _gpu_name_prev = CE_name
                 
    sink_name = ret_name("CPU", _cpu_counter)           
    DAG.add_node(sink_name, _type="CPU", _cmin=-1, _cmax=-1, amin=-1, amax=-1, _d=-1, p=-1, _q=-1, e_name="Sink") ##Adding CPU
    print("2 Adding CPU named: ", sink_name)
    DAG.add_edge("CPU_0", "CPU_1") ##Sink to first actual node
    DAG.add_edge(ret_name("CPU", _cpu_counter - 1), sink_name) ##last node to sink
    return DAG
        

    
if __name__ == "__main__":


    file1 = "api_40k.csv"
    lists1 = csv_to_lists(file1)
    file2 = "gpu_trace_40k.csv"
    lists2 = csv_to_lists(file2)
    #print(lists2[:10])
    file3 = "gpu_kern_exec_trace_40k.csv"
    lists3 = csv_to_lists(file3)
    first_line = lists3[0]
    _dict_api = list_to_dict_api(lists1, "API")
    #print_dict_head(_dict_api)
    _dict_gpu = list_to_dict_gpu(lists2, "GPU")
    #print_dict_head(_dict_gpu)
    first_match = find_period_starts(_dict_api, _dict_gpu, first_line)
    first_sync, first_sync_loc, second_sync, second_sync_loc = find_period(_dict_api, first_match, _dict_gpu)
    #print(api_index)
    DAG = generate_dag_new(_dict_api, _dict_gpu, first_sync, first_sync_loc, second_sync, second_sync_loc)
    nodes = DAG.nodes(data=True)
    edges = DAG.edges(data=True)
    #print("nodes:", nodes)
    #print("edges:", edges)
    for node in nodes:
        print(node)
    for edge in edges:
        print(edge)
    #write_dot(DAG, "DAG.dot")

    
    
    


    
