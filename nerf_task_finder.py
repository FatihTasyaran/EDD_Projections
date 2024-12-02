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


def list_to_dict_api(a_list):

    api_dict = {} ##API entries are unique for sure
    
    for item in a_list:
        api_dict[int(a_list["CorrID"])] = item

    return api_dict

def list_to_dict_gpu(a_list):

    gpu_dict = {} ##GPU entries share corr id if they are part of a graph
    
    for item in a_list:
        corr_id_int = int(item["CorrId"])
        if(corr_id_int in ap):
            api_dict[int(a_list["CorrID"])] = item

    return gpu_dict

def list_to_dict_real(a_list, a_list_2):

    before = 0

    period_max_nodes = -1
    period_max_start = -1
    period_max_end = -1
    period_max_corrid_start = -1
    period_max_corrid_end = -1
    period_max_nodes_second = -1
    period_max_
    for idx, item in enumerate(a_list):
        #print("item:", item["Name"])
        if(item["Name"].find("ngp::generate_training_samples_nerf") != -1):
            difference = idx - before
            if(difference > period_max_nodes):
                period_max_start = before
                period_max_end = idx
                period_max_nodes = difference
                period_max_corrid_start = int(a_list[before]["CorrId"])
                period_max_corrid_end = int(item["CorrId"])
            before = idx


    for item in a_list:
        if(int(item["CorrId"]) >= period_max_corrid_start and int(item["CorrId"]) <= period_max_corrid_end):
            print("BBBitem:", item)
            
            
    for item in a_list_2:
        if(int(item["CorrID"]) >= period_max_corrid_start and int(item["CorrID"]) <= period_max_corrid_end):
            print("AAAitem:", item)


    print("Longest period:", period_max_nodes)
    print("Longest period start:", period_max_start)
    print("Longest period end:", period_max_end)
    print("Longest period CorrId Start:", period_max_corrid_start)
    print("Longest period CorrId End:", period_max_corrid_end)

    
    
def list_to_dict(a_list, TYPE):

    before = 0
    for idx, item in enumerate(a_list):
        #print("item:", item["Name"])
        if(item["Name"].find("ngp::generate_training_samples_nerf") != -1):
            print("difference: ", idx - before)
            print("#######")
            print("THIS:", item)
            print("BEFORE:", a_list[before])
            print("Time difference: ", int(item["Start (ns)"]) - int(a_list[before]["Start (ns)"]))
            print("FPS: " , 1 / ((int(item["Start (ns)"]) - int(a_list[before]["Start (ns)"])) / 1000000000))
            before = idx
            print("#######")
            
def main():

    global DAG
    
    file1 = "nerf3_cuda_api_trace.csv"
    lists1 = csv_to_lists(file1)
    file2 = "nerf3_cuda_gpu_trace.csv"
    lists2 = csv_to_lists(file2)
    file3 = "nerf3_cuda_kern_exec_trace.csv"
    lists3 = csv_to_lists(file3)
    first_line = lists3[0]
    #_dict_api = list_to_dict_api(lists1, "API")
    _dict_gpu = list_to_dict_real(lists2, lists1)
    exit(1)
    
    ###
    
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
    chibi_DAG = ret_chibi_task(DAG)
    #print("API index:", api_index)
    
def ret_dag_task():

    global DAG
    global times_cpu
    
    main()
    return DAG, times_cpu["Complete_Task_min"], times_cpu["Complete_Task_max"]
    
if __name__ == "__main__":

    main()
    
    
    
    


    
