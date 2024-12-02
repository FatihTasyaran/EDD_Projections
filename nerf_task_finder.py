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
            print("corr_id_int:", corr_id_int, "api_index:", api_index_counter)
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


    
    
def write_manual_dot(DAG):

    writer = open("NERF_DAG.dot", "w+")
    writer.write("digraph G{" + "\n")
    nodes = dict(DAG.nodes())
    edges = dict(DAG.edges())
    for node in nodes:
        if(node.find("CPU") != -1):
            this_node = nodes[node]
            #my_xlabel = 'xlabel="'
            #my_xlabel = my_xlabel + this_node["e_name"] + ', '
            #my_xlabel = my_xlabel + str(this_node["_cmin"]) + ', '
            #my_xlabel = my_xlabel + str(this_node["_cmax"]) + '"'
            #my_xlabel = "" ##Takes too much space
            my_node = " [shape=ellipse,color=black];" + "\n" 
            writer.write(node + my_node)
        if(node.find("SM") != -1):
            this_node = nodes[node]
            #my_xlabel = 'xlabel="'
            #my_xlabel = my_xlabel + this_node["e_name"] + ', '
            #my_xlabel = my_xlabel + str(this_node["_cmin"]) + ', '
            #my_xlabel = my_xlabel + str(this_node["_cmax"]) + '"'
            #my_xlabel = "" ##Takes too much space
            my_node = " [shape=box,color=green];" + "\n"
            writer.write(node + my_node)
        if(node.find("CE") != -1):
            #my_xlabel = 'xlabel="'
            #my_xlabel = my_xlabel + this_node["e_name"] + ", "
            #my_xlabel = my_xlabel + str(this_node["_cmin"]) + ", "
            #my_xlabel = my_xlabel + str(this_node["_cmax"]) + '"'
            #my_xlabel = "" ##Takes too much space
            my_node = " [shape=diamond,color=red];" + "\n"
            writer.write(node + my_node)

    for edge in edges:
        writer.write(edge[0] + " -> " + edge[1] + "\n")
            
    writer.write("}" + "\n")



    writer.close()



def find_cpu_loc(api_list, corr_id):

    loc = -1
    for loc, item in enumerate(api_list):
        if(int(item["CorrID"]) == int(corr_id)):
            return loc

    return loc


def list_to_dict_period(gpu_list, api_list):

    period_max_nodes = -1
    period_max_start = -1
    period_max_end = -1
    period_max_corrid_start = -1
    period_max_corrid_end = -1
    period_max_idx_start = -1
    period_max_idx_end = -1
    counter = 0
    before = 0
    for idx, item in enumerate(gpu_list):
        if(item["Name"].find("ngp::generate_training_samples_nerf") != -1):
            difference = idx - before
            if(difference > period_max_nodes and counter > 2):
                period_max_start = before
                period_max_end = idx
                period_max_nodes = difference
                period_max_corrid_start = int(gpu_list[before]["CorrId"])
                period_max_corrid_end = int(item["CorrId"])
                period_max_idx_start = before
                period_max_idx_end = before
            if(difference > period_max_nodes and counter <= 2):
                counter = counter + 1
            before = idx


    ##Bound start
    not_found = True
    save_corr_id = -1
    while(not_found):
        period_max_start -= 1
        item = gpu_list[period_max_start]
        name = item["Name"]
        print("Looked at: ", item)
        print("Find: ", name.find("mem"))
        if(name.find("mem") == -1):
            not_found = False
        else:
            save_corr_id = item["CorrId"]

    period_max_corrid_start = int(save_corr_id)

    
    ##Bound end
    not_found = True
    save_corr_id = -1
    period_max_corrid_end_cpu = -1
    while(not_found):
        period_max_idx_end -= 1
        gpu_corr_id = int(gpu_list[period_max_end]["CorrId"])
        print("gpu_corr_id?:", gpu_corr_id)
        cpu_loc = find_cpu_loc(api_list, gpu_corr_id)
        print("cpu_loc:", cpu_loc, "gpu_corr_id:", gpu_corr_id, "cpu_name:", api_list[cpu_loc]["Name"])
        if(cpu_loc != -1):
            while(not_found):
                cpu_item = api_list[cpu_loc]
                cpu_name = cpu_item["Name"]
                print("cpu_name:", cpu_name, "corrID:", cpu_item["CorrID"])
                if(cpu_item["Name"].find("Synchronize") != -1):
                    period_max_corrid_end_cpu = cpu_item["CorrID"]
                    not_found = False
                else:
                    cpu_loc -= 1
    
    
    print("Longest period:", period_max_nodes)
    print("Longest period start:", period_max_start)
    print("Longest period end:", period_max_end)
    print("Longest period CorrId Start:", period_max_corrid_start)
    print("Longest period CorrId End:", period_max_corrid_end)
    print("Longest period CorrId End CPU:", period_max_corrid_end_cpu)

    period_start_gpu = int(period_max_corrid_start)
    period_start_cpu = int(period_max_corrid_start)
    period_end_cpu = int(period_max_corrid_end_cpu)
    period_end_gpu = -1
    for item in gpu_list:
        if(int(item["CorrId"]) < int(period_end_cpu)):
            period_end_gpu = int(item["CorrId"])
    print("period_start_gpu:", period_start_gpu)
    print("period_end_gpu:", period_end_gpu)

    print("period_start_cpu:", period_start_cpu)
    print("period_end_cpu:", period_end_cpu)


    return period_start_gpu, period_end_gpu, period_start_cpu, period_end_cpu

    


def reverse_dict(api_list, gpu_list):

    api_dict = {}
    gpu_dict = {}
    
    for item in api_list:
        int_corr_id = int(item["CorrID"])
        api_dict[int_corr_id] = item

    for item in gpu_list:
        int_corr_id = int(item["CorrId"])
        if(int_corr_id in gpu_dict):
            gpu_dict[int_corr_id].append(item)
        else:
            gpu_dict[int_corr_id] = [] ##There might be multiple entries with same corrid, which are graphkernel calls
            gpu_dict[int_corr_id].append(item)
            

    return api_dict, gpu_dict
    

##def aggregated_dag(DAG):

def get_name(counter, _type):

    return _type + "_" + str(counter)

def get_gpu_name_scenario(gpu_kernel_name):

    gpu_type = ""
    scenario = ""

    if(gpu_kernel_name.find("memcpy") != -1 and gpu_kernel_name.find("Async") == -1):
        gpu_type = "CE"
        scenario = "SyncCopy"
    elif(gpu_kernel_name.find("memcpy") != -1 and gpu_kernel_name.find("Async") != -1):
        gpu_type = "CE"
        scenario = "ASyncCopy"
    else:
        gpu_type = "SM"
        scenario = "kernel" ##or memset, which is executed by SM

    print("GPU Kernel Name:", gpu_kernel_name, "Returning Type: ", gpu_type, gpu_kernel_name.find("memcpy"), gpu_kernel_name.find("Async"))
    return gpu_type, scenario


##Async name is on the cpu side, and add sink node, then done
def dicts_to_dag(period_start_gpu, period_end_gpu, period_start_cpu, period_end_cpu, api_dict, gpu_dict):
    
    DAG = nx.DiGraph()

    
    cpu_type_name_counter = 1 ##Because we will have a source node which is CPU0
    gpu_sm_type_name_counter = 1
    gpu_ce_type_name_counter = 1
    cpu_type_prev_name = "CPU_0" ##Source node
    gpu_type_prev_name = ""
    is_waiting = False
    waiting_for = ""
    DAG.add_node("CPU_0", _type = "0", e_name = "Source")
    for idx in range(period_start_cpu, period_end_cpu + 1):
        if(idx in api_dict):
            cpu_node = api_dict[idx]
            cpu_name = get_name(cpu_type_name_counter, "CPU")
            cpu_type_name_counter += 1
            DAG.add_node(cpu_name, _type = "0", e_name = cpu_node["Name"])
            DAG.add_edge(cpu_type_prev_name, cpu_name) ##This is for sure
            if(is_waiting):
                DAG.add_edge(waiting_for, cpu_name) ##Waiting for Sync Copy to Finish
                is_waiting = False ##We waited and it's finished
                waiting_for = ""
            cpu_type_prev_name = cpu_name

        if(idx in gpu_dict):
            no_calls = len(gpu_dict[idx])
            gpu_node = gpu_dict[idx][0] ##First kernel of graph launch
            gpu_kernel_name = gpu_node["Name"]
            gpu_type, scenario = get_gpu_name_scenario(gpu_kernel_name)
            gpu_name = ""
            if(gpu_type == "CE"):
                gpu_name = get_name(gpu_ce_type_name_counter, "CE")
                DAG.add_node(cpu_name, _type = "2", e_name = gpu_node["Name"])
                if(gpu_type_prev_name != ""):
                    DAG.add_edge(gpu_type_prev_name, gpu_name)
                DAG.add_edge(cpu_name, gpu_name)
                gpu_ce_type_name_counter += 1
                gpu_type_prev_name = gpu_name
                if(scenario == "SyncCopy"):
                    is_waiting = True
                    waiting_for = gpu_name
            else:
                gpu_name = get_name(gpu_sm_type_name_counter, "SM")
                DAG.add_node(cpu_name, _type = "1", e_name = gpu_node["Name"])
                if(gpu_type_prev_name != ""):
                    DAG.add_edge(gpu_type_prev_name, gpu_name)
                DAG.add_edge(cpu_name, gpu_name)
                gpu_sm_type_name_counter += 1
                gpu_type_prev_name = gpu_name

        
            for i in range(1, len(gpu_dict[idx])): ##Cuda graph calls
                gpu_node = gpu_dict[idx][i] ##First kernel of graph launch, we added the first one already
                gpu_kernel_name = gpu_node["Name"]
                gpu_type, scenario = get_gpu_name_scenario(gpu_kernel_name)
                gpu_name = ""
                if(gpu_type == "CE"):
                    gpu_name = get_name(gpu_ce_type_name_counter, "CE")
                    DAG.add_node(cpu_name, _type = "2", e_name = gpu_node["Name"])
                    if(gpu_type_prev_name != ""):
                        DAG.add_edge(gpu_type_prev_name, gpu_name)
                    DAG.add_edge(cpu_name, gpu_name)
                    gpu_ce_type_name_counter += 1
                    gpu_type_prev_name = gpu_name
                    if(scenario == "SyncCopy"):
                        is_waiting = True
                        waiting_for = gpu_name
                else:
                    gpu_name = get_name(gpu_sm_type_name_counter, "SM")
                    DAG.add_node(cpu_name, _type = "1", e_name = gpu_node["Name"])
                    if(gpu_type_prev_name != ""):
                        DAG.add_edge(gpu_type_prev_name, gpu_name)
                    DAG.add_edge(cpu_name, gpu_name)
                    gpu_sm_type_name_counter += 1
                    gpu_type_prev_name = gpu_name


    return DAG
        
            
            
            
def main():

    global DAG
    
    file1 = "nerf3_cuda_api_trace.csv"
    lists1 = csv_to_lists(file1)
    file2 = "nerf3_cuda_gpu_trace.csv"
    lists2 = csv_to_lists(file2)
    file3 = "nerf3_cuda_kern_exec_trace.csv"
    lists3 = csv_to_lists(file3)
    first_line = lists3[0]

    api_list = lists1
    gpu_list = lists2
    
    period_start_gpu, period_end_gpu, period_start_cpu, period_end_cpu = list_to_dict_period(gpu_list, api_list)
    api_dict, gpu_dict = reverse_dict(api_list, gpu_list)
    #dict_api, dict_gpu, dict_calls = list_to_dicts_calls(period_start_gpu, period_end_gpu, period_start_cpu, period_end_cpu, api_list, gpu_list)
    DAG = dicts_to_dag(period_start_gpu, period_end_gpu, period_start_cpu, period_end_cpu, api_dict, gpu_dict)
    write_manual_dot(DAG)

    
def ret_dag_task():

    global DAG
    global times_cpu
    
    main()
    return DAG, times_cpu["Complete_Task_min"], times_cpu["Complete_Task_max"]
    
if __name__ == "__main__":

    main()
    
    
    
    


    
