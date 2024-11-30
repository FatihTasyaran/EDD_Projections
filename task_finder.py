import csv
import networkx as nx
from networkx.drawing.nx_pydot import write_dot

api_index = {}
api_index_counter = 0
gpu_index = {}
gpu_index_counter = 0
node_name_to_corr_id_cpu = {} ##This maps node ids to correlation_ids
node_name_to_corr_id_sm = {} ##This maps node ids to correlation_ids
node_name_to_corr_id_ce = {} ##This maps node ids to correlation_ids
first_sync_loc = -1
second_sync_loc = -1 
last_sync_loc = -1
adding_order = [[]]
times_cpu = {}
times_gpu = {}
DAG = -1

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
            #print("First kernel launch corrID:", key)
            api_first_match = key
            break

    for key in _dict_gpu:
        if(_dict_gpu[key]['Start (ns)'] == gpu_start):
            #print("First gpu exec corrID:", key)
            break



    return api_first_match


def find_period(_dict_api, first_match, _dict_gpu):


    global api_index
    
    global first_sync_loc
    global second_sync_loc
    global last_sync_loc

    first_sync = -1
    second_sync = -1
    
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
        if(i > start_loc and _dict_api[api_index[i]]["Name"] == "cudaStreamSynchronize" and first_sync != -1 and second_sync != -1):
            last_sync_loc = i
        

    #print("First_sync_loc:", first_sync_loc, "First_sync:", first_sync)
    #print("Second_sync_loc:", second_sync_loc, "Second_sync:", second_sync)
    #print("Last_sync_loc:", last_sync_loc)

    return first_sync, first_sync_loc, second_sync, second_sync_loc ##No need to return anymore but,..


def find_periods_and_aggregate_data(_dict_api, first_match, _dict_gpu):

    ##Don't forget to add: other cpu jobs
    
    global api_index
    global node_name_to_corr_id_cpu
    global node_name_to_corr_id_sm
    global node_name_to_corr_id_ce

    global first_sync_loc
    global second_sync_loc
    global last_sync_loc

    global adding_order

    global times_cpu
    global times_gpu

    times_cpu["CPU_0"] = [1] ##or 0 idk it's in ns so, pretty effectless
    
    #print("adding_order:", adding_order)

    no_nodes_in_period = (second_sync_loc) - (first_sync_loc)
    #print("no_nodes_in_period: ", no_nodes_in_period, "len_order", len(adding_order))
    
    start_loc = first_sync_loc + (no_nodes_in_period * 2 )  ##Starts from second_period
    ##Can give a table of min, max, in report
    pointer = 0
    for i in range(start_loc + 1, last_sync_loc + 1):
        added_nodes_loc = pointer % no_nodes_in_period
        _cpu_node = _dict_api[api_index[i]]
        _corr_id = _cpu_node["CorrID"]
        cpu_name = adding_order[added_nodes_loc][0] ##We have a CPU node anyway
        if(cpu_name in times_cpu):
            times_cpu[cpu_name].append(_cpu_node["Duration (ns)"])
        else:
            times_cpu[cpu_name] = []
            times_cpu[cpu_name].append(_cpu_node["Duration (ns)"])
        if(_corr_id in _dict_gpu):
            _gpu_node = _dict_gpu[_corr_id]
            gpu_type_name = adding_order[added_nodes_loc][1] ##We are adding maximum of 2 nodes at each iteration
            if(gpu_type_name in times_gpu):
                times_gpu[gpu_type_name].append(_gpu_node["Duration (ns)"])
            else:
                times_gpu[gpu_type_name] = []
                times_gpu[gpu_type_name].append(_gpu_node["Duration (ns)"])
        
        pointer = pointer + 1

    sink_name = "CPU_" + str(no_nodes_in_period + 1)
    times_cpu[sink_name] = []
    times_cpu["Complete_Task"] = []
    for i in range(start_loc + 1, last_sync_loc - 1, no_nodes_in_period):
        first_cpu_node_before = _dict_api[api_index[i - no_nodes_in_period]]
        first_cpu_node = _dict_api[api_index[i]]
        synch_before = _dict_api[api_index[i - 1]]
        #print("first_cpu_node:", first_cpu_node["Name"])
        #print("synch_before: ", synch_before["Name"])
        first_cpu_node_before_start = first_cpu_node_before["Start (ns)"]
        first_start = first_cpu_node["Start (ns)"]
        before_start = synch_before["Start (ns)"]
        before_duration = synch_before["Duration (ns)"]
        wait_time = first_start - (before_start + before_duration)
        task_time = first_start - first_cpu_node_before_start 
        times_cpu[sink_name].append(wait_time)
        times_cpu["Complete_Task"].append(task_time)
    times_cpu["Complete_Task_min"] = min(times_cpu["Complete_Task"])
    times_cpu["Complete_Task_max"] = max(times_cpu["Complete_Task"])
    #print("synch_before: ", synch_before)
    #print("Ratio:", task_time / wait_time)

    
def ret_name(_type, counter):

    name = ""

    name = name + _type
    name = name + "_"
    name = name + str(counter)

    
    return name


def generate_dag_new(_dict_api, _dict_gpu, first_sync, first_sync_loc, second_sync, second_sync_loc):


    global adding_order
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

    order_counter = 0
    DAG.add_node("CPU_0", _type="CPU", _cmin=-1, _cmax=-1, amin=-1, amax=-1, _d=-1, p=-1, _q=-1, e_name="Source") ##Adding CPU
    for i in range(first_sync_loc + 1, second_sync_loc + 1): ##When like that, - +1 to +1 - it's first mem copy to last sync_loc
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
        adding_order[order_counter].append(CPU_name)
        node_name_to_corr_id_cpu[CPU_name] = [_corr_id]
        if(_cpu_counter_prev != -1):
            cpu_name_prev = ret_name("CPU", _cpu_counter_prev)
            DAG.add_edge(cpu_name_prev, CPU_name, sus_min = 0, sus_max = 0)
        _corr_id_to_name[_corr_id] = CPU_name
        ##Scenario 3, add edge from latest gpu node
        if(_cpu_node_type == 2):
            DAG.add_edge(_gpu_name_prev, CPU_name, sus_min = 0, sus_max = 0)
        _cpu_counter_prev = _cpu_counter
        _cpu_counter = _cpu_counter + 1

        if(_gpu_node != -1):
            if(_gpu_node["GrdX"] != ''): ##GPU node is compute(SM) type
                _gpu_node_type = 1
                GPU_name = ret_name("SM", _gpu_compute_counter)
                DAG.add_node(GPU_name, _type="SM", e_name=_gpu_node["Name"].replace(":", "+++")) ##Adding CPU
                adding_order[order_counter].append(GPU_name)
                node_name_to_corr_id_sm[GPU_name] = [_corr_id]
                if(_gpu_compute_counter_prev != -1 or _gpu_ce_counter_prev != -1):
                    DAG.add_edge(_gpu_name_prev, GPU_name, sus_min = 0, sus_max = 0)
                _gpu_compute_counter_prev = _gpu_compute_counter
                _gpu_compute_counter = _gpu_compute_counter + 1
                related_cpu_node = _corr_id_to_name[_corr_id]
                DAG.add_edge(related_cpu_node, GPU_name, sus_min = 0, sus_max = 0) ##Every GPU type node is dispatched by CPU
                _gpu_name_prev = GPU_name
            else: ##GPU node is memory(CE) type
                _gpu_node_type = 2
                CE_name= ret_name("CE", _gpu_ce_counter)
                DAG.add_node(CE_name, _type="CE", e_name=_gpu_node["Name"].replace(":", "+++")) ##Adding CPU
                adding_order[order_counter].append(CE_name)
                node_name_to_corr_id_ce[CE_name] = [_corr_id]
                if(_gpu_compute_counter_prev != -1 or _gpu_ce_counter_prev != -1):
                    DAG.add_edge(_gpu_name_prev, CE_name, sus_min = 0, sus_max = 0)
                _gpu_ce_counter_prev = _gpu_ce_counter
                _gpu_ce_counter = _gpu_ce_counter + 1
                related_cpu_node = _corr_id_to_name[_corr_id]
                DAG.add_edge(related_cpu_node, CE_name, sus_min = 0, sus_max = 0) ##Every GPU type node is dispatched by CPU
                _gpu_name_prev = CE_name
        order_counter = order_counter + 1
        adding_order.append([])
    adding_order.pop()
    sink_name = ret_name("CPU", _cpu_counter)           
    DAG.add_node(sink_name, _type="CPU", _cmin=-1, _cmax=-1, amin=-1, amax=-1, _d=-1, p=-1, _q=-1, e_name="Sink") ##Adding CPU
    DAG.add_edge("CPU_0", "CPU_1", sus_min = 0, sus_max = 0) ##Source to first actual node
    DAG.add_edge(ret_name("CPU", _cpu_counter - 1), sink_name, sus_min = 0, sus_max = 0) ##last node to sink
    return DAG
        

def ret_aggregated_dag(DAG):
    
    new_DAG = nx.DiGraph()

    nodes = dict(DAG.nodes())
    edges = dict(DAG.edges())

    for node in nodes:
        this_node = nodes[node]
        if(node.find("CPU") != -1):
            c_min = min(times_cpu[node])
            c_max = max(times_cpu[node])
            new_DAG.add_node(node, _type = "0", _cmin = c_min, _cmax = c_max, _amin = -1, _amax = -1, _d = -1, _p = -1, _q = -1, e_name = this_node["e_name"])
        if(node.find("SM") != -1 or node.find("CE") != -1):
            c_min = min(times_gpu[node])
            c_max = max(times_gpu[node])
            if(node.find("SM") != -1):
                new_DAG.add_node(node, _type = "1", _cmin = c_min, _cmax = c_max, _amin = -1, _amax = -1, _d = -1, _p = -1, _q = -1, e_name = this_node["e_name"])
            if(node.find("CE") != -1):
                new_DAG.add_node(node, _type = "2", _cmin = c_min, _cmax = c_max, _amin = -1, _amax = -1, _d = -1, _p = -1, _q = -1, e_name = this_node["e_name"])

    for edge in edges:
        new_DAG.add_edge(edge[0], edge[1])

    return new_DAG

def write_manual_dot(DAG):

    writer = open("DAG.dot", "w+")
    writer.write("digraph G{" + "\n")
    nodes = dict(DAG.nodes())
    edges = dict(DAG.edges())
    for node in nodes:
        if(node.find("CPU") != -1):
            this_node = nodes[node]
            my_xlabel = 'xlabel="'
            my_xlabel = my_xlabel + this_node["e_name"] + ', '
            my_xlabel = my_xlabel + str(this_node["_cmin"]) + ', '
            my_xlabel = my_xlabel + str(this_node["_cmax"]) + '"'
            my_xlabel = "" ##Takes too much space
            my_node = " [shape=ellipse,color=black," + my_xlabel + "];\n"
            writer.write(node + my_node)
        if(node.find("SM") != -1):
            this_node = nodes[node]
            my_xlabel = 'xlabel="'
            my_xlabel = my_xlabel + this_node["e_name"] + ', '
            my_xlabel = my_xlabel + str(this_node["_cmin"]) + ', '
            my_xlabel = my_xlabel + str(this_node["_cmax"]) + '"'
            my_xlabel = "" ##Takes too much space
            my_node = " [shape=box,color=green," + my_xlabel + "];\n"
            writer.write(node + my_node)
        if(node.find("CE") != -1):
            my_xlabel = 'xlabel="'
            my_xlabel = my_xlabel + this_node["e_name"] + ", "
            my_xlabel = my_xlabel + str(this_node["_cmin"]) + ", "
            my_xlabel = my_xlabel + str(this_node["_cmax"]) + '"'
            my_xlabel = "" ##Takes too much space
            my_node = " [shape=diamond,color=red," + my_xlabel + "];\n"
            writer.write(node + my_node)

    for edge in edges:
        writer.write(edge[0] + " -> " + edge[1] + "\n")
            
    writer.write("}" + "\n")



    writer.close()


def main():

    global DAG
    
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
    find_periods_and_aggregate_data(_dict_api, first_match, _dict_gpu)
    '''
    nodes = DAG.nodes(data=True)    
    edges = DAG.edges(data=True)
    for node in nodes:
        print(node)
    for edge in edges:
        print(edge)
    '''
    DAG = ret_aggregated_dag(DAG)
    write_manual_dot(DAG)
    #print("API index:", api_index)
    
def ret_dag_task():

    global DAG
    global times_cpu
    
    main()
    return DAG, times_cpu["Complete_Task_min"], times_cpu["Complete_Task_max"]
    
if __name__ == "__main__":

    main()
    
    
    
    


    
