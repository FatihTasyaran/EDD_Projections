import networkx as nx
import math
import get_four_basic_tasks
import test_tasks_0
import utils_refactored as utils
import subprocess
import global_definitions

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
        self.job_level_jitter_roots = {} ##OK
        ##
        self.nodes_to_job_ids = {} ##OK
        
        

        

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
        self.write_projections_to_file()

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
                                 "priority": node_info["_p"]}
                        task.job_level_projections[projection][job_id] = _dict
                        
                ##For non-CPU projections, add suspension as jitter
                if(projection != "0"):
                    if(projection not in task.job_level_jitter_roots):
                        task.job_level_jitter_roots[projection] = {}
                    projection_roots = utils.find_roots_in_DAG(projection_dag)
                    if(len(projection_roots) != 0):
                        for i in range(len(projection_roots)):
                            one_root = projection_roots[i]
                            one_root_jobs = task.nodes_to_job_ids[projection][one_root]
                            edges = list(task.DAG.in_edges(one_root))
                            incoming_all = []
                            for edge in edges:
                                incoming = edge[0]
                                incoming_jobs = task.nodes_to_job_ids["0"][incoming]
                                incoming_all.append(incoming_jobs)
                            if(len(one_root_jobs) != len(incoming_jobs)):
                                print("Error: Unequal number of jobs during jitter root mapping, exiting..")
                                exit(1)

                            for i in range(len(one_root_jobs)):
                                task.job_level_jitter_roots[projection][one_root_jobs[i]] = []
                                for j in range(len(incoming_all)):
                                    task.job_level_jitter_roots[projection][one_root_jobs[i]].append(incoming_all[j][i])
                

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
                              "end_types": end_types,
                              "end_jobs": end_jobs,
                              "edge_type": "suspension"}
                    new[key].append(to_add)

        return new

    def add_non_suspension_edges(self, task_id, task, job_level_suspensions):
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
                    _dict = {"pred_tid": task_id,
                             "pred_jid": source_jobs[i],
                             "succ_tid": task_id,
                             "succ_jid": target_jobs[i],
                             "sus_min": 0,
                             "sus_max": 0,
                             "end_types:": None,
                             "end_jobs": None,
                             "edge_type": "only_precedence"}
                    job_level_suspensions[source_type].append(_dict)

        for _type in job_level_suspensions:
            job_level_suspensions[_type] = sorted(job_level_suspensions[_type], key=lambda x: (x['succ_jid'], x['pred_jid'], x['pred_tid']))
            
        return job_level_suspensions
    
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
            task.job_level_suspensions = self.add_non_suspension_edges(task_id, task, task.job_level_suspensions)
            
                
    def write_projections_to_file(self):
        
        for _type_alpha in global_definitions.TYPES_ALPHA:
            _type = global_definitions.TYPES_ALPHA[_type_alpha]
            writer_jobs = open(_type_alpha + "_jobs.csv", "w+")
            writer_jobs.write("Task ID, Job ID, Arrival min, Arrival max, Cost min, Cost max, Deadline, Priority\n")
            writer_prec = open(_type_alpha + "_prec.csv", "w+")
            writer_prec.write("Predecessor TID, Predecessor JID, Successor TID, Successor JID, Sus_Min, Sus_Max\n")
            for task in self.tasks:
                for key in task.job_level_projections[_type]:
                    job = task.job_level_projections[_type][key]
                    writer_jobs.write(f"{job['Task_id']}, {job['Job_id']}, {job['a_min']}, {job['a_max']}, {job['c_min']}, {job['c_max']}, {job['deadline']}, {job['priority']}\n")
                for s in task.job_level_suspensions[_type]:
                    writer_prec.write(f"{s['pred_tid']}, {s['pred_jid']}, {s['succ_tid']}, {s['succ_jid']}, {s['sus_min']}, {s['sus_max']}\n")


    def read_and_update_response_times(self, _type):

        ##Huh
                    

    def run_analysis(self):

        iter = 0
        
        for _type_alpha in global_definitions.TYPES_ALPHA:
            _type = global_definitions.TYPES_ALPHA[_type_alpha]
            jobs_file_name = _type + "_jobs.csv"
            prec_file_name = _type + "_prec.csv"
        
            result = subprocess.run(['./nptest', jobs_file_name, '-p', prec_file_name, '-r'], capture_output=True, text=True)

            if result.returncode == 0:
                print(_type + " " + str(iter) + " Iteration successful")
            else:
                print(_type + " " + str(iter) + " iteration failed with error:", result.stderr)
                exit(1)

        for _type_alpha in global_definitions.TYPES_ALPHA:
            _type = global_definitions.TYPES_ALPHA[_type_alpha]
            self.update_response_times(_type)

        for _type_alpha in global_definitions.TYPES_ALPHA:
            _type = global_definitions.TYPES_ALPHA[_type_alpha]
            self.update_projections(_type)
        
                                    
    
##Here we assume for now: sink and source are always CPU nodes. And after the first iteration first step, we are using response times.    
if __name__ == "__main__":

    #def __init__(self, DAG, period, deadline):
    DAG1, DAG2, DAG3, DAG4, DAG5= test_tasks_0.return_tasks()
    TASK1 = TASK(DAG1, 350, 350)
    TASK2 = TASK(DAG4, 90, 90)
    TASK3 = TASK(DAG5, 160, 160)
    TASKSET_ZERO = TASKSET([TASK1, TASK2, TASK3]) ##Populates data structures within TASKs w.r.to resulted hyperperiod

    

    ##Usage of some functions

    #utils.print_task_level_suspensions_dict(TASK1)
    #utils.visualize_bfs_w_depth(DAG1)
    

    
