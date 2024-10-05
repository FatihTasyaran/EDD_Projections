import networkx as nx
import math
import get_four_basic_tasks
import utils


class TASK:

    def __init__(self, DAG, period, deadline):
        ##Task properties
        self.DAG = DAG
        self.period = period
        self.deadline = deadline
        ##Computed task features
        self.all_suspensions = self.recursive_paths(self.DAG)
        self.suspensions_dict = self.create_suspensions_dict(self.all_suspensions)
        self.cpu_projection = self.generate_cpu_projection(self.DAG, self.suspensions_dict) ##Make this called and computed here
        

    ##Start is the node where search is started, source and destination define an edge
    def recursive_search(self, G, node_start, node_source, node_destination, path, all_paths):
        path.append((node_source, node_destination))
        nodes = dict(G.nodes)
        ##All conditions satisfied, FOUND
        if(nodes[node_destination]["_type"] == nodes[node_start]["_type"] and utils.check_different(G, path)):
            all_paths.append(list(path))
            ##Start with consecutively same types, SKIP
        elif(not utils.check_different(G, path) and len(path) == 2):
            path.pop()
            return
        ##Same types exist but there are other, 
        elif(nodes[node_source]["_type"] == nodes[node_destination]["_type"] and not utils.check_different(G, path)):
            path.pop()
            return
        else:
            new_out_edges = G.out_edges(nbunch = node_destination)
            temp = node_source
            node_source = node_destination
            for edge in new_out_edges:
                node_destination = edge[1]
                self.recursive_search(G, node_start, node_source, node_destination, path, all_paths)

        path.pop()

    def recursive_paths(self, G):

        nodes = dict(G.nodes(data=True))
        all_suspensions = []
        for node in nodes:
            out_edges = G.out_edges(nbunch = node)
            for edge in out_edges:
                path = []
                all_paths = []
                self.recursive_search(G, node, node, edge[1], path, all_paths)
                all_suspensions.extend(all_paths)


        return all_suspensions

    
    def create_suspensions_dict(self, all_suspensions):

        suspensions_dict = {}
        enum = 1
        for suspension in all_suspensions: ##Enumerating manually here
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
                suspensions_dict[new_key]['type'] = utils.find_type(source_node)
                suspensions_dict[new_key]['paths'] = []
                suspensions_dict[new_key]['paths'].append(suspension)
                enum = enum + 1

        return suspensions_dict


    def generate_cpu_projection(self, G, suspensions_dict):

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
            source_type = utils.find_type(edge[0])
            target_type = utils.find_type(edge[1])
            if(source_type == "CPU" and target_type == "CPU"):
                cpu_projection.add_edge(edge[0], edge[1], susp_min = 0, susp_max = 0)


        ##Add suspension edges
        for key in suspensions_dict:

            suspension = suspensions_dict[key]
            if(suspension['type'] == "CPU"):
                min_susp, max_susp = utils.return_path_with_maximum_suspension_first_iter(G, suspension)
                cpu_projection.add_edge(suspension['source_node'], suspension['target_node'], susp_min = min_susp, susp_max = max_susp)
        ###############################################

        print("##############################")
        print("CPU Projection All Edges")
        edges = cpu_projection.edges(data=True)
        for edge in edges:
            print(edge)
        print("##############################")
        return cpu_projection



class TASKSET:

    ##dags is a list of DAG class instances
    def __init__(self, task_list):
        self.task_list = task_list
        
        self.cpu_jobs_input_path = "cpu_jobs.csv"
        self.cpu_prec_input_path = "cpu_prec.csv"
        
        self.ce_jobs_input_path = "ce_jobs.csv"
        self.ce_prec_input_path = "ce_prec.csv"

        self.sm_jobs_input_path = "sm_jobs.csv"
        self.sm_prec_input_path = "sm_prec.csv"

    def find_suspension_time_from_cpu_projection(self, task, source, target):

        #We assume there is maximum of one edge between two nodes 
        edges = task.cpu_projection.edges(data = True)
        susp_min = -1
        susp_max = -1
        for edge in edges:
            if(edge[0] == source and edge[1] == target):
                susp_min = edge[2]['susp_min']
                susp_max = edge[2]['susp_max']

        return susp_min, susp_max

    def generate_job_precs(self, nodes_to_job_ids):
        ##We use the same enumeration with generate_cpu_projection_input, so it generates
        ##same ids for tasks
        prec_lines = []
        
        for task_id, task in enumerate(self.task_list, start = 1):
            task_edges = task.cpu_projection.edges(data=True)
            task_precs = nodes_to_job_ids[task_id]
            

            for edge in task_edges:
                source = edge[0]
                target = edge[1]

                ##We assume that edge will exist in all instances with same order of the list
                if(len(nodes_to_job_ids[task_id][source]) != len(nodes_to_job_ids[task_id][source])):
                    print("Error Code 2: Number of job instances between two segments of a task is not equal, therefore I can't write precedence file, exiting..")
                    exit(1)
                for i in range(0, len(nodes_to_job_ids[task_id][source])):
                    susp_min, susp_max = self.find_suspension_time_from_cpu_projection(task, source, target)
                    prec_lines.append([task_id,
                                       nodes_to_job_ids[task_id][source][i],
                                       task_id,
                                       nodes_to_job_ids[task_id][target][i],
                                       susp_min,
                                       susp_max
                                       ])

        return prec_lines
        
    def generate_cpu_projection_input(self):

        ###############################################################################
        ##Jobs and Precedences Together##
        periods = []
        for task in self.task_list:
            periods.append(task.period)

        hyperperiod = utils.lcm_of_list(periods)
        all_lines = []
        prec_lines = []
        nodes_to_job_ids = {}
        for task_id, task in enumerate(self.task_list, start = 1):
            repeat = int(hyperperiod / task.period)
            if(task_id not in nodes_to_job_ids):
                nodes_to_job_ids[task_id] = {}
            for i in range(0, repeat):
                nodes = task.cpu_projection.nodes(data=True)
                edges = task.cpu_projection.edges(data=True)
                no_jobs = len(nodes)
                for job_id, node in enumerate(nodes, start = 1):
                    node_name = node[0]
                    node = node[1] ##Bypass key, get dictionary
                    if(node_name in nodes_to_job_ids[task_id]):
                        nodes_to_job_ids[task_id][node_name].append(i*no_jobs + job_id)
                    else:
                        nodes_to_job_ids[task_id][node_name] = []
                        nodes_to_job_ids[task_id][node_name].append(i*no_jobs + job_id)
                    '''
                    print("task_id:", task_id,
                          "job_id: ", (i * no_jobs) + job_id,
                          "arrival min: ", (i * task.period) + node['_amin'],
                          "arrival max: ", (i * task.period) + node['_amax'],
                          "cost min: ", node['_cmin'],
                          "cost max", node['_cmax'],
                          "deadline:", (i * task.period) + node['_d'],
                          "priority:", node['_p'])
                    '''
                    all_lines.append([task_id,
                                      (i * no_jobs) + job_id,
                                      (i * task.period) + node['_amin'],
                                      (i * task.period) + node['_amax'],
                                      node['_cmin'],
                                      node['_cmax'],
                                      (i * task.period) + node['_d'],
                                      node['_p']])

                    

        #print("nodes_to_job_ids:", nodes_to_job_ids)
        prec_lines = self.generate_job_precs(nodes_to_job_ids)
        writer_jobs = open(self.cpu_jobs_input_path, "w+")
        writer_prec = open(self.cpu_prec_input_path, "w+")
        writer_jobs.write("Task ID, Job ID, Arrival min, Arrival max, Cost min, Cost max, Deadline, Priority\n")
        writer_prec.write("Predecessor TID, Predecessor JID, Successor TID, Successor JID, Sus_Min, Sus_Max\n")
        for line in all_lines:
            to_write = ""
            for field in line:
                to_write = to_write + str(field) + ","
        
            to_write = to_write[:-1]
            to_write = to_write + "\n"
            writer_jobs.write(to_write)

        for line in prec_lines:
            to_write = ""
            for field in line:
                to_write = to_write + str(field) + ","
        
            to_write = to_write[:-1]
            to_write = to_write + "\n"
            writer_prec.write(to_write)
            

    def generate_ce_projection_input():
        x = 1
                                      
    def generate_sm_projection_input():
        x = 1

    def run_cpu_parse_and_update():
        x = 1

    def run_ce_parse_and_update():
        x = 1

    def run_sm_parse_and_update():
        x = 1
        







        
##Here we assume for now: sink and source are always CPU nodes. And after the first iteration first step, we are using response times.    
if __name__ == "__main__":

    
    DAG1, DAG2 = get_four_basic_tasks.return_tasks()
    TASK1 = TASK(DAG1, 100, 150)
    TASK2 = TASK(DAG1, 180, 200)
    
    
    TASKSET_ZERO = TASKSET([TASK1, TASK2])
    TASKSET_ZERO.generate_cpu_projection_input()
    
    '''
    DAG3 = create_digraph()
    all_suspensions_DAG3 = recursive_paths(DAG3)
    suspensions_dict_DAG3 = create_suspensions_dict(all_suspensions_DAG3)
    cpu_projection_DAG3 = generate_cpu_projection(DAG3, suspensions_dict_DAG3)

    TASK3 = TASK(DAG3, 100, 150, suspensions_dict_DAG3, cpu_projection_DAG3)
    '''
