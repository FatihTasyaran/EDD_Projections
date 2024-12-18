import networkx as nx
import math
import get_four_basic_tasks
import test_tasks_0
import utils
import subprocess


class TASK:

    def __init__(self, DAG, period, deadline):
        ##Task properties
        self.DAG = DAG
        self.period = period
        self.deadline = deadline
        ##Computed task features
        self.all_suspensions = self.recursive_paths()
        self.suspensions_dict = self.create_suspensions_dict()
        self.cpu_projection_first = self.generate_cpu_projection_first_iter()
        ##We generate all projections for first iterations because we update jitters 
        self.jitter_suspensions_dict = {} ##This is computed during sm and ce projections and updated
        self.sm_projection_first = self.generate_sm_projection_first_iter()
        self.ce_projection_first = self.generate_ce_projection_first_iter()
        #self.cpu_projection_ctd = self.generate_cpu_projection_ctd() 
        #self.sm_projection_ctd = self.generate_sm_projection_ctd()
        #self.ce_projection_ctd = self.generate_ce_projection_ctd() 
        

    ##This finds paths between any two nodes
    ##use this to update jitter on roots of sm and ce projection dags
    ##!!This function may not be very efficient
    def recursive_paths_between_two_nodes(self, start_node, end_node, path=[]):
        #print("type(path):", type(path), "path:", path, type([start_node]))
        path = path + [start_node]
        if start_node == end_node:
            return [path]
        if start_node not in self.DAG:
            return []
        paths = []
        for node in self.DAG.successors(start_node):
            if node not in path:
                new_paths = self.recursive_paths_between_two_nodes(node, end_node, path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths

    ##Start is the node where search is started, source and destination define an edge
    ##This finds paths between any two nodes of the same type with intermediate different typed nodes
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

    def recursive_paths(self):

        nodes = dict(self.DAG.nodes(data=True))
        all_suspensions = []
        for node in nodes:
            out_edges = self.DAG.out_edges(nbunch = node)
            for edge in out_edges:
                path = []
                all_paths = []
                self.recursive_search(self.DAG, node, node, edge[1], path, all_paths)
                all_suspensions.extend(all_paths)


        return all_suspensions

    
    def create_suspensions_dict(self):

        suspensions_dict = {}
        enum = 1
        for suspension in self.all_suspensions: ##Enumerating manually here
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


    def generate_cpu_projection_first_iter(self):

        cpu_projection = nx.DiGraph()
        all_nodes = dict(self.DAG.nodes(data=True))
        all_edges = self.DAG.edges(data=True)
        access_nodes = self.DAG.nodes(data=True)

        for node in all_nodes:
            if(access_nodes[node]["_type"] == "CPU"):
                node_data = self.DAG.nodes[node]
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
        for key in self.suspensions_dict:

            suspension = self.suspensions_dict[key]
            if(suspension['type'] == "CPU"):
                min_susp, max_susp = utils.return_path_with_maximum_suspension_first_iter(self.DAG, suspension)
                cpu_projection.add_edge(suspension['source_node'], suspension['target_node'], susp_min = min_susp, susp_max = max_susp)
        ###############################################

        print("##############################")
        print("CPU Projection All Edges")
        edges = cpu_projection.edges(data=True)
        for edge in edges:
            print(edge)
        print("##############################")
        
        return cpu_projection


    ##This function is actually very similiar to generate_cpu_projection() but there are small changes and there might be more later
    ##therefore, it is better to keep it as a separate function
    def generate_sm_projection_first_iter(self):

        sm_projection = nx.DiGraph()
        all_nodes = dict(self.DAG.nodes(data=True))
        all_edges = self.DAG.edges(data=True)
        access_nodes = self.DAG.nodes(data=True)

        ##This part is different than generate_cpu_projection(), suspension time from root node of DAG (which is a CPU node) to root node of this
        ##projection is added as jitter in release time
        for node in all_nodes:
            if(access_nodes[node]["_type"] == "SM"):
                node_data = self.DAG.nodes[node]
                sm_projection.add_node(node, **node_data)

        
        print("##############################")
        print("SM Projection All Nodes Before Update")
        nodes = sm_projection.nodes(data=True)
        for node in nodes:
            print(node)
        print("##############################")
        

        ###############################################
        ##Add related edges here

        ##Edges that remains the same, source and target same type
        for edge in all_edges:
            source_type = utils.find_type(edge[0])
            target_type = utils.find_type(edge[1])
            if(source_type == "SM" and target_type == "SM"):
                sm_projection.add_edge(edge[0], edge[1], susp_min = 0, susp_max = 0)


        ##Add suspension edges
        for key in self.suspensions_dict:

            suspension = self.suspensions_dict[key]
            if(suspension['type'] == "SM"):
                min_susp, max_susp = utils.return_path_with_maximum_suspension_first_iter(self.DAG, suspension)
                sm_projection.add_edge(suspension['source_node'], suspension['target_node'], susp_min = min_susp, susp_max = max_susp)
        ###############################################

        print("##############################")
        print("SM Projection All Edges")
        edges = sm_projection.edges(data=True)
        for edge in edges:
            print(edge)
        print("##############################")

        ##Add suspension of root from original DAG to root of this projection
        ##Add jitter for root nodes in projection DAG
        root_nodes = []
        for node in sm_projection:
            if(sm_projection.in_degree(node) == 0):
                root_nodes.append(node)

        task_root = utils.find_roots_in_DAG(self.DAG)
        task_root = task_root[0] ##Currently, only implements single root in task DAG

        
        for node in root_nodes:
            paths = dag_root_to_projection_root_paths = self.recursive_paths_between_two_nodes(task_root, node)

            for path in paths:
                path.pop() ##Remove the last node at the end of the path which is the root node itself
                
            self.jitter_suspensions_dict[node] = paths
            min_extra_jitter = utils.minimum_extra_jitter_from_paths(self.DAG, paths)
            max_extra_jitter = utils.maximum_extra_jitter_from_paths(self.DAG, paths)

                        
            sm_projection.nodes(data=True)[node]['_amin'] = sm_projection.nodes(data=True)[node]['_amin'] + min_extra_jitter
            sm_projection.nodes(data=True)[node]['_amax'] = sm_projection.nodes(data=True)[node]['_amax'] + max_extra_jitter
            
        print("##############################")
        print("SM Projection All Nodes After Update")
        nodes = sm_projection.nodes(data=True)
        for node in nodes:
            print(node)
        print("##############################")
        
        return sm_projection


    ##This function is actually very similiar to generate_sm_projection() but there are small changes and there might be more later
    ##therefore, it is better to keep it as a separate function
    def generate_ce_projection_first_iter(self):

        ce_projection = nx.DiGraph()
        all_nodes = dict(self.DAG.nodes(data=True))
        all_edges = self.DAG.edges(data=True)
        access_nodes = self.DAG.nodes(data=True)

        ##This part is different than generate_cpu_projection(), suspension time from root node of DAG (which is a CPU node) to root node of this
        ##projection is added as jitter in release time
        for node in all_nodes:
            if(access_nodes[node]["_type"] == "CE"):
                node_data = self.DAG.nodes[node]
                ce_projection.add_node(node, **node_data)
                
        print("##############################")
        print("CE Projection All Nodes Before Update")
        nodes = ce_projection.nodes(data=True)
        for node in nodes:
            print(node)
        print("##############################")
        

        ###############################################
        ##Add related edges here

        ##Edges that remains the same, source and target same type
        for edge in all_edges:
            source_type = utils.find_type(edge[0])
            target_type = utils.find_type(edge[1])
            if(source_type == "CE" and target_type == "CE"):
                ce_projection.add_edge(edge[0], edge[1], susp_min = 0, susp_max = 0)


        ##Add suspension edges
        for key in self.suspensions_dict:

            suspension = self.suspensions_dict[key]
            if(suspension['type'] == "CE"):
                min_susp, max_susp = utils.return_path_with_maximum_suspension_first_iter(self.DAG, suspension)
                ce_projection.add_edge(suspension['source_node'], suspension['target_node'], susp_min = min_susp, susp_max = max_susp)
        ###############################################

        print("##############################")
        print("CE Projection All Edges")
        edges = ce_projection.edges(data=True)
        for edge in edges:
            print(edge)
        print("##############################")

        ##Add suspension of root from original DAG to root of this projection
        ##Add jitter for root nodes in projection DAG
        root_nodes = []
        for node in ce_projection:
            if(ce_projection.in_degree(node) == 0):
                root_nodes.append(node)

        task_root = utils.find_roots_in_DAG(self.DAG)
        task_root = task_root[0] ##Currently, only implements single root in task DAG

        
        for node in root_nodes:
            paths = dag_root_to_projection_root_paths = self.recursive_paths_between_two_nodes(task_root, node)

            for path in paths:
                path.pop() ##Remove the last node at the end of the path which is the root node itself
                
            self.jitter_suspensions_dict[node] = paths
            min_extra_jitter = utils.minimum_extra_jitter_from_paths(self.DAG, paths)
            max_extra_jitter = utils.maximum_extra_jitter_from_paths(self.DAG, paths)

                        
            ce_projection.nodes(data=True)[node]['_amin'] = ce_projection.nodes(data=True)[node]['_amin'] + min_extra_jitter
            ce_projection.nodes(data=True)[node]['_amax'] = ce_projection.nodes(data=True)[node]['_amax'] + max_extra_jitter
            

        print("##############################")
        print("CE Projection All Nodes After Update")
        nodes = ce_projection.nodes(data=True)
        for node in nodes:
            print(node)
        print("##############################")
        
        return ce_projection
    
                

class TASKSET:

    ##task_list is a list of TASK class instances
    def __init__(self, task_list):
        self.task_list = task_list
        
        self.cpu_jobs_input_path = "cpu_jobs.csv"
        self.cpu_prec_input_path = "cpu_prec.csv"
        self.cpu_rta_path = "cpu_jobs.rta.csv"
        
        self.ce_jobs_input_path = "ce_jobs.csv"
        self.ce_prec_input_path = "ce_prec.csv"
        self.ce_rta_path = "ce_jobs.rta.csv"

        self.sm_jobs_input_path = "sm_jobs.csv"
        self.sm_prec_input_path = "sm_prec.csv"
        self.sm_rta_path = "sm_jobs.rta.csv"

        self.last_cpu_rta = {}
        self.last_ce_rta = {}
        self.last_sm_rta = {}

        self.last_known_rta = {}
        self.last_known_rta['CPU'] = {}
        self.last_known_rta['CE'] = {}
        self.last_known_rta['SM'] = {}

        self.job_file_definitions = {}
        self.job_file_definitions['CPU'] = {}
        self.job_file_definitions['CE'] = {}
        self.job_file_definitions['SM'] = {}

        self.nodes_to_job_ids = {}
        ##An edge's refined suspension time is depend on the response time of immediate predecessor's
        ##previous response time
        ##This dictionary maps that connections to faciliate updating suspension times
        ##It is generated in self.run_analysis()
        self.job_level_suspensions = {}
        self.exit_not_satisfied = False
        

    def check_exit(self, old_interval, new_interval):

        if not(old_interval[0] <= new_interval[0] and old_interval[1] <= new_interval[1]):
            self.exit_not_satisfied = True

    def map_suspension_nodes_to_jobs(self):

        for task_num, task in enumerate(self.task_list, start=1):

            for key in task.suspensions_dict:
                task.suspensions_dict[key]['compute_mapping'] = {}
                task.suspensions_dict[key]['compute_mapping']['start_node'] = []
                suspension_time_start_node = task.suspensions_dict[key]['compute']['suspension_time_start_node']
                suspension_time_end_nodes = task.suspensions_dict[key]['compute']['suspension_time_end_nodes']
                suspension_time_start_jobs = []
                suspension_time_end_jobs = {}
                for job_id in self.nodes_to_job_ids[task_num][suspension_time_start_node]:
                    suspension_time_start_jobs.append(job_id)

                for suspension_time_end_node in suspension_time_end_nodes:
                    suspension_time_end_jobs[suspension_time_end_node] = []
                    for job_id in self.nodes_to_job_ids[task_num][suspension_time_end_node]:
                        suspension_time_end_jobs[suspension_time_end_node].append(job_id)

                task.suspensions_dict[key]['compute_mapping']['start_node'] = suspension_time_start_jobs
                task.suspensions_dict[key]['compute_mapping']['end_nodes'] = suspension_time_end_jobs

                
    #This modifies the suspensions in tasks, maybe move this function to TASK class?
    def generate_suspension_compute_sets(self):

        
        for task_num, task in enumerate(self.task_list, start=1):
                
            for key in task.suspensions_dict:

                suspension_edge_source_node = task.suspensions_dict[key]['source_node']
                suspension_edge_target_node = task.suspensions_dict[key]['target_node']
                suspension_time_start_node = suspension_edge_source_node
                suspension_time_end_nodes = []
                
                for path in task.suspensions_dict[key]['paths']:
                    suspension_time_end_node = path[len(path) - 1][0] ##Immediate predecessor of other type
                    suspension_time_end_nodes.append(suspension_time_end_node)


                ##Reduce list to unique elements if there are multiple paths starts and ends with the same node
                suspension_time_end_nodes = list(set(suspension_time_end_nodes))
                task.suspensions_dict[key]['compute'] = {}
                task.suspensions_dict[key]['compute']['suspension_time_start_node'] = suspension_time_start_node
                task.suspensions_dict[key]['compute']['suspension_time_end_nodes'] = suspension_time_end_nodes

                '''
                print("task:", task_num, "suspension:", task.suspensions_dict[key], "\n",
                      "suspension_edge_source_node:", suspension_edge_source_node, "\n",
                      "suspension_edge_target_node:", suspension_edge_target_node, "\n",
                      "suspension_time_start_node:", suspension_time_start_node, "\n",
                      "suspension_time_end_nodes:", suspension_time_end_nodes, "\n",
                      "suspension:", task.suspensions_dict[key])
                '''
                

                
        self.map_suspension_nodes_to_jobs()

    def update_job_file_definitions(self, all_lines, _type):
        #writer_jobs.write("Task ID, Job ID, Arrival min, Arrival max, Cost min, Cost max, Deadline, Priority\n")
        
        for line_num, line in enumerate(all_lines):
            self.job_file_definitions[_type][line_num] = {'tid': line[0],
                                                            'jid': line[1],
                                                            'amin': line[2],
                                                            'amax': line[3],
                                                            'cmin': line[4],
                                                            'cmax': line[5],
                                                            'deadline': line[6],
                                                            'priority': line[7]}
            
        
    def find_suspension_time_from_cpu_projection_first(self, task, source, target):

        #We assume there is maximum of one edge between two nodes 
        edges = task.cpu_projection_first.edges(data = True)
        susp_min = -1
        susp_max = -1
        for edge in edges:
            if(edge[0] == source and edge[1] == target):
                susp_min = edge[2]['susp_min']
                susp_max = edge[2]['susp_max']

        return susp_min, susp_max

    def generate_cpu_job_precs(self):
        ##We use the same enumeration with generate_cpu_projection_input, so it generates
        ##same ids for tasks
        prec_lines = []
        
        for task_id, task in enumerate(self.task_list, start = 1):
            
            task_edges = task.cpu_projection_first.edges(data=True)
            task_precs = self.nodes_to_job_ids[task_id]
            self.job_level_suspensions[task_id] = {}
            self.job_level_suspensions[task_id]['CPU'] = []
            

            for edge in task_edges:
                source = edge[0]
                target = edge[1]

                ##We assume that edge will exist in all instances with same order of the list
                if(len(self.nodes_to_job_ids[task_id][source]) != len(self.nodes_to_job_ids[task_id][source])):
                    print("Error Code 2: Number of job instances between two segments of a task is not equal, therefore I can't write precedence file, exiting..")
                    exit(1)
                for i in range(0, len(self.nodes_to_job_ids[task_id][source])):
                    susp_min, susp_max = self.find_suspension_time_from_cpu_projection_first(task, source, target)
                    prec_lines.append([task_id,
                                       self.nodes_to_job_ids[task_id][source][i],
                                       task_id,
                                       self.nodes_to_job_ids[task_id][target][i],
                                       susp_min,
                                       susp_max
                                       ])
                    self.job_level_suspensions[task_id]['CPU'].append({'pred_tid': task_id,
                                                                       'pred_jid': self.nodes_to_job_ids[task_id][source][i],
                                                                       'succ_tid': task_id,
                                                                       'succ_jid': self.nodes_to_job_ids[task_id][target][i],
                                                                       'susp_min': susp_min,
                                                                       'susp_max': susp_max})

        return prec_lines


    ##!!Make a mapping of which job is affected of which job's response time
    ##Make a mapping between periods-nodes-jobs, like immediate predecessors and paths (immediate predecessors actually become paths after 1st iteration)
    ##
    def generate_cpu_projection_first_input(self):

        ###############################################################################
        ##Jobs and Precedences Together##
        periods = []
        for task in self.task_list:
            periods.append(task.period)

        hyperperiod = utils.lcm_of_list(periods)
        all_lines = []
        prec_lines = []
        for task_id, task in enumerate(self.task_list, start = 1):
            
            repeat = int(hyperperiod / task.period)
            if(task_id not in self.nodes_to_job_ids):
                self.nodes_to_job_ids[task_id] = {}
            for i in range(0, repeat):
                nodes = task.cpu_projection_first.nodes(data=True)
                edges = task.cpu_projection_first.edges(data=True)
                no_jobs = len(nodes)
                for job_id, node in enumerate(nodes, start = 1):
                    node_name = node[0]
                    node = node[1] ##Bypass key, get dictionary
                    if(node_name in self.nodes_to_job_ids[task_id]):
                        self.nodes_to_job_ids[task_id][node_name].append(i*no_jobs + job_id)
                    else:
                        self.nodes_to_job_ids[task_id][node_name] = []
                        self.nodes_to_job_ids[task_id][node_name].append(i*no_jobs + job_id)
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

                    
        
        self.update_job_file_definitions(all_lines, "CPU")
        prec_lines = self.generate_cpu_job_precs()
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
            
        writer_jobs.close()
        writer_prec.close()



    def find_suspension_time_from_ce_projection_first(self, task, source, target):

        #We assume there is maximum of one edge between two nodes 
        edges = task.ce_projection_first.edges(data = True)
        susp_min = -1
        susp_max = -1
        for edge in edges:
            if(edge[0] == source and edge[1] == target):
                susp_min = edge[2]['susp_min']
                susp_max = edge[2]['susp_max']

        return susp_min, susp_max

    def generate_ce_job_precs(self):
        ##We use the same enumeration with generate_ce_projection_input, so it generates
        ##same ids for tasks
        prec_lines = []
        
        for task_id, task in enumerate(self.task_list, start = 1):
            task_edges = task.ce_projection_first.edges(data=True)
            task_precs = self.nodes_to_job_ids[task_id]
            self.job_level_suspensions[task_id]['CE'] = []
            
            for edge in task_edges:
                source = edge[0]
                target = edge[1]

                ##We assume that edge will exist in all instances with same order of the list
                if(len(self.nodes_to_job_ids[task_id][source]) != len(self.nodes_to_job_ids[task_id][source])):
                    print("Error Code 2: Number of job instances between two segments of a task is not equal, therefore I can't write precedence file, exiting..")
                    exit(1)
                for i in range(0, len(self.nodes_to_job_ids[task_id][source])):
                    susp_min, susp_max = self.find_suspension_time_from_ce_projection_first(task, source, target)
                    prec_lines.append([task_id,
                                       self.nodes_to_job_ids[task_id][source][i],
                                       task_id,
                                       self.nodes_to_job_ids[task_id][target][i],
                                       susp_min,
                                       susp_max
                                       ])
                    self.job_level_suspensions[task_id]['CE'].append({'pred_tid': task_id,
                                                                        'pred_jid': self.nodes_to_job_ids[task_id][source][i],
                                                                        'succ_tid': task_id,
                                                                        'succ_jid': self.nodes_to_job_ids[task_id][target][i],
                                                                        'susp_min': susp_min,
                                                                        'susp_max': susp_max})

        return prec_lines
            
    ##!!Make a mapping of which job is affected of which job's response time
    ##Make a mapping between periods-nodes-jobs, like immediate predecessors and paths (immediate predecessors actually become paths after 1st iteration)
    ##
    def generate_ce_projection_first_input(self):

        ###############################################################################
        ##Jobs and Precedences Together##
        periods = []
        for task in self.task_list:
            periods.append(task.period)

        hyperperiod = utils.lcm_of_list(periods)
        all_lines = []
        prec_lines = []
        for task_id, task in enumerate(self.task_list, start = 1):
            repeat = int(hyperperiod / task.period)
            if(task_id not in self.nodes_to_job_ids):
                self.nodes_to_job_ids[task_id] = {}
            for i in range(0, repeat):
                nodes = task.ce_projection_first.nodes(data=True)
                edges = task.ce_projection_first.edges(data=True)
                no_jobs = len(nodes)
                for job_id, node in enumerate(nodes, start = 1):
                    node_name = node[0]
                    node = node[1] ##Bypass key, get dictionary
                    if(node_name in self.nodes_to_job_ids[task_id]):
                        self.nodes_to_job_ids[task_id][node_name].append(i*no_jobs + job_id)
                    else:
                        self.nodes_to_job_ids[task_id][node_name] = []
                        self.nodes_to_job_ids[task_id][node_name].append(i*no_jobs + job_id)
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

                    
        
        self.update_job_file_definitions(all_lines, "CE")
        prec_lines = self.generate_ce_job_precs() ##Make this generate_ce_job_precs
        writer_jobs = open(self.ce_jobs_input_path, "w+")
        writer_prec = open(self.ce_prec_input_path, "w+")
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

        writer_jobs.close()
        writer_prec.close()



    def find_suspension_time_from_sm_projection_first(self, task, source, target):

        #We assume there is maximum of one edge between two nodes 
        edges = task.sm_projection_first.edges(data = True)
        susp_min = -1
        susp_max = -1
        for edge in edges:
            if(edge[0] == source and edge[1] == target):
                susp_min = edge[2]['susp_min']
                susp_max = edge[2]['susp_max']

        return susp_min, susp_max

    def generate_sm_job_precs(self):
        ##We use the same enumeration with generate_sm_projection_input, so it generates
        ##same ids for tasks
        prec_lines = []
        
        for task_id, task in enumerate(self.task_list, start = 1):
            task_edges = task.sm_projection_first.edges(data=True)
            task_precs = self.nodes_to_job_ids[task_id]
            self.job_level_suspensions[task_id]['SM'] = []

            for edge in task_edges:
                source = edge[0]
                target = edge[1]

                ##We assume that edge will exist in all instances with same order of the list
                if(len(self.nodes_to_job_ids[task_id][source]) != len(self.nodes_to_job_ids[task_id][source])):
                    print("Error Code 2: Number of job instances between two segments of a task is not equal, therefore I can't write precedence file, exiting..")
                    exit(1)
                for i in range(0, len(self.nodes_to_job_ids[task_id][source])):
                    susp_min, susp_max = self.find_suspension_time_from_sm_projection_first(task, source, target)
                    prec_lines.append([task_id,
                                       self.nodes_to_job_ids[task_id][source][i],
                                       task_id,
                                       self.nodes_to_job_ids[task_id][target][i],
                                       susp_min,
                                       susp_max
                                       ])
                    self.job_level_suspensions[task_id]['SM'].append({'pred_tid': task_id,
                                                                        'pred_jid': self.nodes_to_job_ids[task_id][source][i],
                                                                        'succ_tid': task_id,
                                                                        'succ_jid': self.nodes_to_job_ids[task_id][target][i],
                                                                        'susp_min': susp_min,
                                                                        'susp_max': susp_max})

        return prec_lines
            
    ##!!Make a mapping of which job is affected of which job's response time
    ##Make a mapping between periods-nodes-jobs, like immediate predecessors and paths (immediate predecessors actually become paths after 1st iteration)
    ##
    def generate_sm_projection_first_input(self):

        ###############################################################################
        ##Jobs and Precedences Together##
        periods = []
        for task in self.task_list:
            periods.append(task.period)

        hyperperiod = utils.lcm_of_list(periods)
        all_lines = []
        prec_lines = []
        for task_id, task in enumerate(self.task_list, start = 1):
            repeat = int(hyperperiod / task.period)
            if(task_id not in self.nodes_to_job_ids):
                self.nodes_to_job_ids[task_id] = {}
            for i in range(0, repeat):
                nodes = task.sm_projection_first.nodes(data=True)
                edges = task.sm_projection_first.edges(data=True)
                no_jobs = len(nodes)
                for job_id, node in enumerate(nodes, start = 1):
                    node_name = node[0]
                    node = node[1] ##Bypass key, get dictionary
                    if(node_name in self.nodes_to_job_ids[task_id]):
                        self.nodes_to_job_ids[task_id][node_name].append(i*no_jobs + job_id)
                    else:
                        self.nodes_to_job_ids[task_id][node_name] = []
                        self.nodes_to_job_ids[task_id][node_name].append(i*no_jobs + job_id)
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

                    
        
        self.update_job_file_definitions(all_lines, "SM")
        prec_lines = self.generate_sm_job_precs() ##Make this generate_ce_job_precs
        writer_jobs = open(self.sm_jobs_input_path, "w+")
        writer_prec = open(self.sm_prec_input_path, "w+")
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
            
        writer_jobs.close()
        writer_prec.close()


    def parse_output(self, out_file, _type):

        result = {}
        
        reader = open(out_file)
        lines = reader.readlines()
        lines = lines[1:] ##Skip the header
        for line in lines:
            fields = line.strip("\n").split(",")
            task_id = int(fields[0])
            job_id = int(fields[1])
            bcct = int(fields[2])
            wcct = int(fields[3])
            bcrt = int(fields[4])
            wcrt = int(fields[5])

            
            
            if task_id not in result:
                result[task_id] = {}

            if job_id not in result[task_id]:
                result[task_id][job_id] = {}

            result[task_id][job_id]['bcct'] = bcct
            result[task_id][job_id]['wcct'] = wcct
            result[task_id][job_id]['bcrt'] = bcrt
            result[task_id][job_id]['wcrt'] = wcrt

        if(_type == "CPU"):
            self.last_known_rta["CPU"] = result
        elif(_type == "CE"):
            self.last_known_rta["CE"] = result
        elif(_type == "SM"):
            self.last_known_rta["SM"] = result
        else:
            print("Error Code 4: Encountered weird analysis type in parse_output(), exiting..")
            exit(1)
        

    

    def update_exec_output_fields(self, exec_outputs, result):

        fields = result.split(",")

        exec_outputs['filename'].append(fields[0])
        exec_outputs['sched_result'].append(int(fields[1]))
        exec_outputs['no_jobs_in_set'].append(int(fields[2]))
        exec_outputs['no_nodes_created'].append(int(fields[3]))
        exec_outputs['no_stages_explored'].append(int(fields[4]))
        exec_outputs['no_edges_discovered'].append(int(fields[5]))
        exec_outputs['max_exp_front_width'].append(int(fields[6]))
        exec_outputs['cpu_time_in_sec'].append(float(fields[7]))
        exec_outputs['peak_mem_used'].append(float(fields[8]))
        exec_outputs['is_timeout'].append(float(fields[9]))
        exec_outputs['no_processors_assumed'].append(float(fields[10]))
        
        return exec_outputs



    def update_ce_by_cpu(self, result):

        
        for task_id, task in enumerate(self.task_list, start=1):
            #print("##################################")
            #print("!!Before, Task Number:", task_id, "Suspensions Dict:", task.suspensions_dict)
            #print("##################################")
            projection = task.ce_projection_first
            for edge in projection.edges(data=True):
                if(edge[2]['susp_min'] != 0 and edge[2]['susp_max'] != 0):
                    #print("edge:", edge, "this is a suspension edge")
                    for key in task.suspensions_dict:
                        if(task.suspensions_dict[key]['source_node'] == edge[0] and task.suspensions_dict[key]['target_node'] == edge[1]):
                            print("task.suspensions_dict:", task.suspensions_dict[key])
                            print("nodes_to_job_ids:", self.nodes_to_job_ids)
                            print("job_level_suspensions:", self.job_level_suspensions)
                        
                            
            #print("##################################")
            #print("!!After, Task Number:", task_id, "Suspensions Dict:", task.suspensions_dict)
            #print("##################################")
            #print("task_id:", task_id, "ce_projection edges:", task.ce_projection_first.edges(data=True))

    
    def update_cpu(self):

        for task_id, task in enumerate(self.task_list, start = 1):
            projection = task.cpu_projection_first
            for edge in projection.edges(data=True):
                if(edge[2]['susp_min'] != 0 and edge[2]['susp_max'] != 0): ##Find suspension edges
                                        
                    lower_bound = edge[2]['susp_min']
                    
                        
                    for key in task.suspensions_dict:
                        if(task.suspensions_dict[key]["source_node"] == edge[0] and task.suspensions_dict[key]["target_node"] == edge[1]):
                            
                            for i in range(len(task.suspensions_dict[key]['compute_mapping']['start_node'])): 
                                ##Min and max will change for end node, for now just do the one end node
                                compute_start_job = task.suspensions_dict[key]['compute_mapping']['start_node'][i]
                                new_susp_min = 2**20
                                new_susp_max = -2**20
                                for end_node in task.suspensions_dict[key]['compute_mapping']['end_nodes']:
                                    compute_end_job = task.suspensions_dict[key]['compute_mapping']['end_nodes'][end_node][i]
                                    compute_start_type = utils.find_type(task.suspensions_dict[key]['compute']['suspension_time_start_node'])
                                    compute_end_type = utils.find_type(end_node)
                                    compute_start_bcct = self.last_known_rta[compute_start_type][task_id][compute_start_job]['bcct']
                                    compute_start_wcct = self.last_known_rta[compute_start_type][task_id][compute_start_job]['wcct']
                                    compute_end_bcct = self.last_known_rta[compute_end_type][task_id][compute_end_job]['bcct']
                                    compute_end_wcct = self.last_known_rta[compute_end_type][task_id][compute_end_job]['wcct']
                                    new_susp_min_temp = compute_end_bcct - compute_start_wcct
                                    new_susp_max_temp = compute_end_wcct - compute_start_bcct
                                    if(new_susp_min_temp < new_susp_min):
                                        new_susp_min = new_susp_min_temp
                                    if(new_susp_max_temp > new_susp_max):
                                        new_susp_max = new_susp_max_temp

                                    
                                    #print("job_level_suspensions:", self.job_level_suspensions)
                                    suspension_edge_source_job_id = self.nodes_to_job_ids[task_id][edge[0]][i]
                                    suspension_edge_target_job_id = self.nodes_to_job_ids[task_id][edge[1]][i]
                                    
                                    #print("suspension_edge_source_job_id:", suspension_edge_source_job_id)
                                    #print("suspension_edge_target_job_id:", suspension_edge_target_job_id)
                                    
                                    for job_level_suspension in self.job_level_suspensions[task_id]['CPU']:
                                        if(job_level_suspension['pred_jid'] == suspension_edge_source_job_id and
                                           job_level_suspension['succ_jid'] == suspension_edge_target_job_id):
                                            #print("CPU edge[2]['susp_min']:", edge[2]['susp_min'], "new_susp_min:", new_susp_min)
                                            #print("CPU edge[2]['susp_max']:", edge[2]['susp_max'], "new_susp_max:", new_susp_max)
                                            update_min = max(new_susp_min, lower_bound)
                                            self.check_exit([job_level_suspension['susp_min'], job_level_suspension['susp_max']], [update_min, new_susp_max])
                                            job_level_suspension['susp_min'] = update_min
                                            job_level_suspension['susp_max'] = new_susp_max
                                            
                                            
                                            
    def bcct_wcct_by_job_id(self, task_id, job_id, node):

        jittering_type = utils.find_type(node)
        bcct = self.last_known_rta[jittering_type][task_id][job_id]['bcct']
        wcct = self.last_known_rta[jittering_type][task_id][job_id]['wcct']
        return bcct, wcct


    def update_jitter_on_root(self, task_id, jittered_job, bcct_of_all, wcct_of_all, _type):

        for key in self.job_file_definitions[_type]:
            if(self.job_file_definitions[_type][key]['tid'] == task_id and self.job_file_definitions[_type][key]['jid'] == jittered_job):
                self.job_file_definitions[_type][key]['amin'] = bcct_of_all
                self.job_file_definitions[_type][key]['amax'] = wcct_of_all

                                            
    def update_ce(self):

        ##Update jitter on root nodes
        for task_id, task in enumerate(self.task_list, start = 1):
            for jittered in task.jitter_suspensions_dict:
                if(utils.find_type(jittered) == "CE"): ##This is a root node in CE projection, therefore we will add the ct from immediate predecessor
                        for i in range(len(self.nodes_to_job_ids[task_id][jittered])):
                            jittered_job = self.nodes_to_job_ids[task_id][jittered][i]
                            paths = task.jitter_suspensions_dict[jittered]
                            bcct_of_all = 2**20
                            wcct_of_all = 0
                            for path in paths:
                                immediate_predecessor = path[-1]
                                jittering_job = self.nodes_to_job_ids[task_id][immediate_predecessor][i]
                                #print("jittered_job:", jittered_job, "jittering_job:", jittering_job)
                                bcct, wcct = self.bcct_wcct_by_job_id(task_id, jittering_job, immediate_predecessor)

                                if bcct < bcct_of_all:
                                    bcct_of_all = bcct
                                if wcct > wcct_of_all:
                                    wcct_of_all = wcct

                            self.update_jitter_on_root(task_id, jittered_job, bcct_of_all, wcct_of_all, "CE")
                                    

        ##Update suspension time suspension edges
        for task_id, task in enumerate(self.task_list, start = 1):
            projection = task.ce_projection_first
            for edge in projection.edges(data=True):
                if(edge[2]['susp_min'] != 0 and edge[2]['susp_max'] != 0): ##Find suspension edges

                    lower_bound = edge[2]['susp_min']
                        
                    for key in task.suspensions_dict:
                        if(task.suspensions_dict[key]["source_node"] == edge[0] and task.suspensions_dict[key]["target_node"] == edge[1]):
                            
                            for i in range(len(task.suspensions_dict[key]['compute_mapping']['start_node'])): 
                                ##Min and max will change for end node, for now just do the one end node
                                compute_start_job = task.suspensions_dict[key]['compute_mapping']['start_node'][i]
                                new_susp_min = 2**20
                                new_susp_max = -2**20
                                for end_node in task.suspensions_dict[key]['compute_mapping']['end_nodes']:
                                    compute_end_job = task.suspensions_dict[key]['compute_mapping']['end_nodes'][end_node][i]
                                    compute_start_type = utils.find_type(task.suspensions_dict[key]['compute']['suspension_time_start_node'])
                                    compute_end_type = utils.find_type(end_node)
                                    compute_start_bcct = self.last_known_rta[compute_start_type][task_id][compute_start_job]['bcct']
                                    compute_start_wcct = self.last_known_rta[compute_start_type][task_id][compute_start_job]['wcct']
                                    compute_end_bcct = self.last_known_rta[compute_end_type][task_id][compute_end_job]['bcct']
                                    compute_end_wcct = self.last_known_rta[compute_end_type][task_id][compute_end_job]['wcct']

                                    print("dict:", task.suspensions_dict[key],
                                          "sbcct:", compute_start_bcct,
                                          "swcct:", compute_start_wcct,
                                          "ebcct:", compute_end_bcct,
                                          "ewcct:", compute_end_wcct)

                                    #exit(1)
                                    
                                    new_susp_min_temp = compute_end_bcct - compute_start_wcct
                                    new_susp_max_temp = compute_end_wcct - compute_start_bcct
                                    if(new_susp_min_temp < new_susp_min):
                                        new_susp_min = new_susp_min_temp
                                    if(new_susp_max_temp > new_susp_max):
                                        new_susp_max = new_susp_max_temp

                                        
                                    #print("job_level_suspensions:", self.job_level_suspensions)
                                    suspension_edge_source_job_id = self.nodes_to_job_ids[task_id][edge[0]][i]
                                    suspension_edge_target_job_id = self.nodes_to_job_ids[task_id][edge[1]][i]
                                    
                                    #print("suspension_edge_source_job_id:", suspension_edge_source_job_id)
                                    #print("suspension_edge_target_job_id:", suspension_edge_target_job_id)
                                    
                                    for job_level_suspension in self.job_level_suspensions[task_id]['CE']:
                                        if(job_level_suspension['pred_jid'] == suspension_edge_source_job_id and
                                           job_level_suspension['succ_jid'] == suspension_edge_target_job_id):
                                            #print("CE edge[2]['susp_min']:", edge[2]['susp_min'], "new_susp_min:", new_susp_min)
                                            #print("CE edge[2]['susp_max']:", edge[2]['susp_max'], "new_susp_max:", new_susp_max)
                                            if(new_susp_min >= edge[2]['susp_min']):
                                                update_min = max(new_susp_min, lower_bound)
                                                self.check_exit([job_level_suspension['susp_min'], job_level_suspension['susp_max']], [update_min, new_susp_max])
                                                job_level_suspension['susp_min'] = update_min
                                                job_level_suspension['susp_max'] = new_susp_max



    def update_sm(self):

        ##Update jitter on root nodes
        for task_id, task in enumerate(self.task_list, start = 1):
            for jittered in task.jitter_suspensions_dict:
                if(utils.find_type(jittered) == "SM"): ##This is a root node in CE projection, therefore we will add the ct from immediate predecessor
                        for i in range(len(self.nodes_to_job_ids[task_id][jittered])):
                            jittered_job = self.nodes_to_job_ids[task_id][jittered][i]
                            paths = task.jitter_suspensions_dict[jittered]
                            bcct_of_all = 2**20
                            wcct_of_all = 0
                            for path in paths:
                                immediate_predecessor = path[-1]
                                jittering_job = self.nodes_to_job_ids[task_id][immediate_predecessor][i]
                                #print("jittered_job:", jittered_job, "jittering_job:", jittering_job)
                                bcct, wcct = self.bcct_wcct_by_job_id(task_id, jittering_job, immediate_predecessor)

                                if bcct < bcct_of_all:
                                    bcct_of_all = bcct
                                if wcct > wcct_of_all:
                                    wcct_of_all = wcct

                            self.update_jitter_on_root(task_id, jittered_job, bcct_of_all, wcct_of_all, "SM")
                                    

        ##Update suspension time suspension edges
        for task_id, task in enumerate(self.task_list, start = 1):
            projection = task.sm_projection_first
            for edge in projection.edges(data=True):
                if(edge[2]['susp_min'] != 0 and edge[2]['susp_max'] != 0): ##Find suspension edges

                    lower_bound = edge[2]['susp_min']
                        
                    for key in task.suspensions_dict:
                        if(task.suspensions_dict[key]["source_node"] == edge[0] and task.suspensions_dict[key]["target_node"] == edge[1]):
                            
                            for i in range(len(task.suspensions_dict[key]['compute_mapping']['start_node'])): 
                                ##Min and max will change for end node, for now just do the one end node
                                compute_start_job = task.suspensions_dict[key]['compute_mapping']['start_node'][i]
                                new_susp_min = 2**20
                                new_susp_max = -2**20
                                for end_node in task.suspensions_dict[key]['compute_mapping']['end_nodes']:
                                    compute_end_job = task.suspensions_dict[key]['compute_mapping']['end_nodes'][end_node][i]
                                    compute_start_type = utils.find_type(task.suspensions_dict[key]['compute']['suspension_time_start_node'])
                                    compute_end_type = utils.find_type(end_node)
                                    compute_start_bcct = self.last_known_rta[compute_start_type][task_id][compute_start_job]['bcct']
                                    compute_start_wcct = self.last_known_rta[compute_start_type][task_id][compute_start_job]['wcct']
                                    compute_end_bcct = self.last_known_rta[compute_end_type][task_id][compute_end_job]['bcct']
                                    compute_end_wcct = self.last_known_rta[compute_end_type][task_id][compute_end_job]['wcct']
                                    new_susp_min_temp = compute_end_bcct - compute_start_wcct
                                    new_susp_max_temp = compute_end_wcct - compute_start_bcct
                                    if(new_susp_min_temp < new_susp_min):
                                        new_susp_min = new_susp_min_temp
                                    if(new_susp_max_temp > new_susp_max):
                                        new_susp_max = new_susp_max_temp


                                    #print("job_level_suspensions:", self.job_level_suspensions)
                                    
                                    suspension_edge_source_job_id = self.nodes_to_job_ids[task_id][edge[0]][i]
                                    suspension_edge_target_job_id = self.nodes_to_job_ids[task_id][edge[1]][i]
                                    
                                    #print("suspension_edge_source_job_id:", suspension_edge_source_job_id)
                                    #print("suspension_edge_target_job_id:", suspension_edge_target_job_id)
                                    
                                    for job_level_suspension in self.job_level_suspensions[task_id]['SM']:
                                        if(job_level_suspension['pred_jid'] == suspension_edge_source_job_id and
                                           job_level_suspension['succ_jid'] == suspension_edge_target_job_id):
                                            update_min = max(new_susp_min, lower_bound)
                                            self.check_exit([job_level_suspension['susp_min'], job_level_suspension['susp_max']], [update_min, new_susp_max])
                                            job_level_suspension['susp_min'] = update_min
                                            job_level_suspension['susp_max'] = new_susp_max
                                            
                                        

                                    
    def write_new_inputs(self):

        #writer_jobs.write("Task ID, Job ID, Arrival min, Arrival max, Cost min, Cost max, Deadline, Priority\n")
        #writer_prec.write("Predecessor TID, Predecessor JID, Successor TID, Successor JID, Sus_Min, Sus_Max\n")
        
        #print(self.job_level_suspensions)
        #print(self.job_file_definitions)
        ##Write CPU
        ##Jobs ##Does it necessary?
        writer = open(self.cpu_jobs_input_path, "w+")
        writer.write("Task ID, Job ID, Arrival min, Arrival max, Cost min, Cost max, Deadline, Priority\n")
        for key in self.job_file_definitions["CPU"]:
            _dict = self.job_file_definitions["CPU"][key]
            writer.write(f"{_dict['tid']}, {_dict['jid']}, {_dict['amin']}, {_dict['amax']}, {_dict['cmin']}, {_dict['cmax']}, {_dict['deadline']}, {_dict['priority']}\n")
        writer.close()
        ##Suspensions and precedences
        writer = open(self.cpu_prec_input_path, "w+")
        writer.write("Predecessor TID, Predecessor JID, Successor TID, Successor JID, Sus_Min, Sus_Max\n")
        for task in self.job_level_suspensions:
            for item in self.job_level_suspensions[task]["CPU"]:
                writer.write(f"{item['pred_tid']}, {item['pred_jid']}, {item['succ_tid']}, {item['succ_jid']}, {item['susp_min']}, {item['susp_max']}\n")
        writer.close()


        ##Write CE
        writer = open(self.ce_jobs_input_path, "w+")
        writer.write("Task ID, Job ID, Arrival min, Arrival max, Cost min, Cost max, Deadline, Priority\n")
        for key in self.job_file_definitions["CE"]:
            _dict = self.job_file_definitions["CE"][key]
            writer.write(f"{_dict['tid']}, {_dict['jid']}, {_dict['amin']}, {_dict['amax']}, {_dict['cmin']}, {_dict['cmax']}, {_dict['deadline']}, {_dict['priority']}\n")
        writer.close()
        ##Suspensions and precedences
        writer = open(self.ce_prec_input_path, "w+")
        writer.write("Predecessor TID, Predecessor JID, Successor TID, Successor JID, Sus_Min, Sus_Max\n")
        for task in self.job_level_suspensions:
            for item in self.job_level_suspensions[task]["CE"]:
                writer.write(f"{item['pred_tid']}, {item['pred_jid']}, {item['succ_tid']}, {item['succ_jid']}, {item['susp_min']}, {item['susp_max']}\n")
        writer.close()


        ##Write SM
        writer = open(self.sm_jobs_input_path, "w+")
        writer.write("Task ID, Job ID, Arrival min, Arrival max, Cost min, Cost max, Deadline, Priority\n")
        for key in self.job_file_definitions["SM"]:
            _dict = self.job_file_definitions["SM"][key]
            writer.write(f"{_dict['tid']}, {_dict['jid']}, {_dict['amin']}, {_dict['amax']}, {_dict['cmin']}, {_dict['cmax']}, {_dict['deadline']}, {_dict['priority']}\n")
        writer.close()
        ##Suspensions and precedences
        writer = open(self.sm_prec_input_path, "w+")
        writer.write("Predecessor TID, Predecessor JID, Successor TID, Successor JID, Sus_Min, Sus_Max\n")
        for task in self.job_level_suspensions:
            for item in self.job_level_suspensions[task]["SM"]:
                writer.write(f"{item['pred_tid']}, {item['pred_jid']}, {item['succ_tid']}, {item['succ_jid']}, {item['susp_min']}, {item['susp_max']}\n")
        writer.close()
        
        

    def ctd_iterations(self, exec_outputs):

        ##CPU
        result = subprocess.run(['./nptest', 'cpu_jobs.csv', '-p', 'cpu_prec.csv', '-r'], capture_output=True, text=True)

        if result.returncode == 0:
            print("CPU Iteration successful")
        else:
            print("CPU iteration failed with error:", result.stderr)
            exit(1)

        exec_outputs = self.update_exec_output_fields(exec_outputs, result.stdout)
        result = self.parse_output(self.cpu_rta_path, "CPU")

        ##CE
        result = subprocess.run(['./nptest', 'ce_jobs.csv', '-p', 'ce_prec.csv', '-r'], capture_output=True, text=True)

        if result.returncode == 0:
            print("CE Iteration successful")
        else:
            print("CE Iteration failed with error:", result.stderr)
            exit(1)


        exec_outputs = self.update_exec_output_fields(exec_outputs, result.stdout)
        result = self.parse_output(self.ce_rta_path, "CE")


        ##SM
        result = subprocess.run(['./nptest', 'sm_jobs.csv', '-p', 'sm_prec.csv', '-r'], capture_output=True, text=True)

        if result.returncode == 0:
            print("SM Iteration successful")
        else:
            print("SM Iteration failed with error:", result.stderr)
            exit(1)


        exec_outputs = self.update_exec_output_fields(exec_outputs, result.stdout)
        result = self.parse_output(self.sm_rta_path, "SM")

        self.update_cpu()
        self.update_ce()
        self.update_sm()

        self.write_new_inputs()

        return exec_outputs

    def print_quickly(self):

        print("###############################################################")
        for task in self.job_level_suspensions:
            for key in self.job_level_suspensions[task]:
                for item in self.job_level_suspensions[task][key]:
                    print("task:", task, "key:", key, "min:", item['susp_min'], "max:", item['susp_max'])
        print("###############################################################")

    def exit_condition(self):

        for task in self.job_level_suspensions:
            for susp in self.job_level_suspensions[task]:
                for type in self.job_level_suspensions[task][susp]:
                    print(type)


        
    def run_analysis(self):
        self.generate_cpu_projection_first_input()
        self.generate_ce_projection_first_input()
        self.generate_sm_projection_first_input()

        self.generate_suspension_compute_sets()

        exec_outputs = {'filename': [], 'sched_result': [], 'no_jobs_in_set': [],
                        'no_nodes_created': [], 'no_stages_explored': [], 'no_edges_discovered': [],
                        'max_exp_front_width': [], 'cpu_time_in_sec': [], 'peak_mem_used': [],
                        'is_timeout': [], 'no_processors_assumed': []}


        ##Running first iteration for all because we need bcct and wcct of different types to be able to do the second iteration's operations
        ##Testing cpu projection file

        ###First iteration##
        ##CPU
        result = subprocess.run(['./nptest', 'cpu_jobs.csv', '-p', 'cpu_prec.csv', '-r'], capture_output=True, text=True)

        if result.returncode == 0:
            #print("First CPU Execution successful:", result.stdout)
            print("First CPU Execution successful")
        else:
            print("First CPU Execution failed with error:", result.stderr)
            exit(1)


        exec_outputs = self.update_exec_output_fields(exec_outputs, result.stdout)
        result = self.parse_output(self.cpu_rta_path, "CPU")

        ##CE
        result = subprocess.run(['./nptest', 'ce_jobs.csv', '-p', 'ce_prec.csv', '-r'], capture_output=True, text=True)

        if result.returncode == 0:
            #print("First CE Execution successful:", result.stdout)
            print("First CE Execution successful")
        else:
            print("First CE Execution failed with error:", result.stderr)
            exit(1)


        exec_outputs = self.update_exec_output_fields(exec_outputs, result.stdout)
        result = self.parse_output(self.ce_rta_path, "CE")


        ##SM
        result = subprocess.run(['./nptest', 'sm_jobs.csv', '-p', 'sm_prec.csv', '-r'], capture_output=True, text=True)

        if result.returncode == 0:
            #print("First SM Execution successful:", result.stdout)
            print("First SM Execution successful")
        else:
            print("First SM Execution failed with error:", result.stderr)
            exit(1)


        exec_outputs = self.update_exec_output_fields(exec_outputs, result.stdout)
        result = self.parse_output(self.sm_rta_path, "SM")
        
        ###First iteration##
        exit(1)
        self.update_cpu()
        self.update_ce()
        self.update_sm()
        
        self.write_new_inputs()
        
        ##!!Also update the arrival time smin smax!!!!!
        self.print_quickly()
        iteration = 1
        ##
        while(self.exit_not_satisfied or iteration == 1):
            self.exit_not_satisfied = False
            self.ctd_iterations(exec_outputs)
            iteration = iteration + 1
            print("Iteration: ", iteration)
            self.print_quickly()
            #print(exec_outputs)
            
        ##
        for key in exec_outputs:
            print(key, exec_outputs[key])
        
        
        






        
##Here we assume for now: sink and source are always CPU nodes. And after the first iteration first step, we are using response times.    
if __name__ == "__main__":

    #def __init__(self, DAG, period, deadline):
    DAG1, DAG2, DAG3 = test_tasks_0.return_tasks()
    TASK1 = TASK(DAG1, 350, 350)
    TASK2 = TASK(DAG2, 120, 120)
    TASK3 = TASK(DAG3, 60, 60)

    #utils.visualize_bfs_w_depth(DAG1)
    #utils.visualize_bfs_w_depth(DAG2)
    #utils.visualize_bfs_w_depth(DAG3)

    TASKSET_ZERO = TASKSET([TASK1, TASK2, TASK3])
    TASKSET_ZERO.run_analysis()
    

    ##Several baselines
    ##This is one; everything is at job level
    ##By min-maxing S_i^max and S_i^min for all j and (next step)
    
    ##use it i[On comparison as a baseline (task-level)
    #Daniel Casini -> another baseline
    #Nidhi knows which analysis
