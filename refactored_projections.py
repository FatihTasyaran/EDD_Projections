import networkx as nx
import math
import get_four_basic_tasks
import test_tasks_0
import test_tasks_limited
import utils_refactored as utils
import subprocess
import global_definitions_limited as global_definitions ##Change this line if need to go with more types
import copy
import sys
import task_finder

##Types
CPU = 0
SM = 1
CE = 2



class TASK:

    def __init__(self, DAG, period, deadline):
        ##Task properties
        self.DAG = DAG ##Task level 
        self.period = period
        self.deadline = deadline
        ##Computed task features
        self.task_level_all_suspensions = self.recursive_paths()
        self.task_level_suspensions_dict = self.create_suspensions_dict()
        

        self.task_level_projections = {} ##No predetermined class
        self.generate_projections() 
        ##
        self.job_level_projections = {} ##OK
        self.job_level_suspensions = {} ##OK
        self.job_level_suspension_paths = {} ##Need to complete this one as well
        self.job_level_jitter_roots = {} ##OK
        self.job_level_jitter_root_paths = {} ##This is used to compute response times along the path leading to jitter root in the new analysis
        ## ##OK
        self.nodes_to_job_ids = {} ##OK
        ##
        self.last_iteration_projections = {}
        self.last_iteration_suspensions = {}
        

        

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


    def find_type_of_node(self, node):
        
        return self.DAG.nodes(data=True)[node]["_type"]

    ##That is; if in a suspension path, let's say CE1-CPU2-SM1-|CE2|-CPU3-SM3-CE3 there is another node of the same type, in this case it is CE2, we should discard that path
    ##Because, we need to have two suspension edges in that case: 1->CE1-CPU2-SM1-CE2 2->CE2-CPU3-SM3-CE3
    def is_suspension_type_node_in_path(self, _type, a_path): 
        for node in a_path:
            if(self.find_type_of_node(node) == _type):
                return True

        return False
        
    def singular_paths_for_new_analysis(self, a_suspensions_dict):

        for _item in a_suspensions_dict:
            _source_node = a_suspensions_dict[_item]["source_node"]
            _target_node = a_suspensions_dict[_item]["target_node"]
            _suspension_type = a_suspensions_dict[_item]["type"]
            singular_paths_complete = self.recursive_paths_between_two_nodes(_source_node, _target_node)
            singular_paths_complete = [x for x in singular_paths_complete if not self.is_suspension_type_node_in_path(_suspension_type, x[1:-1])]
            a_suspensions_dict[_item]["singular_paths_complete"] = singular_paths_complete
            singular_paths_intermediate = copy.deepcopy(singular_paths_complete)
            for i, singular_path in enumerate(singular_paths_intermediate):
                singular_paths_intermediate[i] = singular_path[1:-1]
                
            a_suspensions_dict[_item]["singular_paths_intermediate"] = singular_paths_intermediate
        return a_suspensions_dict
        
    
    def create_suspensions_dict(self):

        t = global_definitions.TYPES_ALPHA
        nodes = self.DAG.nodes(data=True)
        suspensions_dict = {}
        enum = 1
        for suspension in self.task_level_all_suspensions: ##Enumerating manually here
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
                suspensions_dict[new_key]['type'] = nodes[source_node]["_type"] ##Can further augment this with t up there
                suspensions_dict[new_key]['paths'] = []
                suspensions_dict[new_key]['paths'].append(suspension)
                enum = enum + 1
                

        if(global_definitions.NEW_ANALYSIS):
            suspensions_dict = self.singular_paths_for_new_analysis(suspensions_dict)
        return suspensions_dict


    def generate_projections(self):

        types_list = global_definitions.TYPES
        type_names = global_definitions.TYPES_NUMERIC
        
        for _type in global_definitions.TYPES:
            to_generate = nx.DiGraph()
            all_nodes = dict(self.DAG.nodes(data=True))
            all_edges = self.DAG.edges(data=True)
            access_nodes = self.DAG.nodes(data=True)

            ##Add nodes
            for node in all_nodes:
                if(access_nodes[node]["_type"] == _type):
                    node_data = self.DAG.nodes[node]
                    to_generate.add_node(node, **node_data)
            ##Add projection edges
            ##Edges that remains the same, source and target same type
            for edge in all_edges:
                source_node = edge[0]
                target_node = edge[1]
                source_type = all_nodes[source_node]["_type"] 
                target_type = all_nodes[target_node]["_type"]
                if(source_type == _type and target_type == _type):
                    to_generate.add_edge(source_node, target_node, susp_min = 0, susp_max = 0)


            ##Add suspension edges
            for key in self.task_level_suspensions_dict:
                
                suspension = self.task_level_suspensions_dict[key]
                if(suspension['type'] == _type):
                    min_susp, max_susp = utils.return_path_with_maximum_suspension_first_iter(self.DAG, suspension)
                    to_generate.add_edge(suspension['source_node'], suspension['target_node'], susp_min = min_susp, susp_max = max_susp)


            if(_type != "0"): ##We are always assuming type 0 is CPU
                ##Therefore, here we add suspension time from CPU root to other projection roots as jitter
                root_nodes = []
                for node in to_generate:
                    if(to_generate.in_degree(node) == 0):
                        root_nodes.append(node)

                task_root = utils.find_roots_in_DAG(self.DAG)
                task_root = task_root[0] ##Currently, only implements single root in task DAG

                for node in root_nodes:
                    paths = self.recursive_paths_between_two_nodes(task_root, node)

                    for path in paths:
                        path.pop() ##Remove the last node at the end of the path which is the root node itself

                    min_extra_jitter = utils.minimum_extra_jitter_from_paths(self.DAG, paths)
                    max_extra_jitter = utils.maximum_extra_jitter_from_paths(self.DAG, paths)


                    to_generate.nodes(data=True)[node]['_amin'] = to_generate.nodes(data=True)[node]['_amin'] + min_extra_jitter
                    to_generate.nodes(data=True)[node]['_amax'] = to_generate.nodes(data=True)[node]['_amax'] + max_extra_jitter
                    
            self.task_level_projections[_type] = to_generate


def print_projection(_type, a_dag):
    print("#################################################")
    print("Printing projection, type: ", _type)
    print("Nodes:")
    for node in a_dag.nodes(data=True):
        print(node)
    print("Edges:")
    for edge in a_dag.edges(data=True):
        print(edge)
    print("#################################################")
            
                
class TASKSET:

    ##TASKS is a list of TASK objects
    def __init__(self, TASKS):
        
        self.tasks = TASKS
        self.populate_with_jobs()
        self.populate_with_precs()
        self.add_jitter_values_to_jitter_roots()
        if(global_definitions.NEW_ANALYSIS):
            self.add_job_level_suspension_paths()
            self.add_job_level_jitter_root_paths()
        self.write_projections_to_file(0)
        
        if(global_definitions.DEBUG):
            for task_id, task in enumerate(self.tasks):
                print("##THIS IS TASK ", task_id + 1)
                utils.print_a_task(task)

        self.run_analysis()

        
    ##This add jobs for a given set of tasks and periods
    def populate_with_jobs(self):

        periods = []
        for task in self.tasks:
            periods.append(task.period)
        hyperperiod = utils.lcm_of_list(periods)

        
        for task_id, task in enumerate(self.tasks, start=1):
            period = task.period
            repeat = int(hyperperiod / period)
            for projection in task.task_level_projections:
                projection_dag = task.task_level_projections[projection]
                projection_len = len(projection_dag.nodes)
                projection_roots = [-1]
                if(projection not in task.nodes_to_job_ids):
                    task.nodes_to_job_ids[projection] = {}
                
                for i in range(repeat):
                    for node_id, node in enumerate(projection_dag.nodes(data=True)):
                        job_id = i * projection_len + node_id + 1 ##Start counting from 1
                        node_name = node[0]
                        node_info = node[1]
                        if(node_name not in task.nodes_to_job_ids[projection]):
                            task.nodes_to_job_ids[projection][node_name] = []
                        task.nodes_to_job_ids[projection][node_name].append(job_id)
                        
                        if(projection not in task.job_level_projections):
                            task.job_level_projections[projection] = {}
                        _dict = {"Task_id": task_id,
                                 "Job_id": job_id,
                                 "a_min": node_info["_amin"] + (i * period),
                                 "a_max": node_info["_amax"] + (i * period),
                                 "c_min": node_info["_cmin"],
                                 "c_max": node_info["_cmax"],
                                 "deadline": node_info["_d"] * (i + 1),
                                 "priority": node_info["_p"],
                                 "bcct": -1,
                                 "wcct": -1,
                                 "bcrt": -1,
                                 "wcrt": -1,
                                 "n_bcrt": -1,
                                 "n_wcrt": -1}
                        task.job_level_projections[projection][job_id] = _dict


                ##Here, instead of incoming jobs, take the path from CPU root
                ##For non-CPU projections, add suspension as jitter
                if(projection != "0"):
                    if(projection not in task.job_level_jitter_roots):
                        task.job_level_jitter_roots[projection] = {}
                    projection_roots = utils.find_roots_in_DAG(projection_dag)
                    if(len(projection_roots) != 0):
                        for i in range(len(projection_roots)):
                            one_root = projection_roots[i]
                            print("This root:", one_root)
                            one_root_jobs = task.nodes_to_job_ids[projection][one_root]
                            edges = list(task.DAG.in_edges(one_root))
                            incoming_all = []
                            for edge in edges:
                                print("this_edge: ", edge)
                                incoming = edge[0]
                                try:
                                    incoming_jobs = task.nodes_to_job_ids["0"][incoming]
                                except:
                                    incoming_jobs = "CPU_0" ##This is a workaround fow now because naive method will not gonna work anyway
                                incoming_all.append(incoming_jobs)
                            if(len(one_root_jobs) != len(incoming_jobs)):
                                print("Error: Unequal number of jobs during jitter root mapping, exiting..")
                                exit(1)
                            
                            for i in range(len(one_root_jobs)):
                                task.job_level_jitter_roots[projection][one_root_jobs[i]] = []
                                for j in range(len(incoming_all)):
                                    task.job_level_jitter_roots[projection][one_root_jobs[i]].append(incoming_all[j][i])
                                    
                        

    def find_task_level_cpu_root(self, task_id):

        task = self.tasks[task_id - 1] ##Because we are starting from 1 while enumerating
        nodes = task.DAG.nodes(data=True)
        for node in nodes:
            if task.DAG.in_degree(node[0]) == 0:
                return node[0]##We assume there is one root at the moment
        

    def add_jitter_values_to_jitter_roots(self):

        for task_id, task in enumerate(self.tasks, start=1):
            #print("task_id:", task_id)
            #print("job_level_jitter_roots:", task.job_level_jitter_roots)
            cpu_root = self.find_task_level_cpu_root(task_id)
            cpu_root_node = task.DAG.nodes(data=True)[cpu_root]
            cpu_root_amin = cpu_root_node["_amin"]
            cpu_root_amax = cpu_root_node["_amax"]

            for projection in task.job_level_jitter_roots:
                #print("projection:", projection)
                for root_job in task.job_level_jitter_roots[projection]:
                    #print("root_job_entry:, BEFORE", task.job_level_projections[projection][root_job])
                    root_job_entry = task.job_level_projections[projection][root_job]
                    root_job_entry["a_min"] = root_job_entry["a_min"] + cpu_root_amin
                    root_job_entry["a_max"] = root_job_entry["a_max"] + cpu_root_amax
                    #print("root_job_entry:, AFTER", task.job_level_projections[projection][root_job])

    
                            
    def get_jobs_for_node(self, task, _type, node):

        #print("node:", node, "node jobs:", task.nodes_to_job_ids[_type][node])
        return task.nodes_to_job_ids[_type][node]

    def find_type_of_node(self, task, node):
        
        #print("node:", node, "type:", task.DAG.nodes(data=True)[node]["_type"])
        return task.DAG.nodes(data=True)[node]["_type"]
    
    def get_jobs_list_for_nodes_list(self, task, nodes):

        jobs = []
        types = []
        
        _type = self.find_type_of_node(task, nodes[0])
        _len = len(task.nodes_to_job_ids[_type][nodes[0]])

        for node in nodes:
            _type = self.find_type_of_node(task, node)
            types.append(_type)
            
        for i in range(_len):
            this_release_jobs = []
            for node in nodes:
                _type = self.find_type_of_node(task, node)
                this_release_jobs.append(task.nodes_to_job_ids[_type][node][i])
            jobs.append(this_release_jobs)
                
        return types, jobs

    def transform_to_individual(self, task_id, job_level_suspensions):
        ##At the moment, we assume there is no precedence between tasks

        new = {}
        
        for key in job_level_suspensions:
            new[key] = []
            for _dict in job_level_suspensions[key]:
                for i in range(len(_dict['start_job'])):
                    pred_jid = _dict["start_job"][i]
                    succ_jid = _dict["suspension_target_end_job"][i]
                    end_types = _dict["suspension_time_end_types"]
                    end_jobs = _dict["suspension_time_end_jobs"][i]
                    to_add = {"pred_tid": task_id, ##This is the same with start job while computing new bound
                              "pred_jid": pred_jid,
                              "succ_tid": task_id,
                              "succ_jid": succ_jid,
                              "sus_min": _dict["susp_min_first"],
                              "sus_max": _dict["susp_max_first"],
                              "sus_min_first": _dict["susp_min_first"],
                              "sus_max_first": _dict["susp_max_first"],
                              "end_types": end_types,
                              "end_jobs": end_jobs,
                              "edge_type": "suspension"}
                    new[key].append(to_add)

        return new

    def add_non_suspension_edges(self, task_id, task, job_level_suspensions, MODE): ##MODE IS 0 IF CALLED FROM NAIVE ANALYSIS SUSPENSIONS FUNCTION, 1 IF CALLED FROM NEW ANALYSIS SUSPENSIONS FUNCTION
        ##Note that if a path is augmented as suspension, it's response must be bigger than zero
        
        edges = task.DAG.edges()
        
        for edge in edges:
            source = edge[0]
            target = edge[1]

            source_type = self.find_type_of_node(task, source)
            target_type = self.find_type_of_node(task, target)

            if(source_type == target_type):
                source_jobs = task.nodes_to_job_ids[source_type][source]
                target_jobs = task.nodes_to_job_ids[source_type][target]
                
                for i in range(len(source_jobs)):
                    _dict = {}
                    if(not MODE):
                        _dict = {"pred_tid": task_id,
                                 "pred_jid": source_jobs[i],
                                 "succ_tid": task_id,
                                 "succ_jid": target_jobs[i],
                                 "sus_min": 0,
                                 "sus_max": 0,
                                 "sus_min_first": 0,
                                 "sus_max_first": 0,
                                 "end_types:": None,
                                 "end_jobs": None,
                                 "edge_type": "only_precedence"}
                    else:
                        _dict = {"pred_tid": task_id,
                                 "pred_jid": source_jobs[i],
                                 "succ_tid": task_id,
                                 "succ_jid": target_jobs[i],
                                 "sus_min": 0,
                                 "sus_max": 0,
                                 "sus_min_first": 0,
                                 "sus_max_first": 0,
                                 "intermediate_path": None,
                                 "intermediate_path_types": None,
                                 "edge_type": "only_precedence"}
                    job_level_suspensions[source_type].append(_dict)

        for _type in job_level_suspensions:
            job_level_suspensions[_type] = sorted(job_level_suspensions[_type], key=lambda x: (x['succ_jid'], x['pred_jid'], x['pred_tid']))
            
        return job_level_suspensions


    ##This adds suspensions for a given set of tasks and periods
    def populate_with_precs(self):

        ##Where are non-suspension edges?        
        for task_id, task in enumerate(self.tasks, start=1):
                
            for key in task.task_level_suspensions_dict:

                suspension_edge_source_node = task.task_level_suspensions_dict[key]['source_node']
                suspension_edge_target_node = task.task_level_suspensions_dict[key]['target_node']
                suspension_time_start_node = suspension_edge_source_node
                suspension_time_end_nodes = []

                
                for path in task.task_level_suspensions_dict[key]['paths']:
                    suspension_time_end_node = path[len(path) - 1][0] ##Immediate predecessor of other type
                    suspension_time_end_nodes.append(suspension_time_end_node)


                ##Reduce list to unique elements if there are multiple paths starts and ends with the same node
                suspension_time_end_nodes = list(set(suspension_time_end_nodes))

                start_type = task.task_level_suspensions_dict[key]["type"]
                _dict = {}
                if(start_type not in task.job_level_suspensions):
                    task.job_level_suspensions[start_type] = []

                suspension_time_start_jobs = self.get_jobs_for_node(task, start_type, suspension_time_start_node)
                suspension_target_end_jobs = self.get_jobs_for_node(task, start_type, suspension_edge_target_node)
                suspension_time_end_types, suspension_time_end_jobs = self.get_jobs_list_for_nodes_list(task, suspension_time_end_nodes)
                susp_min, susp_max = utils.return_path_with_maximum_suspension_first_iter(task.DAG, task.task_level_suspensions_dict[key])

                for i in range(len(suspension_time_start_jobs)):
                    _dict = {"start_job": suspension_time_start_jobs,
                             "suspension_target_end_job": suspension_target_end_jobs,
                             "suspension_time_end_types": suspension_time_end_types,
                             "suspension_time_end_jobs": suspension_time_end_jobs,
                             "susp_min_first": susp_min,
                             "susp_max_first": susp_max} ##Sus min and sus max for now is path

                task.job_level_suspensions[start_type].append(_dict)
            task.job_level_suspensions = self.transform_to_individual(task_id, task.job_level_suspensions)
            task.job_level_suspensions = self.add_non_suspension_edges(task_id, task, task.job_level_suspensions, 0)


    def add_job_level_suspension_paths(self):
        ##Also add only precedence edges for new analysis
        for task_id, task in enumerate(self.tasks, start=1):
            for key in task.task_level_suspensions_dict:

                suspension_edge_source_node = task.task_level_suspensions_dict[key]['source_node']
                suspension_edge_target_node = task.task_level_suspensions_dict[key]['target_node']
                type_suspension_source = self.find_type_of_node(task, suspension_edge_source_node)
                type_suspension_target = self.find_type_of_node(task, suspension_edge_target_node)
                if(type_suspension_source != type_suspension_target):
                    print("Error: source and target nodes of a suspension are not the same, exiting..")
                    exit(1)
                    
                if(type_suspension_source not in task.job_level_suspension_paths):
                    task.job_level_suspension_paths[type_suspension_source] = []


                source_jobs = self.get_jobs_for_node(task, type_suspension_source, suspension_edge_source_node)
                target_jobs = self.get_jobs_for_node(task, type_suspension_source, suspension_edge_target_node)
                singular_paths_intermediate = task.task_level_suspensions_dict[key]['singular_paths_intermediate']

                for i in range(len(source_jobs)): ##At the end of each iteration, will register one suspension
                    _paths = []
                    _types = []
                    
                    for intermediate in singular_paths_intermediate: ##Paths in this list of lists will be combined as alternatives
                        _jobs_for_each_node = []
                        _types_for_each_node = []
                        
                        for node in intermediate:
                            node_type = self.find_type_of_node(task, node)
                            _jobs_for_each_node.append(self.get_jobs_for_node(task, node_type, node)[i])
                            _types_for_each_node.append(node_type)                

                        _paths.append(_jobs_for_each_node)
                        _types.append(_types_for_each_node)
                        
                    start_job = source_jobs[i]
                    end_job = target_jobs[i]
                    susp_min, susp_max = utils.return_path_with_maximum_suspension_first_iter(task.DAG, task.task_level_suspensions_dict[key])
                    _dict = {'pred_tid': task_id,
                             'pred_jid': start_job,
                             'succ_tid': task_id,
                             'succ_jid': end_job,
                             'sus_min' : susp_min,
                             'sus_max': susp_max,
                             'sus_min_first': susp_min,
                             'sus_max_first': susp_max,
                             'intermediate_path': _paths,
                             'intermediate_path_types':_types,
                             'edge_type': 'suspension'}
                    task.job_level_suspension_paths[type_suspension_source].append(_dict)
            task.job_level_suspension_paths = self.add_non_suspension_edges(task_id, task, task.job_level_suspension_paths, 1)
            
    def add_job_level_jitter_root_paths(self):

        for task_id, task in enumerate(self.tasks, start=1):
            for projection in task.task_level_projections:
                projection_dag = task.task_level_projections[projection]
                projection_len = len(projection_dag.nodes)
                projection_roots = [-1]


                if(projection != "0" and global_definitions.NEW_ANALYSIS == 1):
                    projection_roots = utils.find_roots_in_DAG(projection_dag)
                    if(len(projection_roots) != 0):
                        for i in range(len(projection_roots)):
                            projection_root = projection_roots[i]
                            cpu_root = self.find_task_level_cpu_root(task_id) 
                            paths = task.recursive_paths_between_two_nodes(cpu_root, projection_root)
                            for j in range(len(paths)):
                                paths[j] = paths[j][:-1]
                            if(projection not in task.job_level_jitter_root_paths):
                                task.job_level_jitter_root_paths[projection] = {}
                            projection_root_jobs = task.nodes_to_job_ids[projection][projection_root]
                            for k in range(len(projection_root_jobs)):
                                task.job_level_jitter_root_paths[projection][projection_root_jobs[k]] = {'jtypes': [], 'jids': []}
                                for l in range(len(paths)): ##If there are multiple paths, we will take max,min during computation
                                    path = paths[i]
                                    projection_path = []
                                    projection_path_types = []
                                    for m in range(len(path)):
                                        path_node = path[m]
                                        path_node_type = self.find_type_of_node(task, path_node)
                                        path_job = task.nodes_to_job_ids[path_node_type][path_node][k]
                                        projection_path.append(path_job)
                                        projection_path_types.append(path_node_type)
                                    task.job_level_jitter_root_paths[projection][projection_root_jobs[k]]['jtypes'].append(projection_path_types)
                                    task.job_level_jitter_root_paths[projection][projection_root_jobs[k]]['jids'].append(projection_path)
        
    
    def write_projections_to_file(self, _iter):
        
        for _type_alpha in global_definitions.TYPES_ALPHA:
            _type = global_definitions.TYPES_ALPHA[_type_alpha]
            
            if(global_definitions.NEW_ANALYSIS):
                affix = "NEW"
            else:
                affix = "NAIVE"
                    
            writer_jobs = open(_type_alpha + "_" + str(_iter) + "_" + affix + "_jobs.csv", "w+")
            writer_jobs.write("Task ID, Job ID, Arrival min, Arrival max, Cost min, Cost max, Deadline, Priority\n")
            writer_prec = open(_type_alpha + "_" + str(_iter) + "_" + affix + "_prec.csv", "w+")
            writer_prec.write("Predecessor TID, Predecessor JID, Successor TID, Successor JID, Sus_Min, Sus_Max\n")
            for task in self.tasks:
                for key in task.job_level_projections[_type]:
                    job = task.job_level_projections[_type][key]
                    writer_jobs.write(f"{job['Task_id']}, {job['Job_id']}, {job['a_min']}, {job['a_max']}, {job['c_min']}, {job['c_max']}, {job['deadline']}, {job['priority']}\n")
                if(not global_definitions.NEW_ANALYSIS):
                    for s in task.job_level_suspensions[_type]:
                        writer_prec.write(f"{s['pred_tid']}, {s['pred_jid']}, {s['succ_tid']}, {s['succ_jid']}, {s['sus_min']}, {s['sus_max']}\n")
                else:
                    for s in task.job_level_suspension_paths[_type]:
                        writer_prec.write(f"{s['pred_tid']}, {s['pred_jid']}, {s['succ_tid']}, {s['succ_jid']}, {s['sus_min']}, {s['sus_max']}\n")
            writer_jobs.close()
            writer_prec.close()

        

    def read_and_update_response_times(self, _iter):

        for _type_alpha in global_definitions.TYPES_ALPHA:
            _type = global_definitions.TYPES_ALPHA[_type_alpha]
            if(global_definitions.NEW_ANALYSIS):
                affix = "NEW"
            else:
                affix = "NAIVE"
            rta_file = _type_alpha + "_" + str(_iter) + "_" + affix + "_jobs.rta.csv"

            reader = open(rta_file, "r")
            lines = reader.readlines()
            lines = lines[1:]
            
            for line in lines:
                fields = line.strip("\n").split(",")
                task_id = int(fields[0])
                job_id = int(fields[1])
                bcct = int(fields[2])
                wcct = int(fields[3])
                bcrt = int(fields[4])
                wcrt = int(fields[5])
                if(global_definitions.NEW_ANALYSIS):
                    n_bcrt = int(fields[6])
                    n_wcrt = int(fields[7])

                for iter_task_id, task in enumerate(self.tasks, start = 1):
                    if(task_id != iter_task_id):
                        continue

                    task.job_level_projections[_type][job_id]['bcct'] = bcct
                    task.job_level_projections[_type][job_id]['wcct'] = wcct
                    task.job_level_projections[_type][job_id]['bcrt'] = bcrt
                    task.job_level_projections[_type][job_id]['wcrt'] = wcrt
                    if(global_definitions.NEW_ANALYSIS):
                        task.job_level_projections[_type][job_id]['n_bcrt'] = n_bcrt
                        task.job_level_projections[_type][job_id]['n_wcrt'] = n_wcrt


                
    def update_projections_new_analysis(self):

        for _type_alpha in global_definitions.TYPES_ALPHA:
            _type = global_definitions.TYPES_ALPHA[_type_alpha]
            if(_type != "0"): ##CPU projection doesn't have such case
                for task_id, task in enumerate(self.tasks):
                    for jitter_root in task.job_level_jitter_root_paths[_type]:
                        _dict = task.job_level_jitter_root_paths[_type][jitter_root]
                        new_amin_global = 2**20
                        new_amax_global = 0
                        for i in range(len(_dict['jids'])):
                            new_amin_local = 0
                            new_amax_local = 0
                            for k in range(len(_dict['jids'])):
                                one_job_type = _dict['jtypes'][i][k]
                                one_job_id = _dict['jids'][i][k]
                                new_amin_local = new_amin_local + task.job_level_projections[one_job_type][one_job_id]['n_bcrt']
                                new_amax_local = new_amax_local + task.job_level_projections[one_job_type][one_job_id]['n_wcrt']
                            if(new_amin_global < new_amin_local):
                                new_amin_global = new_amin_local
                            if(new_amax_global < new_amax_global):
                                new_amax_global = new_amax_local ##Do we have ?: +initial a_min
                    ##?new_amin_global: find_cpu_root + amin, new_amax_global: find_cpu_root + amax?

        ##Other suspensions
        for _type_alpha in global_definitions.TYPES_ALPHA:
            _type = global_definitions.TYPES_ALPHA[_type_alpha]
            for task_id, task in enumerate(self.tasks):
                for suspension in task.job_level_suspension_paths[_type]:
                    if(suspension['edge_type'] != 'only_precedence'):
                        new_sus_min = suspension['sus_min']
                        new_sus_max = suspension['sus_max']
                        intermediate_path = suspension['intermediate_path']
                        intermediate_path_types = suspension['intermediate_path_types']
                        for i in range(len(intermediate_path)):
                            path_sus_min = 0
                            path_sus_max = 0
                            _path = intermediate_path[i]
                            _types = intermediate_path_types[i]
                            for j in range(len(_path)):
                                job = _path[j]
                                job_type = _types[j]
                                path_sus_min = path_sus_min + task.job_level_projections[job_type][job]['n_bcrt']
                                path_sus_max = path_sus_max + task.job_level_projections[job_type][job]['n_wcrt']
                            if(path_sus_min < new_sus_min):
                                new_sus_min = path_sus_min
                            if(path_sus_max > new_sus_max):
                                new_sus_max = path_sus_max


                        suspension['sus_min'] = new_sus_min
                        suspension['sus_max'] = new_sus_max

                        
                            
    def update_projections(self):

        #self.print_all_jitter_roots()
        
        ##Jitter root case
        for _type_alpha in global_definitions.TYPES_ALPHA:
            _type = global_definitions.TYPES_ALPHA[_type_alpha]
            if(_type != "0"): ##CPU projection doesn't have such case 
                for task_id, task in enumerate(self.tasks):
                    for jitter_root in task.job_level_jitter_roots[_type]:
                        related_jobs = task.job_level_jitter_roots[_type][jitter_root]
                        related_bccts = []
                        related_wccts = []
                        for related_job in related_jobs:
                            bcct = task.job_level_projections["0"][related_job]['bcct'] ##Because it's guaranteed to be a CPU node
                            wcct = task.job_level_projections["0"][related_job]['wcct'] ##Because it's guaranteed to be a CPU node
                            related_bccts.append(bcct)
                            related_wccts.append(wcct)
                        new_bcct = min(related_bccts)
                        new_wcct = max(related_wccts)
                        task.job_level_projections[_type][jitter_root]['a_min'] = new_bcct
                        task.job_level_projections[_type][jitter_root]['a_max'] = new_wcct
                        #print("type:", _type, "new a_min:", new_bcct)
                        #print("type:", _type, "new a_max:", new_wcct)
                
        ##Other suspensions
        for _type_alpha in global_definitions.TYPES_ALPHA:
            _type = global_definitions.TYPES_ALPHA[_type_alpha]
            for task_id, task in enumerate(self.tasks):
                for suspension in task.job_level_suspensions[_type]:
                    if(suspension['edge_type'] != 'only_precedence'):
                        related_bccts = []
                        related_wccts = []
                        for i in range(len(suspension['end_types'])):
                            end_type = suspension['end_types'][i]
                            end_job = suspension['end_jobs'][i]
                            bcct = task.job_level_projections[end_type][end_job]['bcct']
                            wcct = task.job_level_projections[end_type][end_job]['wcct']
                            related_bccts.append(bcct)
                            related_wccts.append(wcct)
                        related_bcct = min(related_bccts)
                        #print("#######################")
                        #print(suspension)
                        #print("related_wccts:", related_wccts)
                        related_wcct = max(related_wccts)
                        start_job = suspension['pred_jid']
                        start_bcct = task.job_level_projections[_type][start_job]['bcct']
                        start_wcct = task.job_level_projections[_type][start_job]['wcct']
                        #print("type:", _type, "before sus_min:", suspension["sus_min"])
                        #print("type:", _type, "before sus_max:", suspension["sus_max"])
                        min_susp_candidate = related_bcct - start_wcct
                        min_susp = max(min_susp_candidate, suspension["sus_min_first"])
                        max_susp = related_wcct - start_bcct
                        suspension["sus_min"] = min_susp
                        suspension["sus_max"] = max_susp
                        #print("type:", _type, "new sus_min:", min_susp)
                        #print("type:", _type, "new sus_max:", max_susp)
                        #print("related_bcct:", related_bcct, "related_wcct:", related_wcct, "start_bcct:", start_bcct, "start_wcct:", start_wcct)
                        #print("related_wcct - start_bcct:", related_wcct - start_bcct)
                        #print("#######################")

    def check_exit(self, _iter, stop, average_suspension_times):
        
        if(iter == 0):
            return stop

        stop = True
        for task in self.tasks:
            for _type in task.job_level_suspensions:
                _len = len(task.job_level_suspensions[_type])
                for i in range(_len):
                    old_min = task.last_iteration_suspensions[_type][i]['sus_min']
                    old_max = task.last_iteration_suspensions[_type][i]['sus_max']

                    new_min = task.job_level_suspensions[_type][i]['sus_min']
                    new_max = task.job_level_suspensions[_type][i]['sus_max']
                    #/print("new_min:", new_min, "old_min:", old_min, "new_max:", new_max, "old_max:", old_max)
                    if(new_min < old_min):
                        stop = False
                    if(new_max > old_max):
                        stop = False

                    average_suspension_times[_iter].append(new_max - new_min)

        if(stop):
            print("Stop: Non-growing boundaries")

        return stop, average_suspension_times


    def check_exit_new_analysis(self, _iter, stop, average_suspension_times):
        
        if(iter == 0):
            return stop

        stop = True
        for task in self.tasks:
            for _type in task.job_level_suspension_paths:
                _len = len(task.job_level_suspension_paths[_type])
                for i in range(_len):
                    old_min = task.last_iteration_suspensions[_type][i]['sus_min']
                    old_max = task.last_iteration_suspensions[_type][i]['sus_max']

                    new_min = task.job_level_suspension_paths[_type][i]['sus_min']
                    new_max = task.job_level_suspension_paths[_type][i]['sus_max']
                    #/print("new_min:", new_min, "old_min:", old_min, "new_max:", new_max, "old_max:", old_max)
                    if(new_min < old_min):
                        stop = False
                    if(new_max > old_max):
                        stop = False

                    average_suspension_times[_iter].append(new_max - new_min)

        if(stop):
            print("Stop: Non-growing boundaries")

        return stop, average_suspension_times

    def check_exit_helper(self, _iter, stop, average_suspension_times):


        if(not global_definitions.NEW_ANALYSIS):
            stop, average_suspension_times = self.check_exit(_iter, stop, average_suspension_times)
        else:
            stop, average_suspension_times = self.check_exit_new_analysis(_iter, stop, average_suspension_times)

        return stop, average_suspension_times
    
    def report_ast(self, ast):

        _len = len(ast[0])
        for i in range(_len):
            if(len(ast[i]) == 0):
                return
            #print("ast[i]: ", ast[i])
            print("Iter,", i, ",avg,", sum(ast[i]) / _len)
    
    def check_result(self, result, stop, ast):

        print("Result:", result.stdout)
        if(int(result.stdout.split(",")[1]) == 0):
            print("Stop: Unschedulable set")
            stop = True
            #self.report_ast(ast)
            #exit(1)
        return stop
    
    def run_analysis(self):

        
        type_core_numbers = {"0": "2", "1": "2", "2": "2"}
        _iter = 0
        _new_cont = 0
        average_suspension_times = [[]]
        stop = False
        while(not stop):
            for _type_alpha in global_definitions.TYPES_ALPHA:
                _type = global_definitions.TYPES_ALPHA[_type_alpha]
                affix = ""
                
                if(global_definitions.NEW_ANALYSIS):
                    affix = "NEW"
                else:
                    affix = "NAIVE"
                    
                jobs_file_name = _type_alpha + "_" + str(_iter) + "_" + affix + "_jobs.csv"
                prec_file_name = _type_alpha + "_" + str(_iter) + "_" + affix + "_prec.csv"
                #result = subprocess.run(['./nptest', jobs_file_name, '-p', prec_file_name, '-r', '-m', type_core_numbers[_type], '-g'], capture_output=True, text=True)
                result = subprocess.run(['./nptest', jobs_file_name, '-p', prec_file_name, '-r', '-m', type_core_numbers[_type]], capture_output=True, text=True)

                if result.returncode == 0:
                    print(_type_alpha + " iteration " + str(_iter) + " successful")
                else:
                    print(_type_alpha + " iteration " + str(_iter) + " failed with error:", result.stderr)
                    exit(1)


                    
                stop = self.check_result(result, stop, average_suspension_times)
                if(stop):
                    self.report_ast(average_suspension_times)
                    exit(1)

            for task in self.tasks:
                if(not global_definitions.NEW_ANALYSIS):
                    task.last_iteration_projections = copy.deepcopy(task.job_level_projections)
                    task.last_iteration_suspensions = copy.deepcopy(task.job_level_suspensions)
                else:
                    task.last_iteration_projections = copy.deepcopy(task.job_level_projections)
                    task.last_iteration_suspensions = copy.deepcopy(task.job_level_suspension_paths)

            self.read_and_update_response_times(_iter)
            if(not global_definitions.NEW_ANALYSIS):
                self.update_projections()
            else:
                self.update_projections_new_analysis()

            
            stop, average_suspension_times = self.check_exit_helper(_iter, stop, average_suspension_times)
            nogo = True
            if(stop and global_definitions.NEW_ANALYSIS and _new_cont < 5 and nogo):
                stop = False
                _new_cont = _new_cont + 1
            average_suspension_times.append([])
            _iter = _iter + 1
            self.write_projections_to_file(_iter)
        self.report_ast(average_suspension_times)
        

def re_assign_dag_properties(DAG, deadline, period, priority):
    
    nodes = dict(DAG.nodes())
    edges = dict(DAG.edges())

    for node in nodes:
        #print("node: ", nodes[node])
        nodes[node]['_d'] = deadline
        nodes[node]['_p'] = priority
        nodes[node]['_q'] = 1 ##Single element for now
        nodes[node]['_amin'] = 0
        nodes[node]['_amax'] = 0

    return DAG

##Here we assume for now: sink and source are always CPU nodes. And after the first iteration first step, we are using response times.    
if __name__ == "__main__":

    if(len(sys.argv) > 1):
        global_definitions.NEW_ANALYSIS = int(sys.argv[1])

    ##Inıtial
    '''
    #def __init__(self, DAG, period, deadline):
    DAG1, DAG2, DAG3, DAG4, DAG5, DAG6 = test_tasks_0.return_tasks()
    TASK1 = TASK(DAG1, 350, 350)
    TASK3 = TASK(DAG5, 70, 70)
    TASK4 = TASK(DAG5, 350, 350)
    TASK5 = TASK(DAG5, 70, 70)
    TASK6 = TASK(DAG5, 70, 70)
    TASK7 = TASK(DAG5, 70, 70)
    TASK8 = TASK(DAG5, 70, 70)
    TASK9 = TASK(DAG5, 70, 70)
    TASK10 = TASK(DAG5, 70, 70)
    TASK11 = TASK(DAG5, 70, 70)
    TASK12 = TASK(DAG5, 70, 70)
    TASK13 = TASK(DAG5, 70, 70)
    TASK14 = TASK(DAG5, 70, 70)
    TASK15 = TASK(DAG5, 70, 70)
    TASK2 = TASK(DAG4, 350, 350)
    #TASK3 = TASK(DAG5, 350, 350)
    TASKSET_ZERO = TASKSET([TASK2, TASK4]) ##Populates data structures within TASKs w.r.to resulted hyperperiod
    '''

    ##Empirically generated tasks
    '''
    a_DAG1, task_time_min, task_time_max = task_finder.ret_dag_task()
    a_DAG1_deadline = 100 * task_time_max
    a_DAG1_period = 100 * task_time_max
    a_DAG1_priority = 1
    a_DAG1 = re_assign_dag_properties(a_DAG1, a_DAG1_deadline, a_DAG1_period, a_DAG1_priority)

    nodes = dict(a_DAG1.nodes())
    print(nodes["CPU_1"])
    
    a_DAG2, task_time_min, task_time_max = task_finder.ret_dag_task()
    a_DAG2_deadline = 100 * task_time_max
    a_DAG2_period = 100 * task_time_max
    a_DAG2_priority = 1
    a_DAG2 = re_assign_dag_properties(a_DAG2, a_DAG2_deadline, a_DAG2_period, a_DAG2_priority)

    
    
    TASK1 = TASK(a_DAG1, a_DAG1_deadline, a_DAG1_period)
    print("TASK1 created")
    TASK2 = TASK(a_DAG1, a_DAG1_deadline, a_DAG1_period)
    print("TASK2 created")
    TASKSET_ZERO = TASKSET([TASK1, TASK2]) ##Populates data structures within TASKs w.r.to resulted hyperperiod
    '''
    ##Usage of some functions

    #utils.print_task_level_suspensions_dict(TASK1)
    #utils.visualize_bfs_w_depth(DAG1)
    #utils.visualize_bfs_w_depth(DAG4)

    ##Limited tasks
    DAG1, DAG2 = test_tasks_limited.return_tasks()

    TASK1 = TASK(DAG1, 100, 100)
    TASK2 = TASK(DAG1, 100, 100)

    TASKSET_ZERO = TASKSET([TASK1]) ##Populates data structures within TASKs w.r.to resulted hyperperiod
